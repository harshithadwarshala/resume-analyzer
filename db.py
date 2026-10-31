import sqlite3
from datetime import datetime

DB_FILE = "recruitment.db"


def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT
        );
        CREATE TABLE IF NOT EXISTS applications (
            resume_id TEXT PRIMARY KEY,
            job_id TEXT,
            candidate_id TEXT,
            resume_text TEXT,
            match_percentage REAL,
            ats_score INTEGER,
            matched_skills TEXT,
            missing_skills TEXT,
            applied_at TEXT
        );
        """)


def _next_id(conn, table, prefix):
    n = conn.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0] + 1
    return f"{prefix}-{n:03d}"


def add_job(title, description):
    with get_conn() as conn:
        job_id = _next_id(conn, "jobs", "JOB")
        conn.execute(
            "INSERT INTO jobs VALUES (?,?,?,?)",
            (job_id, title, description,
             datetime.now().isoformat(timespec="seconds"))
        )
    return job_id


def get_jobs():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY job_id"
        ).fetchall()
    return [dict(r) for r in rows]


def get_job(job_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM jobs WHERE job_id=?", (job_id,)
        ).fetchone()
    return dict(row) if row else None


def add_application(job_id, name, email, phone,
                    resume_text, match, ats,
                    matched, missing):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT candidate_id FROM candidates WHERE email=?",
            (email,)
        ).fetchone()

        if row:
            candidate_id = row[0]
        else:
            candidate_id = _next_id(conn, "candidates", "CAND")
            conn.execute(
                "INSERT INTO candidates VALUES (?,?,?,?)",
                (candidate_id, name, email, phone)
            )

        resume_id = _next_id(conn, "applications", "RES")
        conn.execute(
            "INSERT INTO applications VALUES (?,?,?,?,?,?,?,?,?)",
            (resume_id, job_id, candidate_id, resume_text,
             match, ats,
             ", ".join(matched), ", ".join(missing),
             datetime.now().isoformat(timespec="seconds"))
        )
    return candidate_id, resume_id


def get_applications(job_id):
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT a.resume_id, a.candidate_id, c.name, c.email,
                   a.match_percentage, a.ats_score,
                   a.matched_skills, a.missing_skills
            FROM applications a
            JOIN candidates c
              ON a.candidate_id = c.candidate_id
            WHERE a.job_id=?
            ORDER BY a.match_percentage DESC
        """, (job_id,)).fetchall()
    return [dict(r) for r in rows]

def get_resume_text(resume_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT resume_text FROM applications WHERE resume_id=?",
            (resume_id,)
        ).fetchone()
    return row[0] if row else ""