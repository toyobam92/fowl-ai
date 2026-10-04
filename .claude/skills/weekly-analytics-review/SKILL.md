---
name: weekly-analytics-review
description: Run FOWL AI's weekly product-analytics review — archive new GA4 exports, update metrics-history.csv and the site dashboards, check in on experiments in analytics/EXPERIMENTS.md, and flip analytics/roadmap.md items from planned to live as they ship. Reads the week straight from the GA4 Data API via the analytics-mcp-fowlai MCP (manual CSV exports are a fallback). Use when the user asks for the "weekly review," drops new GA export CSVs, or a scheduled weekly reminder fires — run it on Monday, once the Mon-Sun week has closed in the property timezone.
---

# Weekly analytics review

FOWL AI is run like a product, not just a newsletter: every site change is an experiment with a hypothesis, a metric, a result, and a decision, logged in `analytics/EXPERIMENTS.md`. This skill is the weekly loop that keeps that log and the metrics history honest. Run it in the `fowlai-site-upload` directory.

## 1. Get the week's data

### 1a. Only run on a closed week

The reporting week is **Monday–Sunday in the property's own timezone (`America/Los_Angeles`)**. A week is not readable until it has closed there — 23:59 PT Sunday, which is ~03:00 ET Monday. **Run this review on Monday, not Sunday evening.**

Reviews before 2026-10-04 were all run Sunday evening against a still-open week, so every row through `2026-09-21–27` is biased low. Re-pulling the closed Sep 21–27 week gave 635 active users where the Sunday-evening CSV said 609 (−4.1%), 629 new users vs 602, 349 key events vs 344. The bias is small but systematic and it lands in exactly the week-over-week deltas this log is read for. If a row must be written mid-week for some reason, label it partial in the chat report and re-pull it once the week closes — never present it as final.

### 1b. Prefer the GA4 MCP over manual CSV exports

The `analytics-mcp-fowlai` MCP reads the property directly — **account `396215392`, property `539490882`** — so no manual export step is needed:

```
mcp__analytics-mcp-fowlai__run_report(
  property_id=539490882,
  date_ranges=[{"start_date": "<monday>", "end_date": "<sunday>"}],
  dimensions=[...], metrics=[...])
```

Useful shapes: `dimensions=[]` with `metrics=["activeUsers","newUsers","screenPageViews","keyEvents","engagementRate","userEngagementDuration","sessions","bounceRate"]` for the headline row; `dimensions=["pagePath"]` for per-page views/bounce; `dimensions=["date"]` for the daily shape (worth checking every week — it's what distinguishes a real trend from one anomalous spike day); `dimensions=["eventName","isKeyEvent"]` to audit what actually counts as a key event. Note `avg_engagement_time_s` is `userEngagementDuration / activeUsers`, not a metric of its own.

When pulling from the MCP there is no raw CSV to archive, so write the queried numbers into `analytics/raw-exports/<end-date>/` as a small CSV or JSON yourself, noting that the source was the Data API rather than a UI export. The point of step 2 is an auditable record of what was read, whatever the source.

### 1c. Fall back to CSV exports

If the MCP is unavailable, look in `~/Downloads` for GA4 exports newer than the latest date folder in `analytics/raw-exports/`. Expected filenames follow the pattern Google Analytics uses on export: `Reports_snapshot*.csv` (the multi-table site snapshot — users, top pages, traffic sources, Nth-day retention, platform, city) and `Demographic_details_Country*.csv` (country breakdown). The user may export others over time (referrers, device category, etc.) — archive whatever's there.

If neither the MCP nor a new export is available, **stop and tell the user** what to export and where to drop it. Do not fabricate a week's data from the last snapshot.

### 1d. "Key events" does not mean conversions

Confirmed 2026-10-04: `generate_lead` is the only event in the property marked as a key event, it fires only on `/contact/`, and it tracks Contact page views 1:1 (114 views / 113 key events, Sep 28–Oct 4) on a page with no `<form>` and no `generate_lead` call in the repo. **Every `key_events` number in `metrics-history.csv` is a count of Contact page views.** It also inflates `engagement_rate`, since a key event marks a session engaged.

`subscribe_click`, `subscribe_attempt`, `subscribe_start`, `subscribe_request_returned`, `form_start` and `form_submit` are all firing and collected, just not marked as key events — so the long-standing "instrumentation" blocker is really two marking steps in GA4 Admin → Events. Until those are done, do not describe `key_events` as conversions anywhere in `EXPERIMENTS.md` or the dashboards.

## 2. Archive

Read the `# Start date / # End date` header comment in the CSV to get the date range (format `YYYYMMDD`). Copy the raw file(s) unmodified into `analytics/raw-exports/<end-date>/`, named clearly (`reports-snapshot.csv`, `demographic-details-country.csv`, etc.) — this is the source of truth if a parsed number is ever in question.

## 3. Append to metrics-history.csv

Parse the new export(s) and append one row to `analytics/metrics-history.csv` using the existing header schema. If a metric a new export adds isn't in the schema yet, add a column (never silently drop data) and backfill earlier rows with an empty value. Keep one row per reporting period — don't overwrite prior weeks.

## 4. Update the site-snapshot dashboard

Both dashboards' repo file paths and published Artifact URLs are in `analytics/dashboards/dashboards.json` — read it rather than searching or asking. Edit `analytics/dashboards/site-snapshot.html` (the file, not the scratchpad copy — this repo copy is the durable source) with the new period's numbers, then republish it by calling `Artifact` with that file path **and** `url` set to the `site-snapshot` entry's URL, so it updates in place instead of minting a new link. Once `metrics-history.csv` has 2+ rows, add week-over-week deltas (▲/▼ vs. prior week) to the stat tiles instead of a single static number — that's the point of tracking history. Follow the dataviz skill for any chart changes.

## 5. Walk the experiment log

Open `analytics/EXPERIMENTS.md` and, for every entry:

- **Status: Planned** — check `git log` in this repo for commits since the last review that plausibly ship it (match ticket language/page). If shipped, move it to `Reading`, set the shipped date and commit hash, and set baseline = the metrics-history row immediately before the ship date (or "not available" if it shipped before tracking existed, as with the first three entries).
- **Status: Reading** — compute days since shipped. If **≥ 7 days and ≥ 2 metrics-history rows** have accumulated since ship, fill in **Result** (what the metric actually did, with numbers) and **Decision** (Keep / Iterate / Revert / Inconclusive — say which and why). Small-sample weeks (this site is still low-traffic) should be called out as directional, not conclusive, until the sample is large enough to trust. If less than 7 days or 2 rows, leave as `Reading` and note progress (e.g. "1 of 2 reads collected") rather than forcing a premature call.
- **Status: Decided** — leave alone unless the user wants to revisit.

Update the Quick View table at the top of `EXPERIMENTS.md` to match.

## 6. Walk the roadmap

Open `analytics/roadmap.md`. For every `planned` or `in_progress` item, check `git log` since the last review for a commit that plausibly ships it — use the item's **match hints** column as a cue, not an exact-string requirement (judgment call, same as ticket matching in step 5). On a match:

- Flip status to `live` (or `in_progress` if the commit reads like a partial/first pass), fill in `Shipped` with the date and commit hash.
- Add a matching entry to `analytics/EXPERIMENTS.md` — a new roadmap page shipping is exactly the kind of change this whole system exists to measure (pick a sensible primary metric: a new hub page → engagement rate / pages-per-session on that page; the "This Week in 5 Minutes" signature page → return-visit rate, since that's its entire premise).
- Regenerate the status badges in `analytics/dashboards/phase1-roadmap.html` to match (badge class `live`/`progress`/`planned`/`later`, see the file's existing CSS) and update the progress meter numbers (live / in-progress / planned counts and the fraction in the meter).
- Republish via `Artifact` with `file_path` = the repo copy and `url` = the `phase1-roadmap` entry in `dashboards.json`.

**Never auto-flip a `later` item**, even if a commit looks related — those were explicitly deferred; confirm with the user first if you see something that looks like it touches one.

If nothing matched this week, leave `roadmap.md` and the dashboard untouched — don't touch the artifact just to redeploy an unchanged file.

## 7. Report back and suggest next

Summarize in chat, briefly: what shipped this week (both experiments and roadmap items), what moved (with numbers), any decisions made, and any still pending more data. Then look at `TICKETS.md` for the highest-priority item with no matching `EXPERIMENTS.md` entry yet and suggest it as next up — remember `TICKET-6` (sitewide event instrumentation) blocks getting a trustworthy read on several other experiments, so keep surfacing it until it ships. If nothing on `roadmap.md` shipped in a while, it's fair to nudge toward the next `planned` item too.

## 8. Branch, commit, and open a PR — don't push to main

`analytics/` (including `dashboards/`, `roadmap.md`, `EXPERIMENTS.md`, `metrics-history.csv`, `raw-exports/`) lives in the site's git repo (`fowlai-site-upload`, remote `origin` → `github.com/toyobam92/fowl-ai.git`). Don't commit straight to `main` or push directly — instead:

```
git checkout -b update/weekly-review-<date>
git add -A
git commit -m "Weekly analytics review (<date>): <one-line summary>"
git push -u origin update/weekly-review-<date>
gh pr create --title "Weekly analytics review (<date>)" --body "<what shipped/moved/decided this week>"
```

`.github/workflows/pr-notify.yml` pings Telegram with the diff automatically when the PR opens, and `.github/workflows/telegram-approve.yml` merges it (deploying the updated dashboards/logs) once the user replies `APPROVE <PR#>` — no separate ask-before-push step needed here anymore.
