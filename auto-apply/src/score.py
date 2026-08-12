"""Score a job description against the canonical profile.

Output JSON: {score, track, match_reasons, gaps, resume_variant} plus a decision
derived from config score_thresholds (auto_prep / digest / archive).

Usage:
  python -m src.score --jd fixtures/prosper.txt
  python -m src.score --jd fixtures/prosper.txt --out applications/prosper/
  python -m src.score --jd fixtures/prosper.txt --save \
      --company Prosper --title "Sr. Manager, Credit Risk Analytics" \
      --url https://... [--ats greenhouse]
Requires ANTHROPIC_API_KEY in the environment.
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from src.llm import CONFIG, MODEL, ROOT, call, client, parse_json

TRACKS = {"credit-risk", "ds-ml", "ai-tpm", "health-tech"}
DB = ROOT / "db" / "autoapply.db"


def available_variants() -> list[str]:
    return sorted(p.stem for p in (ROOT / "assets/resumes").glob("*.md"))


def score_jd(jd: str) -> dict:
    system = (ROOT / "assets/prompts/score_prompt.md").read_text()
    profile = (ROOT / "assets/profile.md").read_text()
    variants = available_variants()
    user = (
        f"<PROFILE>\n{profile}\n</PROFILE>\n\n"
        f"<JOB_DESCRIPTION>\n{jd}\n</JOB_DESCRIPTION>\n\n"
        f"<AVAILABLE_VARIANTS>\n{', '.join(variants)}\n</AVAILABLE_VARIANTS>"
    )
    raw = call(client(), system, user, max_tokens=1500)
    result = parse_json(raw)
    if result is None:
        # Unparseable scoring output = no score. Never guess.
        sys.exit(f"BLOCKED — scoring output unparseable:\n{raw[:500]}")
    return validate(result, variants)


def validate(result: dict, variants: list[str]) -> dict:
    problems = []
    score = result.get("score")
    if not isinstance(score, int) or not 1 <= score <= 100:
        problems.append(f"score must be int 1-100, got {score!r}")
    if result.get("track") not in TRACKS:
        problems.append(f"track must be one of {sorted(TRACKS)}, got {result.get('track')!r}")
    for key, want in (("match_reasons", 3), ("gaps", 2)):
        val = result.get(key)
        if not isinstance(val, list) or len(val) != want:
            problems.append(f"{key} must be a list of {want}, got {val!r}")
    if problems:
        sys.exit("BLOCKED — invalid scoring output:\n" + "\n".join(problems))
    if result.get("resume_variant") not in variants:
        print(f"warning: recommended variant {result.get('resume_variant')!r} not on disk; "
              f"falling back to {variants[0]!r}", file=sys.stderr)
        result["resume_variant"] = variants[0]
    return result


def decide(score: int) -> str:
    t = CONFIG["score_thresholds"]
    if score >= t["auto_prep"]:
        return "auto_prep"
    if score >= t["digest"]:
        return "digest"
    return "archive"


def save_job(result: dict, jd: str, company: str, title: str,
             url: str, ats: str | None) -> int:
    conn = sqlite3.connect(DB)
    conn.executescript((ROOT / "db" / "schema.sql").read_text())  # idempotent
    cur = conn.execute(
        """INSERT INTO jobs (url, company, title, ats_type, jd_text, score, track,
                             match_reasons, gaps, resume_variant, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'scored')
           ON CONFLICT(url) DO UPDATE SET
             jd_text=excluded.jd_text, score=excluded.score, track=excluded.track,
             match_reasons=excluded.match_reasons, gaps=excluded.gaps,
             resume_variant=excluded.resume_variant, status='scored'""",
        (url, company, title, ats, jd, result["score"], result["track"],
         json.dumps(result["match_reasons"]), json.dumps(result["gaps"]),
         result["resume_variant"]),
    )
    conn.commit()
    job_id = cur.lastrowid or conn.execute(
        "SELECT id FROM jobs WHERE url = ?", (url,)).fetchone()[0]
    conn.close()
    return job_id


def run(args: argparse.Namespace) -> int:
    jd = Path(args.jd).read_text()
    print(f"Scoring against profile (model={MODEL})...", file=sys.stderr)
    result = score_jd(jd)
    result["decision"] = decide(result["score"])

    print(json.dumps(result, indent=2))
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "score.json").write_text(json.dumps(result, indent=2))
        print(f"Wrote {out / 'score.json'}", file=sys.stderr)
    if args.save:
        job_id = save_job(result, jd, args.company, args.title, args.url, args.ats)
        print(f"Saved to jobs table (id={job_id}, status=scored)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--jd", required=True, help="Path to job description .txt")
    p.add_argument("--out", help="Optional directory to write score.json")
    p.add_argument("--save", action="store_true",
                   help="Upsert result into the jobs table (requires --company/--title/--url)")
    p.add_argument("--company")
    p.add_argument("--title")
    p.add_argument("--url")
    p.add_argument("--ats", help="greenhouse | lever | ashby | workday | other")
    a = p.parse_args()
    if a.save and not (a.company and a.title and a.url):
        p.error("--save requires --company, --title, and --url")
    sys.exit(run(a))
