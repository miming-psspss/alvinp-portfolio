# ATM Data Extraction & Reporting Automation

Two Tkinter desktop tools that resolved a 3-year ATM transaction reporting backlog in a
day, replacing a manual process of opening password-protected RAR archives one by one and
copying data out by hand.

**This is the original SAMCO-specific tool.** The workflow built here was later extracted,
generalized, and re-engineered into a product-ready, client-agnostic package for VAs — see
[`batch-financial-report-processing`](../batch-financial-report-processing), which takes
the same core extraction/reporting logic and packages it with install scripts, setup docs,
and guide PDFs for someone outside SAMCO to run without any of the original context.

## What's here

**`ExtractionGUIupdated`** — batch RAR extraction tool
Points at a source folder of password-protected `.rar` archives (one per ATM/month),
extracts them in bulk via `unrar`, and organizes the output DATR (transaction) files into
a clean destination folder structure by year/month. Built and tested on Linux Fedora.

- Auto-detects RAR files across a source directory
- Handles the shared archive password (entered once, shown/hidden toggle, optionally saved
  to a local config file — not committed to this repo)
- Checks for `unrar` on startup and tells you how to install it if missing
  (`sudo dnf install unrar`)
- Threaded extraction with a live log panel and running "files extracted" counter, so it
  doesn't freeze the UI on large batches

**`Print.py`** — DATR file processor & analyzer
Takes the extracted DATR files and turns them into something reviewable: parses each
transaction file, displays them in a sortable/filterable table (year, month, per-file
totals), and exports everything to a single master CSV for reporting. Compatible with
Python 3.14 / Tcl 9+.

- Recursively loads DATR files from a folder tree
- Live preview table with search/filter and column sorting
- Transaction detail view on double-click
- One-click "Generate Master CSV" for the consolidated report
- Remembers last-used source/output paths between runs (local config, not committed)

## Why two separate tools

Extraction and reporting were split deliberately: `ExtractionGUIupdated` only needs to run
once per archive batch (and needs `unrar` + the archive password), while `Print.py` gets
run repeatedly afterward by whoever's building the report — no password or archive access
needed at that stage. Keeping them separate meant the reporting step could be handed to
someone without also handing them the extraction credentials.

## Running locally

Both are self-contained Tkinter scripts, no build step:

```bash
python3 ExtractionGUIupdated
python3 Print.py
```

Requires `unrar` on the system for the extraction step (`sudo dnf install unrar` on
Fedora; `sudo apt install unrar` on Debian/Ubuntu).

## Note on data

No sample DATR files or archives are included, since the original data is confidential
ATM transaction data from SAMCO. The screenshots in this folder show the tools running
against real (redacted) output for reference.
