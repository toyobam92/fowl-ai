#!/usr/bin/env python3
"""Post this week's Nova video scripts to Facebook, Threads, and Instagram
via their APIs.

Only ever invoked by telegram-approve.yml in response to an explicit
"PUBLISH <PR#>" reply, after that PR is already merged -- mirrors the same
"never auto-publish, always gate on an explicit human reply" pattern used
for EmailOctopus (SCHEDULE <PR#>). All three can be posted headlessly
because each has a real, supported, token-authenticated API under
Standard Access with no App Review needed for this account.

Instagram posts via the newer Instagram-Login API product
(graph.instagram.com, not graph.facebook.com) -- a separate credential
and host from the classic Facebook-Login Instagram Graph API, which
remained genuinely blocked behind App Review (see project memory,
2026-08-12 through 2026-08-14). This is not the same integration that
was previously ruled out.

TikTok is still posted manually through a live browser session -- no
headless posting exists for it (same Cloudflare/bot-detection risk that
ruled out headless EmailOctopus scheduling), flagged in the same "still
needs posting" reminder auto-publish-nova.yml sends after a successful
post elsewhere.

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
IG_API_BASE = f"https://graph.instagram.com/{GRAPH_API_VERSION}"

# Threads and Instagram video containers both process asynchronously (same
# lineage -- Instagram Graph API's container-then-publish design, which
# Threads' API was modeled on) -- poll a bounded number of times rather
# than either a fixed sleep (often too short) or an unbounded loop (could
# hang the Action). If it's still not FINISHED after this many attempts,
# fail cleanly; the post stays unpublished and the next day's
# auto-publish-nova.yml run retries it from scratch.
THREADS_POLL_ATTEMPTS = 12
THREADS_POLL_INTERVAL_SECONDS = 5
IG_POLL_ATTEMPTS = 12
IG_POLL_INTERVAL_SECONDS = 5

# Not a known requirement for the Graph API the way it was for EmailOctopus's
# Cloudflare WAF (see sync-signups.yml / schedule-watchdog.yml) -- but a
# default urllib User-Agent has bitten this repo enough times that setting an
# explicit one here too is cheap insurance, not a fix for a confirmed issue.
USER_AGENT = "fowlai-post-to-meta/1.0"

# Post a missed slot if it's only a day late (AI news survives that);
# anything staler is held for a human decision. See the days_late guard.
MAX_DAYS_LATE = 1


def load_state():
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def api_request(base, path, params, method="POST"):
    """POST/GET against a Graph-family API (Facebook, Threads, or
    Instagram -- same request/error shape). Raises RuntimeError with the
    API's own error message (not just the raw HTTPError) so failures are
    diagnosable from the Telegram/Action-log output alone."""
    url = f"{base}/{path}"
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(
        url,
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


def graph_request(path, params, method="POST"):
    return api_request(GRAPH_API_BASE, path, params, method)


def threads_request(path, params, method="POST"):
    return api_request(THREADS_API_BASE, path, params, method)


def ig_request(path, params, method="POST"):
    return api_request(IG_API_BASE, path, params, method)


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
    """Threads container-then-publish flow: create a video container, poll
    until Threads finishes processing it server-side, then publish. Mirrors
    Instagram Graph API's video container design (same lineage at Meta)."""
    create = threads_request(
        f"{threads_user_id}/threads",
        {
            "access_token": threads_token,
            "media_type": "VIDEO",
            "video_url": post["video_path"],
            "text": post["caption"],
        },
    )
    creation_id = create.get("id")
    if not creation_id:
        raise RuntimeError(f"Threads container creation returned no id: {create}")

    status = None
    for _ in range(THREADS_POLL_ATTEMPTS):
        time.sleep(THREADS_POLL_INTERVAL_SECONDS)
        check = threads_request(
            str(creation_id),
            {"access_token": threads_token, "fields": "status,error_message"},
            method="GET",
        )
        status = check.get("status")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError(f"Threads container processing failed: {check.get('error_message', check)}")
    else:
        raise RuntimeError(f"Threads container still {status!r} after {THREADS_POLL_ATTEMPTS} polls -- giving up for this run.")

    publish = threads_request(
        f"{threads_user_id}/threads_publish",
        {"access_token": threads_token, "creation_id": creation_id},
    )
    if "id" not in publish:
        raise RuntimeError(f"Threads publish returned no id: {publish}")
    return publish["id"]


def post_instagram_video(post, ig_user_id, ig_token):
    """Instagram container-then-publish flow via the newer Instagram-Login
    API (graph.instagram.com) -- media_type=REELS is required for video
    posts to this account's feed; Instagram consolidated all video posting
    into Reels, there's no separate plain-video feed post type anymore."""
    create = ig_request(
        f"{ig_user_id}/media",
        {
            "access_token": ig_token,
            "media_type": "REELS",
            "video_url": post["video_path"],
            "caption": post["caption"],
        },
    )
    creation_id = create.get("id")
    if not creation_id:
        raise RuntimeError(f"Instagram container creation returned no id: {create}")

    status = None
    for _ in range(IG_POLL_ATTEMPTS):
        time.sleep(IG_POLL_INTERVAL_SECONDS)
        check = ig_request(
            str(creation_id),
            {"access_token": ig_token, "fields": "status_code,status"},
            method="GET",
        )
        status = check.get("status_code")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError(f"Instagram container processing failed: {check.get('status', check)}")
    else:
        raise RuntimeError(f"Instagram container still {status!r} after {IG_POLL_ATTEMPTS} polls -- giving up for this run.")

    publish = ig_request(
        f"{ig_user_id}/media_publish",
        {"access_token": ig_token, "creation_id": creation_id},
    )
    if "id" not in publish:
        raise RuntimeError(f"Instagram publish returned no id: {publish}")
    return publish["id"]


def main():
    page_token = os.environ.get("META_PAGE_ACCESS_TOKEN")
    page_id = os.environ.get("META_PAGE_ID")
    threads_token = os.environ.get("META_THREADS_ACCESS_TOKEN")
    threads_user_id = os.environ.get("META_THREADS_USER_ID")
    ig_token = os.environ.get("META_IG_ACCESS_TOKEN")
    ig_user_id = os.environ.get("META_IG_USER_ID")
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
    # Threads/Instagram credentials are optional-ish in the sense that
    # their absence only disables that platform for this run, not the
    # whole script -- Facebook posting must never be held hostage to a
    # gap in either config.
    threads_configured = bool(threads_token and threads_user_id)
    if not threads_configured:
        print("META_THREADS_ACCESS_TOKEN/META_THREADS_USER_ID not set -- skipping Threads this run.")
    ig_configured = bool(ig_token and ig_user_id)
    if not ig_configured:
        print("META_IG_ACCESS_TOKEN/META_IG_USER_ID not set -- skipping Instagram this run.")

    state = load_state()
    any_attempted = False
    any_failed = False
    late_notes = []
    stale_notes = []

    today_date = datetime.date.today()
    today = today_date.isoformat()

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
        # Existing entries committed before Threads support won't have this
        # key at all -- setdefault on the dict itself only helps brand-new
        # posts, so backfill it explicitly for posts that already exist.
        published.setdefault("threads", False)

        needs_facebook = not published.get("facebook")
        needs_threads = threads_configured and not published.get("threads")
        needs_instagram = ig_configured and not published.get("instagram")

        if not needs_facebook and not needs_threads and not needs_instagram:
            print(f"{label}: already posted everywhere this script handles, skipping.")
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

        # How late is this? A slot can be missed entirely when the APPROVE
        # (and therefore the render) lands after the publish window closes
        # -- that happened for 2026-08-21, approved ~3h after the 7:30pm ET
        # cron and posted the next evening with nothing saying so. One day
        # late is still worth posting for AI news; staler than that gets
        # held for a human call rather than quietly shipping old news.
        days_late = 0
        if publish_date:
            try:
                days_late = (today_date - datetime.date.fromisoformat(publish_date)).days
            except ValueError:
                days_late = 0
        if days_late > MAX_DAYS_LATE:
            stale_notes.append(f"{label} (scheduled {publish_date}, {days_late} days late)")
            print(f"{label}: scheduled for {publish_date} -- {days_late} days late, holding for a decision instead of posting stale news.")
            continue

        if not post.get("video_path"):
            # The whole point of this guard: video files aren't ready yet
            # (HeyGen API key still pending as of 2026-08-11). Skip cleanly
            # rather than crash or post a broken/empty request.
            print(f"{label}: video_path is null, skipping -- video not rendered yet.")
            continue

        if needs_facebook:
            any_attempted = True
            try:
                fb_id = post_facebook_video(post, page_id, page_token)
                published["facebook"] = True
                print(f"{label}: posted to Facebook (post id {fb_id}).")
            except RuntimeError as e:
                any_failed = True
                print(f"{label}: Facebook post FAILED -- {e}")

        if needs_threads:
            any_attempted = True
            try:
                threads_id = post_threads_video(post, threads_user_id, threads_token)
                published["threads"] = True
                print(f"{label}: posted to Threads (post id {threads_id}).")
            except RuntimeError as e:
                any_failed = True
                print(f"{label}: Threads post FAILED -- {e}")

        if needs_instagram:
            any_attempted = True
            try:
                ig_id = post_instagram_video(post, ig_user_id, ig_token)
                published["instagram"] = True
                print(f"{label}: posted to Instagram (post id {ig_id}).")
            except RuntimeError as e:
                any_failed = True
                print(f"{label}: Instagram post FAILED -- {e}")

        # Stamp when this actually went out. Without it social-state.json
        # only carries the *scheduled* date, so a slipped post reads as if
        # it went out on time -- which also silently pollutes the
        # posting-time experiment in analytics/EXPERIMENTS.md.
        if published.get("facebook") or published.get("threads") or published.get("instagram"):
            post.setdefault("posted_at", datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
            if days_late > 0:
                day_word = "day" if days_late == 1 else "days"
                late_notes.append(f"{label} ({days_late} {day_word} late, scheduled {publish_date})")

    save_state(state)

    if not any_attempted:
        print("Nothing to post -- either everything's already published, nothing's due yet, or no videos are rendered yet.")

    # Tagged summary line so callers (auto-publish-nova.yml) can decide
    # whether to notify without grepping prose output -- same pattern as
    # check_nova_render.py's RESULT: line.
    detail = "; ".join(late_notes)
    if any_failed:
        print(f"RESULT:failed:{detail}")
    elif any_attempted:
        print(f"RESULT:posted:{detail}")
    elif stale_notes:
        # Nothing posted, but something is sitting there too stale to ship
        # on its own -- that needs a human, not silence.
        print(f"RESULT:stale:{'; '.join(stale_notes)}")
    else:
        print("RESULT:nothing:")

    # Non-zero exit only on an actual posting failure so the caller
    # (telegram-approve.yml) can tell "ran but nothing failed" apart from
    # "a post genuinely errored out" and notify accordingly.
    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
