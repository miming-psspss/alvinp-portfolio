# ATM Data Extraction & Reporting Automation

Resolved a 3-year ATM transaction reporting backlog at SAMCO in a single day.
`atm_extraction_gui.py` opens a batch of password-protected archives (RAR/ZIP/7Z/TAR),
finds the target report files inside, and consolidates them into structured reports —
cutting a multi-hour manual process down to under 5 minutes.

**Note:** this copy has had the real archive password and local file paths removed —
set your own values in the `rar_password`, `default_source`, and `default_dest` fields
before running.

- `atm_extraction_gui.py` — Tkinter GUI for batch archive extraction
- `Print.py` — report printing/formatting utility
