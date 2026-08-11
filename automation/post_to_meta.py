#!/usr/bin/env python3
"""Post this week's Nova video scripts to Facebook + Instagram via the Meta Graph API.

Only ever invoked by telegram-approve.yml in response to an explicit
"PUBLISH <PR#>" reply, after that PR is already merged -- mirrors the same
"never auto-publish, always gate on an explicit human reply" pattern used
for EmailOctopus (SCHEDULE <PR#>). Facebook + Instagram can be posted
headlessly because the Graph API is a real, supported, token-authenticated
API -- unlike EmailOctopus (no public send API) or TikTok (no
programmatic posting without a business review most creator accounts
don't have), which both need an interactive, human-driven browser
session instead. See automation/social-state.json and
.claude/skills/weekly-social-post/SKILL.md for the rest of the pipeline.

Reads/writes automation/social-state.json directly. Does not touch git --
the caller (telegram-approve.yml) commits+pushes whatever this script
changes on disk, same as it already does for automation/inbox.json.

video_path is a placeholder until Nova's videos are actually rendered
(blocked on a HeyGen API key, as of 2026-08-11) -- any post whose
video_path is still null is skipped with a clear log line, never crashed
on and never silently posted as broken.
"""
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

# Not a known requirement for the Graph API the way it was for EmailOctopus's
# Cloudflare WAF (see sync-signups.yml / schedule-watchdog.yml) -- but a
# default urllib User-Agent has bitten this repo enough times that setting an
# explicit one here too is cheap insurance, not a fix for a confirmed issue.
USER_AGENT = "fowlai-post-to-meta/1.0"

# How long to wait for an Instagram media container to finish processing
# before giving up on that one post. Video containers process
# asynchronously server-side; publishing before they're FINISHED fails.
IG_CONTAINER_POLL_ATTEMPTS = 10
IG_CONTAINER_POLL_DELAY_SECONDS = 6


def load_state():
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def graph_request(path, params, method="POST"):
    """POST/GET against the Graph API. Raises RuntimeError with the Graph
    API's own error message (not just the raw HTTPError) so failures are
    diagnosable from the Telegram/Action-log output alone."""
    url = f"{GRAPH_API_BASE}/{path}"
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
        raise RuntimeError(f"Graph API {method} {path} failed ({e.code}): {err}") from e


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


def post_instagram_video(post, ig_user_id, page_token):
    """Instagram's content publishing API is a two-step container-then-publish
    flow: create a media container, wait for it to finish processing, then
    publish it. Posting REELS is the correct media_type for a short vertical
    video like Nova's episodes (a plain video post is deprecated in favor of
    Reels for this content shape)."""
    container = graph_request(
        f"{ig_user_id}/media",
        {
            "access_token": page_token,
            "media_type": "REELS",
            "video_url": post["video_path"],
            "caption": post["caption"],
        },
    )
    creation_id = container.get("id")
    if not creation_id:
        raise RuntimeError(f"Instagram container creation returned no id: {container}")

    for attempt in range(IG_CONTAINER_POLL_ATTEMPTS):
        status = graph_request(
            creation_id,
            {"access_token": page_token, "fields": "status_code"},
            method="GET",
        )
        code = status.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise RuntimeError(f"Instagram container {creation_id} failed processing: {status}")
        time.sleep(IG_CONTAINER_POLL_DELAY_SECONDS)
    else:
        raise RuntimeError(
            f"Instagram container {creation_id} never finished processing "
            f"after {IG_CONTAINER_POLL_ATTEMPTS} attempts -- not publishing a half-ready post."
        )

    publish = graph_request(
        f"{ig_user_id}/media_publish",
        {"access_token": page_token, "creation_id": creation_id},
    )
    if "id" not in publish:
        raise RuntimeError(f"Instagram media_publish returned no id: {publish}")
    return publish["id"]


def main():
    page_token = os.environ.get("META_PAGE_ACCESS_TOKEN")
    page_id = os.environ.get("META_PAGE_ID")
    ig_user_id = os.environ.get("META_IG_USER_ID")
    missing = [
        name
        for name, val in (
            ("META_PAGE_ACCESS_TOKEN", page_token),
            ("META_PAGE_ID", page_id),
            ("META_IG_USER_ID", ig_user_id),
        )
        if not val
    ]
    if missing:
        print(f"Missing required env var(s): {', '.join(missing)} -- cannot post to Meta.")
        sys.exit(1)

    state = load_state()
    any_attempted = False
    any_failed = False

    for post in state.get("posts", []):
        published = post.setdefault("platforms_published", {"facebook": False, "instagram": False, "tiktok": False})
        needs_facebook = not published.get("facebook")
        needs_instagram = not published.get("instagram")

        if not needs_facebook and not needs_instagram:
            print(f"{post['day']} (hook {post['hookId']}): already posted to Facebook + Instagram, skipping.")
            continue

        if not post.get("video_path"):
            # The whole point of this guard: video files aren't ready yet
            # (HeyGen API key still pending as of 2026-08-11). Skip cleanly
            # rather than crash or post a broken/empty request.
            print(f"{post['day']} (hook {post['hookId']}): video_path is null, skipping -- video not rendered yet.")
            continue

        any_attempted = True

        if needs_facebook:
            try:
                fb_id = post_facebook_video(post, page_id, page_token)
                published["facebook"] = True
                print(f"{post['day']}: posted to Facebook (post id {fb_id}).")
            except RuntimeError as e:
                any_failed = True
                print(f"{post['day']}: Facebook post FAILED -- {e}")

        if needs_instagram:
            try:
                ig_id = post_instagram_video(post, ig_user_id, page_token)
                published["instagram"] = True
                print(f"{post['day']}: posted to Instagram (media id {ig_id}).")
            except RuntimeError as e:
                any_failed = True
                print(f"{post['day']}: Instagram post FAILED -- {e}")

    save_state(state)

    if not any_attempted:
        print("Nothing to post -- either everything's already published or no videos are rendered yet.")

    # Non-zero exit only on an actual posting failure so the caller
    # (telegram-approve.yml) can tell "ran but nothing failed" apart from
    # "a post genuinely errored out" and notify accordingly.
    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
