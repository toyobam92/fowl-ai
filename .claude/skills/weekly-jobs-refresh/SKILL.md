---
name: weekly-jobs-refresh
description: Autonomously refresh the AI Jobs Board (/jobs) — check for dead links, replace stale listings with current ones across the three categories, bump the "updated" dates, then open a PR gated on Telegram approval instead of pushing straight to main. Use when it's time to refresh the jobs board, the recurring cloud routine fires, or the user asks to update /jobs.
---

# Weekly jobs refresh

Keeps `jobs/index.html` (the AI Jobs Board) current without a human starting the work. It is self-contained inside this repo (`fowlai-site-upload`) so it works whether run locally in Claude Code or by the unattended recurring cloud routine, which only has access to this repo.

**Reuses the existing publish pipeline as-is — no new GitHub Actions needed.** `pr-notify.yml` already fires on any PR from a branch starting with `update/` and pings Telegram with the diff stat. `telegram-approve.yml` already merges on a plain `APPROVE <PR#>` reply for any PR number — it has no jobs-specific logic to add. This skill only ever touches `jobs/index.html` and its own state file; it never needs to modify those workflows.

**Cadence:** roughly weekly, gated by `automation/jobs-state.json`, not by wall-clock alone — the recurring trigger can fire more or less often than weekly and this stays idempotent.

## 0. Check state first

Read `automation/jobs-state.json` (create `{"status": "idle", "last_refreshed": null, "pr_number": null}` if missing). Branch on `status`:

- **`idle`** → if `last_refreshed` is set and fewer than 7 days have passed, exit quietly (no Telegram message, nothing to do). Otherwise proceed to step 1.
- **`pending`** (a PR was opened last cycle) → check `gh pr view <pr_number> --json state,mergedAt`:
  - Merged → set `status: "idle"`, `last_refreshed: <today>`, `pr_number: null`; commit+push directly to `main`; exit (nothing further to do this cycle).
  - Closed without merging → set `status: "idle"` but leave `last_refreshed` unchanged so the next cycle retries; commit+push to `main`; exit.
  - Still open → exit quietly. Never open a second PR while one is outstanding.

## 1. Research current listings

Use `WebSearch`/`WebFetch` to find real, currently-open opportunities for each of the three categories already on the page (`jobs/index.html`, sections `#section-evaluation`, `#section-emerging`, `#section-company`):

- **AI Evaluation** — Mercor, Handshake AI Fellowship, Surge AI, Invisible Technologies, Scale AI / Outlier, DataAnnotation, Turing, and similar AI trainer/evaluator programs.
- **Emerging Career Roles** — this section links out to LinkedIn job-search URLs (`job-cta search`), not specific postings, so it rarely goes stale. Only touch it if a title has clearly fallen out of use or a clearly-better emerging title should be added.
- **AI Company & Startup Roles** — openai.com/careers, anthropic.com/careers, deepmind.google/careers, and comparable AI-native company career pages.

Prioritize replacing rows that are actually broken (see step 2) over rewriting rows that still work — this should be incremental churn each cycle, not a full rewrite.

## 2. Check existing links

For every unique `href` on a `job-cta apply` or `job-cta referral` link (skip `job-cta search` — those are stable LinkedIn search URLs, not postings), `WebFetch` it and flag anything that 404s, redirects to a generic "job not found" page, or otherwise reads as expired. Replace flagged rows with a fresh listing found in step 1, keeping the same `.job-row` markup shape (title, company/context line, location, badges, pay, CTA link+label). Before adding any new link, `WebFetch` it too and confirm it resolves to a real, live posting — don't add a link you haven't verified.

## 3. Update the page

Edit `jobs/index.html` directly:
- Swap out dead/stale `.job-row` entries per step 2, preserving existing markup conventions (badge classes `new`/`hot`/`freelance`/`fellowship`, CTA classes `apply`/`referral`/`search`).
- Update each of the three `.cat-count` lines ("N roles · updated Mon DD") — role count if it changed, date to today.
- Update the top `.updated-badge` line ("Updated Month DD, YYYY") to today's full date.
- Do not touch CSS, JS (`filterJobs`), or page structure outside the job rows and these date/count strings.

## 4. Branch, commit, and open a PR

```
git checkout -b update/jobs-refresh-<YYYY-MM-DD>
git add jobs/index.html
git commit -m "Refresh AI jobs board — <YYYY-MM-DD>"
git push -u origin update/jobs-refresh-<YYYY-MM-DD>
gh pr create --title "Refresh AI jobs board — <YYYY-MM-DD>" --body "<summary: how many rows replaced/added per category, which dead links were removed and why, any listing you couldn't verify>"
```

Then update `automation/jobs-state.json` on `main` directly (separate commit, not on the branch): `status: "pending"`, `pr_number: <N>` (leave `last_refreshed` as-is until the PR actually merges — step 0 updates it then).

```
git checkout main
git add automation/jobs-state.json
git commit -m "Mark jobs refresh PR #<N> pending"
git push
```

Stop here. Do not merge, and do not push `jobs/index.html` straight to `main`. `pr-notify.yml` pings Telegram automatically when the PR opens; `telegram-approve.yml` merges it (site deploy only) on `APPROVE <PR#>`.

## 5. Report back

Summarize in chat (or, if run unattended by the cloud routine, this is the routine's entire output): how many listings were replaced/added per category, which dead links were removed, the PR link, and anything flagged as unverified.
