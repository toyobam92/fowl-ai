#!/usr/bin/env python3
"""Submit tomorrow's approved Nova script+look to HeyGen for rendering.

Only ever invoked by telegram-approve.yml, synchronously, right after an
"APPROVE <PR#>" merge of an update/nova-<date> branch -- mirrors the same
"never render/publish without an explicit human approval" pattern used for
post_to_meta.py (PUBLISH <PR#>). This script only submits the render job
(a fast API call); render_check_nova.py (run on a schedule by
render-check-nova.yml) polls until it's actually done and hands the
finished video off to automation/social-state.json.

Reads/writes automation/nova-pipeline-state.json directly. Does not touch
git -- the caller (telegram-approve.yml) commits+pushes whatever this
script changes on disk, same as it already does for social-state.json
after post_to_meta.py runs.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

STATE_PATH = "automation/nova-pipeline-state.json"
HEYGEN_API_BASE = "https://api.heygen.com"
NOVA_GROUP_ID = "6eef573ef32844d8b881010bf917601f"
SIGN_OFF = "I'm Nova. Stay ahead — for more AI news, subscribe to the link in the bio."
FALLBACK_VOICE_ID = "02X8sHnuxFpsq1caYWN0"

# Migrated to v3 2026-08-17: the legacy v2 endpoints (sunset 2026-10-31)
# started returning 401 for this API key on 2026-08-17 despite working on
# 2026-08-13, so the sunset date can't be trusted as a migration deadline.
# v3 shape per developers.heygen.com: POST /v3/videos with a flat
# {type, avatar_id, script, voice_id, aspect_ratio, resolution} body
# replaces v2's nested video_inputs/dimension payload.
VIDEO_GENERATE_PATH = "/v3/videos"


def heygen_request(path, api_key, method="GET", payload=None):
    url = f"{HEYGEN_API_BASE}{path}"
    headers = {"X-Api-Key": api_key}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HeyGen {method} {path} failed ({e.code}): {body}") from e


# No per-look voice lookup anymore: v2's avatar_group listing (which
# carried default_voice_id) is dead, and v3's /v3/avatars/looks response
# includes no voice field at all (verified 2026-08-18). Every look in the
# Nova group shared the same default_voice_id when that data was last
# visible (2026-08-17), and it's pinned here as FALLBACK_VOICE_ID.


def main():
    api_key = os.environ.get("HEYGEN_API_KEY")
    if not api_key:
        print("Missing HEYGEN_API_KEY -- cannot render.")
        sys.exit(1)

    with open(STATE_PATH, encoding="utf-8") as f:
        state = json.load(f)

    if state.get("status") != "pr_open":
        print(f"nova-pipeline-state.json status is {state.get('status')!r}, not 'pr_open' -- nothing to render.")
        sys.exit(1)

    script = state.get("script") or ""
    look = state.get("picked_look") or {}
    avatar_id = look.get("avatar_id")
    if not script or not avatar_id:
        print("Missing script or picked_look.avatar_id in state -- cannot render.")
        sys.exit(1)

    # Belt-and-suspenders: the skill is instructed to always include the
    # sign-off, but a rendered video missing it is a much more expensive
    # mistake to catch after the fact than a cheap string check here.
    if SIGN_OFF not in script:
        script = script.rstrip() + "\n\n" + SIGN_OFF

    voice_id = FALLBACK_VOICE_ID

    payload = {
        "type": "avatar",
        "avatar_id": avatar_id,
        "script": script,
        "voice_id": voice_id,
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "title": f"FOWL AI - Nova - {state.get('publish_date')}",
    }

    result = heygen_request(VIDEO_GENERATE_PATH, api_key, method="POST", payload=payload)
    data = result.get("data") if isinstance(result.get("data"), dict) else result
    video_id = data.get("video_id") or data.get("id")
    if not video_id:
        raise RuntimeError(f"HeyGen {VIDEO_GENERATE_PATH} returned no video_id: {result}")

    state["video_id"] = video_id
    state["status"] = "rendering"
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

    print(f"Submitted HeyGen render (video_id {video_id}) for {state.get('publish_date')}.")


if __name__ == "__main__":
    main()
