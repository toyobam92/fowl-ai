#!/usr/bin/env python3
"""Poll HeyGen for a Nova video submitted by render_nova_video.py, and once
it's done, hand the finished video off to automation/social-state.json so
auto-publish-nova.yml's daily cron can post it on its scheduled day.

Only ever invoked by render-check-nova.yml on a schedule. Idempotent and
safe to run when there's nothing to check -- it's a no-op unless
nova-pipeline-state.json status is exactly "rendering".

Reads/writes both automation/nova-pipeline-state.json and
automation/social-state.json directly. Does not touch git -- the caller
commits+pushes whatever changed on disk, same pattern as post_to_meta.py.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

NOVA_STATE_PATH = "automation/nova-pipeline-state.json"
SOCIAL_STATE_PATH = "automation/social-state.json"
HEYGEN_API_BASE = "https://api.heygen.com"


def heygen_get(path, api_key):
    req = urllib.request.Request(f"{HEYGEN_API_BASE}{path}", headers={"X-Api-Key": api_key})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HeyGen GET {path} failed ({e.code}): {body}") from e


def emit_result(kind, detail=""):
    """Single tagged line on stdout that render-check-nova.yml greps for to
    decide whether/what to notify -- avoids the workflow having to infer
    what happened by diffing JSON state across git commits in bash."""
    print(f"RESULT:{kind}:{detail}")


def main():
    api_key = os.environ.get("HEYGEN_API_KEY")
    if not api_key:
        print("Missing HEYGEN_API_KEY -- cannot check render status.")
        emit_result("error", "missing HEYGEN_API_KEY")
        sys.exit(1)

    with open(NOVA_STATE_PATH, encoding="utf-8") as f:
        nova_state = json.load(f)

    if nova_state.get("status") != "rendering":
        print(f"nova-pipeline-state.json status is {nova_state.get('status')!r}, not 'rendering' -- nothing to check.")
        emit_result("noop")
        return

    video_id = nova_state.get("video_id")
    if not video_id:
        print("status is 'rendering' but no video_id set -- inconsistent state, leaving as-is for manual review.")
        emit_result("noop")
        return

    status = heygen_get(f"/v1/video_status.get?video_id={video_id}", api_key)
    data = status.get("data", {})
    render_status = data.get("status")

    if render_status in ("processing", "pending", "waiting"):
        print(f"video_id {video_id} still {render_status} -- checking again next run.")
        emit_result("noop")
        return

    if render_status == "failed":
        error = data.get("error")
        print(f"video_id {video_id} FAILED to render: {error}")
        # Reset to idle rather than looping on a dead render forever --
        # last_proposed stays as-is so the 2-day proposal guard still holds.
        nova_state["status"] = "failed"
        with open(NOVA_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(nova_state, f, indent=2)
            f.write("\n")
        emit_result("failed", str(error))
        sys.exit(1)

    if render_status != "completed":
        print(f"video_id {video_id} in unexpected status {render_status!r} -- leaving as-is.")
        emit_result("noop")
        return

    video_url = data.get("video_url")
    if not video_url:
        print(f"video_id {video_id} completed but has no video_url: {data}")
        emit_result("error", "completed with no video_url")
        sys.exit(1)

    publish_date = nova_state.get("publish_date")
    day_name = (
        datetime.date.fromisoformat(publish_date).strftime("%A") if publish_date else "Unknown"
    )

    with open(SOCIAL_STATE_PATH, encoding="utf-8") as f:
        social_state = json.load(f)
    social_state.setdefault("posts", []).append(
        {
            "day": day_name,
            "publish_date": publish_date,
            # picked_topic is a plain string (the topic title itself) in
            # this schema, not an object -- nova-daily-prep's step 2 sets
            # it directly to one of the proposed topics' titles. Fixed
            # 2026-08-14: this line previously assumed a dict shape
            # (`.get("title")`) and crashed with AttributeError on every
            # real completed render, since no video had gone through this
            # path before to expose it.
            "topic": nova_state.get("picked_topic"),
            "script": nova_state.get("script"),
            "caption": nova_state.get("caption"),
            "video_path": video_url,
            "platforms_published": {"facebook": False, "instagram": False, "tiktok": False, "threads": False},
        }
    )
    with open(SOCIAL_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(social_state, f, indent=2)
        f.write("\n")

    # Reset the pipeline for the next cycle -- keep last_proposed (the
    # 2-day proposal guard) but clear everything specific to this episode.
    nova_state.update(
        {
            "status": "idle",
            "publish_date": None,
            "tone": None,
            "topics": [],
            "rejected_titles": [],
            "picked_topic": None,
            "script": None,
            "caption": None,
            "picked_look": None,
            "look_alternates": [],
            "pr_number": None,
            "pr_branch": None,
            "video_id": None,
        }
    )
    with open(NOVA_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(nova_state, f, indent=2)
        f.write("\n")

    print(f"video_id {video_id} completed -- queued for auto-publish on {publish_date} ({day_name}).")
    emit_result("completed", publish_date or "")


if __name__ == "__main__":
    main()
