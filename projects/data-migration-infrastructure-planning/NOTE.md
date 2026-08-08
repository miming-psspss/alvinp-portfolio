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

The full migration pipeline and source ledgers are not included here, as they contain
confidential member and financial data.
