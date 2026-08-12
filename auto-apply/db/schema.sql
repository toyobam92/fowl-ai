CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT UNIQUE NOT NULL,
  company TEXT NOT NULL,
  title TEXT NOT NULL,
  ats_type TEXT,
  jd_text TEXT,
  score INTEGER,
  track TEXT,
  match_reasons TEXT,
  gaps TEXT,
  resume_variant TEXT,
  status TEXT DEFAULT 'discovered',
  discovered_at TEXT DEFAULT (datetime('now')),
  UNIQUE(company, title) ON CONFLICT IGNORE
);

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER REFERENCES jobs(id),
  resume_path TEXT,
  cover_letter_path TEXT,
  diff_report_path TEXT,
  audit_result TEXT,
  method TEXT,
  submitted_at TEXT
);

CREATE TABLE IF NOT EXISTS answers_bank (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_norm TEXT UNIQUE,
  answer TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER REFERENCES jobs(id),
  kind TEXT,
  detail TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);
