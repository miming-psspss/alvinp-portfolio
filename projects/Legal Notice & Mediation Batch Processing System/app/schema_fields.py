"""
Canonical case fields, with human-readable labels and common header aliases
used to auto-guess a mapping from an arbitrary Excel header row.

This is the single source of truth for "what fields exist on a case" --
both the import mapping screen and (indirectly) the templates draw from
these names.
"""

# field_key -> (label shown in the mapping UI, required?, [aliases for auto-matching])
SCHEMA_FIELDS = {
    "case_no":            ("Case No.",              True,  ["case no", "case no.", "case number", "case #"]),
    "member_name":         ("Member Name",           True,  ["member", "member-patron's", "member patron", "name", "name of borrower", "borrower", "member name"]),
    "billing_address":     ("Billing Address",       False, ["address", "billing address", "residence"]),
    "age":                 ("Age",                   False, ["age"]),
    "gender":              ("Gender",                False, ["gender", "sex"]),
    "civil_status":        ("Civil Status",          False, ["civil status", "marital status"]),
    "occupation":          ("Occupation",            False, ["occupation", "livelihood", "livelihood/occupation"]),
    "contact_number":      ("Contact Number",        False, ["contact", "contact number", "mobile", "phone"]),
    "email":               ("Email",                 False, ["email", "email/social media address", "social media"]),
    "voucher_number":      ("Voucher Number",        False, ["voucher", "voucher number", "cv no.", "cash voucher no."]),
    "kind_of_loan":        ("Kind of Loan",          False, ["kind of loan", "loan type", "type of loan"]),
    "principal":           ("Principal",             False, ["principal", "loan granted", "amount granted", "loan granted|principal"]),
    "date_granted":        ("Date Granted",          False, ["date granted"]),
    "maturity_date":       ("Maturity Date",         False, ["maturity date"]),
    "end_of_calculation":  ("End of Calculation",    False, ["end of calculation", "computation cut-off date"]),
    "number_of_days":      ("Number of Days",        False, ["number of days", "no. of days"]),
    "amortization":        ("Amortization",          False, ["amortization"]),
    "balance":             ("Balance",               False, ["balance"]),
    "past_due_interest":   ("Past Due Interest",     False, ["past due interest", "pdi", "pastdue"]),
    "penalty":             ("Penalty",               False, ["penalty"]),
    "less_total_pdi":      ("Less Total PDI",        False, ["less total pdi"]),
    "less_total_pen":      ("Less Total Penalty",    False, ["less total pen", "less total penalty"]),
    "total_amount_due":    ("Total Amount Due",      False, ["total amount due", "total payable", "total due"]),
    "mediator":            ("Mediator",              False, ["mediator"]),
    "status":              ("Status",                False, ["status"]),
    "authorized_representative": ("Authorized Representative", False, ["authorized representative", "requesting party rep"]),
    "representative_designation": ("Representative Designation", False, ["designation"]),
    "notice_date":         ("Notice Date",           False, ["notice date", "date"]),
    "conference_round":    ("Conference Round",      False, ["conference round", "mediation conference"]),
    "conference_date":     ("Conference Date",       False, ["conference date"]),
    "conference_time":     ("Conference Time",       False, ["conference time"]),
    "conference_venue":    ("Conference Venue",      False, ["conference venue", "venue"]),
    "first_appearance_date": ("First Appearance Date", False, ["first appearance date", "1st date"]),
    "reset_date":          ("Reset Date",            False, ["reset date", "re-set date"]),
    "reset_reason":        ("Reset Reason",          False, ["reset reason", "reason for re-setting"]),
    "mediation_result":    ("Mediation Result",      False, ["mediation result", "result"]),
    "failure_reason":      ("Failure Reason",        False, ["failure reason", "failed mediation due to"]),
    "action_taken":        ("Action Taken",          False, ["action taken"]),
    "returned_reason":     ("Returned Reason",       False, ["returned without action due to"]),
    "agreement_date":      ("Agreement Date",        False, ["agreement date"]),
    "payment_schedule":    ("Payment Schedule",      False, ["payment schedule"]),
    "report_date":         ("Report Date",           False, ["report date"]),
    "comments":            ("Comments",              False, ["comments", "comments & suggestions"]),
}

REQUIRED_FIELDS = [key for key, (_, required, _) in SCHEMA_FIELDS.items() if required]


def guess_field_for_header(header_text: str):
    """Returns the best-guess field_key for a raw Excel header string, or None."""
    if not header_text:
        return None
    normalized = str(header_text).strip().lower().rstrip(":")
    for field_key, (label, _, aliases) in SCHEMA_FIELDS.items():
        candidates = [field_key.replace("_", " "), label.lower()] + aliases
        if normalized in candidates:
            return field_key
    # loose contains-match as a fallback (only for reasonably specific candidates,
    # so short generic words like "age" or "id" can't accidentally match unrelated columns)
    for field_key, (label, _, aliases) in SCHEMA_FIELDS.items():
        candidates = [field_key.replace("_", " "), label.lower()] + aliases
        for c in candidates:
            if len(c) < 4:
                continue
            if c in normalized or normalized in c:
                return field_key
    return None
