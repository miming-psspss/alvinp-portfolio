"""
Data layer for the Legal Notice & Mediation Batch Processing System.

Replaces the DATABASE / PEOPLE sheets from the original Excel workbook
with a proper SQLite schema. Column names are kept close to the original
headers so the mapping is traceable, but normalized to snake_case.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cases.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS cases (
    case_no INTEGER PRIMARY KEY,
    member_name TEXT NOT NULL,
    billing_address TEXT,
    age INTEGER,
    gender TEXT,
    civil_status TEXT,
    occupation TEXT,
    contact_number TEXT,
    email TEXT,
    voucher_number TEXT,
    kind_of_loan TEXT,
    principal REAL,
    date_granted TEXT,
    maturity_date TEXT,
    end_of_calculation TEXT,
    number_of_days INTEGER,
    amortization REAL,
    balance REAL,
    past_due_interest REAL,
    penalty REAL,
    less_total_pdi REAL,
    less_total_pen REAL,
    total_amount_due REAL,
    mediator TEXT,
    status TEXT DEFAULT 'PENDING',

    -- Mediation lifecycle fields (not in the original DATABASE sheet --
    -- added to support the notice/tracking/settlement/report templates).
    authorized_representative TEXT,
    representative_designation TEXT,
    notice_date TEXT,
    conference_round TEXT,
    conference_date TEXT,
    conference_time TEXT,
    conference_venue TEXT,
    first_appearance_date TEXT,
    reset_date TEXT,
    reset_reason TEXT,
    mediation_result TEXT,
    failure_reason TEXT,
    action_taken TEXT,
    returned_reason TEXT,
    agreement_date TEXT,
    payment_schedule TEXT,
    report_date TEXT,
    comments TEXT
);

CREATE TABLE IF NOT EXISTS generation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_no INTEGER NOT NULL,
    document_type TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    output_path TEXT NOT NULL,
    FOREIGN KEY (case_no) REFERENCES cases(case_no)
);
"""


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def list_cases(search: str = ""):
    conn = get_connection()
    if search:
        rows = conn.execute(
            "SELECT case_no, member_name, kind_of_loan, total_amount_due, status "
            "FROM cases WHERE member_name LIKE ? ORDER BY case_no",
            (f"%{search}%",),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT case_no, member_name, kind_of_loan, total_amount_due, status "
            "FROM cases ORDER BY case_no"
        ).fetchall()
    conn.close()
    return rows


def get_case(case_no: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM cases WHERE case_no = ?", (case_no,)).fetchone()
    conn.close()
    return dict(row) if row else None


def log_generation(case_no: int, document_type: str, output_path: str, when: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO generation_log (case_no, document_type, generated_at, output_path) "
        "VALUES (?, ?, ?, ?)",
        (case_no, document_type, when, output_path),
    )
    conn.commit()
    conn.close()


def get_generation_history(case_no: int):
    conn = get_connection()
    rows = conn.execute(
        "SELECT document_type, generated_at, output_path FROM generation_log "
        "WHERE case_no = ? ORDER BY generated_at DESC",
        (case_no,),
    ).fetchall()
    conn.close()
    return rows
