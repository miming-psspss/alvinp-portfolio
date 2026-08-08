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

## Screenshots

Part 2 (consolidation) first-run setup, showing the dependency check before it runs and
completing:

![Part 2 first-run setup check](<./_PART2 Batch Financial Report Processing for VAs_/screenshot/Screenshot 2026-08-09 023308.png>)
![Part 2 first-run setup complete](<./_PART2 Batch Financial Report Processing for VAs_/screenshot/Screenshot 2026-08-09 023345.png>)

The consolidator tool itself, before and after loading report files (masked account/card
numbers, on by default):

![Part 2 consolidator, empty state](<./_PART2 Batch Financial Report Processing for VAs_/screenshot/Screenshot 2026-08-09 023414.png>)
![Part 2 consolidator, loaded and masked data](<./_PART2 Batch Financial Report Processing for VAs_/screenshot/Screenshot 2026-08-09 023715.png>)

Part 1 (extraction), captured from a screen-recording inside a clean Windows 11 VM
(QEMU/KVM) — set up specifically to test the install/setup flow the way a non-technical
VA would actually experience it, on a machine with nothing pre-installed:

![Part 1 first-run setup, checking dependencies](<./_PART1 v2 Batch Financial Report Processing_/screenshot/Screenshot From 2026-07-20 21-37-02.png>)
![Windows UAC prompt for the installer](<./_PART1 v2 Batch Financial Report Processing_/screenshot/Screenshot From 2026-07-20 21-38-18.png>)
![Screencast library on the Linux host used to record the VM session](<./_PART1 v2 Batch Financial Report Processing_/screenshot/Screenshot From 2026-07-20 21-38-39.png>)
![Setup detecting an existing Python install, installing 7-Zip](<./_PART1 v2 Batch Financial Report Processing_/screenshot/Screenshot From 2026-07-20 21-38-47.png>)
![Setup complete, all dependencies installed](<./_PART1 v2 Batch Financial Report Processing_/screenshot/Screenshot From 2026-07-20 21-38-54.png>)
![Extraction tool, Configuration tab](<./_PART1 v2 Batch Financial Report Processing_/screenshot/Screenshot From 2026-07-20 21-39-01.png>)
![Extraction tool, password field masked before a processing run](<./_PART1 v2 Batch Financial Report Processing_/screenshot/Screenshot From 2026-07-20 21-41-38.png>)
![Extraction tool, run completed successfully](<./_PART1 v2 Batch Financial Report Processing_/screenshot/Screenshot From 2026-07-20 21-41-22.png>)

*(These are frames pulled from the VM screencast rather than clean stills, so the VM
window chrome and desktop are visible — left in deliberately as evidence the install flow
was actually tested end-to-end on a bare Windows 11 environment, not just run on my own
dev machine.)*

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
