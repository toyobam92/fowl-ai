"""Telegram approve flow: one-tap human approval before any submission.

`notify` sends each prepared application to your Telegram chat — screenshot,
score, role summary — and marks it awaiting_approval. `poll` long-polls for
your reply:

    APPROVE <job-id>  -> runs the ATS adapter with --submit (cap + kill switch
                         checked first), confirms back with the result
    SKIP <job-id>     -> archives the job

Only messages from TELEGRAM_CHAT_ID are honored; everything else is ignored.
Replies never weaken the adapter's own gates — a job that regressed to
needs_answers, a hit daily cap, or kill_switch all refuse the submit.

Usage:
  python -m apply.approve notify [--job-id N]
  python -m apply.approve poll [--once]
Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
Cron (poll piggybacks fine on the discovery schedule):
  */15 8-22 * * *  cd /path/to/auto-apply && python -m apply.approve poll --once
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

from apply.answers import CONFIG, ROOT, connect

OFFSET_FILE = ROOT / "db" / "telegram_offset"
REPLY_RE = re.compile(r"^\s*(approve|skip)\s+#?(\d+)\s*$", re.IGNORECASE)
POLL_TIMEOUT_S = 50


def _env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        sys.exit(f"{name} not set")
    return val


def tg(method: str, files: dict | None = None, **params) -> dict:
    url = f"https://api.telegram.org/bot{_env('TELEGRAM_BOT_TOKEN')}/{method}"
    resp = requests.post(url, data=params, files=files, timeout=POLL_TIMEOUT_S + 10)
    payload = resp.json()
    if not payload.get("ok"):
        raise RuntimeError(f"telegram {method} failed: {payload}")
    return payload["result"]


def send_text(text: str) -> None:
    tg("sendMessage", chat_id=_env("TELEGRAM_CHAT_ID"), text=text)


def latest_out_dir(conn, job_id: int) -> Path | None:
    row = conn.execute(
        "SELECT detail FROM events WHERE job_id = ? AND kind = 'prepared' "
        "ORDER BY id DESC LIMIT 1", (job_id,)).fetchone()
    return Path(row[0]) if row else None


def latest_application(conn, job_id: int):
    return conn.execute(
        "SELECT resume_path, cover_letter_path FROM applications WHERE job_id = ? "
        "ORDER BY id DESC LIMIT 1", (job_id,)).fetchone()


def caption_for(row) -> str:
    job_id, company, title, score, track, reasons, gaps = row
    lines = [f"#{job_id}  {company} — {title}"]
    if score is not None:
        lines.append(f"Score {score} ({track or 'untracked'})")
    for r in (json.loads(reasons) if reasons else [])[:2]:
        lines.append(f"+ {r}")
    for g in (json.loads(gaps) if gaps else [])[:1]:
        lines.append(f"- {g}")
    lines.append(f"Reply:  APPROVE {job_id}   or   SKIP {job_id}")
    return "\n".join(lines)[:1024]  # Telegram caption limit


def notify(conn, job_id: int | None = None) -> int:
    where, args = "status = 'prepared'", []
    if job_id is not None:
        where, args = "id = ? AND status IN ('prepared', 'awaiting_approval')", [job_id]
    rows = conn.execute(
        f"SELECT id, company, title, score, track, match_reasons, gaps "
        f"FROM jobs WHERE {where}", args).fetchall()
    if not rows:
        print("nothing awaiting notification")
        return 0
    chat_id = _env("TELEGRAM_CHAT_ID")
    for row in rows:
        jid, caption = row[0], caption_for(row)
        shot = None
        out = latest_out_dir(conn, jid)
        if out and (out / "application_screenshot.png").exists():
            shot = out / "application_screenshot.png"
        if shot:
            with open(shot, "rb") as fh:
                tg("sendPhoto", files={"photo": fh}, chat_id=chat_id, caption=caption)
        else:
            tg("sendMessage", chat_id=chat_id, text=caption + "\n(no screenshot found)")
        conn.execute("UPDATE jobs SET status = 'awaiting_approval' WHERE id = ?", (jid,))
        conn.execute("INSERT INTO events (job_id, kind, detail) VALUES (?, 'approval_requested', ?)",
                     (jid, caption.splitlines()[0]))
        conn.commit()
        print(f"sent #{jid} for approval")
    return 0


def submitted_today(conn) -> int:
    return conn.execute(
        "SELECT COUNT(*) FROM applications WHERE submitted_at >= date('now')").fetchone()[0]


def do_submit(conn, job_id: int, ats: str) -> str:
    if CONFIG.get("kill_switch"):
        return f"#{job_id}: kill_switch is on — not submitting."
    cap = CONFIG.get("daily_submit_cap", 5)
    if submitted_today(conn) >= cap:
        return f"#{job_id}: daily submit cap ({cap}) reached — try tomorrow."
    if ats != "greenhouse":
        return (f"#{job_id}: no adapter for ATS {ats!r} yet — submit manually; "
                f"assets are in {latest_out_dir(conn, job_id)}")
    app = latest_application(conn, job_id)
    if not app or not app[0]:
        return f"#{job_id}: no prepared application on file — run the adapter first."
    out = latest_out_dir(conn, job_id) or Path(app[0]).parent
    import apply.greenhouse as gh
    rc = gh.run(argparse.Namespace(
        job_id=job_id, url=None, resume=app[0], cover_letter=app[1],
        out=str(out), submit=True, headed=False))
    if rc == 0:
        return f"#{job_id}: SUBMITTED ✅  ({submitted_today(conn)}/{cap} today)"
    return (f"#{job_id}: submit BLOCKED (exit {rc}) — the adapter refused "
            f"(missing resume or unanswered required question). See {out}/application_report.json")


def handle_reply(conn, text: str) -> str:
    m = REPLY_RE.match(text or "")
    if not m:
        return "Commands:  APPROVE <job-id>   SKIP <job-id>"
    action, job_id = m.group(1).lower(), int(m.group(2))
    row = conn.execute("SELECT status, ats_type FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        return f"#{job_id}: no such job."
    status, ats = row
    if action == "skip":
        conn.execute("UPDATE jobs SET status = 'archived' WHERE id = ?", (job_id,))
        conn.execute("INSERT INTO events (job_id, kind, detail) VALUES (?, 'skipped', 'via telegram')",
                     (job_id,))
        conn.commit()
        return f"#{job_id}: archived."
    if status == "submitted":
        return f"#{job_id}: already submitted."
    if status not in ("awaiting_approval", "prepared"):
        return f"#{job_id}: status is {status!r} — nothing awaiting approval."
    reply = do_submit(conn, job_id, ats)
    conn.execute("INSERT INTO events (job_id, kind, detail) VALUES (?, 'approve_reply', ?)",
                 (job_id, reply))
    conn.commit()
    return reply


def _offset() -> int:
    try:
        return int(OFFSET_FILE.read_text())
    except (OSError, ValueError):
        return 0


def poll(conn, once: bool = False) -> int:
    chat_id = _env("TELEGRAM_CHAT_ID")
    while True:
        updates = tg("getUpdates", offset=_offset() + 1,
                     timeout=0 if once else POLL_TIMEOUT_S)
        for u in updates:
            OFFSET_FILE.write_text(str(u["update_id"]))
            msg = u.get("message") or {}
            text = msg.get("text")
            if not text or str((msg.get("chat") or {}).get("id")) != chat_id:
                continue  # ignore anything not from the configured chat
            reply = handle_reply(conn, text)
            print(f"{text!r} -> {reply!r}")
            send_text(reply)
        if once:
            return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["notify", "poll"])
    p.add_argument("--job-id", type=int, help="notify: a single job (re-sends if awaiting)")
    p.add_argument("--once", action="store_true", help="poll: one pass instead of looping")
    a = p.parse_args()
    conn = connect()
    sys.exit(notify(conn, a.job_id) if a.command == "notify" else poll(conn, a.once))
