# CAS — n8n VoP Governance Workflow (Work in Progress)

## What this is

A test-environment build validating a "CAS" (Cooperative AI System) governance concept: a
workflow that checks requests against defined policies before responding, instead of an
unconstrained AI making judgment calls on its own.

This build runs entirely against **fictional data** (10 fictional members, 4 staff, 3
board members, 8 policies). It is a personal/independent proof-of-concept, not a system
deployed in production anywhere.

## Status: Phase 5 of 8 (Phases 0–4 complete)

1. **Phase 0 — Environment Provisioning** — done. Docker + n8n + Postgres, host/VM parity.
2. **Phase 1 — Data Layer** — done. Fictional dataset (members, staff,
   board_of_directors, policies_index) imported into its own Postgres database, separate
   from n8n's internal persistence.
3. **Phase 2 — Workflow 2, Query Intake & VoP Flow Scope Check** — done. Requester lookup
   branches three ways (member / staff / BOD, each in its own Postgres table), merges with
   the target member's record, then routes through a Switch node enforcing policies P-01
   through P-05 (loan eligibility, delinquency block, tenure restriction, cross-member
   access, BOD escalation). Every branch ends in a Decision node logging
   `{decision, reason}`. Tested against all 10 fictional member profiles plus negative and
   regression cases. See `workflows/02-query-intake-vop-scope-check.json`.
4. **Phase 3 — Workflow 3, RAG Retrieval** — done. Per the project's VoP standards,
   retrieval is a keyword-to-policy match (Code node) against structured Postgres lookup,
   not embeddings/vector search, appropriate to the current scale (8 policies, ~15
   members). All 5 keyword paths verified against live data; P-05's path is confirmed
   structurally unreachable by design (Workflow 2 always intercepts "restructur" queries
   first), documented as harmless rather than treated as a bug.
5. **Phase 4 — Workflow 4, Auditor Mode Check** — done for its core objective. P-06
   required no new work (already covered by Workflow 3's escalation node). P-08
   (role-based query boundaries) required extending requester lookup to a full
   member/staff/BOD three-way branch, then built and tested on both the pass path
   (Frontline staff) and the block path (Secretary/BOD). Treasurer and Chairperson
   ceiling testing was deliberately scoped out for this pass — Secretary has the
   narrowest BOD ceiling and functionally represents BOD interests for
   cooperative-operations queries, so the Secretary block path is treated as sufficient
   proof the mechanism works. Carried forward as an explicit open item for Phase 8.
6. **Phase 5 — Workflow 5, Hybrid Inference + Confidence Check** — next up. Confidence is
   defined as retrieval/policy-match certainty, not LLM self-reported confidence: exactly
   one clearly-applicable policy and member record retrieved = confident and deliverable;
   zero, multiple, or conflicting matches = not confident, routes to escalate-Compliance.
7. **Phase 6 — Workflow 6, Logging (Shadow Mode)** — not yet built. Beyond passive
   logging, this will include a per-run tally by outcome type and an explicit
   `FAILED_TRAP_BATCH` flag if a batch of 10+ trap questions produces zero blocks or
   escalations combined.
8. **Phase 7** — not yet scoped.
9. **Phase 8 — Wrap-up** — not started. Must include revisiting the Treasurer/Chairperson
   BOD-ceiling testing deferred in Phase 4, plus any other open items carried forward from
   earlier phases (see the build log for the full list).

**Note on this repo's workflow exports:** only Workflow 2's JSON is currently checked in
(`workflows/02-query-intake-vop-scope-check.json`). Workflows 3 and 4 are built and tested
in the local n8n instance per the build log, but not yet exported/committed here — that
export is still pending.

## Architecture

- **n8n** (self-hosted via Docker Compose, not n8n Cloud)
- **PostgreSQL** — two separate databases: one for n8n's own internal state (`n8n_db`),
  one for the fictional test dataset (`cas_test`: members, staff, board_of_directors,
  policies_index). Kept separate after an early build mistake merged them (see the build
  log for the fix).
- Retrieval is direct structured SQL lookup rather than embeddings/vector search — a
  deliberate, stated decision for this dataset size (8 policies, ~15 members), not a
  placeholder for something more sophisticated later without cause.

## Running it locally

```bash
git clone https://github.com/miming-psspss/alvinp-portfolio.git
cd alvinp-portfolio/cas-n8n-vop-workflow
cp .env.example .env   # then fill in your own values
docker compose up -d
```

Once running, import `workflows/02-query-intake-vop-scope-check.json` into your n8n
instance via the n8n UI (Workflows → Import from File) to inspect the logic.
`cas-schema.sql` documents the Postgres schema for the fictional test dataset.

Note: the credential reference embedded in the workflow JSON points to a local
Postgres connection by name only (no password or connection string is included) —
you'll need to set up your own Postgres credential in n8n after import.

## Why this exists

Built as a scoped, low-risk way to validate a governance-aware AI workflow concept
before considering anything similar for real use — keeping AI-assisted decisions
constrained by explicit, auditable policy rules rather than open-ended judgment calls.

Workflow 2 (query intake/scope check) and Workflow 4 (Auditor Mode check) aren't separate
inventions bolted onto n8n — they're VoP Flow and Auditor Mode, the same governance
framework used across this portfolio's other projects, made literal and executable as
workflow nodes rather than a process a person follows by hand.
