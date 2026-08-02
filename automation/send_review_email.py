#!/usr/bin/env python3
"""Send a copy of the in-progress issue draft to the owner's own inbox for review.

This is a review copy only -- it goes to a single address (the repo owner),
never to the subscriber list. Sending to subscribers only ever happens via
EmailOctopus (see automation/emailoctopus-draft.mjs), gated on a separate
explicit "SCHEDULE <PR#>" reply.
"""
import argparse
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_ADDRESS = os.environ.get("REVIEW_TO_ADDRESS", GMAIL_ADDRESS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-path", required=True, help="Path to the issue HTML file")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--note", default="", help="Short note prepended above the issue content")
    args = parser.parse_args()

    with open(args.issue_path, encoding="utf-8") as f:
        html = f.read()

    if args.note:
        note_html = f'<p style="background:#fffbe6;border:1px solid #f0e0a0;padding:10px 14px;font-family:sans-serif;">{args.note}</p>'
        idx = html.lower().find("<body")
        if idx != -1:
            close = html.find(">", idx)
            html = html[: close + 1] + note_html + html[close + 1 :]
        else:
            html = note_html + html

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Review] {args.subject}"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = TO_ADDRESS
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, [TO_ADDRESS], msg.as_string())

    print(f"Sent review copy of '{args.subject}' to {TO_ADDRESS}")


if __name__ == "__main__":
    main()
