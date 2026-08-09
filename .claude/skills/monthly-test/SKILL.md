---
name: monthly-test
description: Produce FOWL AI's monthly "Tests" head-to-head — propose 5 tool-matchup ideas via Telegram, wait for a pick, actually run the identical task through each picked AI tool, score the real output files, draft the writeup, then open a PR gated on Telegram approval. Use when it's time for this month's test, the recurring cloud routine fires, or the user asks to run/draft the next FOWL AI test.
---

# Monthly test

FOWL AI Tests (`/tests/`) is a monthly feature: the same real task, given word-for-word to several AI tools, judged only on the actual files they produce — never the chat transcript. The whole brand promise is "no sponsorships, real files, real numbers." That promise only holds if every scored claim in the writeup traces back to a file this run actually opened. **Never simulate, guess, or reconstruct what a tool "would have" produced — if a tool can't actually be run this cycle, say so and stop, don't approximate.**

This mirrors the `weekly-issue` skill's shape (propose → pick → produce → PR → Telegram-gated merge) but the "produce" step is fundamentally different: it requires driving real, logged-in AI-tool web sessions, which only an interactive Claude Code session with browser tools can do. A cloud routine can propose and can notice a pick, but it can never run the test itself.

**Shared inbox namespacing — read this before touching `automation/inbox.json`.** This repo's Telegram relay (`telegram-approve.yml`) funnels every non-`APPROVE`/`SCHEDULE` message into one shared `automation/inbox.json`, also consumed by the `weekly-issue` skill (bare digits `1`-`5` / `MORE` for its own topic pick, and otherwise free text for issue revision feedback). To avoid two automations racing over the same message: **every reply meant for this skill's pick step must be prefixed `TEST `** — `TEST 1` through `TEST 5`, or `TEST MORE`. When scanning the inbox, only ever match/consume entries with that exact prefix (case-insensitive); ignore everything else and leave it in place. `weekly-issue` has been updated to reciprocally skip `TEST `-prefixed entries when looking for its own revision feedback — don't undo that.

## 0. Check state and inbox first

Read `automation/test-state.json` (create `{"status": "idle", "last_proposed": null}` if missing) and `automation/inbox.json` (`[]` if missing/drained). Branch on `status`:

- **`idle`** → propose only if `last_proposed` is unset or **25+ days** old (monthly cadence — no day-of-week gate needed, unlike the weekly issue, since this isn't tied to a specific weekday). Otherwise exit quietly. If due, go to step 1.
- **`awaiting_pick`** → scan the inbox for an entry matching `TEST 1`-`TEST 5` or `TEST MORE` (case-insensitive, trimmed). Anything else in the inbox is not yours — leave it untouched. If no match, exit. If found, remove *only that entry* from the inbox (commit that removal on its own, same pattern as `weekly-issue`) and go to step 2.
- **`needs_run`** (a matchup is picked but hasn't been run/drafted yet) → this state can only be advanced by an *interactive* session (browser access required — see step 3). If this run is the unattended cloud routine, do nothing except, once per day at most, re-send the Telegram nudge from step 2 if `last_nudged` is unset or 20+ hours old (update `last_nudged` when you do) — don't spam every fire. If this run is interactive and the user has asked to run this month's test, proceed to step 3.
- **`drafted`** (PR open) → check whether the PR (`pr_number`) is merged. If merged: set `status: "idle"`, clear `matchups`/`rejected_matchups`/`picked_matchup`/`pr_number`/`last_nudged`, commit+push to `main`, exit. If not merged, nothing to do — exit (no revision-via-Telegram loop for this skill; ask interactively for changes instead, same as the EmailOctopus `SCHEDULE` step).
- Anything else → treat as idle, start over.

## 1. Propose 5 matchups

Light `WebSearch` pass for what's current, then sketch 5 distinct matchup ideas. Each needs:
- A concrete, real-world task that produces an actual downloadable file or verifiable artifact (a resume, a cover letter, a one-page pitch deck, a budget spreadsheet, a landing page, a cron script, a resignation letter — anything with a checkable output, not just prose in a chat window).
- 3-5 AI tools worth comparing on it (vary these month to month — don't always reuse Claude/ChatGPT/Codex/Claude Code; e.g. Gemini, Perplexity, Copilot, Claude.ai vs. Claude Code specifically, etc. are all fair game when relevant to the task).
- A one-sentence why-this-task-now.

Figure out the next test number by listing folders under `tests/` (excluding `tests/index.html` itself) — same approach as `weekly-issue` step 3 for issue numbers.

Write to `automation/test-state.json`:

```json
{
  "status": "awaiting_pick",
  "last_proposed": "<today>",
  "test_number": <next N>,
  "matchups": [{"task": "...", "tools": ["...", "..."], "why": "..."}, ...],
  "rejected_matchups": [],
  "picked_matchup": null,
  "pr_number": null,
  "last_nudged": null,
  "last_updated": "<now>"
}
```

Commit+push directly to `main`. Send via `gh workflow run notify.yml -f text="..."` (never curl Telegram directly — no bot token exists in this environment, same reason as `weekly-issue`):

```
🧪 This month's FOWL AI Test — pick one (reply "TEST <number>"):
1. <task> — testing <tools> — <why>
2. ...
3. ...
4. ...
5. ...

Reply "TEST MORE" for five different options.
```

Stop here.

## 2. Act on the pick

(Reached only from step 0 with an inbox entry already removed.)

- **`TEST MORE`** → move current `matchups` into `rejected_matchups`, generate 5 new ideas not repeating any rejected task, `status` stays `awaiting_pick`, commit+push, message the new list. Stop.
- **`TEST 1`-`TEST 5`** → set `picked_matchup` to that entry, `status: "needs_run"`, commit+push. Then send:
  ```
  🧪 Picked: <task> (<tools>). This needs a live browser to actually run each tool, so it can't happen unattended — open Claude Code and ask me to run this month's test when you're ready.
  ```
  Stop here in this run regardless of whether it's the cloud routine or an interactive session — step 3 only proceeds when the *user* explicitly asks in an interactive session, not automatically just because state flipped to `needs_run`.

## 3. Run the test (interactive only — never attempt from the unattended cloud routine)

For the picked task and each picked tool:

1. **Write the exact prompt once**, verbatim, reused word-for-word across every tool — this is the whole point of the test. Note it down for the "Show the exact prompt we used" section later.
2. **Drive the tool for real.** Use `claude-in-chrome` for web-based tools (claude.ai, chatgpt.com, chatgpt.com/codex, gemini.google.com, etc.) — the user needs to already be logged in; if a tool isn't logged in or isn't reachable, **stop and tell the user via chat which tool failed and why, don't substitute a guess.** For Claude Code itself, run the task directly in a scratch directory.
3. **Get the real output file.** If the tool's product produces a downloadable file (.docx, .pdf, .pptx, .xlsx, a code file), download and open/inspect it for real — page counts, structure, actual rendered content. If a tool only ever returns chat text with no artifact, that itself is a scoreable fact (per the existing rubric philosophy: "we check the actual file, not the chat reply" — a tool that never produces a real file is disadvantaged on whatever rubric category covers deliverable format).
4. **Save everything to a scratch directory** (this session's scratchpad, not the repo) before drafting: each tool's raw output file, extracted text (especially the opening paragraph/summary for the "Summary Showdown" section), and objective facts (page count, word count, file format).

Never write a rubric score, a quoted line, or a claim in the final page that doesn't trace back to a file actually opened this run.

## 4. Design a rubric for this specific task

Reuse the pattern from `tests/best-ai-resume-generator/index.html` (5 categories, each scored 1-5 dots from the real file only, total out of 25, plus a legend 5=Excellent … 1=Poor) but **write categories that actually matter for this task** — don't reuse the resume test's categories (Content Depth, Structure & ATS-Safety, Page-Fit Verification, Visual Polish, Honesty) verbatim for an unrelated task. E.g. a landing-page test might score Copy Clarity, Responsive Layout, Load-Bearing CTA Placement, Accessibility, Honesty (no fabricated stats). Honesty (no fabricated facts/credentials/numbers not present in the source brief) is worth keeping as a recurring category regardless of task, since it's core to the brand's credibility claim.

## 5. Draft the page

Use `tests/best-ai-resume-generator/index.html` as the structural/CSS template (same approach as `weekly-issue` step 6 reusing the latest issue's HTML) — same masthead pattern, methodology card, scoreboard table, "Summary Showdown" (verbatim opening lines per tool), "Sample View" (per-tool real facts: page count / word count / what it did differently), "What We Found" narrative, closing CTA. Replace only the task-specific content. Write to `tests/<slug>/index.html`. Include `Article` JSON-LD matching the pattern already on the resume-generator page.

## 6. Site plumbing

- `tests/index.html`: move the current "latest" row to a plain archive row, add the new test as the new `latest` row, update the empty-note if present.
- `sitemap.xml`: add `<url><loc>https://www.fowl-ai.com/tests/<slug>/</loc><priority>0.9</priority><changefreq>monthly</changefreq></url>`.
- `llms.txt`: no change needed unless its Tests description goes stale.
- Do **not** add to `feed.xml` — that's issues-only, tests aren't part of the newsletter RSS scope.

## 7. Branch, commit, PR

```
git checkout -b draft/test-<N>-<slug>
git add -A
git commit -m "Test #<N>: <short title>"
git push -u origin draft/test-<N>-<slug>
gh pr create --title "Test #<N>: <short title>" --body "<summary + which tools ran cleanly vs. couldn't be tested + files changed>"
```

Update `automation/test-state.json` on `main`: `status: "drafted"`, `pr_number: <N>`. Commit+push directly. `pr-notify.yml` fires on any PR now (no branch-prefix allowlist, fixed 2026-08-09) and `telegram-approve.yml`'s generic `APPROVE <PR#>` already merges any PR — neither needs a test-specific change.

Stop here. Don't merge, don't push to `main` beyond the state file.

## 8. Report back

Summarize: test number/task, which tools ran successfully vs. had to be skipped (and why), the PR link, and the final scoreboard.
