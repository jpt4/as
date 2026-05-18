# ADR-0144: Resolution Question Evidence Surface

Date: 2026-05-18

## Status

Accepted.

## Context

The project status report now names unresolved command-token questions, renders
their short summaries, and also shows already resolved sub-decisions. That is
useful, but the unresolved side still requires a second pass through the
source-status artifacts to see why a question remains blocked.

For example, the status report says that write-buffer `buffer-full-boundary`
remains unresolved, but not that RAA has an explicit guard while SEMSIM and
FSMSIM do not. It says standard-signal `command-token-vs-binary-input` remains
open, but not that the formal model names a command-table token while the
legacy witnesses exclude `standard-signal` from special-message dispatch and
treat ordinary standard input separately.

Agents choosing the next safe slice need those source conflicts in the first
diagnostic surface.

## Decision

Add optional `resolution_question_evidence` metadata to accepted source-status
records. Each entry names:

- `question_id`, matching an unresolved resolution question; and
- `evidence`, a concise source-backed reason the question remains unresolved.

Project status JSON will expose this list on each accepted
`frontier.source_statuses[]` entry, and the default text report will render a
`Resolution question evidence:` section grouped by command label.

Malformed `resolution_question_evidence` metadata rejects the owning
source-status record as `source-status-schema`, matching existing fail-closed
handling for unresolved and resolved question metadata.

This ADR bumps project status JSON schema from `13` to `14`.

## Success Criteria

- Red project-status tests fail before implementation because
  `schema_version: 14`, `resolution_question_evidence`, text rendering, and
  schema validation are absent.
- Accepted standard-signal and write-buffer source-status entries expose
  evidence for each unresolved question.
- Project status text renders the source evidence for unresolved questions.
- Malformed `resolution_question_evidence` metadata rejects the source-status
  record as `source-status-schema`.
- Runtime behavior remains unchanged.
- Full repository tests remain green.

## Consequences

The first diagnostic command becomes a better work-selection surface. It can
show not only what is blocked, but the concrete source disagreement or absence
of authority behind each blocker.

This does not resolve any command-token question and does not change Universal
Cell behavior.

## Test Plan

- Red: run focused project-status tests after adding assertions for
  `schema_version: 14`, missing evidence fields, missing text output, and
  malformed evidence fixtures.
- Green: update project-status aggregation/rendering and source-status JSON.
- Regression: run focused project-status tests, project status text/JSON
  checks, JSON formatting, `py_compile`, `git diff --check`, and the full
  default suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py`,
`sources/standard_signal_command_semantics_status.json`, and
`sources/write_buffer_command_semantics_status.json`.

The red focused run executed 60 tests and failed because project status still
reported `schema_version: 13`, omitted `resolution_question_evidence`, omitted
the default text `Resolution question evidence:` section, and accepted
malformed evidence metadata.

The green focused run passed 60 project-status tests after implementation.
Project status JSON now reports `schema_version: 14` and each accepted
standard-signal/write-buffer source-status entry carries
`resolution_question_evidence`. Default text output now renders the source
conflict behind each unresolved standard-signal and write-buffer question.

Runtime behavior remains unchanged.

Verification passed: JSON formatting, `py_compile`, and `git diff --check`
passed; project status text and JSON were accepted at `schema_version: 14`;
and `python -m unittest discover` passed 641 tests.
