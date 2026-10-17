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
  RESULT:overdue:<detail>     -- an earlier episode never posted and WILL post tonight
                                 (not dropped, within post_to_meta's MAX_DAYS_LATE)
  RESULT:stale:<detail>       -- the pipeline is parked on a slot that already passed
                                 (topic never picked, PR never approved, or render
                                 failed), so nothing newer gets proposed until it clears
  RESULT:none:                -- nothing scheduled today, normal on off days

Two things this deliberately does NOT report, because post_to_meta.py will
not post them and auto-publish-nova.yml already says so when relevant:
  - posts marked "dropped" (a human said never ship this), and
  - posts more than MAX_DAYS_LATE days late (held as stale, nightly "⏸️ Held
    back" notice from auto-publish-nova.yml).
Until 2026-10-17 both counted as "overdue", so the dropped 2026-09-14 episode
produced a daily "still queued, posts tonight" nudge for three weeks -- and,
because that branch returned early, hid whatever the pipeline's real status
was underneath it.
"""
import datetime
import json

NOVA_STATE_PATH = "automation/nova-pipeline-state.json"
SOCIAL_STATE_PATH = "automation/social-state.json"

# Must match post_to_meta.MAX_DAYS_LATE -- that script is the one deciding
# what actually ships tonight, this one only predicts it. Kept as a literal
# (not an import) so this check never depends on post_to_meta's imports;
# scripts/test_check_publish_readiness.py asserts the two stay equal.
MAX_DAYS_LATE = 1

# nova-pipeline-state.json statuses that mean "an episode is in flight for
# publish_date and nova-daily-prep will not propose anything new until it
# clears". A publish_date in the past with one of these is a parked pipeline:
# the 2026-10-07 topic list sat in awaiting_topic_pick from 2026-10-06 with no
# nudge at all (this script said "none" because publish_date != today), and
# no episode shipped after 2026-10-05.
PARKED_STATUSES = ("awaiting_topic_pick", "pr_open", "failed")

# How long nova-daily-prep keeps an unpicked list / unapproved PR alive past
# its slot before dropping it (see .claude/skills/nova-daily-prep/SKILL.md).
# Quoted in the stale message so the owner knows what happens if they do
# nothing.
PREP_DROP_AFTER_DAYS = 2


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def unposted(post):
    pub = post.get("platforms_published") or {}
    # tiktok is manual-only and always False, so it can't count here.
    return not (pub.get("facebook") and pub.get("threads") and pub.get("instagram"))


def queued(post):
    """A rendered, unposted post that post_to_meta.py would still consider
    shipping. Dropped posts are excluded: post_to_meta skips them, so they
    must not be described as queued here either."""
    return bool(post.get("video_path")) and unposted(post) and not post.get("dropped")


def _days_past(today, iso_date):
    return (today - datetime.date.fromisoformat(iso_date)).days


def _stale_detail(nova, today):
    """One-line, human-ready description of a parked pipeline, including
    what happens if nobody acts -- the workflow pastes it verbatim."""
    status = nova.get("status")
    publish_date = nova["publish_date"]
    days = _days_past(today, publish_date)
    if status == "awaiting_topic_pick":
        return (
            f"the {publish_date} topic list was never picked ({days}d past). "
            f"nova-daily-prep drops it after {PREP_DROP_AFTER_DAYS} days and proposes fresh "
            f"topics on the next slot; reply NOVA 1/2/3 before then only if you still want it"
        )
    if status == "pr_open":
        pr = nova.get("pr_number") or "?"
        return (
            f"PR #{pr} for {publish_date} was never approved ({days}d past). "
            f"nova-daily-prep closes it after {PREP_DROP_AFTER_DAYS} days and proposes fresh "
            f"topics on the next slot; reply APPROVE {pr} before then only if you still want it"
        )
    # failed
    return (
        f"the {publish_date} render failed ({days}d past) and nothing retries it on its own. "
        f"Run render-retry-nova.yml once the cause is fixed, or set "
        f"automation/nova-pipeline-state.json back to idle to let the next slot propose"
    )


def assess(nova, social, today):
    """Decide what the nudge should say for the given state on `today`
    (a datetime.date). Returns (kind, detail, log_lines). Pure -- no I/O --
    so fixtures can drive every branch directly."""
    today_iso = today.isoformat()
    log = []
    posts = [p for p in social.get("posts", []) if queued(p)]

    if any(p.get("publish_date") == today_iso for p in posts):
        log.append("Today's episode is rendered and queued -- it posts in tonight's window.")
        return "ready", "", log

    # Episodes from earlier days that never went out. post_to_meta posts one
    # that's at most MAX_DAYS_LATE days late in tonight's window -- say so.
    # Anything staler it holds back (and auto-publish-nova.yml reports that
    # itself every night), so don't claim it posts tonight; log it and keep
    # looking at what the pipeline is doing.
    overdue = sorted(
        (p for p in posts if p.get("publish_date") and p["publish_date"] < today_iso),
        key=lambda p: p["publish_date"],
    )
    posting_tonight = []
    for p in overdue:
        days = _days_past(today, p["publish_date"])
        detail = f"{p.get('day', '?')} {p['publish_date']} ({days}d late)"
        if days <= MAX_DAYS_LATE:
            posting_tonight.append(detail)
        else:
            log.append(f"Held as stale, post_to_meta will not auto-post it: {detail}")
    if posting_tonight:
        log.append(f"Overdue episode still queued: {posting_tonight[0]}")
        return "overdue", posting_tonight[0], log

    # Nothing queued -- is the pipeline parked on a slot that already passed?
    publish_date = nova.get("publish_date")
    status = nova.get("status")
    if publish_date and publish_date < today_iso and status in PARKED_STATUSES:
        detail = _stale_detail(nova, today)
        log.append(f"Pipeline parked: {detail}")
        return "stale", detail, log

    # Is one actually due today, and where is it stuck?
    if publish_date != today_iso:
        log.append("No Nova episode scheduled for today -- nothing to check.")
        return "none", "", log

    if status == "pr_open":
        return "needs_approval", str(nova.get("pr_number") or "?"), log
    if status == "rendering":
        return "rendering", str(nova.get("video_id") or "?"), log
    if status == "awaiting_topic_pick":
        return "needs_pick", today_iso, log
    log.append(f"Episode for today in unexpected status {status!r} -- flagging.")
    return "needs_pick", today_iso, log


def emit(kind, detail=""):
    print(f"RESULT:{kind}:{detail}")


def main(today=None):
    today = today or datetime.date.today()
    kind, detail, log = assess(load(NOVA_STATE_PATH), load(SOCIAL_STATE_PATH), today)
    for line in log:
        print(line)
    emit(kind, detail)


if __name__ == "__main__":
    main()
