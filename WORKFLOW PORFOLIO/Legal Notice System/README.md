# Legal Notice & Mediation Batch Processing System

Python/PySide6 rebuild of the original Excel/VBA mediation case system.
All 11 real document types from the original file are wired up (Statement of
Account, Mediation Forms 2-9, Envelope). Some fields (conference scheduling,
mediation outcomes) are still blank placeholders pending the actual process
workflow -- see the field maps for what's mapped vs. still open.

## Setup
```
pip install -r requirements.txt
python main.py
```

Once the app is open, click **"Import Cases from Excel..."** at the top and select any
Excel file with your case data. A mapping screen will open where you:
- Pick which sheet has the data (auto-detected if there's only one obvious candidate)
- Confirm/adjust which row is the header row (auto-guessed)
- Match each of your columns to the fields the program needs (auto-suggested where the
  wording is close enough, e.g. "Loan Amt" won't auto-match "Principal" but you can map
  it manually in one click)

Only **Case No.** and **Member Name** are required to import; everything else is optional.
Your confirmed mapping is remembered for that exact header shape, so re-importing a
fresh export of the same spreadsheet format skips the manual step next time.

## How it's organized
- `app/db.py` — SQLite schema (cases, generation_log) and data access
- `app/schema_fields.py` — single source of truth for what fields a case has,
  their labels, and alias keywords used to auto-suggest column matches
- `app/import_mapping.py` — reads any sheet/header row, suggests a mapping,
  performs the import, and remembers confirmed mappings per header shape
- `app/mapping_dialog.py` — the PySide6 dialog where the user confirms/adjusts
  the column mapping before anything is imported
- `app/generator.py` — generic renderer: reads a field-map JSON, validates
  required fields, renders the matching docx template. No document-type-specific
  code -- adding a new document type means adding a JSON + a template, not new code.
- `app/org_config.py` — organization-level constants (TIN, standing authorized
  representative, etc.) merged into every generated document automatically
- `templates/*.docx` — Jinja-style docx templates, editable by non-programmers
- `templates/field_maps/*.json` — maps template variables to case data columns,
  and lists which fields are required before generation is allowed
- `main.py` — PySide6 GUI: import cases, search/select a case, pick a document
  type, generate, see per-case generation history

## Adding a new document type
1. Build a docx template with `{{ variable }}` placeholders (see `build_template.js`
   pattern, or just edit in Word).
2. Add `templates/field_maps/<key>.json` with `document_type`, `template_file`,
   `required_fields`, and `field_map`.
3. Add the key to `AVAILABLE_DOCUMENT_TYPES` in `main.py`.
No changes to `generator.py` needed.

## Packaging to a Windows .exe
This needs to run on a Windows machine (or via a Windows CI runner) since
PyInstaller builds for the OS it runs on:
```
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "templates;templates" main.py
```
