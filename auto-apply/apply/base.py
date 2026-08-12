"""Shared Playwright machinery for ATS adapters.

Every adapter module provides:
  ATS               — name used for applications.method and approve-flow routing
  QUESTION_SCOPES   — CSS candidates for the screening-question container
  SUBMIT_SELECTORS  — candidates for the submit control
  open_application(page)        — get from the landing page to the visible form
  fill_identity(page) -> dict   — deterministic fields from config applicant:
  upload_resume(page, path) -> bool
  paste_cover_letter(page, text) -> bool
and calls run_adapter(module, args) from its CLI.

Common safety contract (enforced here, identically for all ATSes):
STOP before submit unless --submit; EEO/demographic controls never auto-filled;
--submit refuses on missing resume or unanswered required questions;
kill_switch blocks everything; unknown questions -> events + exit 2.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from apply.answers import CONFIG, ROOT, connect, lookup, record_unknown, seed

TIMEOUT_MS = 15000
# Matches the control itself or any ancestor that belongs to an EEO/demographic block.
EEO_GUARD_CSS = ("#eeoc_fields, [id*=demographic i], [class*=demographic i], "
                 "[name^=eeo], [id^=eeo]")


def first_visible(page, selectors: list[str]):
    for sel in selectors:
        loc = page.locator(sel).first
        try:
            if loc.count() and loc.is_visible():
                return loc
        except Exception:
            continue
    return None


def by_label(page, pattern: str):
    try:
        loc = page.get_by_label(re.compile(pattern, re.IGNORECASE)).first
        if loc.count() and loc.is_visible():
            return loc
    except Exception:
        pass
    return None


def fill_fields(page, spec: list[tuple[str, list[str], str, str]]) -> dict:
    """spec rows: (name, css candidates, label regex fallback, value)."""
    filled = {}
    for name, ids, label_pat, value in spec:
        if not value:
            continue
        loc = first_visible(page, ids) or (by_label(page, label_pat) if label_pat else None)
        if loc:
            try:
                loc.fill(value)
                filled[name] = value
            except Exception:
                pass
    return filled


def upload_file(page, selectors: list[str], path: str) -> bool:
    for sel in selectors:
        loc = page.locator(sel).first
        if loc.count():
            try:
                loc.set_input_files(path)
                return True
            except Exception:
                continue
    return False


def control_label(control) -> str:
    """Best-effort visible question text for a form control."""
    text = control.evaluate("""el => {
        if (el.labels && el.labels.length) return el.labels[0].textContent;
        if (el.getAttribute('aria-label')) return el.getAttribute('aria-label');
        const id = el.getAttribute('id');
        if (id) {
            const lab = document.querySelector(`label[for="${CSS.escape(id)}"]`);
            if (lab) return lab.textContent;
        }
        const wrap = el.closest('div.field, div[class*=question], fieldset, li, div');
        if (wrap) {
            const lab = wrap.querySelector('label, legend, .label');
            if (lab) return lab.textContent;
        }
        return '';
    }""") or ""
    return re.sub(r"\s+", " ", text).strip()


def group_question(control) -> str:
    """Question text for a radio/checkbox group: fieldset legend over option label."""
    text = control.evaluate("""el => {
        const fs = el.closest('fieldset');
        if (fs) { const lg = fs.querySelector('legend'); if (lg) return lg.textContent; }
        const wrap = el.closest('div.field, div[class*=question]');
        if (wrap) { const lab = wrap.querySelector('.label, label'); if (lab) return lab.textContent; }
        return '';
    }""") or ""
    return re.sub(r"\s+", " ", text).strip()


def answer_control(control, tag: str, answer: str) -> bool:
    if tag == "select":
        try:
            control.select_option(label=answer)
            return True
        except Exception:
            pass
        try:  # partial text match over the option list
            options = control.locator("option").all_text_contents()
            for opt in options:
                if opt.strip() and (opt.strip().lower() in answer.lower()
                                    or answer.lower() in opt.strip().lower()):
                    control.select_option(label=opt)
                    return True
        except Exception:
            pass
        return False
    try:
        control.fill(answer)
        return True
    except Exception:
        return False


def is_required(control) -> bool:
    try:
        if control.get_attribute("required") is not None:
            return True
        if (control.get_attribute("aria-required") or "").lower() == "true":
            return True
    except Exception:
        pass
    return "*" in control_label(control)


def fill_screening_questions(page, conn, job_id: int | None,
                             scopes: list[str]) -> tuple[dict, list]:
    """Answer custom questions from the answers bank; report unknowns."""
    answered, unknown = {}, []
    scope = page.locator("form")
    for css in scopes:
        if page.locator(css).count():
            scope = page.locator(css)
            break
    controls = scope.locator("input, select, textarea")
    seen_questions = set()
    for i in range(controls.count()):
        control = controls.nth(i)
        try:
            if not control.is_visible():
                continue
            tag = control.evaluate("el => el.tagName.toLowerCase()")
            input_type = (control.get_attribute("type") or "text").lower()
            if input_type in ("file", "hidden", "submit", "button"):
                continue
            # Never auto-fill the EEO/demographic block.
            if control.evaluate(f"el => !!el.closest('{EEO_GUARD_CSS}')"):
                continue
            if input_type in ("radio", "checkbox"):
                question = group_question(control)
                if not question:
                    continue
                answer = lookup(conn, question)
                if answer is None:
                    if question not in seen_questions:
                        seen_questions.add(question)
                        unknown.append({"question": question, "required": is_required(control)})
                        record_unknown(conn, job_id, question)
                    continue
                option = control_label(control)
                if option and (option.lower() == answer.lower()
                               or option.lower() in answer.lower()
                               or answer.lower() in option.lower()):
                    control.check()
                    answered[question] = answer
                    seen_questions.add(question)
                continue
            if tag in ("input", "textarea") and control.input_value():
                continue  # already filled (identity fields, pasted cover letter)
            question = control_label(control)
            if not question or question in seen_questions:
                continue
            seen_questions.add(question)
            answer = lookup(conn, question)
            if answer is None:
                unknown.append({"question": question, "required": is_required(control)})
                record_unknown(conn, job_id, question)
                continue
            if answer_control(control, tag, answer):
                answered[question] = answer
            else:
                unknown.append({"question": question, "required": is_required(control)})
                record_unknown(conn, job_id, question)
        except Exception:
            continue
    return answered, unknown


def log_application(conn, job_id: int | None, out: Path, resume: str,
                    cover_letter: str | None, method: str, status: str,
                    submitted: bool) -> None:
    if job_id is None:
        return
    conn.execute(
        "INSERT INTO applications (job_id, resume_path, cover_letter_path, method, "
        "submitted_at) VALUES (?, ?, ?, ?, CASE WHEN ? THEN datetime('now') END)",
        (job_id, resume, cover_letter, method, submitted),
    )
    conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.execute("INSERT INTO events (job_id, kind, detail) VALUES (?, ?, ?)",
                 (job_id, "submitted" if submitted else "prepared", str(out)))
    conn.commit()


def run_adapter(adapter, args: argparse.Namespace) -> int:
    if CONFIG.get("kill_switch"):
        print("kill_switch is on in config.yaml — refusing to run.", file=sys.stderr)
        return 1
    conn = connect()
    seed(conn)

    job_id, url = args.job_id, args.url
    if job_id is not None:
        row = conn.execute("SELECT url, company, title FROM jobs WHERE id = ?",
                           (job_id,)).fetchone()
        if not row:
            print(f"no job with id {job_id}", file=sys.stderr)
            return 1
        url = url or row[0]
        print(f"Job {job_id}: {row[1]} — {row[2]}")
    if not url:
        print("need --url or --job-id", file=sys.stderr)
        return 1

    out = Path(args.out or Path(args.resume).parent)
    out.mkdir(parents=True, exist_ok=True)
    cover_text = Path(args.cover_letter).read_text() if args.cover_letter else None

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        # AUTOAPPLY_CHROMIUM: explicit browser binary for environments where the
        # playwright package and its downloaded browsers are out of sync.
        browser = pw.chromium.launch(headless=not args.headed,
                                     executable_path=os.environ.get("AUTOAPPLY_CHROMIUM"))
        page = browser.new_page()
        page.set_default_timeout(TIMEOUT_MS)
        page.goto(url)
        adapter.open_application(page)

        filled = adapter.fill_identity(page)
        resume_ok = adapter.upload_resume(page, args.resume)
        cover_ok = adapter.paste_cover_letter(page, cover_text) if cover_text else None
        answered, unknown = fill_screening_questions(page, conn, job_id,
                                                     adapter.QUESTION_SCOPES)

        shot = out / "application_screenshot.png"
        page.screenshot(path=str(shot), full_page=True)

        submitted = False
        if args.submit:
            required_unknown = [u for u in unknown if u["required"]]
            if not resume_ok or required_unknown:
                print("REFUSING to submit: "
                      + ("resume upload failed; " if not resume_ok else "")
                      + (f"{len(required_unknown)} required question(s) unanswered"
                         if required_unknown else ""), file=sys.stderr)
                browser.close()
                return 1
            btn = first_visible(page, adapter.SUBMIT_SELECTORS)
            if not btn:
                print("submit button not found", file=sys.stderr)
                browser.close()
                return 1
            btn.click()
            page.wait_for_load_state()
            page.screenshot(path=str(out / "post_submit_screenshot.png"), full_page=True)
            submitted = True
        browser.close()

    report = {
        "url": url, "job_id": job_id, "ats": adapter.ATS, "filled": filled,
        "resume_uploaded": resume_ok, "cover_letter_pasted": cover_ok,
        "questions_answered": answered, "unknown_questions": unknown,
        "eeo_section": "skipped (never auto-filled)",
        "screenshot": str(shot), "submitted": submitted,
    }
    (out / "application_report.json").write_text(json.dumps(report, indent=2))

    status = ("submitted" if submitted
              else "needs_answers" if unknown else "prepared")
    log_application(conn, job_id, out, args.resume, args.cover_letter,
                    adapter.ATS, status, submitted)

    print(f"{status.upper()} — {len(filled)} identity fields, "
          f"resume={'ok' if resume_ok else 'FAILED'}, "
          f"{len(answered)} questions answered, {len(unknown)} unknown")
    for u in unknown:
        print(f"  unanswered{' (REQUIRED)' if u['required'] else ''}: {u['question']}")
    if unknown:
        print("Add answers with: python -m apply.answers add \"<question>\" \"<answer>\"")
    print(f"Review: {shot}")
    if not resume_ok:
        return 1
    return 2 if unknown else 0


def main(adapter) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--job-id", type=int, help="jobs.id — url and status updates come from the DB")
    p.add_argument("--url", help="Application page URL (overrides the job's stored url)")
    p.add_argument("--resume", required=True, help="Path to resume PDF")
    p.add_argument("--cover-letter", help="Path to cover letter .md/.txt (pasted as text)")
    p.add_argument("--out", help="Output dir for screenshot + report (default: resume's dir)")
    p.add_argument("--submit", action="store_true",
                   help="Actually submit — only the approve flow passes this")
    p.add_argument("--headed", action="store_true", help="Show the browser")
    sys.exit(run_adapter(adapter, p.parse_args()))
