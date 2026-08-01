# CAS \u2014 n8n VoP Governance Workflow (Work in Progress)

## What this is

A test-environment build validating a "CAS" (Cooperative AI System) governance concept: a workflow that checks requests against defined policies before responding, instead of an unconstrained AI making judgment calls on its own.

This build runs entirely against **fictional data** (10 fictional members, 4 staff, 3 board members, 8 policies). It is a personal/independent proof-of-concept, not a system deployed in production anywhere.

## Status: In Progress (Phase 2 of 6)

The full design covers 6 workflow stages:

1. Environment Provisioning \u2014 **done**
2. Query Intake & VoP Flow Scope Check \u2014 **in progress** (see `workflows/02-query-intake-vop-scope-check.json`)
3. RAG Retrieval \u2014 not yet built
4. Auditor Mode Check \u2014 not yet built
5. Hybrid Inference + Confidence Check \u2014 not yet built
6. Logging (Shadow Mode) \u2014 not yet built

Workflow 2 currently includes 20 nodes covering: manual trigger, requester/member
lookup (branched by requester type via an If node, then merged), policy retrieval
and matching against the fictional policy set, and multiple named decision branches
(Delinquency Block, Escalate to BOD, Cross-Member Block, Tenure Restriction, Loan
Eligibility Restriction, Escalate Unclear Policy, and a default Proceed path).

## Architecture

- **n8n** (self-hosted via Docker Compose, not n8n Cloud)
- **PostgreSQL** \u2014 one database for n8n's internal state, one for the fictional test dataset (`cas_test`: members, staff, board_of_directors, policies_index)
- Retrieval is currently direct structured SQL lookup rather than embeddings/vector search, by design at this stage

## Running it locally

```bash
git clone https://github.com/miming-psspss/alvinp-portfolio.git
cd alvinp-portfolio/cas-n8n-vop-workflow
cp .env.example .env   # then fill in your own values
docker compose up -d
```

Once running, import `workflows/02-query-intake-vop-scope-check.json` into your n8n
instance via the n8n UI (Workflows \u2192 Import from File) to inspect the logic.
`cas-schema.sql` documents the Postgres schema for the fictional test dataset.

Note: the credential reference embedded in the workflow JSON points to a local
Postgres connection by name only (no password or connection string is included) \u2014
you'll need to set up your own Postgres credential in n8n after import.

## Why this exists

Built as a scoped, low-risk way to validate a governance-aware AI workflow concept
before considering anything similar for real use \u2014 keeping AI-assisted decisions
constrained by explicit, auditable policy rules rather than open-ended judgment calls.
