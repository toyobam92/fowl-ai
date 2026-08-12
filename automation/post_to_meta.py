#!/usr/bin/env python3
"""Post this week's Nova video scripts to Facebook + Threads via their
respective Graph-family APIs.

Only ever invoked by telegram-approve.yml in response to an explicit
"PUBLISH <PR#>" reply, after that PR is already merged -- mirrors the same
"never auto-publish, always gate on an explicit human reply" pattern used
for EmailOctopus (SCHEDULE <PR#>). Both are real, supported,
token-authenticated APIs, so both can post headlessly with no App
Review/browser-login bot-check to dodge.

Instagram is deliberately NOT posted here, even though the Graph API has
an equivalent endpoint (post_instagram_video, removed 2026-08-12) --
instagram_business_content_publish requires Meta App Review, which
requires becoming an irreversible "Tech Provider" first (paused
2026-08-11, see project memory). Rather than have this script fail on
Instagram every single day until that's resolved, Instagram is treated
exactly like TikTok: posted manually through a live browser session
(Meta Business Suite's composer posts to Facebook + Instagram together
already, confirmed working 2026-08-12), flagged in the same "still needs
posting" reminder auto-publish-nova.yml sends after a successful run.

Reads/writes automation/social-state.json directly. Does not touch git --
the caller (telegram-approve.yml) commits+pushes whatever this script
changes on disk, same as it already does for automation/inbox.json.

video_path is a placeholder until a post's video has actually rendered --
any post whose video_path is still null is skipped with a clear log line,
never crashed on and never silently posted as broken.
"""
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

STATE_PATH = "automation/social-state.json"
GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
THREADS_API_BASE = "https://graph.threads.net/v1.0"

# Not a known requirement for the Graph API the way it was for EmailOctopus's
# Cloudflare WAF (see sync-signups.yml / schedule-watchdog.yml) -- but a
# default urllib User-Agent has bitten this repo enough times that setting an
# explicit one here too is cheap insurance, not a fix for a confirmed issue.
USER_AGENT = "fowlai-post-to-meta/1.0"

# How long to wait for a Threads media container to finish processing
# before giving up on that one post. Video containers process
# asynchronously server-side; publishing before they're FINISHED fails.
CONTAINER_POLL_ATTEMPTS = 10
CONTAINER_POLL_DELAY_SECONDS = 6


def load_state():
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def graph_request(path, params, method="POST", base=GRAPH_API_BASE):
    """POST/GET against a Graph-family API -- Facebook and Threads share
    this exact request/error shape, just different hosts. Raises
    RuntimeError with the API's own error message (not just the raw
    HTTPError) so failures are diagnosable from the Telegram/Action-log
    output alone."""
    url = f"{base}/{path}"
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(
        url if method == "GET" else url,
        data=None if method == "GET" else data,
        method=method,
        headers={"User-Agent": USER_AGENT},
    )
    if method == "GET":
        req.full_url = f"{url}?{data.decode()}"
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body).get("error", {}).get("message", body)
        except json.JSONDecodeError:
            err = body
        raise RuntimeError(f"{base} {method} {path} failed ({e.code}): {err}") from e


def post_facebook_video(post, page_id, page_token):
    """Facebook Page feed: upload-by-URL, since video_path is expected to be
    a publicly hosted URL (HeyGen's render output), not a local file --
    avoids needing a multipart upload path here."""
    result = graph_request(
        f"{page_id}/videos",
        {
            "access_token": page_token,
            "file_url": post["video_path"],
            "description": post["caption"],
        },
    )
    if "id" not in result:
        raise RuntimeError(f"Facebook video post returned no id: {result}")
    return result["id"]


def post_threads_video(post, threads_user_id, threads_token):
    """Threads' content publishing API mirrors Instagram's: create a media
    container, wait for it to finish processing, then publish it. Unlike
    Instagram, threads_content_publish needs no App Review -- confirmed
    working under Standard Access, see project memory."""
    container = graph_request(
        f"{threads_user_id}/threads",
        {
            "access_token": threads_token,
            "media_type": "VIDEO",
            "video_url": post["video_path"],
            "text": post["caption"],
        },
        base=THREADS_API_BASE,
    )
    creation_id = container.get("id")
    if not creation_id:
        raise RuntimeError(f"Threads container creation returned no id: {container}")

    for attempt in range(CONTAINER_POLL_ATTEMPTS):
        status = graph_request(
            creation_id,
            {"access_token": threads_token, "fields": "status"},
            method="GET",
            base=THREADS_API_BASE,
        )
        code = status.get("status")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Threads container {creation_id} failed processing: {status}")
        time.sleep(CONTAINER_POLL_DELAY_SECONDS)
    else:
        raise RuntimeError(
            f"Threads container {creation_id} never finished processing "
            f"after {CONTAINER_POLL_ATTEMPTS} attempts -- not publishing a half-ready post."
        )

    publish = graph_request(
        f"{threads_user_id}/threads_publish",
        {"access_token": threads_token, "creation_id": creation_id},
        base=THREADS_API_BASE,
    )
    if "id" not in publish:
        raise RuntimeError(f"Threads threads_publish returned no id: {publish}")
    return publish["id"]


def main():
    page_token = os.environ.get("META_PAGE_ACCESS_TOKEN")
    page_id = os.environ.get("META_PAGE_ID")
    missing = [
        name
        for name, val in (
            ("META_PAGE_ACCESS_TOKEN", page_token),
            ("META_PAGE_ID", page_id),
        )
        if not val
    ]
    if missing:
        print(f"Missing required env var(s): {', '.join(missing)} -- cannot post to Facebook.")
        sys.exit(1)

    # Threads is optional -- if these aren't set, skip Threads for this run
    # rather than fail the whole script (Facebook posting shouldn't depend
    # on Threads credentials existing).
    threads_token = os.environ.get("META_THREADS_ACCESS_TOKEN")
    threads_user_id = os.environ.get("META_THREADS_USER_ID")
    threads_enabled = bool(threads_token and threads_user_id)
    if not threads_enabled:
        print("META_THREADS_ACCESS_TOKEN/META_THREADS_USER_ID not set -- skipping Threads this run.")

    state = load_state()
    any_attempted = False
    any_failed = False

    today = datetime.date.today().isoformat()

    for post in state.get("posts", []):
        # Label posts by whatever identifying fields they actually have --
        # the original PR #13 seed data used hookId, the nova-daily-prep
        # pipeline (added later) uses topic/publish_date instead. Neither
        # schema is guaranteed present on every post, so never assume one.
        label = post.get("day", "?")
        if post.get("hookId") is not None:
            label += f" (hook {post['hookId']})"
        elif post.get("topic"):
            label += f" ({post['topic']})"

        published = post.setdefault("platforms_published", {"facebook": False, "instagram": False, "tiktok": False})
        # Old-schema posts (seeded before Threads support existed) have a
        # platforms_published dict already, just without this key --
        # setdefault on the dict itself only helps when the whole key is
        # missing, so this needs its own explicit default.
        published.setdefault("threads", False)

        needs_facebook = not published.get("facebook")
        needs_threads = threads_enabled and not published.get("threads")

        if not needs_facebook and not needs_threads:
            print(f"{label}: already posted to Facebook + Threads, skipping.")
            continue

        # publish_date gates the nova-daily-prep pipeline's day-before
        # approval model: a video can finish rendering and land in this
        # file well before its scheduled slot, but it should only actually
        # post on (or after, if this run was somehow missed) that date.
        # Posts without publish_date (the legacy PUBLISH <PR#> flow, and
        # PR #13's original seed data) post immediately, same as before --
        # this field is opt-in, not a new requirement.
        publish_date = post.get("publish_date")
        if publish_date and publish_date > today:
            print(f"{label}: scheduled for {publish_date}, not due yet -- skipping.")
            continue

        if not post.get("video_path"):
            # The whole point of this guard: video files aren't ready yet
            # (HeyGen API key still pending as of 2026-08-11). Skip cleanly
            # rather than crash or post a broken/empty request.
            print(f"{label}: video_path is null, skipping -- video not rendered yet.")
            continue

        any_attempted = True

        if needs_facebook:
            try:
                fb_id = post_facebook_video(post, page_id, page_token)
                published["facebook"] = True
                print(f"{label}: posted to Facebook (post id {fb_id}).")
            except RuntimeError as e:
                any_failed = True
                print(f"{label}: Facebook post FAILED -- {e}")

        if needs_threads:
            try:
                threads_id = post_threads_video(post, threads_user_id, threads_token)
                published["threads"] = True
                print(f"{label}: posted to Threads (post id {threads_id}).")
            except RuntimeError as e:
                any_failed = True
                print(f"{label}: Threads post FAILED -- {e}")

    save_state(state)

    if not any_attempted:
        print("Nothing to post -- either everything's already published, nothing's due yet, or no videos are rendered yet.")

    # Tagged summary line so callers (auto-publish-nova.yml) can decide
    # whether to notify without grepping prose output -- same pattern as
    # check_nova_render.py's RESULT: line.
    if any_failed:
        print("RESULT:failed:")
    elif any_attempted:
        print("RESULT:posted:")
    else:
        print("RESULT:nothing:")

    # Non-zero exit only on an actual posting failure so the caller
    # (telegram-approve.yml) can tell "ran but nothing failed" apart from
    # "a post genuinely errored out" and notify accordingly.
    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
