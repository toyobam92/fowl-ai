#!/usr/bin/env python3
"""Verify the Meta Graph API credentials used for posting still work.

Read-only: one GET /me per credential (Facebook page, Threads, Instagram --
the same three post_to_meta.py posts with), so running this can never
publish anything. Exists so "is the token still good?" has an answer
cheaper than waiting for a real publish run to fail: these long-lived
tokens expire (~60 days for Threads/Instagram), and the first symptom
would otherwise be a failed post in the evening publish window.

Invoked by check-meta-tokens.yml (workflow_dispatch only). Prints one
line per credential -- ok (with the account it resolves to), MISSING, or
FAILED with the API's own error -- and never prints the tokens
themselves. Exits non-zero if any credential that is set doesn't work,
so the Action run goes red exactly when something needs re-issuing.

Emits a single tagged RESULT line the workflow can grep, same pattern as
check_nova_render.py / check_publish_readiness.py:
  RESULT:ok:<n>          -- all n configured credentials verified
  RESULT:failed:<names>  -- comma-separated credentials that are set but rejected
  RESULT:missing:        -- no credentials configured at all
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GRAPH_API_VERSION = "v21.0"

USER_AGENT = "fowlai-check-meta-tokens/1.0"

CHECKS = [
    # (label, token env var, id env var, /me URL, fields)
    (
        "Facebook page (META_PAGE_ACCESS_TOKEN)",
        "META_PAGE_ACCESS_TOKEN",
        "META_PAGE_ID",
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/me",
        "id,name",
    ),
    (
        "Threads (META_THREADS_ACCESS_TOKEN)",
        "META_THREADS_ACCESS_TOKEN",
        "META_THREADS_USER_ID",
        "https://graph.threads.net/v1.0/me",
        "id,username",
    ),
    (
        "Instagram (META_IG_ACCESS_TOKEN)",
        "META_IG_ACCESS_TOKEN",
        "META_IG_USER_ID",
        f"https://graph.instagram.com/{GRAPH_API_VERSION}/me",
        "id,username",
    ),
]


def get_me(url, fields, token):
    qs = urllib.parse.urlencode({"fields": fields, "access_token": token})
    req = urllib.request.Request(f"{url}?{qs}", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body).get("error", {}).get("message", body)
        except json.JSONDecodeError:
            err = body
        return None, f"HTTP {e.code}: {err}"


def main():
    checked = 0
    failed = []
    for label, token_var, id_var, url, fields in CHECKS:
        token = os.environ.get(token_var)
        if not token:
            print(f"MISSING  {label}: secret not set")
            continue
        checked += 1
        me, err = get_me(url, fields, token)
        if err:
            print(f"FAILED   {label}: {err}")
            failed.append(token_var)
            continue
        who = me.get("name") or me.get("username") or "?"
        expected_id = os.environ.get(id_var)
        if expected_id and me.get("id") != expected_id:
            # Token works but belongs to a different account than the
            # configured target id -- posting would go somewhere unexpected.
            print(
                f"FAILED   {label}: token resolves to '{who}' (id {me.get('id')}), "
                f"but {id_var} is set to a different id"
            )
            failed.append(token_var)
        else:
            print(f"ok       {label}: valid, acts as '{who}' (id {me.get('id')})")

    if failed:
        print(f"RESULT:failed:{','.join(failed)}")
        sys.exit(1)
    if checked == 0:
        print("RESULT:missing:")
        sys.exit(1)
    print(f"RESULT:ok:{checked}")


if __name__ == "__main__":
    main()
