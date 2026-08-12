# Auto-Apply System — Build Plan

**Architecture:** Discovery → Scoring → Asset Generation → Application Execution → Tracking
**Mode:** Auto-prep + one-tap approve (graduate to full-auto per-ATS once proven)
**Stack:** Python + Playwright + SQLite + Claude API + cron (mirrors your Merchant Copilot Phase 1 pattern — same SQLite-first approach)

---

## Phase 0 — This Week (do NOT wait for the system)

- [ ] Manually apply to Prosper — Sr. Manager, Credit Risk Analytics
- [ ] Manually apply to LexisNexis Risk — Senior Statistical Modeler
- [ ] Manually apply to Credit Acceptance — Sr. Analyst, Predictive Analytics & ML
- [ ] Manually apply to EXL — Senior Credit Risk Analyst
- [ ] Manually apply to Attain Finance — Senior Risk Analyst
- [ ] Save each job description as a .txt file (these become your first test fixtures)
- [ ] Note which ATS each one used (Greenhouse / Lever / Workday / other) — this tells you which adapters to build first

## Phase 1 — Foundation & Decisions

- [ ] Create repo `auto-apply` with folders: `/scrapers`, `/scoring`, `/assets`, `/apply`, `/db`, `/config`
- [ ] Create `config.yaml` with your search filters: fintech/credit risk analytics, remote health tech analytics, remote AI TPM, seniority = Senior/Staff/Manager, remote-only
- [ ] Create SQLite schema: `jobs` (url, title, company, ats_type, jd_text, score, status), `applications` (job_id, resume_version, cover_letter_path, submitted_at, method), `events` (follow-ups, responses)
- [ ] Write a master profile doc (`profile.md`): full work history, quantified achievements at Visa, skills, certs, target comp, work authorization answers, EEO answers, common screening-question answers
- [ ] Store 2-3 base resume variants: credit-risk-focused, ML/DS-focused, AI/TPM-focused
- [ ] Decide notification channel for approve/reject pings (email vs. Telegram bot vs. SMS)

## Phase 2 — Discovery Pipeline

- [ ] Build scraper for LinkedIn job alerts (via email parsing — scraping LinkedIn directly risks account bans; parse the alert emails instead)
- [x] Build scrapers for direct sources: Greenhouse boards API (`boards-api.greenhouse.io`), Lever postings API, Ashby API — these are public JSON, no scraping fragility
- [ ] Add company watchlist: fintech/credit risk companies whose careers pages you poll directly (Prosper, LexisNexis Risk, SoFi, Upstart, Affirm, etc.)
- [ ] Add job boards with RSS/API: Otta, WorkAtAStartup, RemoteOK, Wellfound
- [x] Write dedupe logic (same role posted on multiple boards → one record, keyed on company + normalized title)
- [ ] Schedule discovery run via cron: 2x daily (morning + evening)
- [x] Write each new job to SQLite with status = `discovered`

## Phase 3 — Scoring Engine

- [x] Write scoring prompt for Claude API: input = JD text + your profile.md, output = JSON {score 1-100, track (credit-risk / DS-ML / AI-TPM / health-tech), top 3 match reasons, top 2 gaps, recommended resume variant}
- [x] Set thresholds: ≥80 = auto-prep application, 60-79 = weekly digest for manual review, <60 = archive
- [ ] Test scoring against the 5 saved priority JDs — they should all score ≥80; tune the prompt until they do
- [ ] Test against 5 roles you'd reject — they should score <60
- [ ] Update job status to `scored` with score + track stored

## Phase 4 — Asset Generation

- [ ] Write resume-tailoring prompt: input = base resume variant + JD, output = reordered bullets, keyword-aligned summary, JD-matched skills section (edits only — never fabricates)
- [x] Write cover letter prompt: 3 short paragraphs, references 1-2 specific things about the company, maps your top 2 achievements to their top 2 requirements
- [ ] Add a hallucination guard: diff generated resume against profile.md — flag any claim not present in the source before it can be used
- [ ] Render resume to PDF (markdown → PDF via weasyprint or a docx template)
- [ ] Save assets to `/assets/{company}-{role}/` and log paths in SQLite
- [ ] Update job status to `assets_ready`

## Phase 5 — Application Execution

- [ ] Build Playwright adapter #1: **Greenhouse** (simplest — single page, stable selectors)
- [ ] Build adapter #2: **Lever**
- [ ] Build adapter #3: **Ashby**
- [ ] Each adapter: navigate → fill fields from profile.md → upload resume PDF → paste cover letter → answer screening questions from your stored answers bank → screenshot the completed form → STOP before submit
- [ ] Build the approve flow: send you the screenshot + score + role summary via your chosen channel; "APPROVE" reply triggers submit, "SKIP" archives
- [ ] Handle unknown screening questions: if a question isn't in the answers bank, pause, send it to you, store your answer for future reuse
- [ ] Workday/Taleo roles: do NOT automate — system generates the assets + a checklist link and queues them for a manual 10-minute session
- [ ] Log every submission to `applications` table with screenshot archived
- [ ] After 10 clean approvals on a given adapter with zero corrections, flip that adapter to full-auto for scores ≥90

## Phase 6 — Tracking & Follow-up

- [ ] Gmail integration: label incoming recruiter/ATS emails, match to `applications` records, update status (viewed / rejected / interview)
- [ ] Auto-generate follow-up reminder 7 days post-submit for roles scored ≥85
- [ ] Weekly digest (Sunday): applications sent, response rate, score distribution, adapter error rate
- [ ] Monthly: review which score band actually converts to interviews; recalibrate thresholds

## Phase 7 — Hardening

- [ ] Rate-limit: max 5 auto-submissions/day (protects quality and avoids ATS spam flags)
- [ ] Retry + error screenshots on adapter failures; failed jobs fall back to the manual queue, never silently dropped
- [ ] Kill switch: single config flag pauses all submission
- [ ] Backup SQLite db weekly

---

**Build order if time-constrained:** Phase 0 → 1 → 3 → 4 first. Scoring + asset generation alone saves you 80% of the time per application even if you paste into forms manually for the first two weeks. Adapters come after.
