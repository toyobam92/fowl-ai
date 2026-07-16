# FOWL AI — experiment log

Every change to fowl-ai.com that could plausibly move a metric gets an entry here: **Hypothesis → Metric → Result → Decision.** Content publishing (new issues, job listing refreshes) doesn't need an entry — this is for structural/UX changes to the site itself.

Status values: `Planned` (not shipped) · `Reading` (shipped, collecting data) · `Decided` (enough data to call it — Keep / Iterate / Revert).

Data source: weekly GA4 exports dropped into `analytics/raw-exports/<date>/`, rolled up in `analytics/metrics-history.csv`. See [weekly-analytics-review skill](../.claude/skills/weekly-analytics-review/SKILL.md) for how this log gets updated.

**Known gap:** GA4 tracking on fowl-ai.com only started producing exports as of 2026-07-16. The three experiments below shipped in the days just before/at that first export, so there is no true pre-change baseline for them — they're being read forward from ship date instead of compared against a "before" snapshot. Everything shipped from here on will have a real baseline (the most recent weekly snapshot before it ships).

---

## Quick view

| Experiment | Primary metric | Shipped | Status |
|---|---|---|---|
| [Homepage declutter (new hero)](#homepage-declutter-new-hero) | Homepage bounce rate | 2026-07-15 | Reading |
| [Embedded signup form + social proof](#embedded-signup-form--social-proof) | Newsletter conversion rate | 2026-07-14 | Reading |
| [Issues → Briefings rename + sharper copy](#issues--briefings-rename--sharper-copy) | Avg. engagement time / session | 2026-07-14 | Reading |
| [Jobs Board filters](#jobs-board-filters) | Engagement rate (Jobs Board) | — | Planned |
| [Platforms Directory filters](#platforms-directory-filters) | Engagement rate (Platforms Directory) | — | Planned |
| ["Start here" + related-issue links](#start-here--related-issue-links) | Pages / session | — | Planned |
| [Sitewide event instrumentation](#sitewide-event-instrumentation) | % sessions with a tracked engagement event | — | Planned |

---

## Homepage declutter (new hero)

**Hypothesis:** Removing decorative animation and tightening the hero and section rhythm reduces friction on the page that receives the most Google-organic traffic, lowering bounce rate.
**Metric:** Homepage bounce rate (GA4, page = `FOWL AI | AI Jobs, Platforms & Opportunities`).
**Shipped:** 2026-07-15 (`c1e14c2` — "Declutter homepage: remove gimmicky animations, tighten hero, fix section rhythm")
**Baseline:** Not available (shipped at/before first GA export). First read: 100% bounce, 21 views, 14 users (2026-07-15–16) — 1 day of post-ship data, too small to call.
**Result:** Pending — needs 2+ more weekly reads.
**Decision:** Pending.

## Embedded signup form + social proof

**Hypothesis:** Embedding the signup form directly in the hero (instead of linking out) plus a social-proof line increases newsletter conversion rate.
**Metric:** Newsletter conversion rate — currently not a tracked GA4 event; needs a "subscribe submitted" conversion event (see [Sitewide event instrumentation](#sitewide-event-instrumentation)). Proxy until then: homepage → Contact/subscribe engagement.
**Shipped:** 2026-07-14 (`2eb9ef8` — "Embed signup form in hero and add social proof")
**Baseline:** Not available.
**Result:** Pending — blocked on conversion-event tracking existing at all. This is the clearest case for shipping the instrumentation ticket first.
**Decision:** Pending.

## Issues → Briefings rename + sharper copy

**Hypothesis:** Sharper, less generic homepage copy and reframing "Issues" as "Briefings" makes the value prop clearer, increasing average engagement time per session.
**Metric:** Average engagement time per active user (sitewide + homepage).
**Shipped:** 2026-07-14 (`efeb2da` — "Sharpen homepage landing-page copy and rename Issues to Briefings")
**Baseline:** Not available. First read: 17s avg. engagement/user sitewide (2026-07-15–16).
**Result:** Pending.
**Decision:** Pending.

## Jobs Board filters

**Hypothesis:** Adding filters/search/save-buttons to the Jobs Board gives visitors something to interact with beyond the initial pageview, raising engagement rate and lowering bounce on `/jobs`.
**Metric:** Engagement rate on the AI Jobs Board page.
**Ticket:** TICKET-2 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** 100% bounce, 6 views, 4 users.

## Platforms Directory filters

**Hypothesis:** Same mechanism as the Jobs Board — filters/search or tracked outbound clicks on platform links give GA4 something to count as engagement, lowering bounce on `/platforms`.
**Metric:** Engagement rate on the AI Platforms Directory page.
**Ticket:** TICKET-3 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** 100% bounce, 5 views, 2 users.

## "Start here" + related-issue links

**Hypothesis:** A pinned "start here" issue on the archive, plus a recommended-next-issue link at the bottom of each post, increases pages viewed per session (this is FOWL AI's version of "related articles").
**Metric:** Pages / session (sitewide), and views on `/issues` specifically.
**Ticket:** TICKET-4 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** All Issues page — 100% bounce, 8 views, 6 users.

## Sitewide event instrumentation

**Hypothesis:** Most of the site's bounce rate currently reflects missing GA4 event tracking (only Contact has a working conversion event), not actual visitor disengagement. Adding scroll, outbound-click, and subscribe events will both lower measured bounce and — more importantly — make every other experiment on this list actually measurable.
**Metric:** % of sessions with at least one tracked engagement event, sitewide.
**Ticket:** TICKET-6 in `TICKETS.md`.
**Status:** Planned — not yet shipped. **This should ship before/alongside the others** — every experiment above needs it to produce a trustworthy result.
**Baseline (as of 2026-07-15–16):** 17s avg. engagement/user sitewide; Contact is the only page with a non-100% bounce rate.
