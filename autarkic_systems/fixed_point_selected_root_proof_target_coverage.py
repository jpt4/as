"""Selected-root proof-target coverage for fixed-point construction.

ADR-0321 checks the current selected-root proof-readiness coverage against the
two blocked proof targets for the selected fixed-point construction roots. The
surface deliberately remains a coverage handoff: it proves that the proof
targets are present, accepted, and blocked, not that either selected root has
been proved.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.fixed_point_diagonal_instance_closure_proof_target import (
    load_fixed_point_diagonal_instance_closure_proof_target,
    validate_fixed_point_diagonal_instance_closure_proof_target,
)
from autarkic_systems.fixed_point_selected_root_proof_readiness_coverage import (
    load_fixed_point_selected_root_proof_readiness_coverage,
    validate_fixed_point_selected_root_proof_readiness_coverage,
)
from autarkic_systems.fixed_point_substitution_graph_correctness_proof_target import (
    load_fixed_point_substitution_graph_correctness_proof_target,
    validate_fixed_point_substitution_graph_correctness_proof_target,
)


DEFAULT_COVERAGE = Path("claims/fixed_point_selected_root_proof_target_coverage.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_COVERAGE_ID = "as-fixed-point-selected-root-proof-target-coverage-v1"
REQUIRED_SELECTED_CASE_KINDS = (
    "diagonal-instance-closure",
    "substitution-graph-correctness-proof",
)
REQUIRED_PROOF_TARGET_STATUS = "blocked-proof-closure-targeted"
REQUIRED_NON_CLAIMS = (
    "no diagonal-instance closure proof",
    "no substitution graph correctness proof",
    "no substitution representability proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no fixed-point construction proof",
    "no self-consistency theorem",
)
EXPECTED_READINESS_COVERAGE_PATH = (
    "claims/fixed_point_selected_root_proof_readiness_coverage.json"
)
EXPECTED_PROOF_TARGET_PATHS = {
    "diagonal-instance-closure": (
        "claims/fixed_point_diagonal_instance_closure_proof_target.json"
    ),
    "substitution-graph-correctness-proof": (
        "claims/fixed_point_substitution_graph_correctness_proof_target.json"
    ),
}
PROOF_PROMOTION_NON_CLAIMS = {
    "diagonal-instance closure proof",
    "substitution graph correctness proof",
    "substitution representability proof",
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "fixed-point construction proof",
    "self-consistency theorem",
}

_TARGET_VALIDATORS: dict[str, tuple[Callable[[Path | str], Any], Callable[[Any, Path], Any]]] = {
    "diagonal-instance-closure": (
        load_fixed_point_diagonal_instance_closure_proof_target,
        validate_fixed_point_diagonal_instance_closure_proof_target,
    ),
    "substitution-graph-correctness-proof": (
        load_fixed_point_substitution_graph_correctness_proof_target,
        validate_fixed_point_substitution_graph_correctness_proof_target,
    ),
}


@dataclass(frozen=True)
class FixedPointSelectedRootProofTargetCoverageManifest:
    """Loaded manifest for selected-root proof-target coverage."""

    path: Path
    schema_version: int
    coverage_id: str
    reviewed_at: str
    purpose: str
    selected_root_readiness_coverage_path: str
    proof_target_paths: dict[str, str]
    expected_selected_case_kinds: tuple[str, ...]
    expected_selected_count: int
    expected_proof_target_count: int
    expected_blocked_proof_target_count: int
    expected_proof_closure_ready_count: int
    expected_missing_proof_artifact_count: int
    expected_proof_target_status: str
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SelectedRootProofTargetCoverageEntry:
    """One observed blocked proof target for a selected root."""

    case_kind: str
    target_id: str
    proof_target_status: str
    accepted: bool
    proof_closure_ready: bool
    missing_proof_artifact_count: int
    proof_boundary_preserved: bool
    failed_subjects: tuple[str, ...]

    @property
    def blocked(self) -> bool:
        """Return whether this proof target is accepted but not proof-ready."""

        return (
            self.accepted
            and self.proof_target_status == REQUIRED_PROOF_TARGET_STATUS
            and not self.proof_closure_ready
            and self.missing_proof_artifact_count > 0
        )


@dataclass(frozen=True)
class FixedPointSelectedRootProofTargetCoverageValidation:
    """One validation result for selected-root proof-target coverage."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSelectedRootProofTargetCoverageReport:
    """Validation report for selected-root proof-target coverage."""

    manifest: FixedPointSelectedRootProofTargetCoverageManifest
    selected_root_readiness_coverage_path: Path
    proof_target_paths: dict[str, Path]
    willard_map_path: Path
    selected_root_readiness_coverage_accepted: bool
    selected_case_kinds: tuple[str, ...]
    proof_target_entries: tuple[SelectedRootProofTargetCoverageEntry, ...]
    missing_case_kinds: tuple[str, ...]
    proof_boundary_preserved: bool
    results: tuple[FixedPointSelectedRootProofTargetCoverageValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every coverage validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def selected_case_count(self) -> int:
        """Return the number of currently selected root obligations."""

        return len(self.selected_case_kinds)

    @property
    def proof_target_count(self) -> int:
        """Return the number of accepted proof-target entries."""

        return len(self.proof_target_entries)

    @property
    def blocked_proof_target_count(self) -> int:
        """Return how many selected-root proof targets remain blocked."""

        return sum(1 for entry in self.proof_target_entries if entry.blocked)

    @property
    def proof_closure_ready_count(self) -> int:
        """Return how many selected roots are ready for proof promotion."""

        return sum(1 for entry in self.proof_target_entries if entry.proof_closure_ready)

    @property
    def missing_proof_artifact_count(self) -> int:
        """Return the total missing proof artifacts across selected roots."""

        return sum(
            entry.missing_proof_artifact_count for entry in self.proof_target_entries
        )

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return stable failure subjects for automation and reports."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


@dataclass(frozen=True)
class _DependencyFailure:
    """Small report shim used when a dependency cannot load."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    proof_boundary_preserved: bool = False
    selected_case_kinds: tuple[str, ...] = ()
    case_kind: str = ""
    proof_target_status: str = ""
    proof_closure_ready: bool = False
    missing_proof_artifact_count: int = 0


def load_fixed_point_selected_root_proof_target_coverage(
    path: Path | str = DEFAULT_COVERAGE,
) -> FixedPointSelectedRootProofTargetCoverageManifest:
    """Load the selected-root proof-target coverage manifest."""

    coverage_path = Path(path)
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    proof_target_paths = data.get("proof_target_paths")
    if not isinstance(proof_target_paths, dict):
        raise ValueError("proof_target_paths must be an object")
    if not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in proof_target_paths.items()
    ):
        raise ValueError("proof_target_paths must map text to text")
    return FixedPointSelectedRootProofTargetCoverageManifest(
        path=coverage_path,
        schema_version=_required_int(data, "schema_version"),
        coverage_id=_required_text(data, "coverage_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        selected_root_readiness_coverage_path=_required_text(
            data,
            "selected_root_readiness_coverage_path",
        ),
        proof_target_paths=dict(proof_target_paths),
        expected_selected_case_kinds=tuple(
            _required_text_list(data, "expected_selected_case_kinds")
        ),
        expected_selected_count=_required_int(data, "expected_selected_count"),
        expected_proof_target_count=_required_int(
            data,
            "expected_proof_target_count",
        ),
        expected_blocked_proof_target_count=_required_int(
            data,
            "expected_blocked_proof_target_count",
        ),
        expected_proof_closure_ready_count=_required_int(
            data,
            "expected_proof_closure_ready_count",
        ),
        expected_missing_proof_artifact_count=_required_int(
            data,
            "expected_missing_proof_artifact_count",
        ),
        expected_proof_target_status=_required_text(
            data,
            "expected_proof_target_status",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_selected_root_proof_target_coverage(
    manifest: FixedPointSelectedRootProofTargetCoverageManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSelectedRootProofTargetCoverageReport:
    """Validate selected-root proof-target coverage."""

    checked_willard_map_path = Path(willard_map_path)
    readiness_coverage_path = _resolve_path(
        manifest.path,
        manifest.selected_root_readiness_coverage_path,
    )
    proof_target_paths = {
        case_kind: _resolve_path(manifest.path, path)
        for case_kind, path in manifest.proof_target_paths.items()
    }
    results: list[FixedPointSelectedRootProofTargetCoverageValidation] = [
        _accepted("manifest", f"loaded {manifest.coverage_id}")
    ]
    results.extend(_validate_manifest(manifest))

    readiness_coverage_report = _load_readiness_coverage(
        readiness_coverage_path,
        checked_willard_map_path,
    )
    target_reports = {
        case_kind: _load_proof_target(
            case_kind,
            proof_target_paths.get(case_kind, Path("")),
            checked_willard_map_path,
        )
        for case_kind in REQUIRED_SELECTED_CASE_KINDS
    }
    results.extend(_validate_dependencies(readiness_coverage_report, target_reports))

    selected_case_kinds = tuple(
        getattr(readiness_coverage_report, "selected_case_kinds", ())
    )
    proof_target_entries = tuple(
        entry
        for case_kind in REQUIRED_SELECTED_CASE_KINDS
        for entry in (_proof_target_entry(case_kind, target_reports[case_kind]),)
        if entry.accepted
    )
    proof_target_case_kinds = tuple(entry.case_kind for entry in proof_target_entries)
    missing_case_kinds = tuple(
        case_kind
        for case_kind in selected_case_kinds
        if case_kind not in proof_target_case_kinds
    )
    proof_boundary_preserved = (
        bool(getattr(readiness_coverage_report, "accepted", False))
        and bool(
            getattr(readiness_coverage_report, "proof_boundary_preserved", False)
        )
        and selected_case_kinds == REQUIRED_SELECTED_CASE_KINDS
        and proof_target_case_kinds == REQUIRED_SELECTED_CASE_KINDS
        and not missing_case_kinds
        and all(entry.blocked for entry in proof_target_entries)
        and not any(entry.proof_closure_ready for entry in proof_target_entries)
        and _non_claims_are_guarded(manifest.non_claims)
    )
    results.extend(
        _validate_coverage(
            manifest,
            selected_case_kinds,
            proof_target_entries,
            missing_case_kinds,
            proof_boundary_preserved,
        )
    )

    return FixedPointSelectedRootProofTargetCoverageReport(
        manifest=manifest,
        selected_root_readiness_coverage_path=readiness_coverage_path,
        proof_target_paths=proof_target_paths,
        willard_map_path=checked_willard_map_path,
        selected_root_readiness_coverage_accepted=bool(
            getattr(readiness_coverage_report, "accepted", False)
        ),
        selected_case_kinds=selected_case_kinds,
        proof_target_entries=proof_target_entries,
        missing_case_kinds=missing_case_kinds,
        proof_boundary_preserved=proof_boundary_preserved,
        results=tuple(results),
    )


def fixed_point_selected_root_proof_target_coverage_payload(
    report: FixedPointSelectedRootProofTargetCoverageReport,
) -> dict[str, Any]:
    """Return a JSON-ready selected-root proof-target coverage payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "coverage_manifest": str(report.manifest.path),
        "coverage_id": report.manifest.coverage_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "selected_root_readiness_coverage_path": str(
            report.selected_root_readiness_coverage_path
        ),
        "proof_target_paths": {
            key: str(value) for key, value in report.proof_target_paths.items()
        },
        "willard_map": str(report.willard_map_path),
        "observed_selected_root_readiness_coverage_accepted": (
            report.selected_root_readiness_coverage_accepted
        ),
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "selected_case_kinds": list(report.selected_case_kinds),
        "selected_case_count": report.selected_case_count,
        "proof_target_count": report.proof_target_count,
        "blocked_proof_target_count": report.blocked_proof_target_count,
        "proof_closure_ready_count": report.proof_closure_ready_count,
        "missing_proof_artifact_count": report.missing_proof_artifact_count,
        "missing_case_kinds": list(report.missing_case_kinds),
        "proof_target_entries": [
            _proof_target_entry_payload(entry)
            for entry in report.proof_target_entries
        ],
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "result_count": len(report.results),
        "results": [
            {
                "subject": result.subject,
                "accepted": result.accepted,
                "detail": result.detail,
            }
            for result in report.results
        ],
    }


def format_fixed_point_selected_root_proof_target_coverage_report(
    report: FixedPointSelectedRootProofTargetCoverageReport,
) -> str:
    """Format a concise text report for selected-root proof-target coverage."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point selected-root proof-target coverage: {status}",
        f"Coverage: {report.manifest.coverage_id}",
        "Readiness coverage accepted: "
        + str(report.selected_root_readiness_coverage_accepted).lower(),
        f"Selected roots: {report.selected_case_count}",
        f"Proof targets: {report.proof_target_count}",
        f"Blocked proof targets: {report.blocked_proof_target_count}",
        f"Proof-closure-ready roots: {report.proof_closure_ready_count}",
        f"Missing proof artifacts: {report.missing_proof_artifact_count}",
        "Target coverage: "
        + _joined_or_none(tuple(entry.case_kind for entry in report.proof_target_entries)),
        "Missing targets: " + _joined_or_none(report.missing_case_kinds),
        "Proof boundary preserved: "
        + str(report.proof_boundary_preserved).lower(),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_selected_root_proof_target_coverage_cli(
    argv: list[str] | None = None,
) -> int:
    """Run selected-root proof-target coverage validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_selected_root_proof_target_coverage"
        ),
        description=(
            "Validate blocked proof-target coverage for selected AS "
            "fixed-point construction root obligations."
        ),
    )
    parser.add_argument(
        "--coverage",
        default=str(DEFAULT_COVERAGE),
        help="Path to the selected-root proof-target coverage manifest.",
    )
    parser.add_argument(
        "--willard-map",
        default=str(DEFAULT_WILLARD_MAP),
        help="Path to the Willard definition map.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_selected_root_proof_target_coverage(args.coverage)
    report = validate_fixed_point_selected_root_proof_target_coverage(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_selected_root_proof_target_coverage_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_selected_root_proof_target_coverage_report(report))
    return 0 if report.accepted else 1


def _resolve_path(base_path: Path, value: str) -> Path:
    """Resolve a manifest-local path while preserving root-relative paths."""

    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    candidate = base_path.parent / path
    if candidate.exists():
        return candidate
    return path


def _load_readiness_coverage(path: Path, willard_map_path: Path) -> Any:
    """Load and validate selected-root proof-readiness coverage."""

    try:
        manifest = load_fixed_point_selected_root_proof_readiness_coverage(path)
        return validate_fixed_point_selected_root_proof_readiness_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-selected-root-readiness-coverage-load",),
        )


def _load_proof_target(case_kind: str, path: Path, willard_map_path: Path) -> Any:
    """Load and validate one selected-root proof target."""

    if case_kind not in _TARGET_VALIDATORS:
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-selected-root-proof-target-unknown-case",),
        )
    loader, validator = _TARGET_VALIDATORS[case_kind]
    try:
        manifest = loader(path)
        return validator(manifest, willard_map_path)
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(f"fixed-point-selected-root-target-{case_kind}-load",),
        )


def _validate_manifest(
    manifest: FixedPointSelectedRootProofTargetCoverageManifest,
) -> list[FixedPointSelectedRootProofTargetCoverageValidation]:
    """Validate manifest-local constants and proof-boundary guardrails."""

    return [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "coverage_id",
            manifest.coverage_id == REQUIRED_COVERAGE_ID,
            "coverage id matches",
            "unexpected coverage id",
        ),
        _check(
            "selected_root_readiness_coverage_path",
            (
                manifest.selected_root_readiness_coverage_path
                == EXPECTED_READINESS_COVERAGE_PATH
            ),
            f"{EXPECTED_READINESS_COVERAGE_PATH} referenced",
            "selected-root readiness coverage path mismatch",
        ),
        _check(
            "proof_target_paths",
            manifest.proof_target_paths == EXPECTED_PROOF_TARGET_PATHS,
            "proof-target paths match",
            "proof-target path mismatch",
        ),
        _check(
            "expected_selected_case_kinds",
            manifest.expected_selected_case_kinds == REQUIRED_SELECTED_CASE_KINDS,
            "selected case kinds match",
            "selected case kind mismatch",
        ),
        _check(
            "expected_selected_count",
            manifest.expected_selected_count == len(REQUIRED_SELECTED_CASE_KINDS),
            "selected count matches",
            "selected count mismatch",
        ),
        _check(
            "expected_proof_target_count",
            manifest.expected_proof_target_count == len(REQUIRED_SELECTED_CASE_KINDS),
            "proof-target count matches",
            "proof-target count mismatch",
        ),
        _check(
            "expected_blocked_proof_target_count",
            (
                manifest.expected_blocked_proof_target_count
                == len(REQUIRED_SELECTED_CASE_KINDS)
            ),
            "blocked proof-target count matches",
            "blocked proof-target count mismatch",
        ),
        _check(
            "expected_proof_closure_ready_count",
            manifest.expected_proof_closure_ready_count == 0,
            "proof-closure-ready count matches",
            "proof-closure-ready count mismatch",
        ),
        _check(
            "expected_missing_proof_artifact_count",
            manifest.expected_missing_proof_artifact_count == 6,
            "missing proof artifact count matches",
            "missing proof artifact count mismatch",
        ),
        _check(
            "expected_proof_target_status",
            manifest.expected_proof_target_status == REQUIRED_PROOF_TARGET_STATUS,
            "proof target status matches",
            "proof target status mismatch",
        ),
        _check(
            "non_claims",
            manifest.non_claims == REQUIRED_NON_CLAIMS,
            "all non-claims preserved",
            "missing non-claims",
        ),
        _check(
            "non_claim_promotion_boundary",
            _non_claims_are_guarded(manifest.non_claims),
            "non-claims use explicit no-prefix boundary",
            "proof promotion non-claim boundary",
        ),
        _check("next_as_action", bool(manifest.next_as_action), "next action present"),
    ]


def _validate_dependencies(
    readiness_coverage_report: Any,
    target_reports: dict[str, Any],
) -> list[FixedPointSelectedRootProofTargetCoverageValidation]:
    """Validate that coverage and target dependencies accept."""

    results = [
        _check(
            "readiness_coverage.accepted",
            bool(getattr(readiness_coverage_report, "accepted", False)),
            "selected-root readiness coverage accepted",
            "selected-root readiness coverage rejected",
        )
    ]
    for case_kind in REQUIRED_SELECTED_CASE_KINDS:
        report = target_reports[case_kind]
        results.append(
            _check(
                f"proof_target.{case_kind}.accepted",
                bool(getattr(report, "accepted", False)),
                "proof target accepted",
                "proof target rejected",
            )
        )
    return results


def _proof_target_entry(
    case_kind: str,
    report: Any,
) -> SelectedRootProofTargetCoverageEntry:
    """Extract the common proof-target shape from one dependency report."""

    observed_case_kind = str(getattr(report, "case_kind", ""))
    proof_target_status = str(getattr(report, "proof_target_status", ""))
    accepted = (
        bool(getattr(report, "accepted", False))
        and observed_case_kind == case_kind
        and proof_target_status == REQUIRED_PROOF_TARGET_STATUS
        and bool(getattr(report, "proof_boundary_preserved", False))
    )
    return SelectedRootProofTargetCoverageEntry(
        case_kind=observed_case_kind,
        target_id=str(getattr(getattr(report, "manifest", None), "target_id", "")),
        proof_target_status=proof_target_status,
        accepted=accepted,
        proof_closure_ready=bool(getattr(report, "proof_closure_ready", False)),
        missing_proof_artifact_count=int(
            getattr(report, "missing_proof_artifact_count", 0)
        ),
        proof_boundary_preserved=bool(
            getattr(report, "proof_boundary_preserved", False)
        ),
        failed_subjects=tuple(getattr(report, "failed_subjects", ())),
    )


def _validate_coverage(
    manifest: FixedPointSelectedRootProofTargetCoverageManifest,
    selected_case_kinds: tuple[str, ...],
    proof_target_entries: tuple[SelectedRootProofTargetCoverageEntry, ...],
    missing_case_kinds: tuple[str, ...],
    proof_boundary_preserved: bool,
) -> list[FixedPointSelectedRootProofTargetCoverageValidation]:
    """Validate selected-root proof-target facts against the checked manifest."""

    target_case_kinds = tuple(entry.case_kind for entry in proof_target_entries)
    return [
        _check(
            "selection.selected_case_kinds",
            selected_case_kinds == manifest.expected_selected_case_kinds,
            "selected case kinds match",
            "selected case kind mismatch",
        ),
        _check(
            "selection.selected_count",
            len(selected_case_kinds) == manifest.expected_selected_count,
            "selected count matches",
            "selected count mismatch",
        ),
        _check(
            "proof_target.case_kinds",
            target_case_kinds == manifest.expected_selected_case_kinds,
            "proof target case kinds match",
            "proof target case kind mismatch",
        ),
        _check(
            "proof_target.count",
            len(proof_target_entries) == manifest.expected_proof_target_count,
            "proof-target count matches",
            "proof-target count mismatch",
        ),
        _check(
            "proof_target.missing_count",
            len(missing_case_kinds) == 0,
            "no selected root lacks a proof target",
            "selected root proof target missing",
        ),
        _check(
            "proof_target.statuses",
            all(
                entry.proof_target_status == manifest.expected_proof_target_status
                for entry in proof_target_entries
            ),
            "proof target statuses match",
            "proof target status mismatch",
        ),
        _check(
            "proof_target.blocked_count",
            sum(1 for entry in proof_target_entries if entry.blocked)
            == manifest.expected_blocked_proof_target_count,
            "blocked proof-target count matches",
            "blocked proof-target count mismatch",
        ),
        _check(
            "proof_target.proof_closure_ready_count",
            sum(1 for entry in proof_target_entries if entry.proof_closure_ready)
            == manifest.expected_proof_closure_ready_count,
            "proof-closure-ready count matches",
            "proof-closure-ready count mismatch",
        ),
        _check(
            "proof_target.missing_proof_artifact_count",
            sum(
                entry.missing_proof_artifact_count
                for entry in proof_target_entries
            )
            == manifest.expected_missing_proof_artifact_count,
            "missing proof artifact count matches",
            "missing proof artifact count mismatch",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
            "proof boundary not preserved",
        ),
    ]


def _proof_target_entry_payload(
    entry: SelectedRootProofTargetCoverageEntry,
) -> dict[str, Any]:
    """Return the JSON shape for one selected-root proof-target entry."""

    return {
        "case_kind": entry.case_kind,
        "target_id": entry.target_id,
        "proof_target_status": entry.proof_target_status,
        "accepted": entry.accepted,
        "blocked": entry.blocked,
        "proof_closure_ready": entry.proof_closure_ready,
        "missing_proof_artifact_count": entry.missing_proof_artifact_count,
        "proof_boundary_preserved": entry.proof_boundary_preserved,
        "failed_subjects": list(entry.failed_subjects),
    }


def _required_text(data: dict[str, Any], key: str) -> str:
    """Return a required non-empty text field from JSON data."""

    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    """Return a required integer field from JSON data."""

    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    """Return a required list of non-empty text values from JSON data."""

    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{key} must contain non-empty text")
    return value


def _non_claims_are_guarded(non_claims: tuple[str, ...]) -> bool:
    """Return whether every proof-sensitive non-claim has an explicit no-prefix."""

    return all(f"no {claim}" in non_claims for claim in PROOF_PROMOTION_NON_CLAIMS)


def _check(
    subject: str,
    accepted: bool,
    ok_detail: str,
    fail_detail: str | None = None,
) -> FixedPointSelectedRootProofTargetCoverageValidation:
    """Build a validation result."""

    return FixedPointSelectedRootProofTargetCoverageValidation(
        subject=subject,
        accepted=accepted,
        detail=ok_detail if accepted else (fail_detail or ok_detail),
    )


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointSelectedRootProofTargetCoverageValidation:
    """Build an accepted validation result."""

    return FixedPointSelectedRootProofTargetCoverageValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    """Map detailed validation subjects to compact failure labels."""

    if subject.startswith("readiness_coverage.") or subject.startswith(
        "proof_target."
    ):
        if "missing_proof_artifact" in subject:
            return "fixed-point-selected-root-proof-target-coverage-artifacts"
        if subject.startswith("proof_target.case") or subject.startswith(
            "proof_target.count"
        ):
            return "fixed-point-selected-root-proof-target-coverage-selection"
        if subject.startswith("proof_target.blocked") or subject.startswith(
            "proof_target.proof_closure"
        ):
            return "fixed-point-selected-root-proof-target-coverage-status"
        return "fixed-point-selected-root-proof-target-coverage-dependencies"
    if subject.startswith("expected_missing_proof_artifact"):
        return "fixed-point-selected-root-proof-target-coverage-artifacts"
    if subject.startswith("expected_blocked") or subject.startswith(
        "expected_proof_closure"
    ):
        return "fixed-point-selected-root-proof-target-coverage-status"
    if subject.startswith("selection.") or subject.startswith("expected_selected"):
        return "fixed-point-selected-root-proof-target-coverage-selection"
    if subject.startswith("proof_boundary") or subject.startswith(
        "non_claim_promotion_boundary"
    ):
        return "fixed-point-selected-root-proof-target-coverage-proof-boundary"
    return "fixed-point-selected-root-proof-target-coverage-manifest"


def _joined_or_none(values: tuple[str, ...]) -> str:
    """Render a tuple for text output."""

    return ", ".join(values) if values else "none"


def main() -> int:
    """Module entry point."""

    return run_fixed_point_selected_root_proof_target_coverage_cli()


if __name__ == "__main__":
    raise SystemExit(main())
