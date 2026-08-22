#!/usr/bin/env python3
"""Warn, a couple of hours before the daily publish window, if today's Nova
episode still isn't ready to post.

Only ever invoked by publish-nudge-nova.yml on a schedule. The failure this
exists to prevent: on 2026-08-21 the "APPROVE 29" reply landed ~3 hours
after the 7:30pm ET auto-publish cron, so the video rendered but had no
window left and silently slipped to the next evening. Nothing anywhere said
so -- the only way to notice was diffing repo state by hand.

Emits a single tagged RESULT line the workflow greps, same pattern as
check_nova_render.py:
  RESULT:ready:            -- today's episode is rendered and queued, nothing to do
  RESULT:needs_approval:<pr>  -- PR still open, no APPROVE yet
  RESULT:rendering:<video_id> -- approved but still rendering (usually ~3 min; late = suspect)
  RESULT:needs_pick:<date>    -- topic still unpicked
  RESULT:overdue:<detail>     -- an earlier episode never posted and is still queued
  RESULT:none:                -- nothing scheduled today, normal on off days
"""
import datetime
import json
import sys

NOVA_STATE_PATH = "automation/nova-pipeline-state.json"
SOCIAL_STATE_PATH = "automation/social-state.json"


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def emit(kind, detail=""):
    print(f"RESULT:{kind}:{detail}")


def main():
    today = datetime.date.today().isoformat()
    nova = load(NOVA_STATE_PATH)
    social = load(SOCIAL_STATE_PATH)

    posts = social.get("posts", [])

    def unposted(p):
        pub = p.get("platforms_published", {})
        # tiktok is manual-only and always False, so it can't count here.
        return not (pub.get("facebook") and pub.get("threads") and pub.get("instagram"))

    ready_today = [
        p for p in posts
        if p.get("publish_date") == today and p.get("video_path") and unposted(p)
    ]
    if ready_today:
        print(f"Today's episode is rendered and queued -- it posts in tonight's window.")
        emit("ready")
        return

    # An episode from an earlier day that never went out. It will post in
    # tonight's window (post_to_meta posts anything due on-or-after its
    # date, up to MAX_DAYS_LATE) -- worth saying out loud either way.
    overdue = [
        p for p in posts
        if p.get("publish_date") and p["publish_date"] < today and p.get("video_path") and unposted(p)
    ]
    if overdue:
        oldest = min(overdue, key=lambda p: p["publish_date"])
        days = (datetime.date.today() - datetime.date.fromisoformat(oldest["publish_date"])).days
        detail = f"{oldest.get('day', '?')} {oldest['publish_date']} ({days}d late)"
        print(f"Overdue episode still queued: {detail}")
        emit("overdue", detail)
        return

    # Nothing queued -- is one actually due today, and where is it stuck?
    if nova.get("publish_date") != today:
        print("No Nova episode scheduled for today -- nothing to check.")
        emit("none")
        return

    status = nova.get("status")
    if status == "pr_open":
        emit("needs_approval", str(nova.get("pr_number") or "?"))
    elif status == "rendering":
        emit("rendering", str(nova.get("video_id") or "?"))
    elif status == "awaiting_topic_pick":
        emit("needs_pick", today)
    else:
        print(f"Episode for today in unexpected status {status!r} -- flagging.")
        emit("needs_pick", today)


if __name__ == "__main__":
    main()
