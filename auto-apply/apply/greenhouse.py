"""Greenhouse application adapter (Playwright): fill, upload, screenshot —
STOPS before submit unless --submit is passed by the approve flow.

Classic-board ids first, label-text fallbacks for the newer React boards.
Shared flow + safety contract: see apply/base.py.

Usage:
  python -m apply.greenhouse --job-id 3 --resume applications/prosper/resume.pdf \
      [--cover-letter applications/prosper/cover_letter.md] [--out applications/prosper/]
Exit codes: 0 = prepared (or submitted) clean, 2 = prepared but has unknown
questions, 1 = error / kill switch.
"""

import argparse
import sys

from apply.base import (CONFIG, by_label, fill_fields, first_visible,
                        run_adapter, upload_file)

ATS = "greenhouse"
QUESTION_SCOPES = ["#custom_fields"]
SUBMIT_SELECTORS = ["#submit_app", "button[type=submit]", "input[type=submit]",
                    "button:has-text('Submit')"]


def open_application(page) -> None:
    # Some boards land on the description with an Apply button before the form.
    if not first_visible(page, ["#first_name"]) and not by_label(page, r"first\s*name"):
        apply_btn = first_visible(page, ["a:has-text('Apply')", "button:has-text('Apply')"])
        if apply_btn:
            apply_btn.click()
            page.wait_for_load_state()


def fill_identity(page) -> dict:
    a = CONFIG["applicant"]
    return fill_fields(page, [
        ("first_name", ["#first_name"], r"first\s*name", a["first_name"]),
        ("last_name", ["#last_name"], r"last\s*name", a["last_name"]),
        ("email", ["#email"], r"^e-?mail", a["email"]),
        ("phone", ["#phone"], r"phone", a["phone"]),
        ("location", ["#job_application_location", "#candidate-location"],
         r"location|city", a.get("location", "")),
        ("linkedin", [], r"linkedin", a.get("linkedin", "")),
        ("website", [], r"website|portfolio", a.get("website", "")),
    ])


def upload_resume(page, resume_pdf: str) -> bool:
    return upload_file(page, ["input#resume[type=file]", "input[type=file][id*=resume i]",
                              "input[type=file][name*=resume i]", "input[type=file]"],
                       resume_pdf)


def paste_cover_letter(page, text: str) -> bool:
    # Classic embed hides the textarea behind a "paste" toggle.
    toggle = first_visible(page, ["a[data-source='paste']", "button:has-text('paste')",
                                  "a:has-text('paste')"])
    if toggle:
        try:
            toggle.click()
        except Exception:
            pass
    loc = first_visible(page, ["#cover_letter_text", "textarea[id*=cover i]",
                               "textarea[name*=cover i]"]) or by_label(page, r"cover\s*letter")
    if loc:
        try:
            loc.fill(text)
            return True
        except Exception:
            pass
    return False


def run(args: argparse.Namespace) -> int:
    return run_adapter(sys.modules[__name__], args)


if __name__ == "__main__":
    from apply.base import main
    main(sys.modules[__name__])
