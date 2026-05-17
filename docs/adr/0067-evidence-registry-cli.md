# ADR-0067: Evidence Registry CLI

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0065 and ADR-0066 made transition evidence bundles machine-checkable and
discoverable. The current verification path still requires either unit tests or
custom Python calls. AS should expose a small operator-facing command that
validates the evidence registry directly.

The repository currently has no separate packaging or `tools/` convention, so
the smallest non-inventive surface is a module command:

```sh
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

## Decision

Add a CLI entrypoint to `autarkic_systems/evidence_bundle.py`.

The command will:

- load an evidence bundle registry path;
- validate the registry and all registered bundles;
- print a concise report with `OK` and `FAIL` lines; and
- return exit code `0` only when every validation result is accepted.

This ADR does not add new Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the CLI helpers are absent or
  `python -m autarkic_systems.evidence_bundle` produces no validation report.
- The CLI reports the registry ID and each validation result.
- The CLI returns `0` for the checked-in registry.
- The CLI returns non-zero for a registry with a missing bundle path.
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json`
  works from the repository root.
- Runtime behavior remains unchanged.

## Consequences

Evidence registry validation becomes a direct project command, not only an
internal test assertion.

## Test Plan

- Red: `python -m unittest tests.test_evidence_bundle_cli` fails before CLI
  support exists.
- Green: the same focused test passes after adding the CLI.
- Regression: run evidence registry tests and the full default suite before
  commit.

## After Action Report

Implemented in `autarkic_systems/evidence_bundle.py`.

The focused red run failed because `format_registry_validation_report` and the
CLI runner were absent from `autarkic_systems.evidence_bundle`. The green
implementation adds a small `argparse` command that loads an evidence registry,
validates it through the ADR-0066 registry validator, prints `OK`/`FAIL`
results, and exits `0` only when every validation result is accepted.

The checked command is:

```sh
python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json
```

Runtime behavior remains unchanged.
