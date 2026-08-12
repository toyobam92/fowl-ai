"""Screening-question answers bank (answers_bank table).

Questions are stored normalized (lowercase, punctuation stripped) so the same
question phrased across ATSes matches once. Non-sensitive seeds live in
config.yaml screening_answers; sensitive answers (salary, EEO) are added
locally only — the DB is gitignored.

Usage:
  python -m apply.answers list
  python -m apply.answers add "Desired salary?" "..."
"""

import re
import sqlite3
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = yaml.safe_load((ROOT / "config.yaml").read_text())
DB = ROOT / "db" / "autoapply.db"

WS_RE = re.compile(r"\s+")


def norm_question(q: str) -> str:
    q = q.lower().strip()
    q = re.sub(r"[*✱]|\(required\)|\(optional\)", " ", q)
    q = re.sub(r"[^a-z0-9 ]", " ", q)
    return WS_RE.sub(" ", q).strip()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.executescript((ROOT / "db" / "schema.sql").read_text())  # idempotent
    return conn


def seed(conn: sqlite3.Connection) -> None:
    for q, a in (CONFIG.get("screening_answers") or {}).items():
        conn.execute(
            "INSERT INTO answers_bank (question_norm, answer) VALUES (?, ?) "
            "ON CONFLICT(question_norm) DO NOTHING",
            (norm_question(q), str(a)),
        )
    conn.commit()


def lookup(conn: sqlite3.Connection, question: str) -> str | None:
    """Exact normalized match, else containment either way (longest bank match wins)."""
    q = norm_question(question)
    if not q:
        return None
    row = conn.execute(
        "SELECT answer FROM answers_bank WHERE question_norm = ?", (q,)).fetchone()
    if row:
        return row[0]
    best = None
    for bank_q, answer in conn.execute("SELECT question_norm, answer FROM answers_bank"):
        if bank_q in q or q in bank_q:
            if best is None or len(bank_q) > len(best[0]):
                best = (bank_q, answer)
    return best[1] if best else None


def add(conn: sqlite3.Connection, question: str, answer: str) -> None:
    conn.execute(
        "INSERT INTO answers_bank (question_norm, answer) VALUES (?, ?) "
        "ON CONFLICT(question_norm) DO UPDATE SET answer=excluded.answer",
        (norm_question(question), answer),
    )
    conn.commit()


def record_unknown(conn: sqlite3.Connection, job_id: int | None, question: str) -> None:
    conn.execute(
        "INSERT INTO events (job_id, kind, detail) VALUES (?, 'unknown_question', ?)",
        (job_id, question),
    )
    conn.commit()


if __name__ == "__main__":
    conn = connect()
    seed(conn)
    argv = sys.argv[1:]
    if argv[:1] == ["list"]:
        for q, a in conn.execute("SELECT question_norm, answer FROM answers_bank ORDER BY question_norm"):
            print(f"  {q!r} -> {a!r}")
    elif argv[:1] == ["add"] and len(argv) == 3:
        add(conn, argv[1], argv[2])
        print(f"Stored: {norm_question(argv[1])!r} -> {argv[2]!r}")
    else:
        sys.exit(__doc__)
