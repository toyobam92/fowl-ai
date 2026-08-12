# CLAUDE.md — Auto-Apply System

Job application pipeline for AI/fintech/banking remote roles. Mode: auto-prep everything,
human approves before submit. Fabrication guardrails are non-negotiable.

## Architecture
Discovery -> Scoring -> Asset Generation (BUILT) -> Application Execution -> Tracking

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
- `src/rewrite.py` — 3-stage pipeline: constrained rewrite -> locked-span verification ->
  adversarial audit (separate model call). Any flag = BLOCKED, nothing rendered. Fail closed.
- `src/render.py` — markdown -> PDF (WeasyPrint)
- `assets/prompts/` — the rewrite and audit prompts

## Run
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...
    python -m db.init
    python -m src.rewrite --jd fixtures/prosper.txt --variant credit-risk --out applications/prosper/
    python -m src.render --md applications/prosper/resume.md

## Guardrail invariants — do not weaken these when extending
1. LLM never generates locked fields; templates own them.
2. Audit failure or unparseable audit output BLOCKS the pipeline (fail closed).
3. Numbers are immutable across rewrite.
4. Keyword insertion capped by config `max_jd_keywords_inserted`.
5. Every submission requires human approval until an adapter has 10 clean approvals
   (then full-auto only for score >= `full_auto_min`).

## Build next (in order)
1. `src/score.py` — JD scoring vs profile (JSON: score, track, reasons, gaps, variant)
2. `src/cover_letter.py` — 3-paragraph letter, same audit guardrail
3. `scrapers/` — Greenhouse/Lever/Ashby public APIs + watchlist pollers; write to jobs table
4. `apply/greenhouse.py` — Playwright adapter: fill, upload, screenshot, STOP before submit
5. Approve flow (email/Telegram) + `apply/lever.py`, `apply/ashby.py`
6. Tracking: Gmail label matcher, 7-day follow-up events, Sunday digest

Full phase checklist: see BUILD_PLAN.md
