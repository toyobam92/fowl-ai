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

# v2 is legacy (sunsets 2026-10-31, per HeyGen's own response headers) but is
# what's confirmed working as of 2026-08-11 -- v3 needs a differently-shaped
# character/voice payload that wasn't worked out yet. Migrate before the
# sunset date.
VIDEO_GENERATE_PATH = "/v2/video/generate"


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


def find_voice_id(api_key, avatar_id):
    """Look up the look's own default_voice_id rather than assuming every
    look in the group shares one -- confirmed most do, but no reason to
    hardcode past what the API actually reports for the specific look."""
    result = heygen_request(f"/v2/avatar_group/{NOVA_GROUP_ID}/avatars", api_key)
    for look in result.get("data", {}).get("avatar_list", []):
        if look.get("id") == avatar_id:
            return look.get("default_voice_id") or FALLBACK_VOICE_ID
    return FALLBACK_VOICE_ID


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

    voice_id = find_voice_id(api_key, avatar_id)

    payload = {
        "video_inputs": [
            {
                "character": {"type": "avatar", "avatar_id": avatar_id, "avatar_style": "normal"},
                "voice": {"type": "text", "input_text": script, "voice_id": voice_id},
            }
        ],
        "dimension": {"width": 1080, "height": 1920},
        "title": f"FOWL AI - Nova - {state.get('publish_date')}",
    }

    result = heygen_request(VIDEO_GENERATE_PATH, api_key, method="POST", payload=payload)
    video_id = result.get("data", {}).get("video_id")
    if not video_id:
        raise RuntimeError(f"HeyGen video/generate returned no video_id: {result}")

    state["video_id"] = video_id
    state["status"] = "rendering"
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

    print(f"Submitted HeyGen render (video_id {video_id}) for {state.get('publish_date')}.")


if __name__ == "__main__":
    main()
