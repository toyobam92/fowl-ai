---
name: weekly-analytics-review
description: Run FOWL AI's weekly product-analytics review — archive new GA4 exports, update metrics-history.csv and the site dashboards, check in on experiments in analytics/EXPERIMENTS.md, and flip analytics/roadmap.md items from planned to live as they ship. Use when the user drops new GA export CSVs, asks for the "weekly review," or a scheduled weekly reminder fires.
---

# Weekly analytics review

FOWL AI is run like a product, not just a newsletter: every site change is an experiment with a hypothesis, a metric, a result, and a decision, logged in `analytics/EXPERIMENTS.md`. This skill is the weekly loop that keeps that log and the metrics history honest. Run it in the `fowlai-site-upload` directory.

## 1. Find the new export(s)

Look in `~/Downloads` for GA4 exports newer than the latest date folder in `analytics/raw-exports/`. Expected filenames follow the pattern Google Analytics uses on export: `Reports_snapshot*.csv` (the multi-table site snapshot — users, top pages, traffic sources, Nth-day retention, platform, city) and `Demographic_details_Country*.csv` (country breakdown). The user may export others over time (referrers, device category, etc.) — archive whatever's there.

If nothing new exists, **stop and tell the user** what to export and where to drop it. Do not fabricate a week's data from the last snapshot.

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

## 8. Offer to commit

`analytics/` (including `dashboards/`, `roadmap.md`, `EXPERIMENTS.md`, `metrics-history.csv`, `raw-exports/`) lives in the site's git repo (`fowlai-site-upload`, remote `origin` → `github.com/toyobam92/fowl-ai.git`). After updating them, offer to commit the changes — don't push without being asked.
