"""Ashby application adapter (Playwright): fill, upload, screenshot —
STOPS before submit unless --submit is passed by the approve flow.

Ashby quirks: React app, so the application form sits behind an Apply
button/tab; fields use _systemfield_ ids (single full-name field) with
label-text fallbacks; resume upload is a hidden file input behind an
"Upload File" button. Shared flow + safety contract: see apply/base.py.

Usage:
  python -m apply.ashby --job-id 5 --resume applications/x/resume.pdf \
      [--cover-letter applications/x/cover_letter.md] [--out applications/x/]
Exit codes: 0 = prepared (or submitted) clean, 2 = prepared but has unknown
questions, 1 = error / kill switch.
"""

import argparse
import sys

from apply.base import (CONFIG, by_label, fill_fields, first_visible,
                        run_adapter, upload_file)

ATS = "ashby"
QUESTION_SCOPES = ["form"]
SUBMIT_SELECTORS = ["button:has-text('Submit Application')",
                    "button[type=submit]:has-text('Submit')"]


def open_application(page) -> None:
    # Job page shows Overview first; the form is behind an Apply button/tab.
    if not first_visible(page, ["#_systemfield_name"]) and not by_label(page, r"^name"):
        apply_btn = first_visible(page, ["a:has-text('Apply for this Job')",
                                         "button:has-text('Apply')",
                                         "[role='tab']:has-text('Application')"])
        if apply_btn:
            apply_btn.click()
            page.wait_for_load_state()


def fill_identity(page) -> dict:
    a = CONFIG["applicant"]
    return fill_fields(page, [
        ("name", ["#_systemfield_name", "input[name='_systemfield_name']"],
         r"full\s*name|^name", f"{a['first_name']} {a['last_name']}"),
        ("email", ["#_systemfield_email", "input[name='_systemfield_email']"],
         r"^e-?mail", a["email"]),
        ("phone", ["#_systemfield_phone", "input[name='_systemfield_phone']"],
         r"phone", a["phone"]),
        ("location", ["#_systemfield_location"], r"location|city", a.get("location", "")),
        ("linkedin", [], r"linkedin", a.get("linkedin", "")),
        ("website", [], r"website|portfolio", a.get("website", "")),
    ])


def upload_resume(page, resume_pdf: str) -> bool:
    return upload_file(page, ["#_systemfield_resume", "input[type=file][id*=resume i]",
                              "input[type=file][name*=resume i]", "input[type=file]"],
                       resume_pdf)


def paste_cover_letter(page, text: str) -> bool:
    loc = first_visible(page, ["textarea[id*=cover i]", "textarea[name*=cover i]"]) \
        or by_label(page, r"cover\s*letter")
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
