"""Lever application adapter (Playwright): fill, upload, screenshot —
STOPS before submit unless --submit is passed by the approve flow.

Lever quirks: single full-name field, name=-attribute selectors, current
company in `org`, cover letter pasted into the "Additional information"
comments box, EEO block under name^=eeo (never auto-filled).
Shared flow + safety contract: see apply/base.py.

Usage:
  python -m apply.lever --job-id 4 --resume applications/x/resume.pdf \
      [--cover-letter applications/x/cover_letter.md] [--out applications/x/]
Exit codes: 0 = prepared (or submitted) clean, 2 = prepared but has unknown
questions, 1 = error / kill switch.
"""

import argparse
import sys

from apply.base import (CONFIG, by_label, fill_fields, first_visible,
                        run_adapter, upload_file)

ATS = "lever"
QUESTION_SCOPES = [".application-question", "form"]
SUBMIT_SELECTORS = ["#btn-submit", "button[type=submit]:has-text('Submit')",
                    "button:has-text('Submit application')"]


def open_application(page) -> None:
    # Posting pages link to the form via an "Apply for this job" button.
    if not first_visible(page, ["input[name='name']"]) and not by_label(page, r"full\s*name"):
        apply_btn = first_visible(page, ["a:has-text('Apply for this job')",
                                         "a:has-text('Apply')", "button:has-text('Apply')"])
        if apply_btn:
            apply_btn.click()
            page.wait_for_load_state()


def fill_identity(page) -> dict:
    a = CONFIG["applicant"]
    return fill_fields(page, [
        ("name", ["input[name='name']"], r"full\s*name|^name",
         f"{a['first_name']} {a['last_name']}"),
        ("email", ["input[name='email']"], r"^e-?mail", a["email"]),
        ("phone", ["input[name='phone']"], r"phone", a["phone"]),
        ("org", ["input[name='org']"], r"current\s*(company|employer)|^company",
         a.get("current_company", "")),
        ("location", ["input[name='location']"], r"location|city", a.get("location", "")),
        ("linkedin", ["input[name='urls[LinkedIn]']"], r"linkedin", a.get("linkedin", "")),
        ("website", ["input[name='urls[Portfolio]']", "input[name='urls[Other]']"],
         r"website|portfolio", a.get("website", "")),
    ])


def upload_resume(page, resume_pdf: str) -> bool:
    return upload_file(page, ["#resume-upload-input", "input[name='resume'][type=file]",
                              "input[type=file][id*=resume i]", "input[type=file]"],
                       resume_pdf)


def paste_cover_letter(page, text: str) -> bool:
    # Lever has no dedicated cover-letter field; the convention is the
    # "Additional information" comments box.
    loc = first_visible(page, ["textarea[name='comments']",
                               "textarea[id*=additional i]"]) \
        or by_label(page, r"additional\s*information|cover\s*letter")
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
