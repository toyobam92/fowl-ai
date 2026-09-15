# FOWL AI — experiment log

Every change to fowl-ai.com that could plausibly move a metric gets an entry here: **Hypothesis → Metric → Result → Decision.** Content publishing (new issues, job listing refreshes) doesn't need an entry — this is for structural/UX changes to the site itself.

Status values: `Planned` (not shipped) · `Reading` (shipped, collecting data) · `Decided` (enough data to call it — Keep / Iterate / Revert).

Data source: weekly GA4 exports dropped into `analytics/raw-exports/<date>/`, rolled up in `analytics/metrics-history.csv`. See [weekly-analytics-review skill](../.claude/skills/weekly-analytics-review/SKILL.md) for how this log gets updated.

**Backfill note (2026-09-06):** three GA4 exports (windows ending 2026-08-09, 2026-08-21 and 2026-08-23) had been archived under `analytics/raw-exports/` in earlier cycles but were never appended to `metrics-history.csv`, so every "Result" section below was reading three weeks stale. They are now appended and all reads updated. A `glossary_views` / `glossary_bounce_rate` column pair was added to the schema at the same time (earlier rows backfilled where the value is documented, blank otherwise). Note that several windows overlap by 5–6 days — the archived pulls used "7 days ending today" rather than aligned weeks — so consecutive rows are **not** always independent samples; the overlap is flagged inline wherever a delta is quoted.

**Known gap:** GA4 tracking on fowl-ai.com only started producing exports as of 2026-07-16. The three experiments below shipped in the days just before/at that first export, so there is no true pre-change baseline for them — they're being read forward from ship date instead of compared against a "before" snapshot. Everything shipped from here on will have a real baseline (the most recent weekly snapshot before it ships).

---

## Quick view

| Experiment | Primary metric | Shipped | Status |
|---|---|---|---|
| [Homepage declutter (new hero)](#homepage-declutter-new-hero) | Homepage bounce rate | 2026-07-15 | Decided — Superseded |
| [Embedded signup form + social proof](#embedded-signup-form--social-proof) | Newsletter conversion rate | 2026-07-14 | Reading |
| [Issues → Briefings rename + sharper copy](#issues--briefings-rename--sharper-copy) | Avg. engagement time / session | 2026-07-14 | Reading |
| [Jobs Board filters](#jobs-board-filters) | Engagement rate (Jobs Board) | — | Planned |
| [Platforms Directory filters](#platforms-directory-filters) | Engagement rate (Platforms Directory) | — | Planned |
| ["Start here" + related-issue links](#start-here--related-issue-links) | Pages / session | — | Planned |
| [Sitewide event instrumentation](#sitewide-event-instrumentation) | % sessions with a tracked engagement event | 2026-07-16 | Reading |
| [AI Glossary launch](#ai-glossary-launch) | Bounce rate / engagement on `/glossary/` | 2026-07-20 | Reading |
| [FOWL AI Tests launch](#fowl-ai-tests-launch) | Views / engagement on `/tests/` | 2026-07-25 | Reading |
| [Nova posting time: morning → evening](#nova-posting-time-morning--evening) | Per-post reach (platform insights) | 2026-08-17 | Reading |
| [Nova look: rainbow background vs interior](#nova-look-rainbow-background-vs-interior) | Per-post reach / views (IG Reels) | 2026-08-22 | Reading |
| [Homepage redesign: "Signal" direction](#homepage-redesign-signal-direction) | Homepage bounce rate + sitewide engagement | 2026-08-28 | Reading (1 of 2 reads) |
| [Vibe Code Saturdays page](#vibe-code-saturdays-page) | Views + views-per-user on `/vibe-code-saturdays/` | 2026-08-26 | Reading (1 read) |

---

## Homepage declutter (new hero)

**Hypothesis:** Removing decorative animation and tightening the hero and section rhythm reduces friction on the page that receives the most Google-organic traffic, lowering bounce rate.
**Metric:** Homepage bounce rate (GA4, page = `FOWL AI | AI Jobs, Platforms & Opportunities`).
**Shipped:** 2026-07-15 (`c1e14c2` — "Declutter homepage: remove gimmicky animations, tighten hero, fix section rhythm")
**Baseline:** Not available (shipped at/before first GA export). First read: 100% bounce, 21 views, 14 users (2026-07-15–16) — 1 day of post-ship data, too small to call.
**Result:** Seven reads: 100% bounce (2026-07-15–16, n=21 views) → 64.3% (2026-07-10–16, n=99, overlapping) → 57.6% (2026-07-20–26, n=85) → 72.2% (2026-08-02–08, n=84) → 75.4% (2026-08-03–09, n=72, overlapping) → 68.1% (2026-08-15–21, n=82) → **64.3% (2026-08-17–23, n=70 views/52 users, overlapping)**. Across seven windows the number has ranged 57.6%–75.4% with no shipped change to this page after 2026-07-15, and it moved in both directions repeatedly. The series is a band, not a trend.
**Decision:** **Superseded** — closing this out. The decluttered hero this experiment tested no longer exists: the "Signal" redesign (2026-08-28, `3f29184`) replaced the homepage wholesale, so no further read can attribute anything to the July hero. On the evidence collected, the honest summary is that homepage bounce oscillated in a ~58–75% band at 70–99 views/week and this experiment never had the sample size to resolve a real effect from that noise. Superseded by [Homepage redesign: "Signal" direction](#homepage-redesign-signal-direction), which inherits the metric with a proper baseline. Method note for future entries: this is the second experiment to die of insufficient sample rather than a bad hypothesis — at ~100 users/week, page-level bounce needs multiple weeks pooled, not week-over-week comparison.

## Embedded signup form + social proof

**Hypothesis:** Embedding the signup form directly in the hero (instead of linking out) plus a social-proof line increases newsletter conversion rate.
**Metric:** Newsletter conversion rate — currently not a tracked GA4 event; needs a "subscribe submitted" conversion event (see [Sitewide event instrumentation](#sitewide-event-instrumentation)). Proxy until then: homepage → Contact/subscribe engagement.
**Shipped:** 2026-07-14 (`2eb9ef8` — "Embed signup form in hero and add social proof")
**Baseline:** Not available.
**Result:** Still blocked on a real conversion-event metric — `subscribe_click`/`subscribe_submit` aren't marked as GA4 Key Events yet (manual step, see Sitewide event instrumentation below), so this reads on the Contact-page proxy only. Eight reads: 0% bounce/13 views (2026-07-15–16) → 0%/36 views (2026-07-10–16) → 0%/12 views, 12 of 12 sitewide key events (2026-07-20–26) → 3.0%/35 views, 35 of 35 (2026-08-02–08) → 8.7%/24 views, 23 of 23 (2026-08-03–09) → 13.0%/24 views, 26 of 26 (2026-08-15–21) → 5.7%/36 views/33 users, 38 of 38 (2026-08-17–23) → **7.7%/13 views/13 users, 13 of 13 sitewide key events (2026-09-07–13)**.

**The latest read is the first genuinely alarming one.** Contact views fell 36 → 13 and key events 38 → 13 *while sitewide active users went 105 → 259*. Expressed as a rate that is a fall from 36.2 key events per 100 users to 5.0 — a 7× drop in conversion efficiency, on the largest sample the site has ever produced. Contact is still the lowest-bounce page (7.7%) and still the sole source of every tracked key event, so the page itself isn't broken; visitors are no longer reaching it. The two redesigns (2026-08-28 `3f29184`, 2026-09-09 `8e02395`) are the only structural changes in the intervening period, and both touched the homepage's navigation and CTA layout.
**Decision:** Inconclusive **on the stated hypothesis** (unchanged — the proxy still measures the Contact form, not the hero embed), but **escalate the conversion drop as its own finding.** For 5 consecutive cycles this entry has said the same thing: one manual GA4 Admin step (mark `subscribe_click` and `subscribe_submit` as Key Events) converts an unmeasurable experiment into a measurable one. That step now also blocks diagnosing a 7× conversion regression — with subscribe events untracked, there is no way to tell whether readers stopped converting or simply started converting through a path GA4 can't see. This is no longer a bookkeeping nag; it is the reason the biggest number in this cycle can't be explained.

## Issues → Briefings rename + sharper copy

**Hypothesis:** Sharper, less generic homepage copy and reframing "Issues" as "Briefings" makes the value prop clearer, increasing average engagement time per session.
**Metric:** Average engagement time per active user (sitewide + homepage).
**Shipped:** 2026-07-14 (`efeb2da` — "Sharpen homepage landing-page copy and rename Issues to Briefings")
**Baseline:** Not available. First read: 17s avg. engagement/user sitewide (2026-07-15–16).
**Result:** Eight reads: 17s (2026-07-15–16) → 9s (2026-07-10–16) → 19s (2026-07-20–26) → 11s (2026-08-02–08) → 14s (2026-08-03–09) → 13s (2026-08-15–21) → 15s (2026-08-17–23) → **15s (2026-09-07–13)**. Flat at 15s across a 2.5× increase in traffic — the most stable reading the metric has produced. But the companion number moved hard: sitewide **engagement rate fell 50.0% → 29.9%** (first period this was captured on both sides; added as an `engagement_rate` column to `metrics-history.csv` this cycle).
**Decision:** Inconclusive on the hypothesis, and **this cycle settles the methodological point:** avg. engagement time per active user held at exactly 15s while engagement *rate* dropped 20 points, which is what happens when a large influx of non-engaging visitors dilutes a per-user average that only counts engaged time. The metric is not just too aggregated to isolate a copy change — it is actively misleading about direction. **Formally retiring sitewide avg. engagement time as this experiment's primary metric.** Replacement going forward: sitewide engagement rate (now tracked) plus a homepage-scoped engagement read. Recorded here rather than acted on unilaterally — the entry stays open until Toyo confirms the swap.

## Jobs Board filters

**Hypothesis:** Adding filters/search/save-buttons to the Jobs Board gives visitors something to interact with beyond the initial pageview, raising engagement rate and lowering bounce on `/jobs`.
**Metric:** Engagement rate on the AI Jobs Board page.
**Ticket:** TICKET-2 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** 100% bounce, 6 views, 4 users. **Latest (2026-09-07–13):** 41.7% bounce, 14 views, 10 users. Full series: 100% → 52.9% → 45.5% → 68.4% → 72.2% → 44.4% → 20.0% → 41.7%, on 6–24 views per window. Last cycle's 20.0% duly reverted, as flagged. Note the jobs board content was refreshed 2026-09-09 (`442ca21`, verified September opportunities) and restyled by the same-day redesign — neither is the TICKET-2 interactivity fix, and neither moved views off the 12–14 plateau this page has sat on for four windows. **Views are the buried signal here:** sitewide traffic 2.5×'d and `/jobs/` gained 2 views. Whatever is bringing people to the homepage is not routing them here.

## Platforms Directory filters

**Hypothesis:** Same mechanism as the Jobs Board — filters/search or tracked outbound clicks on platform links give GA4 something to count as engagement, lowering bounce on `/platforms`.
**Metric:** Engagement rate on the AI Platforms Directory page.
**Ticket:** TICKET-3 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** 100% bounce, 5 views, 2 users. **Latest (2026-09-07–13):** **27.3% bounce, 14 views, 10 users** — the lowest this page has ever read. Full series: 100% → 74.1% → 41.2% → 64.3% → 66.7% → 52.9% → 58.8% → 27.3%. The only candidate explanation is the 2026-09-09 redesign, which restyled `platforms/index.html`; TICKET-3 has still not shipped. At 14 views one engaged visitor is worth ~7 points, so this is not evidence of anything on its own — but it is the second consecutive cycle where a ticket page posted a record-low bounce on a shrinking view count, which is the signature of small-sample noise, not improvement. Same buried signal as the Jobs Board: views fell 20 → 14 while the site got 2.5× the traffic. TICKET-3 unchanged as the unblocker; the outbound-click half remains the cheaper and more informative piece, since referral clicks are what this page exists to produce.

## "Start here" + related-issue links

**Hypothesis:** A pinned "start here" issue on the archive, plus a recommended-next-issue link at the bottom of each post, increases pages viewed per session (this is FOWL AI's version of "related articles").
**Metric:** Pages / session (sitewide), and views on `/issues` specifically.
**Ticket:** TICKET-4 in `TICKETS.md`.
**Status:** Planned — not yet shipped.
**Baseline (as of 2026-07-15–16):** All Issues page — 100% bounce, 8 views, 6 users. **Latest (2026-09-07–13):** 8 views, 6 users; bounce not captured (the page fell out of GA4's top-7 page-*title* card, which is the only place bounce is exposed in this pull). Flat at 8 views for a third straight window.

**The case for the second half of TICKET-4 is now much stronger.** This window, individual issue pages pulled **17 views across 7 URLs** (`/issues/2026-09-07/` 6, `/issues/2026-07-13/` 3, `/issues/2026-09-14/` 3, plus 1 each on four older issues) against the archive index's 8. Readers reach issues directly, more than twice as often as they reach the archive — so a recommended-next-issue link at the bottom of each issue page sits where the traffic is, while the pinned "start here" card on `/issues/` sits where it isn't. Recommend splitting TICKET-4 and shipping the issue-footer link first. Also worth noting: `/issues/2026-09-14/` logged 3 views *before its publish date* — a preview/crawler path, not readers.

## Sitewide event instrumentation

**Hypothesis:** Most of the site's bounce rate currently reflects missing GA4 event tracking (only Contact has a working conversion event), not actual visitor disengagement. Adding scroll, outbound-click, and subscribe events will both lower measured bounce and — more importantly — make every other experiment on this list actually measurable.
**Metric:** % of sessions with at least one tracked engagement event, sitewide.
**Ticket:** TICKET-6 in `TICKETS.md`.
**Shipped:** 2026-07-16 (`a57b9a2` — "Ship TICKET-6: sitewide GA4 event instrumentation"). Added `analytics-events.js` (scroll_75, outbound_click, subscribe_click, subscribe_submit) to all 24 site pages. Scope expanded beyond the original ticket: 14 pages (guide, resume-template, interview-guide, both launchlab pages, and 9 issue archive pages) had no GA4 tracking at all and got the base `gtag` snippet added too, not just events. Still needs a manual step: mark `subscribe_click` and `subscribe_submit` as GA4 Key Events in Admin.

**Follow-up (2026-07-18):** Found that `subscribe_click` alone overstates the funnel for every page except the homepage. The homepage hero's inline signup form posts to a Google Form directly (already covered by `subscribe_submit`), but every other page's "Subscribe" button links out to `fowlai.eo.page/vmk69` — a native EmailOctopus-hosted landing page we don't control, so a click there is only ever intent, never confirmed completion. Added `/subscribed/index.html`: a thank-you page that fires `subscribe_submit` (`method: emailoctopus_redirect`) on load. **Manual step still needed from Toyo:** in the EmailOctopus dashboard, set that form's "redirect on success" URL to `https://www.fowl-ai.com/subscribed/`. Until that's set, `subscribe_submit` will only ever fire from the homepage form — EmailOctopus signups sitewide still only show up as `subscribe_click` (intent, not completion).
**Status:** Reading.
**Baseline (as of 2026-07-15–16):** 17s avg. engagement/user sitewide; Contact is the only page with a non-100% bounce rate. **Pre-ship read (2026-07-10–16):** 9s avg. engagement/user sitewide; Contact still the only page that never bounces, but every other page's bounce rate also fell that week without any corresponding UX change shipping — the leading explanation was that the metric itself was noisy/incomplete without broader event tracking, which is what this ticket fixes.
**Result:** 6 fully-post-ship reads now collected. Sitewide avg. engagement/user: 19s (2026-07-20–26) → 11s (2026-08-02–08) → 14s (2026-08-03–09) → 13s (2026-08-15–21) → 15s (2026-08-17–23) → **15s (2026-09-07–13)**. Key events: 12 → 35 → 23 → 26 → 38 → **13**, still 100% `generate_lead` from Contact. Event counts continue to track traffic closely (1,961 events on 259 users, the same ~7.6 events/user ratio as every prior read), which is the instrumentation working exactly as intended even as the traffic mix changed underneath it.

**The 6th read is the one that pays for the ticket.** Because events scale cleanly with users, the collapse in *key* events (38 → 13 on 2.5× the traffic; user key-event rate 31.4% → 4.6%) can be isolated as a real behavioural change rather than a tracking gap. That is precisely the discrimination this instrumentation was built to make, and it is the first time the log has been able to make it.

**Still outstanding, now for the 6th consecutive cycle:** `subscribe_click`/`subscribe_submit` are not marked as GA4 Key Events in Admin, and the EmailOctopus "redirect on success" URL is not set to `https://www.fowl-ai.com/subscribed/`. Both are manual steps only Toyo can do.
**Decision:** Keep — the instrumentation is not in question and has now demonstrated its value. Two updates to the standing rule:

1. **The noise-floor caveat is sample-size-dependent, not permanent.** At ~100 users/week, page bounce swings of 20–50 points carried no information. At 259 users the *sitewide* rate metrics (engagement rate, key-event rate) moved further than any previously observed noise band and should be treated as real; page-level bounce on 2–14 views still should not. Read rates sitewide, read bounce per-page as directional.
2. **The binding constraint has changed.** It is no longer traffic volume — the site just tripled its traffic and the log still can't explain what happened to conversion, because the only conversion event GA4 counts is the Contact form. The single binding constraint is now the two manual GA4/EmailOctopus steps above.

## AI Glossary launch

**Hypothesis:** Publishing an AI/LLM/MCP terms glossary gives search-intent visitors (people looking up specific terms) a reference page that's inherently sticky, and captures long-tail organic traffic the rest of the site doesn't target.
**Metric:** Bounce rate and average engagement time per active user on `/glossary/`.
**Roadmap item:** [AI Glossary](roadmap.md) (Core Content) — flipped `in_progress` → `live` this cycle.
**Shipped:** 2026-07-20 (`af46d07` — "Add AI Glossary and AI & Future of Work FAQ pages").
**Baseline:** Not available (new page).
**Result:** Five reads. 1st (2026-07-20–26): 8 views, 3 users, 16.7% bounce, 39s avg. engagement. 2nd (2026-08-02–08): **0 views** — absent from the pages report entirely. 3rd (2026-08-15–21): 5 views, 3 users, 50.0% bounce, **95s avg. engagement**. 4th (2026-08-17–23): 6 views, 3 users, 25.0% bounce, **95s avg. engagement** (overlaps read 3 by 5 days). 5th (2026-09-07–13): **2 views, 2 users, 2s avg. engagement**, bounce not captured.

**The 5th read breaks the finding.** Engagement time went 95s → 2s in the same window that `8e02395` (2026-09-09, "unified visual identity") rewrote `glossary/index.html` — 74 lines changed. At n=2 this is not evidence of a regression, and the honest reading is that the page has no measurable audience at all. But it is the one page on the site where a redesign-caused regression is *plausible* (the whole hypothesis rested on the page's structure holding readers), so it should be checked deliberately rather than waited out.
**Decision:** **Iterate — unchanged in direction, sharpened in urgency.** The distribution failure is now terminal-looking: after 8 weeks the page still has zero inbound internal links and its view count is trending toward zero (8 → 0 → 5 → 6 → 2) even as sitewide traffic 2.5×'d. The stickiness finding that justified iterating is now itself in doubt. **Two concrete next steps, in order:** (1) open `/glossary/` post-redesign and confirm the content and any in-page interactivity survived the rewrite — cheap, and it determines whether the 2s reading is a measurement artifact or a real break; (2) then add internal links from the homepage and term-heavy issues and re-read. Same applies to `/faq/` (4 views, 21s, shipped in the same original commit) for the same reason.

## FOWL AI Tests launch

**Hypothesis:** A monthly head-to-head AI tool comparison page gives the site a repeatable, inherently shareable format that pulls search-intent traffic ("X vs Y") the newsletter archive doesn't target.
**Metric:** Views and average engagement time on `/tests/`.
**Shipped:** 2026-07-25 (`01ff460` — "Launch FOWL AI Tests: monthly AI tool head-to-heads", followed by `1c96732` editorial pass).
**Baseline:** Not available (new page).
**Logged late:** this page shipped 2026-07-25 and was flagged as a new path in three consecutive raw exports without ever getting an entry here. Backfilled by the 2026-09-06 review.
**Result:** Five reads: 4 views / 2 users / 100% bounce (2026-08-02–08) → not separately captured (2026-08-03–09) → 3 views / 1 user / 29s engagement (2026-08-15–21) → 3 views / 1 user / 29s engagement (2026-08-17–23, overlapping) → **8 views / 7 users on `/tests/`, plus 1 view each on `/tests/best-ai-landing-page-builder/` (12s) and `/tests/best-ai-resume-generator/` (11s) (2026-09-07–13)**. First movement this page has ever shown: user count went 1 → 7, and for the first time the individual test pages registered at all.
**Status:** Reading. The uptick is real but tiny and arrives in a window where sitewide traffic 2.5×'d, so `/tests/` roughly held its share rather than gaining — and the redesign restyled all three test pages, which is the likelier cause than any change in demand.
**Next step:** unchanged and still owed a decision from Toyo. The structural problem is the same as `/glossary/` — no internal links point at it — and the "monthly" premise is still unmet (two tests exist; the last was published in July). Either commit to the cadence and link it from the homepage and issue footers, or retire it. Seven users in the site's biggest-ever traffic week is not a mandate to keep investing.

## Nova posting time: morning → evening

**Hypothesis:** Moving the Nova auto-publish slot from 8am ET (morning-commute scroll) to ~7:30pm ET (evening leisure scroll, the higher raw-consumption window for short vertical video) increases per-post reach and engagement on Facebook/Instagram/Threads.
**Metric:** Per-post reach and engagement from each platform's own insights (FB Page / IG / Threads) — first entry in this log measured outside GA4, since posts live on-platform; GA4 social-referral sessions as a secondary signal.
**Shipped:** 2026-08-17 — `auto-publish-nova.yml` cron moved `0 12 * * *` → `30 23 * * *` (7:30pm EDT / 6:30pm EST; UTC-fixed so it drifts an hour across DST but stays in the 6–8pm ET band).
**Baseline:** All posts through 2026-08-17 went out at the morning slot (the 2026-08-17 post itself went out late, ~11:23am ET, due to the HeyGen v2-endpoint outage — treat it as neither slot). Small n: only a handful of morning-slot posts exist, so early reads are directional only, same caveat as everything else in this log at current audience size.
**Status:** Reading — compare a few weeks of evening-slot posts against the morning-slot posts during the weekly review before calling it.
**Data caveat (added 2026-08-22):** a post can miss its window and go out a day late (the 2026-08-21 episode did — approved ~3h after the cron, posted the following evening). `post_to_meta.py` now stamps a `posted_at` timestamp on every post in `automation/social-state.json`, so read reach against **`posted_at`, not `publish_date`** — otherwise a slipped post silently lands in the wrong bucket.

## Nova look: rainbow background vs interior

**Hypothesis:** Nova videos shot against the vivid multicolor backdrop ("Avatar in a pink sweater") stop the scroll better than the muted interior looks (living room, bookshelf, brick-wall cafe), producing meaningfully higher reach per post.
**Metric:** Views/reach per post from Instagram Reels insights, attributed via `avatar_id` + `posted_at` in `automation/social-state.json`.
**Shipped:** 2026-08-22 — `nova-daily-prep` step 4 pins `picked_look` to `06c45b55396142b4930282c658142c0f` and suspends the round-robin rotation for the next 3 episodes (first pinned post: 2026-08-24).
**Baseline (observed 2026-08-22, IG Reels grid):** the two rainbow-background posts showed **165 and 146 views**; the four newer interior-look posts showed **17, 92, 17, and 24**.
**Confounds — read the result with these in hand:**
- *Age.* Instagram grids are newest-first, so the two rainbow posts sit at positions 5-6 (~2 weeks old) while the low-view posts are days old, and views accumulate. Most Reels views land in the first 48-72h, so a ~10x gap is larger than age alone should explain — but it is **not** an age-controlled comparison. The pinned run fixes this by comparing posts at matched ages.
- *Posting time.* The [morning → evening](#nova-posting-time-morning--evening) experiment shipped 2026-08-17 and is still in its reading window, so the pinned posts change two variables at once. Accepted deliberately: the look effect looks far larger, and waiting would cost weeks at this posting volume.
- *Topic and hook* vary per episode and are not controlled at all.
- *Letterboxing.* This look is landscape (2752x1536) while the rest of the allowlist is portrait (768x1344), so its videos render with bars top and bottom — normally a disadvantage on Reels. If it still wins, the backdrop is beating a real handicap.
**Status:** Reading — the skill's pin auto-expires after 3 posts carrying this `avatar_id` with `publish_date >= 2026-08-24` and pings Telegram to read the result.
**Next step if it wins:** the win is reproducible beyond this one look — generate more motion-capable looks against vivid backdrops (portrait this time, dropping the letterbox handicap) and widen the allowlist, rather than pinning a single outfit forever.
**2026-09-06 review:** no read taken. Both Nova experiments measure off platform insights (IG Reels / FB / Threads), which this run had no browser access to; the pinned run's 3 posts should have completed by now (first pinned post 2026-08-24), so a read is due. Carried to next cycle.
**2026-09-13 review:** still no read, second cycle running. A browser *was* available this cycle, but it was used for the GA4 pull only — reading IG Reels / FB / Threads insights means signing into Toyo's social accounts, which this scheduled run won't do unattended. The pinned run is now ~3 weeks past its 3-post expiry, so both Nova experiments are sitting on collectable data that nothing in this automated loop can collect. **Recommend removing both from the weekly-review loop and reading them in an attended session instead** — carrying them forward each week is producing a to-do, not a measurement. GA4 does offer one weak proxy that was captured this window: social referral traffic (`l.instagram.com` 3 users / 11 sessions, `l.threads.com` 3 users, `ig / social` 5 sessions) — an order of magnitude below the site's organic traffic, and not a substitute for per-post reach.

## Homepage redesign: "Signal" direction

**Hypothesis:** A full visual redesign of the homepage around the "Signal" direction — replacing the July decluttered hero, with the headline treatment then rolled out sitewide — gives the site's main Google-organic entry point a clearer identity and a stronger next click, lowering homepage bounce and lifting sitewide engagement time.
**Metric:** Homepage bounce rate (primary); sitewide avg. engagement time per active user (secondary). Both read against the last pre-ship window.
**Shipped:** 2026-08-28 — `3f29184` ("Redesign homepage with the Signal design direction"), followed by `d1fbba0` / `cd12d41` (font consistency fixes across the homepage and all published issue pages) and `62a7814` ("Roll the Signal headline treatment out site-wide"). `2adc03a` was reverted by `4dbbf6d` mid-sequence.
**Baseline (2026-08-17–23, the last metrics-history row before ship):** homepage 64.3% bounce, 70 views, 52 users; sitewide 15s avg. engagement/user, 105 active users, 692 events, 38 key events.
**Scope note:** this is the largest single change shipped since tracking began, and it is **not** a clean A/B — the headline rollout touched every page, so the sitewide secondary metric is confounded by the same change it is meant to control for. Read the homepage-specific number as primary and treat sitewide movement as context only.
**Second wave (2026-09-09, `8e02395` "Redesign FOWL AI site and newsletter with a unified visual identity"):** logged here rather than as a separate entry, because it is a continuation of the same redesign arc and lands *mid-window* in the first read below. 28 files, 1,570 insertions / 1,488 deletions; new `assets/site.css`, `assets/home.css`, `assets/site.js`, `assets/vibe-code.*`; `index.html` rewritten (427 lines changed) and every content page restyled. It also changed the homepage `<title>` from "FOWL AI | AI Jobs, Platforms & Opportunities" to "FOWL AI | The future of work. Your next advantage.", which is why the homepage splits into two rows in this window's GA4 page-title table.

**Status:** Reading — **1 of 2 reads collected.**
**Read 1 (2026-09-07–13):** homepage **269 views / 211 users, views-weighted bounce 75.9%** (78.1% on the new title over 223 views; 65.1% on the old title over 46 views), vs. a 64.3% baseline on 70 views. Sitewide: 259 active users (vs 105), 15s avg engagement (vs 15s), **engagement rate 29.9% (vs 50.0%)**, **13 key events (vs 38)**, 1,961 events (vs 692).

**What the first read says, carefully:** homepage traffic nearly quadrupled and homepage bounce went to the top of its all-time band. Both directions are consistent with the redesign succeeding at acquisition and failing at the next click — but the window is badly confounded and the entry should not be called on it:
- The second redesign wave landed **mid-window** (Sep 9), so the 223-view "new title" row covers 4–5 days and the 46-view "old title" row covers 2–3 days of a *different* design. Neither is a clean post-ship read of "Signal".
- 15 sessions came from `fowl-ai-design-preview.toyosibamidele.chatgpt.site`, i.e. Toyo's own redesign review traffic, and are not excluded from any total.
- 28 users (11%) have source "(data not available)", the first time this has been material.
- There is a **14-day unmeasured gap** (Aug 24 – Sep 6) between the baseline and this read, so the traffic jump cannot be located in time — it may have arrived before the redesign shipped.
- The `/vibe-code-saturdays/` page (96 views, #2 on the site) was being actively promoted in this window and is the likeliest source of the traffic increase, which would mean the homepage's bounce rise reflects a changed *audience mix*, not a changed page.

**Read 2 is the decisive one** and needs a clean, non-overlapping week with no code shipped. **Recommendation for next cycle: freeze site changes for 7 days** so read 2 measures the redesign rather than the next thing. If that isn't practical, this entry should be called Inconclusive rather than credited or blamed for the numbers above.
**Supersedes:** [Homepage declutter (new hero)](#homepage-declutter-new-hero), whose treatment this replaced.
**Standing caveat, revised:** at 259 users the *sitewide rate* moves (engagement rate −20pts, key-event rate −27pts) are outside anything previously observed as noise and should be treated as real. The homepage bounce move (64% → 76%) is not — it sits inside the page's historical 58–78% band. Read the rates, not the bounce.

## Vibe Code Saturdays page

**Hypothesis:** A dedicated page for Vibe Code Saturdays (the Brand Brain in-person build sessions) gives FOWL AI a concrete, high-intent destination to point social traffic at — something with an actual next action (apply / RSVP) rather than a newsletter signup — and should therefore hold attention far better than the site's informational pages.
**Metric:** Views and **views per active user** on `/vibe-code-saturdays/` (the depth signal; bounce is unreadable at this site's volume). Secondary: applications submitted via the RSVP form (not yet a tracked GA4 event).
**Shipped:** 2026-08-26 (`7a0bde6` — "Add Vibe Code Saturdays page"), then iterated hard across two weeks: `2fb9b50` (2026-08-26, "the room is part of the product" section), `3eb2e65` / `9deaa61` / `b40fde1` / `d80e3ba` / `a5fad92` (2026-08-27, Brand Brain builder copy + room photo as hero), `aa00c49` (2026-08-29, RSVP points at the real application form), `c1ecbf9` + `4266312` (2026-08-29, animated CLI console and phone demos), `2abbda5` (2026-08-31, Brand Brain Instagram link), `8e02395` (2026-09-09, redesign — page rewritten, 630 lines changed, `assets/vibe-code.css`/`.js` extracted), `5fdd9d6` (2026-09-10, application flow), `df42767` (2026-09-11, BrandBrain project showcase).
**Logged late:** the page shipped 2026-08-26 and was iterated on in ten commits before getting an entry here. Backfilled by the 2026-09-13 review, which is the first cycle with GA4 data covering it. It is also **not on `roadmap.md`** — flagged to Toyo below.
**Baseline:** Not available (new page).
**Result — read 1 (2026-09-07–13):** **96 views, 39 users, 2.46 views per active user, 25s avg. engagement, 381 events**, views-weighted bounce 44.5% (48.3% on 84 views under "Bring an Idea. Leave with a Build."; 18.2% on 12 views under "Vibe Code Saturdays by Brand Brain"). This makes it the **#2 page on the site** at 21.1% of all views, behind only the homepage.

**The finding is depth, not volume.** 2.46 views per user is the highest on the site by a wide margin — the homepage manages 1.27, and no other page with meaningful traffic clears 1.6. People who land here look at more than one thing. That is exactly what the hypothesis predicted and it is the first page on fowl-ai.com to produce it.
**Status:** Reading — 1 read. Two caveats before treating this as established: the page was being actively promoted during this window (social referrals appeared for the first time: `l.instagram.com` 3 users / 11 sessions, `l.threads.com` 3 users, `ig / social` 5 sessions), so the traffic is campaign-driven rather than steady-state; and ten commits landed on it in the fortnight before the read, so this measures the page's final form and nothing about which iteration mattered.
**Open question for Toyo — this page is doing better than anything on the roadmap.** `/vibe-code-saturdays/` is not listed in `roadmap.md`, so the weekly review has no status to flip and no place to track it. Meanwhile every Phase 1 `planned` roadmap item (Newsletter Archive, Books & Resources, Company Tracker, Career/Salary/Interview Hubs, "This Week in 5 Minutes") is still unstarted. Worth deciding explicitly whether Vibe Code Saturdays belongs on the roadmap as a tracked Phase 1 item — the review deliberately did not add it unilaterally.
**Next step:** the RSVP/application submission is not a tracked GA4 event, so the metric that actually matters here — applications — is invisible, exactly as with the subscribe funnel. Adding an event on the application form is a small piece of the same work as the outstanding TICKET-6 manual steps and should be bundled with them.
