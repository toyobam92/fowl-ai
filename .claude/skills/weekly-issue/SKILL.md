---
name: weekly-issue
description: Produce this week's FOWL AI newsletter issue end-to-end — propose 5 topic angles via Telegram, wait for a pick, draft, email a review copy to the owner, iterate on feedback, then open/update a PR gated on Telegram approval instead of pushing straight to main. Use when it's time to start the week's issue, the recurring cloud routine fires, or the user asks to draft/publish/revise the next issue.
---

# Weekly issue

This replaces the old three-prompt manual workflow (research memo → draft → HTML update) with one pass, plus a topic-pick step and an email-review loop so the user chooses the angle and can iterate before anything is merged. It is self-contained inside this repo (`fowlai-site-upload`) so it works whether it's run locally in Claude Code or by the unattended recurring cloud routine, which only has access to this repo — not the sibling `automation/` folder in the outer project directory.

**Telegram is one-way into this skill, not read directly by it, and this skill has no ability to talk to Telegram directly either.** `.github/workflows/telegram-approve.yml` is the *only* thing that receives Telegram messages (via a real-time webhook, not polling) — it handles `APPROVE <PR#>` and `SCHEDULE <PR#>` itself, and relays everything else (topic picks, "MORE", revision feedback) into `automation/inbox.json`, committed to `main`. This skill reads that file instead of ever calling Telegram's API to receive messages — two independent receivers on the same bot would race and silently eat each other's messages (this happened once, 2026-08-02, with the old polling design — see the project memory on this).

**To send a Telegram message, call `gh workflow run notify.yml -f text="..."`.** Never `curl` Telegram directly from this skill — when run by the cloud routine, there is no `TELEGRAM_BOT_TOKEN` in the environment at all (only GitHub Actions secrets have it, and the cloud routine isn't GitHub Actions). This exact mistake shipped once, 2026-08-02: the skill's first version instructed a direct curl "reading the token from the environment," which was never actually provided, so the very first topic-proposal message silently failed to send.

**Cadence:** one issue proposed per week, on Sunday (step 0's `idle` branch gates on both `last_proposed` being 6+ days old *and* today being Sunday — confirmed both checks are necessary 2026-08-02: finishing one issue's cycle same-day triggered a second same-day proposal once, and simply degating to "any Sunday" would still allow two proposals on the same Sunday if a cycle completes within the day), picked whenever the user replies, drafted same run, a review copy emailed to the owner, revised on feedback (as many rounds as needed), merged whenever the user replies `APPROVE <PR#>` (site deploy only), emailed to the real subscriber list only after a further, separate `SCHEDULE <PR#>` reply (targets the next Monday 7:45am ET automatically) — that reply alone is what authorizes touching the real subscriber list, and the schedule stays cancellable in EmailOctopus right up to send time.

## 0. Check state and inbox first

Read `automation/issue-state.json` (create it with `{"status": "idle"}` if it doesn't exist) and `automation/inbox.json` (an array, `[]` if it doesn't exist or has been fully drained). Branch on `status`:

- **`idle`** (no proposal in flight) → **one issue a week, full stop — not "as fast as you reply" and not "once per Sunday no matter what."** Check `last_proposed` in the state file. If it's set and fewer than **6 days** have passed since it, exit quietly (no Telegram message) — a week's issue has already been proposed, regardless of whether it's Sunday again or the previous cycle finished early. Only if `last_proposed` is unset or 6+ days old, check today's day of week: if not Sunday, exit quietly; if Sunday, proceed to step 1 and set `last_proposed` to today when you do.
- **`awaiting_pick`** → look in the inbox for an entry matching a digit 1-5 or `MORE` (case-insensitive); if none, exit (nothing to do yet). If found, remove it from the inbox (write the file back without it, commit) and go to step 2.
- **`drafted`** (PR open, awaiting review/revision/merge) → first check whether the PR (`pr_number`) is now merged (`gh pr view <N> --json mergedAt`). If merged: this issue's cycle is complete — set `status: "idle"` (leave `last_proposed` as-is — it's the "one a week" guard above, not a per-issue field), clear `topics`/`rejected_titles`/`picked_topic`/`pr_number`, commit+push to `main`, and exit. If not yet merged: look in the inbox for a free-text entry (revision feedback) — **skip any entry that's actually addressed to a different automation sharing this same inbox** (currently: anything starting `TEST ` case-insensitively belongs to the monthly-test skill's pick step — leave it untouched, don't drain it). If no *unclaimed* free-text entry remains, exit; if found, remove it from the inbox and go to step 9a (revise).
- Anything else → treat as idle, start over (still respecting the `last_proposed` guard above).

Commit inbox changes (`git add automation/inbox.json && git commit -m "Drain inbox" && git push`) as their own small commit, separate from any state-file update, so a crash mid-run doesn't lose track of what was already consumed.

## 1. Propose 5 topics

Do a *light* research pass with `WebSearch` — enough to sketch 5 distinct plausible angles for this week's issue (not the full deep-dive yet). For each: a one-line title and a one-sentence why-now. Write these to `automation/issue-state.json`:

```json
{
  "week_of": "<upcoming Monday's date -- the actual send day, not the day after; every EmailOctopus send to date has been a Monday 7:45am ET, and this value also becomes the issue's folder date in step 6, so getting it right here matters twice over>",
  "status": "awaiting_pick",
  "last_proposed": "<today's date -- the one-issue-a-week guard, see step 0>",
  "topics": [{"title": "...", "why": "..."}, ...],
  "rejected_titles": [],
  "picked_topic": null,
  "pr_number": null,
  "last_updated": "<now>"
}
```

Commit and push this file directly to `main`. Then send the numbered list via `gh workflow run notify.yml -f text="..."`:

```
This week's issue — pick one:
1. <title> — <why>
2. ...
3. ...
4. ...
5. ...

Reply with a number to pick, or MORE for five different options.
```

Stop here. Do not research further or draft anything yet.

## 2. Act on the pick

(Reached only from step 0 with an inbox entry already removed.)

- **Inbox entry was `MORE`** → move the current `topics` titles into `rejected_titles`, generate 5 new angles that don't repeat any rejected title, update the state file (`topics` replaced, `status` stays `awaiting_pick`), commit+push to `main`, message the new numbered list to Telegram. Stop here.
- **Inbox entry was a digit 1-5** → set `picked_topic` to that entry, `status: "drafting"`, commit+push. Continue in this same run to step 3 — don't wait for another invocation.

## 3. Figure out the issue number and date

Look at the folder names under `issues/` (e.g. `2026-07-27`) and the "Issue N" markers inside the most recent one's `<title>`/masthead to get the last published issue number and date. This week's issue is number+1.

Use the `week_of` value already recorded in `issue-state.json` (from step 1) as this issue's date — don't recompute it independently here. Keeping a single source of truth for the date is what step 6 relies on.

## 4. Research

Use `WebSearch`/`WebFetch` to deepen the picked topic into a full issue. Prioritize, in order:
- AI labor market shifts
- AI-native career changes
- enterprise AI adoption
- AI evaluation and trainer work
- hidden AI gig/platform opportunities
- community chatter (Reddit, etc.) that reveals practical truth over hype

Produce, internally, before drafting:
1. Top 5 developments (with source links), framed around the picked topic
2. The strongest hook for the masthead
3. The "if you read nothing else" paragraph
4. Signal & Chatter bullets
5. Reddit/community chatter bullets
6. One emerging AI-work career title worth explaining
7. AI trainer/eval platform opportunities and new AI jobs worth listing
8. Any claim you can't source cleanly — flag it, don't smooth it over

## 5. Draft

Voice: calm, analytical, useful, high-trust. No hype, no doom, no generic AI commentary — every development needs a concrete "why it matters to a knowledge worker building career leverage" angle.

Structure (same section order every issue):
1. Masthead hook
2. If you read nothing else
3. Intro
4. This Week — 5 Developments (title, body, why it matters, who benefits, the signal, from the inside)
5. Signal & Chatter
6. Reddit / Community Chatter
7. Emerging Career Title
8. AI Trainer Platforms / Opportunity Board
9. New AI Jobs
10. Closing Reflection
11. Reply CTA

## 6. HTML

Use the most recently published issue's HTML (`issues/<latest-date>/index.html` in this repo) as the structural template — it already carries the correct FOWL AI branding, colors, typography, and layout, and already has the `{{UnsubscribeURL}}`/`{{SenderInfoLine}}`/`{{RewardsURL}}` merge tags EmailOctopus requires in its footer. Replace only the issue-specific copy:
- Masthead issue number and date
- Intro line's issue-number reference
- All body sections per the structure above
Preserve section order, keep it email-friendly (no scripts, no external images unless explicitly sourced), keep the masthead hook and "if you read nothing else" tight.

Write the result to a new `issues/<date>/index.html`.

## 7. Site plumbing

Keep these in sync — they don't visually break if stale, so they're easy to forget (see the SEO checklist this mirrors):
- `index.html` — add the new issue to the archive list and update the "latest issue" card.
- `sitemap.xml` — add a `<url>` entry for the new issue page.
- `feed.xml` — add a new `<item>` at the top (RSS 2.0, RFC 822 `pubDate`).
- `llms.txt` — update "Latest Issues" to show the 5 most recent, newest first.
- Add `Article` JSON-LD to the new issue's `<head>` (copy the pattern from the previous issue page — headline/description matching this issue's own `<title>`/meta description).
- If this issue explains terms in a Q&A-like way, consider `FAQPage` JSON-LD too (only done for issues that are genuinely explainer-shaped so far).

## 8. Self-check

Before opening the PR, verify:
- Every major claim has a source link.
- Dates are current and specific; pay ranges are sourced or explicitly framed as estimated.
- The issue has one clear thesis and a concrete, non-generic hook.
- No hype, no doom, no unsupported predictions.
- HTML renders sensibly (spot-check the structure) and links resolve.

Anything you flagged in step 4.8 as unsourced goes into the PR description under "needs manual verification" — don't silently drop it or silently guess a source.

## 9. Branch, commit, PR, and email a review copy

```
git checkout -b draft/issue-<N>
git add -A
git commit -m "Draft issue <N>: <short title>"
git push -u origin draft/issue-<N>
gh pr create --title "Issue <N>: <short title>" --body "<summary + files changed + needs-manual-verification list>"
```

Update `automation/issue-state.json` on `main`: `status: "drafted"`, `pr_number: <N>`. Commit+push directly.

Then trigger the review email:

```
gh workflow run review-email.yml \
  -f ref=draft/issue-<N> \
  -f issue_path=issues/<date>/index.html \
  -f subject="Issue <N>: <short title>" \
  -f note="First draft — reply with any changes, or APPROVE <N> in Telegram when it looks good."
```

**Always pass `-f ref=draft/issue-<N>`** — the draft lives on that branch until merged, not on `main`. Omitting it broke the first real run (2026-08-02): the workflow defaulted to checking out `main`, where the file didn't exist yet.

Stop here. Do not merge, do not push the issue content to `main`, and do not touch EmailOctopus. `pr-notify` pings Telegram automatically when the PR opens; `telegram-approve` merges it (site deploy only) on `APPROVE <PR#>`, and separately kicks off the EmailOctopus schedule only on a later, explicit `SCHEDULE <PR#>` reply.

## 9a. Revise on feedback

(Reached only from step 0 with a free-text inbox entry already removed, `status` was `drafted`.)

Read the current draft (`issues/<date>/index.html` on the `draft/issue-<N>` branch — check it out or diff against it) and the feedback text. Apply the requested changes directly — don't ask clarifying questions back through this channel, since there's no synchronous way to get an answer; make a reasonable interpretation and let the next review email make the result visible. Re-run the relevant parts of steps 5-8 (draft/HTML/site-plumbing/self-check) as needed for just the changed sections.

```
git checkout draft/issue-<N>
git add -A
git commit -m "Revise issue <N> per feedback: <one-line summary of the change>"
git push
```

This updates the existing PR in place (same branch) — don't open a new one. Then trigger the review email again:

```
gh workflow run review-email.yml \
  -f ref=draft/issue-<N> \
  -f issue_path=issues/<date>/index.html \
  -f subject="Issue <N>: <short title>" \
  -f note="Updated per your feedback: <one-line summary>. Reply again to keep iterating, or APPROVE <N> when it looks good."
```

Leave `status` as `"drafted"` — this loop can repeat as many times as needed before `APPROVE`.

## 10. Report back

Summarize in chat (or, if run unattended by the cloud routine, this is the routine's entire output): issue number/date, the PR link, the top developments covered, and anything flagged for manual verification.
