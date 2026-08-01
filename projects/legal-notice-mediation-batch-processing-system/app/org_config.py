"""
Organization-level constants.

These aren't per-case data -- they're the same on every document generated
(the cooperative's name, TIN, standing authorized representative, etc.). Kept
separate from the cases table so they're edited in one place, not copied
into every row.

The values below are FICTIONAL, used for a portfolio/demo version of this
project. Replace with a real cooperative's actual details before using this
for a real deployment.
"""

ORG_CONSTANTS = {
    "coop_name": "Bayanihan Multi-Purpose Cooperative",
    "coop_name_upper": "BAYANIHAN MULTI-PURPOSE COOPERATIVE (BMPC)",
    "coop_acronym": "BMPC",
    "coop_tin": "000-000-000-000",
    "coop_cda_reg_no": "0000-00000000",
    "coop_address": "Rizal Street, Poblacion, San Isidro, Bohol",
    "coop_barangay": "Barangay Poblacion, San Isidro, Bohol",
    "coop_municipality": "San Isidro, Bohol",
    "coop_landline": "038-000-0000",
    "coop_federation": "Bohol Federation of Cooperatives (BFC)",
    "authorized_representative": "[Authorized Representative]",
    "representative_designation": "General Manager",
}
