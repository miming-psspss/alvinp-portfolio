# Alvin Piquero — IT Automation, Systems & Business Specialist

Python and VBA automation projects built for real-world use in a financial cooperative
serving 7,000+ members, plus independent projects extending into workflow automation,
AI governance, and productized tools. I build end-to-end: requirements, design,
deployment, support, and the environments that make all of it work.

I turn multi-hour manual processes into workflows that run in minutes, and have
improved data migration accuracy from roughly 70% to 99% at scale.

- **Location:** Candijay, Bohol, Philippines
- **Email:** alvin_piquero@outlook.ph
- **LinkedIn:** [linkedin.com/in/alvinpiquero481743254](https://www.linkedin.com/in/alvinpiquero481743254/)
- **Resume / CV:** see [`resume/`](./resume)
- **Timezone:** PHT (UTC+8), flexible overlap with US, UK, or AU

---

## My Engineering Philosophy

I build for **reliability**—not just functionality. Every tool, framework, and
environment I create serves one purpose: **reducing failure points and increasing
confidence.**

This philosophy comes from years of real-world debugging:

1. I've fixed hardware issues (a GPU that wouldn't boot taught me to start with the
   simplest fix—a BIOS reset—before tearing anything apart).
2. I've fixed environment issues (Android Studio's build loops taught me to debug the
   toolchain, not just the code).
3. I've fixed production issues (SAMCO's 7,000-member systems taught me to build for
   stability under real pressure).
4. I've fixed AI-generated issues (VoP was born from prompt-drift failures that kept
   creating new errors instead of solving them).

Each failure taught me something. Each fix made me better. And each lesson is now
built into:

- **My hardware:** A reliable PC with dual monitors for real-time output checking,
  plus dual-boot capability for cross-environment testing.
- **My frameworks:** VoP for disciplined, governance-first AI-assisted development.
- **My systems:** Production tools that have run for years without major failures.
- **My portfolio:** Honest documentation of what works—and what I've learned.

**I don't just solve problems. I build systems that prevent them.**

---

## Troubleshooting & Debugging Philosophy

Every system in this portfolio is built on a foundation of deep technical
troubleshooting. I don't just write code—I diagnose, isolate, and resolve problems
at every layer of the stack.

**What this means in practice:**

- **System-level diagnostics:** I troubleshoot hardware, OS, network, and application
  issues. When something breaks, I find the root cause—not just the symptom.

- **Verifying AI-generated code:** AI is powerful, but it hallucinates. I test,
  validate, and fix AI output before it reaches production. I don't trust code
  blindly—I verify it against edge cases and real data.

- **Production incident response:** At SAMCO, I maintained systems running daily for
  7,000+ members. When issues arose (corrupted archives, Excel crashes, data
  mismatches), I diagnosed and resolved them under pressure, often with no external
  support.

- **Systematic isolation:** I use binary-search debugging, log analysis, and
  hypothesis-driven testing to narrow down problems—whether it's a VBA macro,
  a Python script, or an n8n workflow.

- **Preventive thinking:** I don't just fix bugs—I ask *"What else could break?"*
  and build safeguards. This is why SAMCO's loan processing has run smoothly since 2022.

**Real-world example — Hardware:**
When I installed a new GPU, the system failed to boot. I nearly did a full motherboard
teardown. Instead, I stopped, traced back my recent changes, and checked the
motherboard's voltage readings. I realized the new PSU wasn't delivering enough
power *as detected by the motherboard*—even though it should have been sufficient
on paper. The fix wasn't hardware replacement—it was a simple BIOS reset that
recalibrated the power detection.

**Lesson:** Always start with the simplest hypothesis. Check recent changes first.
Gather data before taking things apart. Diagnose before you disassemble.

**Real-world example — Development environment:**
While building an Android app login page, I hit a wall—errors kept cycling, no fix
worked, and AI-generated solutions just branched out into new errors. I restarted
my PC, even considered switching operating systems. The real issue? It wasn't the
code—it was the environment. Android Studio's build system had a bug that no amount
of code changes could fix. Once I stopped debugging the *code* and started debugging
the *environment* (clearing caches, checking SDK versions, fixing Gradle), the build
worked.

**Lesson:** Know the difference between a code bug and an environment bug. Code bugs
are local. Environment bugs affect everything. Don't let AI (or yourself) keep
generating code when the real problem is the toolchain.

**Debugging is not a fallback—it's my first principle.** It's what allows me to work
independently, trust my tools, and deliver reliable systems.

---

## Work Environment & Tools

I don't just write code—I build the environment to write code effectively.

**Hardware:**
- Custom-built PC optimized for development work
- Dual-monitor setup for simultaneous code/output verification and log monitoring
- Multi-boot capability (Windows/Linux) to test across operating systems
- Reliability-focused component selection (I've learned the hard way what fails)

**Why this matters:**
- I can test across environments before deployment
- I can monitor outputs and logs in real-time without context-switching
- I'm not slowed down by hardware failures or underpowered systems
- I can reproduce issues in isolated OS environments

**This investment in my tools reflects my philosophy:** A reliable engineer needs a
reliable workspace. I built mine to match the standards I apply to my code.

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