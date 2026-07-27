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
| [Sitewide event instrumentation](#sitewide-event-instrumentation) | % sessions with a tracked engagement event | 2026-07-16 | Reading |
| [AI Glossary launch](#ai-glossary-launch) | Bounce rate / engagement on `/glossary/` | 2026-07-20 | Reading |

---

## Homepage declutter (new hero)

**Hypothesis:** Removing decorative animation and tightening the hero and section rhythm reduces friction on the page that receives the most Google-organic traffic, lowering bounce rate.
**Metric:** Homepage bounce rate (GA4, page = `FOWL AI | AI Jobs, Platforms & Opportunities`).
**Shipped:** 2026-07-15 (`c1e14c2` — "Declutter homepage: remove gimmicky animations, tighten hero, fix section rhythm")
**Baseline:** Not available (shipped at/before first GA export). First read: 100% bounce, 21 views, 14 users (2026-07-15–16) — 1 day of post-ship data, too small to call.
**Result:** Three reads in: 100% bounce (2026-07-15–16, n=21 views) → 64.3% (2026-07-10–16, n=99, overlapping window) → 57.6% (2026-07-20–26, n=85 views/52 users) — the first fully clean 7-day read, both fully post-ship and fully post-TICKET-6. Bounce has fallen every read. Views/users dipped week-over-week alongside a sitewide traffic dip (94 vs 154 active users total), so the page isn't pulling more visitors, but the ones who land are bouncing less. Caveat: this week is also the first full week of TICKET-6's scroll/outbound event tracking, which mechanically lowers measured bounce sitewide (see Sitewide event instrumentation below) — some of this improvement is better measurement, not confirmed proof the decluttered hero itself is working harder.
**Decision:** Keep (directional) — 11 days and 3 reads since ship, gate met, and the trend is consistently in the right direction with no signal to revert. Not marking this fully Decided: TICKET-6 confounds the exact magnitude this cycle. Will treat next cycle's read (first *stable* week, tracking-wise) as the cleaner comparison.

## Embedded signup form + social proof

**Hypothesis:** Embedding the signup form directly in the hero (instead of linking out) plus a social-proof line increases newsletter conversion rate.
**Metric:** Newsletter conversion rate — currently not a tracked GA4 event; needs a "subscribe submitted" conversion event (see [Sitewide event instrumentation](#sitewide-event-instrumentation)). Proxy until then: homepage → Contact/subscribe engagement.
**Shipped:** 2026-07-14 (`2eb9ef8` — "Embed signup form in hero and add social proof")
**Baseline:** Not available.
**Result:** Still blocked on a real conversion-event metric — `subscribe_click`/`subscribe_submit` aren't marked as GA4 Key Events yet (manual step, see Sitewide event instrumentation below), so this reads on the Contact-page proxy only. Three reads: 0% bounce/13 views (2026-07-15–16) → 0% bounce/36 views/32 users (2026-07-10–16) → 0% bounce/12 views/12 users, **12 of 12 key events sitewide this week came from Contact** (2026-07-20–26). Contact remains the one page that never bounces, and now has a 100% generate_lead rate per active user this week — but this proxy only measures the Contact form, not the homepage-hero signup embed this experiment actually changed.
**Decision:** Inconclusive — gate (≥7 days, ≥2 rows) is technically met, but the metric itself is still the wrong one. Can't call this until `subscribe_click`/`subscribe_submit` are marked as Key Events (needs Toyo to do this in GA4 Admin) so the actual hero-embed conversion path is measurable.

## Issues → Briefings rename + sharper copy

**Hypothesis:** Sharper, less generic homepage copy and reframing "Issues" as "Briefings" makes the value prop clearer, increasing average engagement time per session.
**Metric:** Average engagement time per active user (sitewide + homepage).
**Shipped:** 2026-07-14 (`efeb2da` — "Sharpen homepage landing-page copy and rename Issues to Briefings")
**Baseline:** Not available. First read: 17s avg. engagement/user sitewide (2026-07-15–16).
**Result:** Three reads: 17s (2026-07-15–16) → 9s (2026-07-10–16) → **19s (2026-07-20–26)**, back above the original baseline. The dip and rebound track TICKET-6's rollout almost exactly (shipped 2026-07-16, mid-way through the 2nd read's window) — average engagement time per active user is mechanically sensitive to how much is actually being tracked as "engagement," and this week is the first full window with scroll/outbound events counted end-to-end. Can't isolate the copy/rename's effect from the measurement-window effect with the data available.
**Decision:** Inconclusive — the metric moved in both directions across three reads for reasons that track tooling changes, not (necessarily) visitor behavior. Would need a stable-tracking week-over-week comparison (next cycle onward, now that TICKET-6 has been live a full week) before this is callable either way.

## Jobs Board filters

**Hypothesis:** Adding filters/search/save-buttons to the Jobs Board gives visitors something to interact with beyond the initial pageview, raising engagement rate and lowering bounce on `/jobs`.
**Metric:** Engagement rate on the AI Jobs Board page.
**Ticket:** TICKET-2 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** 100% bounce, 6 views, 4 users. **Latest (2026-07-20–26):** 45.5% bounce, 24 views, 14 users (was 52.9% bounce, 19 views, 10 users the week before). Still trending down, still confounded by TICKET-6's sitewide instrumentation like everything else on this list this cycle — real filters/search would give a cleaner, ticket-specific signal.

## Platforms Directory filters

**Hypothesis:** Same mechanism as the Jobs Board — filters/search or tracked outbound clicks on platform links give GA4 something to count as engagement, lowering bounce on `/platforms`.
**Metric:** Engagement rate on the AI Platforms Directory page.
**Ticket:** TICKET-3 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** 100% bounce, 5 views, 2 users. **Latest (2026-07-20–26):** 41.2% bounce, 18 views, 16 users (was 74.1% bounce, 32 views, 23 users the week before). Same caveat as Jobs Board — trending down, but riding TICKET-6's measurement improvement rather than a shipped fix.

## "Start here" + related-issue links

**Hypothesis:** A pinned "start here" issue on the archive, plus a recommended-next-issue link at the bottom of each post, increases pages viewed per session (this is FOWL AI's version of "related articles").
**Metric:** Pages / session (sitewide), and views on `/issues` specifically.
**Ticket:** TICKET-4 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** All Issues page — 100% bounce, 8 views, 6 users. **Latest (2026-07-20–26):** 28.6% bounce, 10 views, 6 users (was 75.9% bounce, 41 views, 22 users the week before). Biggest drop of the four "Planned" tickets on this list, but again this is TICKET-6's tracking window, not a shipped "start here" fix.

## Sitewide event instrumentation

**Hypothesis:** Most of the site's bounce rate currently reflects missing GA4 event tracking (only Contact has a working conversion event), not actual visitor disengagement. Adding scroll, outbound-click, and subscribe events will both lower measured bounce and — more importantly — make every other experiment on this list actually measurable.
**Metric:** % of sessions with at least one tracked engagement event, sitewide.
**Ticket:** TICKET-6 in `TICKETS.md`.
**Shipped:** 2026-07-16 (`a57b9a2` — "Ship TICKET-6: sitewide GA4 event instrumentation"). Added `analytics-events.js` (scroll_75, outbound_click, subscribe_click, subscribe_submit) to all 24 site pages. Scope expanded beyond the original ticket: 14 pages (guide, resume-template, interview-guide, both launchlab pages, and 9 issue archive pages) had no GA4 tracking at all and got the base `gtag` snippet added too, not just events. Still needs a manual step: mark `subscribe_click` and `subscribe_submit` as GA4 Key Events in Admin.

**Follow-up (2026-07-18):** Found that `subscribe_click` alone overstates the funnel for every page except the homepage. The homepage hero's inline signup form posts to a Google Form directly (already covered by `subscribe_submit`), but every other page's "Subscribe" button links out to `fowlai.eo.page/vmk69` — a native EmailOctopus-hosted landing page we don't control, so a click there is only ever intent, never confirmed completion. Added `/subscribed/index.html`: a thank-you page that fires `subscribe_submit` (`method: emailoctopus_redirect`) on load. **Manual step still needed from Toyo:** in the EmailOctopus dashboard, set that form's "redirect on success" URL to `https://www.fowl-ai.com/subscribed/`. Until that's set, `subscribe_submit` will only ever fire from the homepage form — EmailOctopus signups sitewide still only show up as `subscribe_click` (intent, not completion).
**Status:** Reading.
**Baseline (as of 2026-07-15–16):** 17s avg. engagement/user sitewide; Contact is the only page with a non-100% bounce rate. **Pre-ship read (2026-07-10–16):** 9s avg. engagement/user sitewide; Contact still the only page that never bounces, but every other page's bounce rate also fell that week without any corresponding UX change shipping — the leading explanation was that the metric itself was noisy/incomplete without broader event tracking, which is what this ticket fixes.
**Result:** 1 of 2 post-ship reads collected. The 2026-07-10–16 metrics-history row mostly precedes ship (TICKET-6 landed on the last day of that window), so 2026-07-20–26 is the first row that's fully post-ship — and it shows exactly the level-shift predicted last cycle: sitewide avg. engagement/user rose to 19s (from 9s), and bounce fell on every page except Contact (already at 0%): homepage 64.3%→57.6%, All Issues 75.9%→28.6%, Jobs Board 52.9%→45.5%, Platforms Directory 74.1%→41.2%. Key events this week: 12, all `generate_lead` from Contact — `subscribe_click`/`subscribe_submit` still aren't marked as Key Events in GA4 Admin (manual step still pending from Toyo), so the subscribe funnel remains under-measured.
**Decision:** Pending — needs a 2nd fully-post-ship read (next cycle) before calling this. Directionally, the instrumentation is doing what it was supposed to: bounce/engagement numbers now look less like "everything is broken" and more like real page-level differences (Contact 0%, homepage 58%, All Issues 29%).

## AI Glossary launch

**Hypothesis:** Publishing an AI/LLM/MCP terms glossary gives search-intent visitors (people looking up specific terms) a reference page that's inherently sticky, and captures long-tail organic traffic the rest of the site doesn't target.
**Metric:** Bounce rate and average engagement time per active user on `/glossary/`.
**Roadmap item:** [AI Glossary](roadmap.md) (Core Content) — flipped `in_progress` → `live` this cycle.
**Shipped:** 2026-07-20 (`af46d07` — "Add AI Glossary and AI & Future of Work FAQ pages").
**Baseline:** Not available (new page).
**Result:** Pending — first read (2026-07-20–26): 8 views, 3 active users, 16.7% bounce rate, 39s avg. engagement time per active user, 17 events, 0 key events. Lowest bounce rate of any page on the site this week (aside from Contact's 0%), consistent with the "reference content is sticky" hypothesis, but n=3 users is far too small to call anything yet.
**Decision:** Pending — 1 of 2 reads collected (needs ≥7 days and ≥2 metrics-history rows since ship; only 6 days elapsed as of this cycle's data pull).
