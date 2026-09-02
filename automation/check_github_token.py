#!/usr/bin/env python3
"""Verify a GitHub personal access token stored in this repo's Actions
secrets -- the kind the Telegram webhook worker (telegram-webhook-worker.js)
uses to dispatch telegram-approve.yml, which GitHub emails about when it
nears/passes its expiry date.

Read-only: GET /user and GET /repos/<repo> per candidate token, nothing
is written or dispatched. Repo secrets can't be enumerated from a
workflow, so this probes a list of likely secret names (CANDIDATES) and
reports on whichever are actually set. For each one it prints who the
token authenticates as, its expiry date if GitHub reports one (the
github-authentication-token-expiration header, sent for fine-grained
PATs), and whether it can see this repo. Tokens themselves are never
printed.

Invoked by check-meta-tokens.yml alongside the Graph API check.

  RESULT:ok:<names>      -- these candidates are set and valid
  RESULT:failed:<names>  -- set but rejected by the API (expired/revoked)
  RESULT:missing:        -- none of the candidate names are set
"""
import json
import os
import sys
import urllib.error
import urllib.request

REPO = "toyobam92/fowl-ai"
USER_AGENT = "fowlai-check-github-token/1.0"

# GITHUB_TOKEN deliberately excluded: Actions injects its own ephemeral
# one, which would always pass and prove nothing about a stored PAT.
CANDIDATES = [
    "GH_TOKEN",
    "GH_PAT",
    "GITHUB_PAT",
    "PAT",
    "PERSONAL_ACCESS_TOKEN",
    "WORKER_GH_TOKEN",
    "TELEGRAM_GH_TOKEN",
]


def api_get(path, token):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), dict(r.headers), None
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            msg = json.loads(body).get("message", body)
        except json.JSONDecodeError:
            msg = body
        return None, {}, f"HTTP {e.code}: {msg}"


def main():
    ok, failed = [], []
    for name in CANDIDATES:
        token = os.environ.get(name)
        if not token:
            continue
        user, headers, err = api_get("/user", token)
        if err:
            print(f"FAILED   {name}: {err} (expired or revoked?)")
            failed.append(name)
            continue
        expiry = headers.get("github-authentication-token-expiration", "")
        scopes = headers.get("X-OAuth-Scopes", "")
        detail = f"valid, acts as '{user.get('login')}'"
        if expiry:
            detail += f", expires {expiry}"
        if scopes:
            detail += f", scopes: {scopes}"
        repo, _, repo_err = api_get(f"/repos/{REPO}", token)
        if repo_err:
            detail += f" -- but CANNOT see {REPO} ({repo_err})"
        else:
            detail += f", can see {REPO} (push={repo.get('permissions', {}).get('push')})"
        print(f"ok       {name}: {detail}")
        ok.append(name)

    if failed:
        print(f"RESULT:failed:{','.join(failed)}")
        sys.exit(1)
    if not ok:
        print("RESULT:missing: none of the candidate secret names are set: "
              + ", ".join(CANDIDATES))
        sys.exit(1)
    print(f"RESULT:ok:{','.join(ok)}")


if __name__ == "__main__":
    main()
