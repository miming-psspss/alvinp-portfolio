#!/usr/bin/env bash
# Reorg script for alvinp-portfolio.
# Run this FROM THE ROOT of your local clone of the repo.
# Review with `git status` / `git diff --stat` before committing.
set -e

echo "== 1. resume/ =="
mkdir -p resume
git mv "Alvin_Piquero_Resume_AI Automation Specialist_8-1-2026.pdf" \
       "resume/Alvin_Piquero_Resume_AI_Automation_Specialist.pdf"
git mv "CV_AlvinPiquero_BusinessAnalyst.pdf" \
       "resume/CV_AlvinPiquero_BusinessAnalyst.pdf"

echo "== 2. projects/ (simple moves) =="
mkdir -p projects
git mv "ATM Data Extraction & Reporting Automation" \
       "projects/atm-data-extraction-reporting"
git mv "Barangay Budget Management System" \
       "projects/barangay-budget-management-system"
git mv "Collateral Data Entry System with Print functions" \
       "projects/collateral-data-entry-system"
git mv "Cooperative Banking System Prototype" \
       "projects/cooperative-banking-system-prototype"
git mv "Data Migration & Infrastructure Planning" \
       "projects/data-migration-infrastructure-planning"
git mv "Loan Processing & Automation System with Tool" \
       "projects/loan-processing-automation-system"
git mv "Savings Interest Extractor and Interest Calculator" \
       "projects/savings-interest-extractor-calculator"

echo "== 3. Consolidate the two 'Legal Notice' folders into one =="
# The real rebuilt app currently lives under WORKFLOW PORFOLIO/Legal Notice System.
# The top-level "Legal Notice & Mediation..." folder only has a NOTE.md pointing to it.
# Merge them so there's one project folder instead of two.
git mv "WORKFLOW PORFOLIO/Legal Notice System" \
       "projects/legal-notice-mediation-batch-processing-system"
git mv "Legal Notice & Mediation Batch Processing System/NOTE.md" \
       "projects/legal-notice-mediation-batch-processing-system/ORIGINAL_VBA_CONTEXT.md"
rmdir "Legal Notice & Mediation Batch Processing System"

echo "== 4. Batch Financial Report Processing (VA guide product) =="
git mv "WORKFLOW PORFOLIO/Batch Financial Report Processing" \
       "projects/batch-financial-report-processing"
rmdir "WORKFLOW PORFOLIO"

echo "== 5. VoP -> vop/ (lowercase, matches cas-n8n-vop-workflow naming style) =="
git mv "VoP" "vop"

echo "== 6. CAS planning docs — drop the stray Word lock file, then rename folder =="
git rm "Cooperative AI System (CAS)/~WRL0003.tmp"
git mv "Cooperative AI System (CAS)" "cas-planning-docs"

echo "== 7. Review only — not auto-removed =="
echo "database_fixed.py looks like a leftover duplicate of database.py in"
echo "projects/barangay-budget-management-system/. If it really is dead code, run:"
echo '  git rm "projects/barangay-budget-management-system/database_fixed.py"'

echo
echo "Reorg complete. cas-n8n-vop-workflow/ stays where it is (already well-named)."
echo "Next: git status, review, then:"
echo '  git add -A && git commit -m "Reorganize repo: group projects/, resume/, cas-planning-docs/, consolidate Legal Notice folders"'
