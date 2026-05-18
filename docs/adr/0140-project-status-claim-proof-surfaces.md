# ADR-0140: Project Status Claim And Proof Surfaces

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0138 and ADR-0139 make the base and chain object-language surfaces visible
from `python -m autarkic_systems.project_status`. That proves the aggregate
status can see whether current claim and proof artifacts inhabit the declared
language.

It does not, however, directly show whether the base transition claim examples
evaluate as expected or whether the base transition proof certificates verify.
Those checks already exist in `autarkic_systems.claim_manifest` and
`autarkic_systems.proof_certificates`, and ADR-0134/ADR-0135 give them direct
CLIs. The project status report should summarize those lower surfaces instead
of making operators run separate commands to know whether the base claim and
proof layer is green.

## Decision

Add two base transition summaries to project status JSON and text:

- `transition_claims`, summarizing the transition claim manifest evaluator;
- `transition_proof_certificates`, summarizing the proof-certificate
  verifier over the same transition claim and certificate manifests.

The aggregate `accepted` field will require both summaries to be accepted.
The existing `--transition-claims` and `--transition-certificates` path
overrides will feed both the object-language summary and these semantic
claim/proof summaries.

Project status JSON will bump from `schema_version: 11` to
`schema_version: 12`.

## Success Criteria

- Red project-status tests fail before implementation because JSON still
  reports schema version `11`, omits `transition_claims`, omits
  `transition_proof_certificates`, and text omits the new summary lines.
- JSON reports the accepted transition claim surface with claim count,
  example count, matched count, result count, failed subjects, and per-example
  results.
- JSON reports the accepted transition proof-certificate surface with claim
  count, certificate count, result count, failed subjects, and per-certificate
  results.
- A mismatched transition claim example rejects the aggregate project status
  and renders a compact failed-subject pointer in text.
- A rejected proof certificate rejects the aggregate project status and renders
  a compact failed-subject pointer in text.
- Full repository tests remain green.

## Consequences

The first status command now distinguishes three lower layers:

- semantic claim-example evaluation;
- semantic proof-certificate verification;
- object-language membership for the claim/proof surface.

No new claim semantics, proof rules, source-status rules, evidence bundles, or
runtime behavior are introduced.

## Test Plan

- Red: add project-status JSON/text tests for `transition_claims` and
  `transition_proof_certificates`, including rejected claim/proof fixture
  paths.
- Green: reuse `validate_transition_claim_project` and
  `validate_proof_certificate_project`, convert their existing payloads into
  compact status summaries, and add text rendering helpers.
- Regression: run focused project-status tests, project status text/JSON,
  direct claim/proof JSON CLIs, `py_compile`, `git diff --check`, and the full
  default test suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` with focused tests in
`tests/test_project_status_report.py`.

The red test run executed 56 project-status tests and failed because project
status still reported `schema_version: 11`, omitted the transition claim and
proof-certificate summaries, omitted compact accepted text lines, and did not
reject broken claim/proof fixtures through the aggregate status.

The green implementation reuses `validate_transition_claim_project` and
`validate_proof_certificate_project`, converts their existing structured
payloads into `transition_claims` and `transition_proof_certificates`
summaries, and renders compact accepted/rejected text plus
`Claim/proof failures:` failed-subject lines.

Project status JSON now reports `schema_version: 12`, `accepted: true`,
13 transition claims, 35 matched examples, 13 proof certificates, and empty
claim/proof failed-subject lists on the checked-in manifests.

Verification passed: focused project-status tests ran 56 tests;
`python -m autarkic_systems.project_status` rendered the new claim/proof
summary lines; `python -m autarkic_systems.project_status --format json`
reported `schema_version: 12`; direct claim and proof JSON CLIs were accepted;
`py_compile` passed for the touched Python files; and
`python -m unittest discover` passed 635 tests.
