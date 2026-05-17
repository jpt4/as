# ADR-0071: Evidence CLI JSON Output

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0067 added a human-readable evidence registry CLI. ADR-0070 made that CLI
fail closed over sibling bundle files. The current command is useful for
operators, but downstream automation would have to scrape `OK` and `FAIL`
lines to consume the result.

AS should expose the same registry validation result as structured JSON.

## Decision

Add `--format text|json` to
`python -m autarkic_systems.evidence_bundle`.

The default remains text. JSON output will include:

- registry ID;
- overall accepted status;
- bundle count;
- validation result count; and
- one structured record per validation result.

This ADR does not add new Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because JSON report helpers or CLI
  support are absent.
- `--format json` emits parseable JSON for the checked-in registry.
- JSON output records `accepted: true`, `bundle_count: 3`, and
  `registry-completeness`.
- JSON output records `accepted: false` and the failing subject for a drifted
  registry.
- Default text output remains unchanged.
- Runtime behavior remains unchanged.

## Consequences

Evidence registry validation can now be consumed by future CI, scripts, or
agents without brittle text parsing.

## Test Plan

- Red: `python -m unittest tests.test_evidence_bundle_cli` fails before JSON
  support exists.
- Green: the same focused test passes after adding JSON output.
- Regression: run the actual CLI in text and JSON modes and the full default
  suite before commit.

## After Action Report

Implemented in `autarkic_systems/evidence_bundle.py`.

The focused red run failed because `registry_validation_report_payload` was
absent. The green implementation adds that structured report helper and a
`--format text|json` CLI option. Text remains the default, while JSON output
records registry ID, accepted status, bundle count, result count, and
per-subject validation records.

The checked JSON command is:

```sh
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json
```

Runtime behavior remains unchanged.
