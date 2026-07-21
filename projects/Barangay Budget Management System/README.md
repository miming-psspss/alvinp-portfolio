# Barangay Budget Management System

Role-based financial management system for barangay-level budget tracking, built with
Python and Tkinter. Handles income/expense transactions, cash balance tracking, and
audit logging, with different access levels for administrators, kagawads, and treasurers.

## Features
- **Role-based access** — separate permissions for Barangay Administrator, Kagawad, and
  Treasurer accounts
- **Transaction management** — records income, expenses, and cash adjustments against a
  categorized chart of accounts (Internal Revenue Allotment, Local Tax Collection,
  Service Income, etc.), with an approval status per entry
- **Cash balance tracking** — running cash balance updated per approved transaction
- **Audit logging** — every user action is logged for accountability
- **Reporting** — dedicated report generation and per-user report views

## How it's organized
- `main.py` — application launcher
- `app.py` — main GUI shell, wires together auth, transactions, cash, and reporting
- `auth.py` — login/authentication system
- `database.py` / `database_fixed.py` — SQLite schema and data access layer
- `transaction_manager.py` — transaction creation, validation, and approval logic
- `cash_manager.py` — cash balance calculations
- `reporting.py` — report generation
- `widgets/` — individual Tkinter windows: login, dashboard, transactions, cash,
  admin, user management, audit log, and reporting screens

## Setup
```
pip install -r requirements.txt
python main.py
```

**Note:** the included `barangay_budget.db` contains only placeholder/test data
(dummy names, test amounts) — no real barangay financial records.
