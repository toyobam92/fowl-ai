"""Initialize the SQLite database. Usage: python -m db.init"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "db" / "autoapply.db"

def main():
    conn = sqlite3.connect(DB)
    conn.executescript((ROOT / "db" / "schema.sql").read_text())
    conn.commit()
    conn.close()
    print(f"Initialized {DB}")

if __name__ == "__main__":
    main()
