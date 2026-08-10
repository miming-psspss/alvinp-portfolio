# Alvin Piquero | IT Automation, Systems & Business Specialist

Python and VBA automation projects built for real-world use in a financial cooperative
serving 7,000+ members, plus independent work in workflow automation, AI governance,
and productized tools.

I build end-to-end solutions from requirements and design through deployment, support,
and troubleshooting.

I turn multi-hour manual processes into workflows that run in minutes, and have
improved data migration accuracy from roughly 70% to 99% at scale.

### Selected Impact

- **7,000+ members** supported by production financial systems
- **~70% → ~99%** data-migration field-mapping accuracy
- **3-year reporting backlog → resolved in 1 day**
- **Multi-hour reporting → under 5 minutes**
- **Document generation → under 1 minute**
- Loan-processing system in daily use since **2022**

### Featured Projects

  **1. ATM Reporting Automation**
    3-year backlog → 1 day
  **2. Loan Processing System**
    7,000+ accounts | production since 2022
  **3. Data Migration System**
    ~70% → ~99% field mapping accuracy
  **4. CAS + VoP**
    Governance-aware AI workflow architecture


- **Location:** Candijay, Bohol, Philippines
- **Email:** [alvin_piquero@outlook.ph](mailto\:alvin_piquero@outlook.ph)
- **LinkedIn:** [linkedin.com/in/alvinpiquero481743254](https://linkedin.com/in/alvinpiquero481743254/)
- **Resume / CV:** [`resume/`](./resume)
- **Timezone:** PHT (UTC+8), flexible overlap with US, UK, or AU

---

## Repository Structure

```
resume/               → resume and CV (PDF)
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
| [Loan Processing & Automation System](./projects/loan-processing-automation-system) | Amortization, interest, insurance, and payment tracking for 7,000+ loan accounts, live in daily production since 2022 (original workbook confidential; see project README) |
| [Savings Interest Extractor & Interest Calculator](./projects/savings-interest-extractor-calculator) | Automates quarterly interest calculation across 7,000+ savings and share-capital accounts, Python/Pandas/OpenPyXL |
| [Collateral Data Entry System with Print Functions](./projects/collateral-data-entry-system) | VBA/Excel tool for structured collateral data entry with automated print formatting |
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

### `vop/`, `cas-planning-docs/` + `cas-n8n-vop-workflow/` — Variables of Prompting & the Cooperative AI System

These three folders form one hierarchy, in order:

1. **[`vop/`](./vop) — Variables of Prompting (VoP).** My personal framework for
   structured, disciplined AI-assisted development, built from real prompt-drift failures
   and progressively formalized. Includes the formal spec, a risk/responsible-use
   document, and a working template. VoP is the governance discipline everything below
   is built on.
2. **[`cas-planning-docs/`](./cas-planning-docs) — Cooperative AI System (CAS), the
   concept.** CAS is a governance-first AI concept for cooperative environments: a
   workflow that checks requests against defined policy before responding, instead of an
   unconstrained model making judgment calls on its own, with VoP as its governing
   discipline. Holds the design docs (overview, core architecture, business case & risk,
   validation & rollout, build log).
3. **[`cas-n8n-vop-workflow/`](./cas-n8n-vop-workflow) — the mini-test.** A scoped,
   self-hosted n8n + PostgreSQL build validating one slice of CAS end to end, against a
   fictional dataset (not real member data, not a production deployment). Phases 0
   through 6 are complete — all six workflows (query intake/scope check, RAG retrieval,
   auditor mode check, hybrid inference + confidence check, and logging) built and
   validated, with two small known limitations still open. The README there tracks exact
   build status per stage, a full canvas screenshot, and instructions to run it locally.

---

## My Engineering Philosophy

I build for **reliability**, not just functionality. Every tool and environment I create
is designed to reduce failure points and increase confidence.

This philosophy comes from years of troubleshooting:

1. **Hardware:** Learning to diagnose before replacing or disassembling components.
2. **Development environments:** Learning to distinguish toolchain problems from code problems.
3. **Production systems:** Supporting financial systems serving 7,000+ members.
4. **AI-assisted development:** VoP grew from dealing with prompt drift and AI-generated errors.

Each failure became a lesson that now influences how I design and test systems.

**I don't just solve problems. I build systems that prevent them.**

---

## Troubleshooting & Debugging Philosophy

I don't just write code. I diagnose, isolate, and resolve problems across the stack —
hardware, OS, network, application, and environment issues; testing and validating
AI-generated code against real data and edge cases; troubleshooting corrupted archives,
Excel failures, data mismatches, and workflow issues in live financial operations. My
approach is systematic isolation (logs, controlled tests, binary-search debugging,
hypothesis-driven testing) followed by preventive thinking, building safeguards against
recurring failures, not just fixing the immediate one. I maintain controlled Windows/Linux
environments to support this, so toolchain problems can be isolated from code problems
during testing.

### Real-world examples

**Development environment:**
While building a personal Android side project, repeated AI-generated fixes were creating
new errors. I isolated the problem to the development environment and resolved the
SDK, cache, and Gradle configuration instead of continuing to modify the application.

**Hardware:**
After a GPU installation caused a boot failure, I traced the recent changes and
system readings before disassembling the machine. A BIOS reset resolved the issue.

**Lesson:** Diagnose first. Gather evidence, isolate the failure, then apply the fix.

---

## Certifications

Google Cybersecurity Professional · Google IT Support Professional · Google AI Essentials,
verified badges: [credly.com/users/alvin-piquero](https://www.credly.com/users/alvin-piquero)

## Tech Stack

Python · VBA · SQL/SQLite · PostgreSQL · PySide6 · Tkinter · n8n · ETL pipelines ·
Excel automation · PowerShell

---

## License

Shared for review and evaluation purposes. Code may not be copied or redistributed
without permission. For collaboration or employment opportunities, reach out directly.
