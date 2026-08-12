"""Find which ATS hosts a company's job board by probing all three public APIs.

Usage:
  python -m scrapers.probe prosper
  python -m scrapers.probe "lexisnexis risk solutions" lexisnexis-risk-solutions

Tries each candidate slug (plus hyphenated/compact forms of it) against
Greenhouse, Lever, and Ashby, and prints ready-to-paste config lines for hits.
"""

import sys

import requests

from scrapers.base import TIMEOUT, UA

ENDPOINTS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}


def job_count(ats: str, payload) -> int | None:
    if ats == "lever":
        return len(payload) if isinstance(payload, list) else None
    jobs = payload.get("jobs") if isinstance(payload, dict) else None
    return len(jobs) if isinstance(jobs, list) else None


def variants(name: str) -> list[str]:
    base = name.strip().lower()
    forms = [base, base.replace(" ", "-"), base.replace(" ", ""),
             base.replace(".", ""), base.replace("&", "and")]
    return list(dict.fromkeys(forms))  # dedupe, keep order


def probe(name: str) -> list[tuple[str, str, int]]:
    hits = []
    for slug in variants(name):
        for ats, url in ENDPOINTS.items():
            try:
                resp = requests.get(url.format(slug=slug), headers=UA, timeout=TIMEOUT)
            except requests.RequestException as e:
                print(f"  {ats}/{slug}: network error ({e})", file=sys.stderr)
                continue
            if resp.status_code != 200:
                continue
            try:
                n = job_count(ats, resp.json())
            except ValueError:
                continue
            if n is not None:
                hits.append((ats, slug, n))
    return hits


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    found_any = False
    for name in sys.argv[1:]:
        hits = probe(name)
        print(f"{name}:")
        if not hits:
            print("  no board found on greenhouse/lever/ashby "
                  "(may use Workday/Taleo/custom — manual queue)")
            continue
        found_any = True
        for ats, slug, n in hits:
            print(f"  {ats}: {slug}  ({n} live postings) -> add to config boards.{ats}")
    sys.exit(0 if found_any else 1)
