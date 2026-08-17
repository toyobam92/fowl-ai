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
| [Nova posting time: morning → evening](#nova-posting-time-morning--evening) | Per-post reach (platform insights) | 2026-08-17 | Reading |

---

## Homepage declutter (new hero)

**Hypothesis:** Removing decorative animation and tightening the hero and section rhythm reduces friction on the page that receives the most Google-organic traffic, lowering bounce rate.
**Metric:** Homepage bounce rate (GA4, page = `FOWL AI | AI Jobs, Platforms & Opportunities`).
**Shipped:** 2026-07-15 (`c1e14c2` — "Declutter homepage: remove gimmicky animations, tighten hero, fix section rhythm")
**Baseline:** Not available (shipped at/before first GA export). First read: 100% bounce, 21 views, 14 users (2026-07-15–16) — 1 day of post-ship data, too small to call.
**Result:** Four reads in: 100% bounce (2026-07-15–16, n=21 views) → 64.3% (2026-07-10–16, n=99, overlapping window) → 57.6% (2026-07-20–26, n=85 views/52 users) → **72.2% (2026-08-02–08, n=84 views/60 users)** — the falling trend broke this cycle; bounce jumped back above every prior read except the very first (100%, n=21, too small to count). This wasn't isolated to the homepage: Jobs Board, Platforms Directory, and About all rose sharply the same week (see Sitewide event instrumentation below), while All Issues and Contact held or improved — a sitewide pattern, not a homepage-specific one, and no code shipped this cycle that touches this page.
**Decision:** Downgrading from "Keep (directional)" to **Inconclusive** — the 3-reads-straight-falling story that justified last cycle's Keep call didn't survive a 4th read. At 84 views/60 users this is still a small sample for a metric that swung 15 points sitewide with no shipped change to explain it, so the likelier explanation is week-to-week noise at this traffic level rather than the hero decluttering losing effectiveness. Holding off on any reversion; will keep reading rather than act on either the 3-read improvement or this cycle's reversal.

## Embedded signup form + social proof

**Hypothesis:** Embedding the signup form directly in the hero (instead of linking out) plus a social-proof line increases newsletter conversion rate.
**Metric:** Newsletter conversion rate — currently not a tracked GA4 event; needs a "subscribe submitted" conversion event (see [Sitewide event instrumentation](#sitewide-event-instrumentation)). Proxy until then: homepage → Contact/subscribe engagement.
**Shipped:** 2026-07-14 (`2eb9ef8` — "Embed signup form in hero and add social proof")
**Baseline:** Not available.
**Result:** Still blocked on a real conversion-event metric — `subscribe_click`/`subscribe_submit` aren't marked as GA4 Key Events yet (manual step, see Sitewide event instrumentation below), so this reads on the Contact-page proxy only. Four reads: 0% bounce/13 views (2026-07-15–16) → 0% bounce/36 views/32 users (2026-07-10–16) → 0% bounce/12 views/12 users, 12 of 12 key events sitewide came from Contact (2026-07-20–26) → **3.0% bounce/35 views/33 users, 35 of 35 key events sitewide came from Contact (2026-08-02–08)**. Contact's bounce ticked up off zero for the first time but is still by far the lowest on the site, and it remains the sole source of every tracked key event — but this proxy only measures the Contact form, not the homepage-hero signup embed this experiment actually changed.
**Decision:** Inconclusive — gate (≥7 days, ≥2 rows) is technically met, but the metric itself is still the wrong one. Can't call this until `subscribe_click`/`subscribe_submit` are marked as Key Events (needs Toyo to do this in GA4 Admin) so the actual hero-embed conversion path is measurable.

## Issues → Briefings rename + sharper copy

**Hypothesis:** Sharper, less generic homepage copy and reframing "Issues" as "Briefings" makes the value prop clearer, increasing average engagement time per session.
**Metric:** Average engagement time per active user (sitewide + homepage).
**Shipped:** 2026-07-14 (`efeb2da` — "Sharpen homepage landing-page copy and rename Issues to Briefings")
**Baseline:** Not available. First read: 17s avg. engagement/user sitewide (2026-07-15–16).
**Result:** Four reads: 17s (2026-07-15–16) → 9s (2026-07-10–16) → 19s (2026-07-20–26) → **11s (2026-08-02–08)**, back down near the 2nd read's level and below the original 17s baseline. The metric has now moved in both directions twice across four reads with no shipped change to explain either swing — it continues to track something other than a stable effect of the copy/rename.
**Decision:** Inconclusive — four reads, four different tooling/traffic conditions, no stable comparison window yet. Would need consecutive reads under matched conditions (similar traffic volume, no instrumentation changes) before this is callable either way; at this point leaning toward suspecting the metric itself is too noisy at current traffic levels to isolate a copy-change effect from week-to-week variance.

## Jobs Board filters

**Hypothesis:** Adding filters/search/save-buttons to the Jobs Board gives visitors something to interact with beyond the initial pageview, raising engagement rate and lowering bounce on `/jobs`.
**Metric:** Engagement rate on the AI Jobs Board page.
**Ticket:** TICKET-2 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** 100% bounce, 6 views, 4 users. **Latest (2026-08-02–08):** 68.4% bounce, 20 views, 10 users (was 45.5% bounce, 24 views, 14 users on 2026-07-20–26). Reversed back up this cycle along with most other pages sitewide (see Sitewide event instrumentation) — real filters/search (TICKET-2, still not shipped) would give a cleaner, ticket-specific signal instead of riding sitewide noise.

## Platforms Directory filters

**Hypothesis:** Same mechanism as the Jobs Board — filters/search or tracked outbound clicks on platform links give GA4 something to count as engagement, lowering bounce on `/platforms`.
**Metric:** Engagement rate on the AI Platforms Directory page.
**Ticket:** TICKET-3 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** 100% bounce, 5 views, 2 users. **Latest (2026-08-02–08):** 64.3% bounce, 32 views, 27 users (was 41.2% bounce, 18 views, 16 users on 2026-07-20–26). Same reversal as Jobs Board this cycle — up sitewide, not a signal specific to this page; still needs a shipped fix (TICKET-3) to get a ticket-specific read.

## "Start here" + related-issue links

**Hypothesis:** A pinned "start here" issue on the archive, plus a recommended-next-issue link at the bottom of each post, increases pages viewed per session (this is FOWL AI's version of "related articles").
**Metric:** Pages / session (sitewide), and views on `/issues` specifically.
**Ticket:** TICKET-4 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** All Issues page — 100% bounce, 8 views, 6 users. **Latest (2026-08-02–08):** 20.0% bounce, 5 views, 5 users (was 28.6% bounce, 10 views, 6 users on 2026-07-20–26). The one page on this list that kept improving even as Homepage/Jobs Board/Platforms Directory reversed this cycle — still worth shipping the actual "start here" fix (TICKET-4) rather than reading too much into the trend at n=5.

## Sitewide event instrumentation

**Hypothesis:** Most of the site's bounce rate currently reflects missing GA4 event tracking (only Contact has a working conversion event), not actual visitor disengagement. Adding scroll, outbound-click, and subscribe events will both lower measured bounce and — more importantly — make every other experiment on this list actually measurable.
**Metric:** % of sessions with at least one tracked engagement event, sitewide.
**Ticket:** TICKET-6 in `TICKETS.md`.
**Shipped:** 2026-07-16 (`a57b9a2` — "Ship TICKET-6: sitewide GA4 event instrumentation"). Added `analytics-events.js` (scroll_75, outbound_click, subscribe_click, subscribe_submit) to all 24 site pages. Scope expanded beyond the original ticket: 14 pages (guide, resume-template, interview-guide, both launchlab pages, and 9 issue archive pages) had no GA4 tracking at all and got the base `gtag` snippet added too, not just events. Still needs a manual step: mark `subscribe_click` and `subscribe_submit` as GA4 Key Events in Admin.

**Follow-up (2026-07-18):** Found that `subscribe_click` alone overstates the funnel for every page except the homepage. The homepage hero's inline signup form posts to a Google Form directly (already covered by `subscribe_submit`), but every other page's "Subscribe" button links out to `fowlai.eo.page/vmk69` — a native EmailOctopus-hosted landing page we don't control, so a click there is only ever intent, never confirmed completion. Added `/subscribed/index.html`: a thank-you page that fires `subscribe_submit` (`method: emailoctopus_redirect`) on load. **Manual step still needed from Toyo:** in the EmailOctopus dashboard, set that form's "redirect on success" URL to `https://www.fowl-ai.com/subscribed/`. Until that's set, `subscribe_submit` will only ever fire from the homepage form — EmailOctopus signups sitewide still only show up as `subscribe_click` (intent, not completion).
**Status:** Reading.
**Baseline (as of 2026-07-15–16):** 17s avg. engagement/user sitewide; Contact is the only page with a non-100% bounce rate. **Pre-ship read (2026-07-10–16):** 9s avg. engagement/user sitewide; Contact still the only page that never bounces, but every other page's bounce rate also fell that week without any corresponding UX change shipping — the leading explanation was that the metric itself was noisy/incomplete without broader event tracking, which is what this ticket fixes.
**Result:** 2 of 2 fully-post-ship reads now collected. 1st fully-post-ship read (2026-07-20–26) showed the predicted level-shift: sitewide avg. engagement/user rose to 19s (from 9s), bounce fell on every page except Contact. The 2nd fully-post-ship read (2026-08-02–08) reversed most of that: avg. engagement/user fell back to 11s, and bounce rose on every page except All Issues (28.6%→20.0%) and Contact (0%→3.0%, still lowest on the site): homepage 57.6%→72.2%, Jobs Board 45.5%→68.4%, Platforms Directory 41.2%→64.3%. Key events jumped to 35 this week (from 12), still 100% `generate_lead` from Contact — `subscribe_click`/`subscribe_submit` still aren't marked as Key Events in GA4 Admin (manual step still pending from Toyo), so the subscribe funnel remains under-measured.
**Decision:** Keep (directional) — the instrumentation itself is functioning as intended (event counts scale with traffic, key events are being captured consistently), so there's no reason to revert it. But the 2nd read undercuts last cycle's "level-shift" framing: bounce/engagement swung by double digits in both directions across the two fully-post-ship reads with nothing else shipping, which reads more like this site's traffic volume (94–124 active users/week) being too small for stable week-over-week bounce comparisons than like a durable measurement improvement. Treat every experiment reading off bounce/engagement on this site as directional only until the sample is meaningfully larger — this is now the working assumption going forward, not a one-off caveat.

## AI Glossary launch

**Hypothesis:** Publishing an AI/LLM/MCP terms glossary gives search-intent visitors (people looking up specific terms) a reference page that's inherently sticky, and captures long-tail organic traffic the rest of the site doesn't target.
**Metric:** Bounce rate and average engagement time per active user on `/glossary/`.
**Roadmap item:** [AI Glossary](roadmap.md) (Core Content) — flipped `in_progress` → `live` this cycle.
**Shipped:** 2026-07-20 (`af46d07` — "Add AI Glossary and AI & Future of Work FAQ pages").
**Baseline:** Not available (new page).
**Result:** Gate met (19 days since ship, 2 metrics-history rows since 2026-07-20–26). 1st read (2026-07-20–26): 8 views, 3 active users, 16.7% bounce rate, 39s avg. engagement time per active user, 17 events, 0 key events — lowest bounce of any page that week aside from Contact's 0%. 2nd read (2026-08-02–08): **0 views** — `/glossary/` didn't appear in the pages report at all this pull, down from 3 users the week before.
**Decision:** Inconclusive — going from n=3 to n=0 users week-over-week says more about this page's traffic volume (no internal links point to it yet, so it depends entirely on incidental organic discovery) than about whether the content itself is "sticky." Can't evaluate the core hypothesis without traffic reaching the page in the first place; an internal link from a relevant issue or the homepage would be a reasonable next step before this is testable.

## Nova posting time: morning → evening

**Hypothesis:** Moving the Nova auto-publish slot from 8am ET (morning-commute scroll) to ~7:30pm ET (evening leisure scroll, the higher raw-consumption window for short vertical video) increases per-post reach and engagement on Facebook/Instagram/Threads.
**Metric:** Per-post reach and engagement from each platform's own insights (FB Page / IG / Threads) — first entry in this log measured outside GA4, since posts live on-platform; GA4 social-referral sessions as a secondary signal.
**Shipped:** 2026-08-17 — `auto-publish-nova.yml` cron moved `0 12 * * *` → `30 23 * * *` (7:30pm EDT / 6:30pm EST; UTC-fixed so it drifts an hour across DST but stays in the 6–8pm ET band).
**Baseline:** All posts through 2026-08-17 went out at the morning slot (the 2026-08-17 post itself went out late, ~11:23am ET, due to the HeyGen v2-endpoint outage — treat it as neither slot). Small n: only a handful of morning-slot posts exist, so early reads are directional only, same caveat as everything else in this log at current audience size.
**Status:** Reading — compare a few weeks of evening-slot posts against the morning-slot posts during the weekly review before calling it.
