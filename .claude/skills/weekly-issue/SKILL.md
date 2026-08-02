---
name: weekly-issue
description: Produce this week's FOWL AI newsletter issue end-to-end — propose 5 topic angles via Telegram, wait for a pick, then live web research, draft, branded HTML, and site plumbing (archive list, sitemap, feed, llms.txt) — then open a PR gated on Telegram approval instead of pushing straight to main. Use when it's time to start the week's issue, the recurring Sunday/Monday cloud routine fires, or the user asks to draft/publish the next issue.
---

# Weekly issue

This replaces the old three-prompt manual workflow (research memo → draft → HTML update) with one pass, plus a topic-pick step so the user chooses the week's angle before any drafting happens. It is self-contained inside this repo (`fowlai-site-upload`) so it works whether it's run locally in Claude Code or by the unattended recurring cloud routine, which only has access to this repo — not the sibling `automation/` folder in the outer project directory.

**Cadence:** topics proposed Sunday, picked any time after, drafted once picked, merged/live ~7am Monday, emailed ~7:45am Monday (matches the existing EmailOctopus send history).

**This skill never pushes to `main` and never sends anything.** It ends at an open PR. Merging happens only when the user replies `APPROVE <PR#>` in Telegram. **Scheduling the email is a separate, later step** — merging only deploys the site. The user must reply `SCHEDULE <PR#>` for `send-issue.yml` to build and arm the EmailOctopus schedule (Playwright, `automation/emailoctopus-draft.mjs`) for the next Monday 7:45am ET; that reply alone is what authorizes touching the real subscriber list, and the schedule stays cancellable in EmailOctopus right up to send time. See `.github/workflows/pr-notify.yml` and `.github/workflows/telegram-approve.yml`.

Because this now spans multiple separate invocations (propose → wait → pick → draft), progress is tracked in `automation/issue-state.json`, committed directly to `main` on every update (it's internal bookkeeping, not site content — no PR needed for this file specifically).

## 0. Check state first

Read `automation/issue-state.json` (create it with `{"status": "idle"}` if it doesn't exist). Branch on `status`:

- **`idle`** (new week, no proposal yet) → go to step 1.
- **`awaiting_pick`** → go to step 2 (check for a reply).
- **`drafted`** or anything else → nothing to do, exit. A new week only starts once someone resets status to `idle` (or the `week_of` date is stale — more than ~10 days old — in which case treat it as idle and start over).

## 1. Propose 5 topics

Do a *light* research pass with `WebSearch` — enough to sketch 5 distinct plausible angles for this week's issue (not the full deep-dive yet). For each: a one-line title and a one-sentence why-now. Write these to `automation/issue-state.json`:

```json
{
  "week_of": "<upcoming Tuesday's date>",
  "status": "awaiting_pick",
  "topics": [{"title": "...", "why": "..."}, ...],
  "rejected_titles": [],
  "picked_topic": null,
  "pr_number": null,
  "last_updated": "<now>"
}
```

Commit and push this file directly to `main` (`git add automation/issue-state.json && git commit -m "Propose issue topics for week of <date>" && git push`). Then message Telegram directly (same pattern as the workflows — `curl` to `https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage`, reading the token from the environment the routine provides):

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

## 2. Check for a pick

Call Telegram's `getUpdates` (same stateless offset/ack pattern as `telegram-approve.yml` — fetch with `offset=0`, immediately re-fetch with `offset=<max_id+1>` to clear the backlog regardless of outcome, and only act on messages from the stored chat_id dated within the last ~20 minutes so a stale reply from days ago can't fire on a later, unrelated run).

- **No matching reply yet** → exit. Nothing to do until the next scheduled run.
- **Reply is `MORE`** (case-insensitive) → move the current `topics` titles into `rejected_titles`, generate 5 new angles that don't repeat any rejected title, update the state file (`topics` replaced, `status` stays `awaiting_pick`), commit+push to `main`, message the new numbered list to Telegram. Stop here.
- **Reply is a digit 1-5** → set `picked_topic` to that entry, `status: "drafting"`, commit+push. Continue in this same run to step 3 — don't wait for another invocation.

## 3. Figure out the issue number and date

Look at the folder names under `issues/` (e.g. `2026-07-27`) and the "Issue N" markers inside the most recent one's `<title>`/masthead to get the last published issue number and date. This week's issue is number+1.

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

## 9. Branch, commit, PR

```
git checkout -b draft/issue-<N>
git add -A
git commit -m "Draft issue <N>: <short title>"
git push -u origin draft/issue-<N>
gh pr create --title "Issue <N>: <short title>" --body "<summary + files changed + needs-manual-verification list>"
```

Then update `automation/issue-state.json` on `main`: `status: "drafted"`, `pr_number: <N>`. Commit+push directly.

Stop here. Do not merge, do not push the issue content to `main`, and do not touch EmailOctopus. `pr-notify` pings Telegram automatically when the PR opens; `telegram-approve` merges it (site deploy only) on `APPROVE <PR#>`, and separately kicks off the EmailOctopus schedule only on a later, explicit `SCHEDULE <PR#>` reply.

## 10. Report back

Summarize in chat (or, if run unattended by the cloud routine, this is the routine's entire output): issue number/date, the PR link, the top developments covered, and anything flagged for manual verification.
