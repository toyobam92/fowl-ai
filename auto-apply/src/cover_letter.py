"""Cover letter pipeline with the same fabrication guardrails as rewrite.py.

Stages:
  1. Constrained generation — claims about the candidate only from profile.md,
     claims about the company only from the JD.
  2. Adversarial audit — second Claude call; any flagged claim blocks the pipeline.
     Fail closed: audit failure or unparseable audit output = BLOCKED, nothing written.

Usage:
  python -m src.cover_letter --jd fixtures/prosper.txt --company Prosper \
      --out applications/prosper/
Requires ANTHROPIC_API_KEY in the environment.
"""

import argparse
import json
import sys
from pathlib import Path

from anthropic import Anthropic

from src.llm import MODEL, ROOT, call, client, parse_json


def write_letter(cl: Anthropic, profile: str, jd: str, company: str) -> str:
    system = (ROOT / "assets/prompts/cover_letter_prompt.md").read_text()
    user = (
        f"<PROFILE>\n{profile}\n</PROFILE>\n\n"
        f"<JOB_DESCRIPTION>\n{jd}\n</JOB_DESCRIPTION>\n\n"
        f"<COMPANY>\n{company}\n</COMPANY>"
    )
    return call(cl, system, user, max_tokens=1500)


def audit_letter(cl: Anthropic, profile: str, jd: str, letter: str) -> dict:
    system = (ROOT / "assets/prompts/cover_letter_audit_prompt.md").read_text()
    user = (
        f"<PROFILE>\n{profile}\n</PROFILE>\n\n"
        f"<JOB_DESCRIPTION>\n{jd}\n</JOB_DESCRIPTION>\n\n"
        f"<COVER_LETTER>\n{letter}\n</COVER_LETTER>"
    )
    raw = call(cl, system, user, max_tokens=2000)
    audit = parse_json(raw)
    if audit is None:
        # Unparseable audit = failed audit. Never fail open.
        return {"result": "FAIL", "flagged": [{"claim": "<audit unparseable>",
                                               "problem": raw[:500],
                                               "nearest_source_line": None}]}
    return audit


def run(jd_path: str, company: str, out_dir: str) -> int:
    cl = client()
    profile = (ROOT / "assets/profile.md").read_text()
    jd = Path(jd_path).read_text()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"[1/2] Writing cover letter for {company} (model={MODEL})...")
    letter = write_letter(cl, profile, jd, company)

    print("[2/2] Adversarial audit...")
    audit = audit_letter(cl, profile, jd, letter)
    (out / "cover_letter_audit.json").write_text(json.dumps(audit, indent=2))

    if audit.get("result") != "PASS":
        (out / "BLOCKED_cover_letter.txt").write_text(json.dumps(audit, indent=2))
        print(f"BLOCKED — audit flagged {len(audit.get('flagged', []))} claim(s). "
              f"See cover_letter_audit.json. Nothing was rendered.")
        return 1

    (out / "cover_letter.md").write_text(letter)
    print(f"PASS — cover_letter.md written to {out}/")
    print("Next: python -m src.render --md " + str(out / "cover_letter.md"))
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--jd", required=True, help="Path to job description .txt")
    p.add_argument("--company", required=True, help="Company name for the letter")
    p.add_argument("--out", required=True, help="Output directory")
    a = p.parse_args()
    sys.exit(run(a.jd, a.company, a.out))
