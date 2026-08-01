# Batch Financial Report Processing

A two-part, VA-facing product for batch-extracting password-protected report archives and
consolidating them into a single master report, packaged for someone with no technical
background to install and run on a Windows machine.

**Origin:** this is a generalized, client-agnostic rebuild of the workflow originally
built for SAMCO in
[`atm-data-extraction-reporting`](../atm-data-extraction-reporting). The core
extraction/reporting logic is the same; what changed is everything around it, packaging,
plain-language install guides, `.bat` setup scripts, and removal of any SAMCO-specific
paths or assumptions, so it can be handed to a VA on any client's data.

## Structure

- **`_PART1 v2 Batch Financial Report Processing_/`** — extraction stage. Pulls report
  files out of password-protected archives in bulk.
  - `financial_report_extractor_part1.py` — the extraction script
  - `install_setup.bat` / `run_extractor.bat` — one-time setup and run scripts (no Python
    experience needed, instructions are in `INSTALLATION_STEPS.txt`)
  - `Guide_Proposal.pdf`, `VA_Guide_Part1_Extraction.pdf`, `Workflow_Outline.pdf` — the
    client-facing pitch, the VA walkthrough, and a visual outline of the process

- **`_PART2 Batch Financial Report Processing for VAs_/`** — consolidation stage. Takes
  the extracted files from Part 1 and merges them into one master report.
  - `financial_report_consolidator_part2.py` — the consolidation script
  - `install_setup_part2.bat` / `run_consolidator.bat` — same pattern as Part 1
  - `Guide_Proposal_Part2.pdf`, `VA_Guide_Part2_Consolidation.pdf`,
    `Workflow_Outline_Part2.pdf` — same pattern as Part 1

## Why two parts

Same reasoning as the original ATM tool: extraction needs the archive password,
consolidation doesn't. Splitting them means the person doing the day-to-day report
building never needs archive-level access.
