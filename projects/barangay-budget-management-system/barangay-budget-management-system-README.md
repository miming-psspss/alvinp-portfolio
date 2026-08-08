# Barangay Budget Management System

A desktop financial management tool for barangay (local government unit) treasury
operations: transaction recording, a maker-checker approval workflow, cash balance
tracking, budget allocation by category, and role-based access control. Built with
Python/Tkinter and a local SQLite database — no server or internet connection required.

## Features

- **Role-based access** — three access levels (`viewer`, `treasurer`, `admin`), enforced
  in `auth.py` (`require_access_level`), gating what each user can see and do
- **Transaction recording** — income and expense entries with category, amount, payee/
  payer, and payment method (cash, check, bank transfer), tied to the user who prepared it
- **Approval workflow** — every transaction starts as `pending`; an admin reviews and
  approves or rejects it before it affects the books (`widgets/admin_window.py`)
- **Cash management** — running cash balance with adjustment history
  (`widgets/cash_window.py`, `cash_manager.py`)
- **Budget allocation** — per-category budget by fiscal year, tracking allocated vs.
  remaining amounts
- **Reporting** — daily and monthly reports, exportable via OpenPyXL
  (`widgets/report_window.py`, `reporting.py`)
- **User management** — add/edit users, reset passwords, deactivate accounts
  (`widgets/user_management_window.py`)
- **User activity reports** — DB-backed activity log (`user_audit_log` table), with a
  fallback that synthesizes an activity view from existing transaction/user data if the
  log table is empty (`widgets/user_reports_window.py`)
- **Dashboard** — at-a-glance summary stats on login (`widgets/dashboard.py`)

## How it's organized

- `main.py` — application entry point, launches the Tkinter root window
- `app.py` — main GUI shell, wires together the database, auth, transaction, cash, and
  reporting managers and hosts all the widget screens
- `database.py` — SQLite schema (`users`, `categories`, `transactions`,
  `budget_allocation`, `cash_balance`) and connection/query helpers
- `auth.py` — login, password hashing (SHA-256), and access-level checks
- `transaction_manager.py` — transaction creation, approval, and rejection logic
- `cash_manager.py` — cash balance updates and adjustment history
- `reporting.py` — report generation and Excel export
- `user_manager.py` — user CRUD operations
- `widgets/` — one file per screen (login, dashboard, transactions, cash, reports, admin
  approval queue, audit log, user management, user reports, system settings)

## Setup

```bash
pip install pandas openpyxl
python main.py
```

A local SQLite file (`barangay_budget.db`) is created automatically on first run, seeded
with default budget categories and an initial admin account.

> **Default login:** username `admin`, password `admin123`. This is a seeded demo
> credential set in `database.py` for first-run access — change it immediately after
> logging in for any real deployment.

## Note on data

This is an independent/portfolio project — the database seeds with demo categories and
a single admin account, not real barangay financial data. The **Audit Log** screen
(`widgets/audit_log_window.py`) currently displays illustrative placeholder entries
rather than live logging; the separate **User Reports** screen is the one backed by a
real, queryable activity table.

