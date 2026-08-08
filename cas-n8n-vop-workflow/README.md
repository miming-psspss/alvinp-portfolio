# CAS — n8n VoP Governance Workflow (Work in Progress)

## What this is

A test-environment build validating a "CAS" (Cooperative AI System) governance concept: a
workflow that checks requests against defined policies before responding, instead of an
unconstrained AI making judgment calls on its own.

This build runs entirely against **fictional data** (10 fictional members, 4 staff, 3
board members, 8 policies). It is a personal/independent proof-of-concept, not a system
deployed in production anywhere.

## Status: Phase 6 of 8 complete — Workflows 1–6 built and validated end to end

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
6. **Phase 5 — Workflow 5, Hybrid Inference + Confidence Check** — done. Draft Answer
   wired to a local Ollama model (llama3.2) after a cost-driven pivot away from the
   Anthropic API. Confidence is defined as retrieval/policy-match certainty, not LLM
   self-reported confidence: exactly one clearly-applicable policy and member record
   retrieved = confident and deliverable; zero, multiple, or conflicting matches = not
   confident, routes to escalate-Compliance. A genuine tenure-comparison reasoning bug
   was found and fixed via prompt restructuring; a delinquency-reasoning inconsistency
   was identified and left open as a documented model limitation rather than silently
   patched over.
7. **Phase 6 — Workflow 6, Logging** — done. A `query_log` Postgres table and a Merge
   node unify all nine terminal Decision outcomes into one logging path. All nine
   branches validated against live data (one, restricted-loan-eligibility, via pinned
   test data — no fictional member happens to fall in that tenure band). Three real bugs
   were found and fixed during branch-by-branch validation, including a three-part
   compounding bug surfaced only by testing a nonexistent member.
8. **Phase 7** — not yet scoped.
9. **Phase 8 — Wrap-up** — not started. Must include revisiting the Treasurer/Chairperson
   BOD-ceiling testing deferred in Phase 4, plus the open items below.

## Known limitations (as of Phase 6 close-out)

- **Double-item-per-run logging** — every query currently writes two rows to
  `query_log` instead of one. Root cause not yet fixed; noted rather than hidden.
- **Shared `escalated_compliance` label** — `Decision - Escalate Unclear Policy` and
  `Decision - Escalate Confidence` share one status label, distinguished only by
  free-text reason. Deliberate for now, not yet reconsidered.
- **Treasurer/Chairperson BOD-ceiling paths untested** — see Phase 4 note above.

See the full canvas in [`screenshots/full-workflow-canvas-phases-2-6.png`](./screenshots/full-workflow-canvas-phases-2-6.png).

**Note on this repo's workflow export:** the full pipeline — 32 nodes covering Query
Intake through Auditor Mode Check, Hybrid Inference, and Logging (i.e. all of Workflows
2–6) — is committed as a single n8n export,
[`workflows/cas-vop-full-pipeline.json`](./workflows/cas-vop-full-pipeline.json), since
that's how it's actually built: one continuous canvas rather than six separately-saved
n8n workflow objects. Import it into your own n8n instance (Workflows → Import from File)
to inspect the full logic end to end.

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

Once running, import `workflows/cas-vop-full-pipeline.json` into your n8n instance via
the n8n UI (Workflows → Import from File) to inspect the full logic end to end.
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
