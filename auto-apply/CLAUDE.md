# CLAUDE.md — Auto-Apply System

Job application pipeline for AI/fintech/banking remote roles. Mode: auto-prep everything,
human approves before submit. Fabrication guardrails are non-negotiable.

## Architecture
Discovery -> Scoring (BUILT) -> Asset Generation (BUILT) -> Application Execution -> Tracking

## What exists (Module 1 — resume rewrite pipeline)
- `config.yaml` — filters, thresholds, guardrail settings, company watchlist
- `db/schema.sql` + `python -m db.init` — SQLite: jobs, applications, answers_bank, events
- `assets/profile.md` — canonical facts file, FILLED (2026-08-12, from the 2026 resume PDF).
  It is the only source the rewriter may draw from. Salary/EEO/notice answers are
  deliberately left as [FILL LOCALLY] placeholders — this repo is public; keep those in an
  untracked *.local.md file or the answers_bank table (both gitignored).
- `assets/resumes/credit-risk.md` — base variant, FILLED with real locked spans
  (name, employers, titles, dates, degrees). Add ds-ml.md and ai-tpm.md variants later.
  Note: Visa title is "Data Scientist" per the resume — do not inflate to "Senior".
- `src/llm.py` — shared Claude client, config load, fence-tolerant JSON parsing
- `src/rewrite.py` — 3-stage pipeline: constrained rewrite -> locked-span verification ->
  adversarial audit (separate model call). Any flag = BLOCKED, nothing rendered. Fail closed.
- `src/score.py` — JD scoring vs profile. JSON: {score 1-100, track, 3 match_reasons,
  2 gaps, resume_variant, decision}. Decision from config score_thresholds
  (auto_prep / digest / archive). Unparseable or invalid output = BLOCKED, no score.
  `--save --company --title --url` upserts into the jobs table with status=scored.
- `src/cover_letter.py` — 3-paragraph letter (<=250 words). Candidate claims only from
  profile.md, company claims only from the JD, then adversarial audit
  (cover_letter_audit_prompt.md). Any flag = BLOCKED, nothing written. Fail closed.
- `src/render.py` — markdown -> PDF (WeasyPrint)
- `assets/prompts/` — rewrite, audit, score, cover letter, and cover letter audit prompts

## Run
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...
    python -m db.init
    python -m src.score --jd fixtures/prosper.txt --out applications/prosper/
    python -m src.rewrite --jd fixtures/prosper.txt --variant credit-risk --out applications/prosper/
    python -m src.cover_letter --jd fixtures/prosper.txt --company Prosper --out applications/prosper/
    python -m src.render --md applications/prosper/resume.md

## Guardrail invariants — do not weaken these when extending
1. LLM never generates locked fields; templates own them.
2. Audit failure or unparseable audit output BLOCKS the pipeline (fail closed).
3. Numbers are immutable across rewrite.
4. Keyword insertion capped by config `max_jd_keywords_inserted`.
5. Every submission requires human approval until an adapter has 10 clean approvals
   (then full-auto only for score >= `full_auto_min`).

## Build next (in order)
1. Calibrate scoring: save the 5 priority JDs as fixtures, confirm they score >= 80 and
   5 reject-worthy JDs score < 60; tune score_prompt.md until they do (BUILD_PLAN Phase 3)
2. `scrapers/` — Greenhouse/Lever/Ashby public APIs + watchlist pollers; write to jobs table
3. `apply/greenhouse.py` — Playwright adapter: fill, upload, screenshot, STOP before submit
4. Approve flow (email/Telegram) + `apply/lever.py`, `apply/ashby.py`
5. Tracking: Gmail label matcher, 7-day follow-up events, Sunday digest

Full phase checklist: see BUILD_PLAN.md
