"""
Generic document generator.

Replaces the VBA FeedForm subroutine. Instead of one hardcoded Select Case
block per document type, this reads a field-map JSON and renders whichever
docx template it points to. Adding a new document type means adding a new
JSON file and a new docx template -- no code changes.
"""
import json
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate

from app.org_config import ORG_CONSTANTS

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
FIELD_MAPS_DIR = TEMPLATES_DIR / "field_maps"
OUTPUT_DIR = BASE_DIR / "output"


class ValidationError(Exception):
    """Raised when a case is missing fields a document type requires."""


def load_field_map(document_type_key: str) -> dict:
    path = FIELD_MAPS_DIR / f"{document_type_key}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No field map for '{document_type_key}'. This document type "
            "isn't wired up yet -- add a field map + template before using it."
        )
    with open(path) as f:
        return json.load(f)


def validate_case(case: dict, field_map: dict) -> list[str]:
    """Returns a list of missing/blank required fields. Empty list = OK to generate."""
    missing = []
    for field in field_map.get("required_fields", []):
        value = case.get(field)
        if value is None or str(value).strip() == "":
            missing.append(field)
    return missing


def _format_value(key: str, value):
    if value is None:
        return ""
    if key in ("principal", "amortization", "balance", "less_total_pdi",
               "less_total_pen", "total_amount_due"):
        try:
            return f"{float(value):,.2f}"
        except (TypeError, ValueError):
            return str(value)
    return str(value)


def generate_document(case: dict, document_type_key: str) -> Path:
    field_map = load_field_map(document_type_key)

    missing = validate_case(case, field_map)
    if missing:
        raise ValidationError(
            f"Case {case.get('case_no')} is missing required fields: {', '.join(missing)}"
        )

    template_path = TEMPLATES_DIR / field_map["template_file"]
    doc = DocxTemplate(template_path)

    context = dict(ORG_CONSTANTS)  # org-wide constants first, case fields can still override
    context.update({
        tpl_var: _format_value(tpl_var, case.get(case_field))
        for tpl_var, case_field in field_map["field_map"].items()
    })
    doc.render(context)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = str(case.get("member_name", "unknown")).replace(" ", "_").replace("/", "-")
    out_path = OUTPUT_DIR / f"{field_map['document_type'].replace(' ', '_')}_{case['case_no']}_{safe_name}_{timestamp}.docx"
    doc.save(out_path)
    return out_path
