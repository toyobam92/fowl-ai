#!/usr/bin/env python3
"""Post the approved engagement-comment batch: Threads replies via API,
everything else surfaced as a manual checklist.

Only ever invoked by telegram-approve.yml, synchronously, right after an
"APPROVE <PR#>" merge of an update/engage-<date> branch -- same
merge-is-the-human-gate pattern as render_nova_video.py. Reads/writes
automation/engagement-state.json; the caller commits whatever changed.

Threads is the only platform with a compliant reply API (reply_to_id on
the standard publish flow). Instagram/Facebook have no API for commenting
on other accounts' posts, so those comments -- and any Threads comment
whose numeric media id couldn't be discovered -- are printed as a manual
checklist instead of posted. stdout doubles as the Telegram notification
body, so keep prints human-readable.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

STATE_PATH = "automation/engagement-state.json"
THREADS_API_BASE = "https://graph.threads.net/v1.0"


def threads_post(path, params):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f"{THREADS_API_BASE}{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:200]
        raise RuntimeError(f"Threads POST {path} failed ({e.code}): {body}") from e


def post_threads_reply(token, user_id, text, reply_to_id):
    creation = threads_post(
        f"/{user_id}/threads",
        {"media_type": "TEXT", "text": text, "reply_to_id": reply_to_id, "access_token": token},
    )
    creation_id = creation.get("id")
    if not creation_id:
        raise RuntimeError(f"no creation id returned: {creation}")
    published = threads_post(
        f"/{user_id}/threads_publish",
        {"creation_id": creation_id, "access_token": token},
    )
    if not published.get("id"):
        raise RuntimeError(f"publish returned no id: {published}")
    return published["id"]


def main():
    with open(STATE_PATH, encoding="utf-8") as f:
        state = json.load(f)

    if state.get("status") != "pr_open":
        print(f"engagement-state.json status is {state.get('status')!r}, not 'pr_open' -- nothing to post.")
        return

    token = os.environ.get("META_THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("META_THREADS_USER_ID")

    posted, failed, manual = 0, 0, []
    for c in state.get("comments", []):
        if c.get("status") != "proposed":
            continue
        if c.get("platform") == "threads" and c.get("reply_to_id") and token and user_id:
            try:
                c["posted_id"] = post_threads_reply(token, user_id, c["text"], c["reply_to_id"])
                c["status"] = "posted"
                posted += 1
            except RuntimeError as e:
                # One bad reply shouldn't sink the batch -- record and move on.
                c["status"] = "failed"
                c["error"] = str(e)[:200]
                failed += 1
        else:
            c["status"] = "manual"
            manual.append(c)

    state["status"] = "posted"
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")

    print(f"💬 Engagement batch {state.get('batch_date')}: {posted} posted to Threads, {failed} failed, {len(manual)} manual.")
    if failed:
        for c in state["comments"]:
            if c.get("status") == "failed":
                print(f"❌ {c.get('target')}: {c.get('error')}")
    if manual:
        print("Post these by hand (tap the link, paste the text):")
        for c in manual:
            print(f"- [{c.get('platform')}] {c.get('target')}: {c.get('post_url')}")
            print(f"  → {c.get('text')}")


if __name__ == "__main__":
    main()
