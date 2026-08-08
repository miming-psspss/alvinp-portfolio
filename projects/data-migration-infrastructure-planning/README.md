# Data Migration & Infrastructure Planning

Diagnostics and planning tooling built for a 7,000+ account core-system migration,
used to identify why source PDFs/ledgers were failing extraction (missing packages,
missing OCR binaries, bad file paths) before they silently produced bad field mappings.
Part of the broader migration effort that improved field-mapping accuracy from
roughly 70% to 99%.

- `diagnosticsTool.py` — standalone environment/dependency checker (PDF presence,
  required Python packages, Tesseract OCR availability) run before each extraction
  pass, so failures surface as a clear checklist instead of a stack trace mid-migration.
- `PROGRESS REPORT.docx` — write-up of the migration effort and accuracy improvement.

## Screenshots

The SAMCO Loan Entry System used during migration — document image on the left for
reference against the entry form on the right, empty state:

![Loan entry system, empty state](<./screenshots/Screenshot 2026-08-09 041523.png>)

Loaded against real migration data — 7,259 client records pulled in, source document
image manually redacted before capture to remove borrower information:

![Loan entry system, 7,259 records loaded, source image redacted](<./screenshots/Screenshot 2026-08-09 041719.png>)

The full migration pipeline and source ledgers are not included here, as they contain
confidential member and financial data.