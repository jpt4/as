# ADR-0202: Project Status Sequence Language

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0201 added an explicit object language for network-sequence claims. The
aggregate project-status command still reports only the base transition and
transition-chain language surfaces.

That means project status can report accepted while ignoring a missing or
malformed `language/network_sequence_claim_language.json`, even though
sequence evidence and sequence claims are now first-class status surfaces.

## Decision

Add the network-sequence claim language to `autarkic_systems.project_status`:

- validate `language/network_sequence_claim_language.json`;
- expose `sequence_language` in JSON;
- include sequence language acceptance in aggregate acceptance;
- render sequence language in default text output;
- include sequence-language failed subjects in the language-failure section;
- add a CLI `--sequence-language` override; and
- bump project-status schema version.

This does not add new sequence behavior, claims, evidence artifacts, proof
rules, or project-status summary lines.

## Success Criteria

- Red tests fail before implementation because project status still reports
  schema version `18`, has no `sequence_language`, omits sequence language from
  text output, omits sequence-language failures, and rejects
  `--sequence-language`.
- JSON project status includes accepted sequence language with one claim and
  one certificate.
- Text project status renders the accepted sequence language.
- Missing or malformed sequence-language input makes project status rejected
  with structured language failed subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run project-status text/JSON, refreshed handoff,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented.

The red project-status run executed 83 tests and failed because aggregate
status still reported schema version `18`, had no `sequence_language`, omitted
network-sequence language from text output, omitted sequence-language failures,
rejected `--sequence-language`, and did not accept `sequence_language_path` in
the builder.

The implementation reuses the ADR-0201 sequence object-language validator,
exposes `sequence_language` in JSON, includes it in aggregate acceptance,
renders the accepted one-claim/one-certificate sequence language in default
text output, and includes sequence-language failed subjects in the shared
language-failure section.

Focused verification passed 83 project-status tests. Adjacent verification
with sequence object-language tests passed 95 tests. Live JSON output reported
`schema_version: 19` and accepted sequence language with 32 validation results;
text output reported `Network sequence language: accepted (1 claim, 1
certificate)` and `Language failures: none`. `compileall`, `git diff --check`,
refreshed handoff, and the full default suite passed. The full suite ran 862
tests.
