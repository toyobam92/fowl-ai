# Bounce rate improvement tickets

Source: GA4 snapshot, fowl-ai.com, 2026-07-15–16 (33 users, 2-day sample). Ticket order = priority.

---

### TICKET-1: Add CTA and internal links to homepage
**Priority:** High
**Page:** `/` (homepage)
**Problem:** 100% bounce rate. Homepage is the top entry point from Google organic (21 views) but gives visitors no next step.
**Fix:** Add an above-the-fold CTA (subscribe / read latest issue) and internal links to the Jobs Board and Platforms Directory.
**Acceptance criteria:** CTA visible without scrolling on mobile and desktop; at least one link each to Jobs Board and Platforms Directory above the fold.

---

### TICKET-2: Add filters/search/save to AI Jobs Board
**Priority:** High
**Page:** `/jobs`
**Problem:** 100% bounce rate. No interactive elements, so GA4 has nothing to count as an engagement event beyond the initial pageview.
**Fix:** Add filters (role, remote/hybrid, category), a search box, or save/apply buttons.
**Acceptance criteria:** At least one interactive control fires a GA4 event on use (filter applied, search submitted, or save/apply clicked).

---

### TICKET-3: Add filters/search or outbound-click tracking to AI Platforms Directory
**Priority:** High
**Page:** `/platforms`
**Problem:** 100% bounce rate, same root cause as the Jobs Board — no in-page interactivity to register engagement.
**Fix:** Add filters/search, or instrument outbound clicks on platform links as GA4 events.
**Acceptance criteria:** Clicking an outbound platform link, or using search/filter, fires a tracked event.

---

### TICKET-4: Add "start here" entry point to All Issues archive
**Priority:** Medium
**Page:** `/issues`
**Problem:** 100% bounce rate. Flat list of issues gives cold visitors no obvious starting point.
**Fix:** Surface a "start here" or most-popular issue card above the archive list; add a recommended-next-issue link at the bottom of each issue page.
**Acceptance criteria:** Archive page shows one pinned/featured issue; each issue page links to at least one other issue.

---

### TICKET-5: Add internal link from About TYB page
**Priority:** Low
**Page:** `/about`
**Problem:** 100% bounce rate (low volume — 1 view in this sample, but a dead end regardless).
**Fix:** Add a link back to the newsletter subscribe flow or the Jobs Board.
**Acceptance criteria:** Page contains at least one internal link out.

---

### TICKET-6: Instrument engagement events sitewide
**Priority:** High (blocks accurate measurement of tickets 1–5)
**Page:** sitewide
**Problem:** Sitewide avg. engagement time is 17s, and Contact is the only page with 0% bounce — likely because form submission is the only action currently firing a GA4 engagement/conversion event. Without broader instrumentation, bounce rate partly reflects missing tracking, not just visitor behavior.
**Fix:** Add GA4 events for scroll depth (e.g. 75% scroll), outbound link clicks, and subscribe-button clicks across templates.
**Acceptance criteria:** Scroll, outbound-click, and subscribe events appear in GA4 realtime report on each major page template.
