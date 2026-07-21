# Data Migration & Infrastructure Planning

Tooling built to support migrating 7,000+ savings and share capital accounts to a new
core banking system — extraction, field mapping, transformation, and validation. Iterative
validation with this tooling improved field-mapping accuracy from roughly 70% to 99%
across the full migration.

A separate Python desktop lookup tool (not included in this repo) cut member ID lookup
time by 90%+ (60s → under 5s) for staff during the migration, built for non-technical
users on the new core system.

**Note:** shipped as code only. The original sample data (`SAMCOLoanEntry.xlsx` and
related files) contained real member records, so it's excluded pending a synthetic
replacement dataset.

- `diagnosticsTool.py` — pre-migration data diagnostics
- `IMAGEStoPDF.py` — converts scanned loan document images to PDF
- `PDFtoCSV.py` — extracts tabular data from PDF documents
- `Missing_ID.py` — flags records missing required ID fields
- `SAMCO_LOAN_ENTRY_with_imageRotation.py` — loan entry tool with automatic image
  rotation correction for scanned documents
