---
name: weekly-issue
description: Produce this week's FOWL AI newsletter issue end-to-end — live web research, draft, branded HTML, and site plumbing (archive list, sitemap, feed, llms.txt) — then open a PR gated on Telegram approval instead of pushing straight to main. Use when it's time to start the week's issue, the Sunday cloud routine fires, or the user asks to draft/publish the next issue.
---

# Weekly issue

This replaces the old three-prompt manual workflow (research memo → draft → HTML update) with one pass. It runs the same editorial process, just without you pasting anything by hand. It is self-contained inside this repo (`fowlai-site-upload`) so it works whether it's run locally in Claude Code or by the unattended Sunday cloud routine, which only has access to this repo — not the sibling `automation/` folder in the outer project directory.

**Cadence:** drafted Sunday, merged/live ~7am Monday, emailed ~7:45am Monday (matches the existing EmailOctopus send history). Reply `APPROVE <PR#>` in Telegram around 7am Monday so the site flip and the email draft line up with that schedule — approving earlier just means the site goes live earlier than usual.

**This skill never pushes to `main` and never sends anything.** It ends at an open PR. Merging (and the deploy that follows) happens only when the user replies `APPROVE <PR#>` in Telegram — see `.github/workflows/pr-notify.yml` and `.github/workflows/telegram-approve.yml`. Once merged, `telegram-approve.yml` automatically kicks off `.github/workflows/send-issue.yml`, which uses Playwright to build the EmailOctopus draft (see `automation/emailoctopus-draft.mjs`) — you still press Send yourself in EmailOctopus.

## 1. Figure out the issue number and date

Look at the folder names under `issues/` (e.g. `2026-07-27`) and the "Issue N" markers inside the most recent one's `<title>`/masthead to get the last published issue number and date. This week's issue is number+1, dated the coming Tuesday (the FOWL AI cadence — check the gap from the last issue to confirm before assuming).

## 2. Research

Use `WebSearch`/`WebFetch` to gather this week's developments. Prioritize, in order:
- AI labor market shifts
- AI-native career changes
- enterprise AI adoption
- AI evaluation and trainer work
- hidden AI gig/platform opportunities
- community chatter (Reddit, etc.) that reveals practical truth over hype

Produce, internally, before drafting:
1. Top 5 developments (with source links)
2. The strongest hook for the masthead
3. The "if you read nothing else" paragraph
4. Signal & Chatter bullets
5. Reddit/community chatter bullets
6. One emerging AI-work career title worth explaining
7. AI trainer/eval platform opportunities and new AI jobs worth listing
8. Any claim you can't source cleanly — flag it, don't smooth it over

## 3. Draft

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

## 4. HTML

Use the most recently published issue's HTML (`issues/<latest-date>/index.html` in this repo) as the structural template — it already carries the correct FOWL AI branding, colors, typography, and layout. Replace only the issue-specific copy:
- Masthead issue number and date
- Intro line's issue-number reference
- All body sections per the structure above
Preserve section order, keep it email-friendly (no scripts, no external images unless explicitly sourced), keep the masthead hook and "if you read nothing else" tight.

Write the result to a new `issues/<date>/index.html`.

## 5. Site plumbing

Keep these in sync — they don't visually break if stale, so they're easy to forget (see the SEO checklist this mirrors):
- `index.html` — add the new issue to the archive list and update the "latest issue" card.
- `sitemap.xml` — add a `<url>` entry for the new issue page.
- `feed.xml` — add a new `<item>` at the top (RSS 2.0, RFC 822 `pubDate`).
- `llms.txt` — update "Latest Issues" to show the 5 most recent, newest first.
- Add `Article` JSON-LD to the new issue's `<head>` (copy the pattern from the previous issue page — headline/description matching this issue's own `<title>`/meta description).
- If this issue explains terms in a Q&A-like way, consider `FAQPage` JSON-LD too (only done for issues that are genuinely explainer-shaped so far).

## 6. Self-check

Before opening the PR, verify:
- Every major claim has a source link.
- Dates are current and specific; pay ranges are sourced or explicitly framed as estimated.
- The issue has one clear thesis and a concrete, non-generic hook.
- No hype, no doom, no unsupported predictions.
- HTML renders sensibly (spot-check the structure) and links resolve.

Anything you flagged in step 2.8 as unsourced goes into the PR description under "needs manual verification" — don't silently drop it or silently guess a source.

## 7. Branch, commit, PR

```
git checkout -b draft/issue-<N>
git add -A
git commit -m "Draft issue <N>: <short title>"
git push -u origin draft/issue-<N>
gh pr create --title "Issue <N>: <short title>" --body "<summary + files changed + needs-manual-verification list>"
```

Stop here. Do not merge, do not push to `main`. `pr-notify` will ping Telegram automatically when the PR opens; `telegram-approve` merges it (triggering the GitHub Pages deploy) once the user replies `APPROVE <PR#>`.

## 8. Report back

Summarize in chat (or, if run unattended by the cloud routine, this is the routine's entire output): issue number/date, the PR link, the top developments covered, and anything flagged for manual verification.
