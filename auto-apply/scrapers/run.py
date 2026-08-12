"""Run all configured board scrapers and write new jobs (status='discovered').

Boards come from config.yaml `boards:` — per-ATS lists of board tokens.
A failing board is reported and skipped, never aborts the run (and never
silently dropped). Schedule 2x daily via cron:

  0 8,18 * * *  cd /path/to/auto-apply && python -m scrapers.run >> scrape.log 2>&1

Usage:
  python -m scrapers.run             # all boards in config
  python -m scrapers.run --ats greenhouse   # one ATS only
"""

import argparse
import sys

from scrapers import ashby, greenhouse, lever
from scrapers.base import CONFIG, insert_jobs

SCRAPERS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby}


def run(only_ats: str | None = None) -> int:
    boards = CONFIG.get("boards") or {}
    totals = {"new": 0, "duplicate": 0, "title_filtered": 0, "not_remote": 0}
    errors = []
    for ats, tokens in boards.items():
        if only_ats and ats != only_ats:
            continue
        if ats not in SCRAPERS:
            errors.append(f"{ats}: no scraper for this ATS")
            continue
        for token in tokens or []:
            try:
                jobs = SCRAPERS[ats].fetch(token)
            except Exception as e:
                errors.append(f"{ats}/{token}: {e}")
                continue
            counts = insert_jobs(jobs)
            for k in totals:
                totals[k] += counts[k]
            print(f"{ats}/{token}: {len(jobs)} postings -> "
                  f"{counts['new']} new, {counts['duplicate']} dup, "
                  f"{counts['title_filtered']} off-target, {counts['not_remote']} not remote")

    print(f"\nTOTAL: {totals['new']} new jobs written (status=discovered), "
          f"{totals['duplicate']} duplicates, {totals['title_filtered']} off-target, "
          f"{totals['not_remote']} not remote")
    if errors:
        print(f"\n{len(errors)} board(s) FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--ats", choices=sorted(SCRAPERS),
                   help="Run only this ATS's boards")
    sys.exit(run(p.parse_args().ats))
