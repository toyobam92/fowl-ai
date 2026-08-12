"""Resume rewrite pipeline with fabrication guardrails.

Stages:
  1. Locked facts  — {{LOCKED:...}} spans are verified byte-identical after rewrite.
  2. Constrained rewrite — Claude reorders/rephrases/selects only.
  3. Adversarial audit — second Claude call; any flagged claim blocks the pipeline.

Usage:
  python -m src.rewrite --jd path/to/jd.txt --variant credit-risk --out applications/prosper-sr-mgr/
Requires ANTHROPIC_API_KEY in the environment.
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

from anthropic import Anthropic

from src.llm import CONFIG, MODEL, ROOT
from src.llm import call as _call
from src.llm import client as _client

LOCKED_RE = re.compile(r"\{\{LOCKED:.*?\}\}", re.DOTALL)


def rewrite_resume(client: Anthropic, profile: str, base_resume: str, jd: str) -> str:
    prompt_tpl = (ROOT / "assets/prompts/rewrite_prompt.md").read_text()
    max_kw = CONFIG["guardrails"]["max_jd_keywords_inserted"]
    system = prompt_tpl.replace("{{MAX_KEYWORDS}}", str(max_kw))
    user = (
        f"<PROFILE>\n{profile}\n</PROFILE>\n\n"
        f"<BASE_RESUME>\n{base_resume}\n</BASE_RESUME>\n\n"
        f"<JOB_DESCRIPTION>\n{jd}\n</JOB_DESCRIPTION>"
    )
    return _call(client, system, user)


def audit_resume(client: Anthropic, profile: str, rewritten: str) -> dict:
    system = (ROOT / "assets/prompts/audit_prompt.md").read_text()
    user = (
        f"<PROFILE>\n{profile}\n</PROFILE>\n\n"
        f"<REWRITTEN_RESUME>\n{rewritten}\n</REWRITTEN_RESUME>"
    )
    raw = _call(client, system, user, max_tokens=2000)
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Unparseable audit = failed audit. Never fail open.
        return {"result": "FAIL", "flagged": [{"claim": "<audit unparseable>",
                                               "problem": raw[:500],
                                               "nearest_profile_line": None}]}


def verify_locked_spans(base_resume: str, rewritten: str) -> list[str]:
    """Every {{LOCKED:...}} span in the base must appear verbatim in the rewrite."""
    missing = []
    for span in LOCKED_RE.findall(base_resume):
        if span not in rewritten:
            missing.append(span)
    return missing


def diff_report(base_resume: str, rewritten: str) -> str:
    diff = difflib.unified_diff(
        base_resume.splitlines(), rewritten.splitlines(),
        fromfile="base_resume", tofile="rewritten", lineterm="",
    )
    return "\n".join(diff)


def strip_locked_tags(text: str) -> str:
    """Remove tag wrappers for the final rendered resume."""
    return re.sub(r"\{\{LOCKED:(.*?)\}\}", r"\1", text, flags=re.DOTALL)


def run(jd_path: str, variant: str, out_dir: str) -> int:
    client = _client()
    profile = (ROOT / "assets/profile.md").read_text()
    base_resume = (ROOT / f"assets/resumes/{variant}.md").read_text()
    jd = Path(jd_path).read_text()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] Rewriting ({variant} variant, model={MODEL})...")
    rewritten = rewrite_resume(client, profile, base_resume, jd)

    print("[2/3] Verifying locked spans...")
    missing = verify_locked_spans(base_resume, rewritten)
    if missing:
        (out / "BLOCKED.txt").write_text(
            "Locked spans altered or missing:\n" + "\n".join(missing))
        print(f"BLOCKED — {len(missing)} locked span(s) altered. See BLOCKED.txt")
        return 1

    print("[3/3] Adversarial audit...")
    audit = audit_resume(client, profile, rewritten)
    (out / "audit.json").write_text(json.dumps(audit, indent=2))

    if audit.get("result") != "PASS":
        (out / "BLOCKED.txt").write_text(json.dumps(audit, indent=2))
        print(f"BLOCKED — audit flagged {len(audit.get('flagged', []))} claim(s). "
              f"See audit.json. Nothing was rendered.")
        return 1

    final_md = strip_locked_tags(rewritten)
    (out / "resume.md").write_text(final_md)
    (out / "diff_report.txt").write_text(diff_report(base_resume, rewritten))
    print(f"PASS — resume.md + diff_report.txt written to {out}/")
    print("Next: python -m src.render --md " + str(out / "resume.md"))
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--jd", required=True, help="Path to job description .txt")
    p.add_argument("--variant", default="credit-risk",
                   help="Base resume variant name in assets/resumes/")
    p.add_argument("--out", required=True, help="Output directory")
    a = p.parse_args()
    sys.exit(run(a.jd, a.variant, a.out))
