# Alvin Piquero, IT Automation, Systems, Business Specialist

Python and VBA automation projects built for real-world use in a financial cooperative
serving 7,000+ members, plus a growing set of independent projects extending that work
into new tools and platforms. Built end-to-end, covering requirements, design, deployment,
and support, turning multi-hour manual processes into workflows that run in minutes, and
improving data migration accuracy from roughly 70% to 99% at scale.

- **Location:** Candijay, Bohol, Philippines
- **Email:** alvin_piquero@outlook.ph
- **LinkedIn:** https://www.linkedin.com/in/alvinpiquero481743254/
- **Resume / CV:** see [`resume/`](./resume)
- **Timezone:** PHT (UTC+8), flexible overlap with US, UK, or AU

---

## Repository Structure

```
resume/              → resume and CV (PDF)
projects/             → working software: what I built
vop/                  → Variables of Prompting (VoP), my framework for disciplined AI-assisted dev
cas-planning-docs/    → planning docs for the Cooperative AI System (CAS) concept
cas-n8n-vop-workflow/ → active n8n build implementing CAS, governed by VoP (in progress)
```

### `projects/`

**Production systems** (built and run live at Santa Ana Multi-Purpose Cooperative, SAMCO)

| Project | Description |
|---|---|
| [ATM Data Extraction & Reporting Automation](./projects/atm-data-extraction-reporting) | Resolved a 3-year reporting backlog in a day; extracts transaction data from password-protected archives, cutting a multi-hour process to under 5 minutes. Later generalized into the client-agnostic [Batch Financial Report Processing](./projects/batch-financial-report-processing) product |
| [Legal Notice & Mediation Batch Processing System](./projects/legal-notice-mediation-batch-processing-system) | Python/PySide6 rebuild of a live VBA production tool, all 11 real document types wired up, cut document generation from hours to under 1 minute. See the project README for the reverse-engineering story and `ORIGINAL_VBA_CONTEXT.md` for the source system it replaced |
| Loan Processing & Automation System | Amortization, interest, insurance, and payment tracking for 7,000+ loan accounts, live in daily production since 2022 (original workbook confidential; see [project note](./projects/loan-processing-automation-system)) |
| Savings Interest Extractor & Interest Calculator | Automates quarterly interest calculation across 7,000+ savings and share-capital accounts, Python/Pandas/OpenPyXL (see [project note](./projects/savings-interest-extractor-calculator)) |
| Collateral Data Entry System with Print Functions | VBA/Excel tool for structured collateral data entry with automated print formatting (see [project note](./projects/collateral-data-entry-system)) |
| [Data Migration & Infrastructure Planning](./projects/data-migration-infrastructure-planning) | Tooling used for a 7,000+ account core-system migration, improving field-mapping accuracy from ~70% to 99% |

**Independent / portfolio projects**

| Project | Description |
|---|---|
| [Barangay Budget Management System](./projects/barangay-budget-management-system) | Role-based financial management with approval workflows and audit logging |
| [Cooperative Banking System Prototype](./projects/cooperative-banking-system-prototype) | Teller system covering cash management, savings, and interest |
| [Batch Financial Report Processing](./projects/batch-financial-report-processing) | Two-part VA-facing guide + tool for batch password-protected archive extraction and report consolidation, packaged with install scripts and walkthrough PDFs. Generalized from the SAMCO-specific [ATM Data Extraction & Reporting Automation](./projects/atm-data-extraction-reporting) tool into a client-agnostic product |

Some production systems ship as documentation only (no code) where the original file
contains confidential SAMCO member or financial data and couldn't be safely anonymized,
each has a short note explaining what it does and why the source isn't included. I'm
happy to walk through the architecture, share sanitized code samples, or do a live screen
recording for recruiters or hiring managers. Email me to request access.

### `vop/`, Variables of Prompting

My personal framework for structured, disciplined AI-assisted development, built from
real prompt-drift failures and progressively formalized. Includes the formal spec, a
risk/responsible-use document, and a working template.

### `cas-planning-docs/` + `cas-n8n-vop-workflow/`, Cooperative AI System (CAS)

CAS is a governance-first AI concept for cooperative environments: a workflow that checks
requests against defined policy before responding, instead of an unconstrained model
making judgment calls on its own. `cas-planning-docs/` holds the design docs (overview,
core architecture, business case & risk, validation & rollout, build log).
[`cas-n8n-vop-workflow/`](./cas-n8n-vop-workflow) is the active implementation, a
self-hosted n8n + PostgreSQL build, with Phases 0 through 4 complete (Phase 5, Hybrid
Inference + Confidence Check, in progress), tested against
a fictional dataset. The README there tracks exact build status per stage and includes
instructions to run it locally.

---

## Certifications

Google Cybersecurity Professional · Google IT Support Professional · Google AI Essentials,
verified badges: credly.com/users/alvin-piquero

## Tech Stack

Python · VBA · SQL/SQLite · PostgreSQL · PySide6 · Tkinter · n8n · ETL pipelines ·
Excel automation · PowerShell

---

## License

Shared for review and evaluation purposes. Code may not be copied or redistributed
without permission. For collaboration or employment opportunities, reach out directly.
