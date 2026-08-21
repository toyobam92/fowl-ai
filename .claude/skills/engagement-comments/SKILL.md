---
name: engagement-comments
description: Periodically (Tue/Thu/Sat) find fresh posts from the AI brands and creators in automation/engagement-targets.json, draft 2-3 genuinely additive comments in FOWL AI's voice, and open a PR gated on a single Telegram APPROVE — Threads replies then post via API, Instagram ones come back as a manual checklist. Use when the recurring cloud routine fires, or the user asks to run an engagement round.
---

# Engagement comments

Grows FOWL AI's visibility by commenting on posts from AI brands and creators whose audiences overlap ours — through the same propose → PR → Telegram-approve pipeline as everything else. Nothing ever posts without an explicit `APPROVE <PR#>`.

**Platform reality (don't fight it):** Threads is the only platform with a compliant API for replying to other accounts' posts, and `automation/post_engagement_comments.py` posts those automatically after approve. Instagram/Facebook have **no** API for commenting on others' posts and headless browser commenting trips Meta's bot detection — those comments are delivered as a tap-and-paste Telegram checklist instead. Never attempt headless IG commenting.

**Volume cap — hard rule:** at most **3 comments per batch, 3 batches per week**. Engagement at higher volume reads as farming and risks the account. Skip a batch entirely rather than pad it with weak comments.

**Comment quality bar:** every comment must reference something specific in the target post and add something — a data point, a sharp question, a genuinely useful observation from FOWL AI's future-of-work beat. Never "Great post! 🔥", never a pitch, never a link drop. Write like Nova talks: direct, informed, zero sycophancy. If a draft could be pasted under any post unchanged, it fails the bar.

**Never fail silently past step 1.** On any unrecoverable error after research starts, send `gh workflow run notify.yml -f text="Engagement round failed at step <N>: <error>"` before stopping — same standing rule as nova-daily-prep.

## 0. Check state first

Read `automation/engagement-state.json` (create the idle shape if missing). Branch on `status`:

- **`idle`** → check `last_proposed`: if fewer than 2 days have passed, exit quietly. Only proceed on **Tuesday, Thursday, or Saturday**; other days exit quietly. Go to step 1.
- **`pr_open`** → check the PR (`pr_number`): merged → exit quietly (telegram-approve already ran the poster). Closed unmerged → set `status: "idle"`, clear `pr_number`/`pr_branch`/`comments`, commit+push, exit. Still open → exit quietly.
- **`posted`** → reset to `idle` (keep `last_proposed`), clear `batch_date`/`comments`/`pr_number`/`pr_branch`, commit+push, then apply the `idle` rules above in the same run.

Also drain any inbox entries matching `^ENGAGE ` (feedback like "ENGAGE skip creators this week") and honor them for this batch.

## 1. Find candidate posts

Read `automation/engagement-targets.json`. Use `WebSearch` to find **fresh posts (last ~3 days)** from a rotating subset of targets — mix brands and creators, don't hit the same account twice in a row across batches (check the previous batch's `target` values still in state/git history). A post is a candidate only if FOWL AI can add something real to it.

For each chosen post record: `platform` (`threads` / `instagram`), `target` (account name), `post_url`, and for Threads try to capture the **numeric media id** as `reply_to_id` (from the API/oEmbed/page source when discoverable — it is NOT the shortcode in the URL). If the id can't be found, leave `reply_to_id: null` — the comment still flows through as a manual checklist item, which is fine.

## 2. Draft 2-3 comments

Apply the quality bar above. Keep each under ~280 characters (Threads limit headroom, and short reads better as a comment anywhere).

## 3. Open the PR

Write to `automation/engagement-state.json`: `status: "pr_open"`, `last_proposed: <today>`, `batch_date: <today>`, `pr_branch: "update/engage-<today>"`, `pr_number: null`, and `comments: [{platform, target, post_url, reply_to_id, text, status: "proposed"}]`.

Write a human-readable preview to `automation/engagement-previews/<today>.md` (target, post link, comment text for each).

Then, all on the branch (state rides in the PR, same as Nova PR #26's pattern):

```
git checkout -b update/engage-<today>
git add automation/engagement-state.json automation/engagement-previews/<today>.md
git commit -m "Engagement batch for <today>: <n> comments"
git push -u origin update/engage-<today>
```

**Do not call `gh pr create`** — `open-nova-pr.yml` opens the PR automatically on any `update/engage-*` push (same silent-failure history as the Nova branches; see that workflow's header). Stop right after the push. `pr-notify.yml` pings Telegram; on `APPROVE <PR#>`, `telegram-approve.yml` merges, runs `automation/post_engagement_comments.py` (posts the Threads replies, marks the rest manual), commits the state, and sends the results + manual checklist to Telegram.

## 4. Report back

Summarize: batch date, targets chosen, comment texts, PR link.
