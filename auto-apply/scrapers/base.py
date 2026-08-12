"""Shared scraper plumbing: config filters, normalization, dedupe, jobs-table writes.

Every scraper produces Job rows; insert_jobs() applies the config filters and
dedupes on url and on (company, normalized title) before writing
status='discovered' rows. Nothing is ever silently dropped — skip reasons are
counted and reported by the caller.
"""

import html
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text())
DB = ROOT / "db" / "autoapply.db"

UA = {"User-Agent": "auto-apply/0.1 (personal job search agent)"}
TIMEOUT = 20

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
# Suffixes like "(Remote)", "- Remote, US", "(Hybrid - Atlanta)" that vary per board
TITLE_NOISE_RE = re.compile(r"[\(\[\-–|,]+\s*(remote|hybrid|us|usa|united states)[^)\]]*[\)\]]?\s*$",
                            re.IGNORECASE)


@dataclass
class Job:
    url: str
    company: str
    title: str
    ats_type: str
    jd_text: str
    location: str = ""
    is_remote: bool | None = None  # None = unknown from the source


def get_json(url: str, **kwargs):
    resp = requests.get(url, headers=UA, timeout=TIMEOUT, **kwargs)
    resp.raise_for_status()
    return resp.json()


def strip_html(text: str) -> str:
    """Greenhouse/Ashby descriptions arrive as (sometimes entity-escaped) HTML.

    Greenhouse escapes the HTML itself, so entities in the content are
    double-escaped — unescape once to get HTML, strip tags, unescape again.
    """
    text = html.unescape(text or "")
    text = re.sub(r"</(p|li|div|h[1-6]|br)>", "\n", text, flags=re.IGNORECASE)
    text = html.unescape(TAG_RE.sub(" ", text))
    return WS_RE.sub(" ", text).strip()


def norm_title(title: str) -> str:
    """Dedupe key half: lowercase, strip remote/location suffixes and punctuation."""
    t = TITLE_NOISE_RE.sub("", title.lower())
    return WS_RE.sub(" ", re.sub(r"[^a-z0-9 ]", " ", t)).strip()


def title_matches(title: str) -> bool:
    """A job is worth scoring if its title hits any configured title or keyword."""
    t = title.lower()
    f = CONFIG["search_filters"]
    terms = [x.lower() for x in f.get("titles_any", []) + f.get("keywords_any", [])]
    return any(term in t for term in terms)


def looks_remote(job: Job) -> bool:
    if job.is_remote is not None:
        return job.is_remote
    return "remote" in f"{job.location} {job.title}".lower()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.executescript((ROOT / "db" / "schema.sql").read_text())  # idempotent
    return conn


def insert_jobs(jobs: list[Job]) -> dict:
    """Filter + dedupe + insert with status='discovered'. Returns counts."""
    counts = {"new": 0, "duplicate": 0, "title_filtered": 0, "not_remote": 0}
    remote_only = CONFIG["search_filters"].get("location") == "remote_us"
    conn = _connect()
    seen = {(c.lower(), norm_title(t)) for c, t in
            conn.execute("SELECT company, title FROM jobs")}
    urls = {u for (u,) in conn.execute("SELECT url FROM jobs")}
    for job in jobs:
        if not title_matches(job.title):
            counts["title_filtered"] += 1
            continue
        if remote_only and not looks_remote(job):
            counts["not_remote"] += 1
            continue
        key = (job.company.lower(), norm_title(job.title))
        if job.url in urls or key in seen:
            counts["duplicate"] += 1
            continue
        conn.execute(
            "INSERT INTO jobs (url, company, title, ats_type, jd_text, status) "
            "VALUES (?, ?, ?, ?, ?, 'discovered')",
            (job.url, job.company, job.title, job.ats_type, job.jd_text),
        )
        seen.add(key)
        urls.add(job.url)
        counts["new"] += 1
    conn.commit()
    conn.close()
    return counts
