"""Selected-root proof-readiness coverage for fixed-point construction.

ADR-0318 checks the current fixed-point frontier selector against the two
certificate-ready/proof-open readiness handoffs for the selected root proof
obligations. The module deliberately keeps both root obligations proof-open
and keeps downstream construction cases deferred; it is a scheduling handoff,
not a proof of fixed-point construction or self-consistency.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness import (
    load_fixed_point_diagonal_instance_closure_proof_readiness,
    validate_fixed_point_diagonal_instance_closure_proof_readiness,
)
from autarkic_systems.fixed_point_frontier_selector import (
    load_fixed_point_frontier_selector,
    validate_fixed_point_frontier_selector,
)
from autarkic_systems.fixed_point_substitution_graph_correctness_proof_readiness import (
    load_fixed_point_substitution_graph_correctness_proof_readiness,
    validate_fixed_point_substitution_graph_correctness_proof_readiness,
)


DEFAULT_COVERAGE = Path(
    "claims/fixed_point_selected_root_proof_readiness_coverage.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_COVERAGE_ID = (
    "as-fixed-point-selected-root-proof-readiness-coverage-v1"
)
REQUIRED_READINESS_STATUS = "blocked-certificate-ready-proof-open"
REQUIRED_SELECTED_CASE_KINDS = (
    "diagonal-instance-closure",
    "substitution-graph-correctness-proof",
)
REQUIRED_DEFERRED_CASE_KINDS = (
    "substitution-representability-proof",
    "bridge-equality-proof",
    "fixed-point-equation-lifting",
)
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
EXPECTED_SELECTOR_PATH = "claims/fixed_point_frontier_selector.json"
EXPECTED_READINESS_PATHS = {
    "diagonal-instance-closure": (
        "claims/fixed_point_diagonal_instance_closure_proof_readiness.json"
    ),
    "substitution-graph-correctness-proof": (
        "claims/fixed_point_substitution_graph_correctness_proof_readiness.json"
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

_READINESS_VALIDATORS: dict[
    str,
    tuple[Callable[[Path | str], Any], Callable[[Any, Path], Any]],
] = {
    "diagonal-instance-closure": (
        load_fixed_point_diagonal_instance_closure_proof_readiness,
        validate_fixed_point_diagonal_instance_closure_proof_readiness,
    ),
    "substitution-graph-correctness-proof": (
        load_fixed_point_substitution_graph_correctness_proof_readiness,
        validate_fixed_point_substitution_graph_correctness_proof_readiness,
    ),
}


@dataclass(frozen=True)
class FixedPointSelectedRootProofReadinessCoverageManifest:
    """Loaded manifest for selected-root proof-readiness coverage."""

    path: Path
    schema_version: int
    coverage_id: str
    reviewed_at: str
    purpose: str
    fixed_point_frontier_selector_path: str
    readiness_paths: dict[str, str]
    expected_selected_case_kinds: tuple[str, ...]
    expected_deferred_case_kinds: tuple[str, ...]
    expected_selected_count: int
    expected_deferred_count: int
    expected_readiness_count: int
    expected_missing_readiness_count: int
    expected_certificate_ready_count: int
    expected_readiness_status: str
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SelectedRootReadinessCoverageEntry:
    """One observed proof-readiness handoff for a selected root."""

    case_kind: str
    readiness_id: str
    readiness_status: str
    certificate_ready: bool
    accepted: bool
    proof_boundary_preserved: bool
    failed_subjects: tuple[str, ...]

    @property
    def proof_open(self) -> bool:
        """Return whether the selected root remains proof-open."""

        return self.readiness_status == REQUIRED_READINESS_STATUS


@dataclass(frozen=True)
class FixedPointSelectedRootProofReadinessCoverageValidation:
    """One validation result for selected-root readiness coverage."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSelectedRootProofReadinessCoverageReport:
    """Validation report for selected-root proof-readiness coverage."""

    manifest: FixedPointSelectedRootProofReadinessCoverageManifest
    fixed_point_frontier_selector_path: Path
    readiness_paths: dict[str, Path]
    willard_map_path: Path
    selector_accepted: bool
    selected_case_kinds: tuple[str, ...]
    deferred_case_kinds: tuple[str, ...]
    readiness_entries: tuple[SelectedRootReadinessCoverageEntry, ...]
    missing_case_kinds: tuple[str, ...]
    proof_boundary_preserved: bool
    results: tuple[FixedPointSelectedRootProofReadinessCoverageValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every coverage validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def selected_case_count(self) -> int:
        """Return the number of currently selected root obligations."""

        return len(self.selected_case_kinds)

    @property
    def deferred_case_count(self) -> int:
        """Return the number of deferred downstream obligations."""

        return len(self.deferred_case_kinds)

    @property
    def readiness_count(self) -> int:
        """Return the number of observed selected-root readiness entries."""

        return len(self.readiness_entries)

    @property
    def missing_readiness_count(self) -> int:
        """Return how many selected roots lack an accepted readiness handoff."""

        return len(self.missing_case_kinds)

    @property
    def certificate_ready_count(self) -> int:
        """Return how many selected-root handoffs are certificate-ready."""

        return sum(1 for entry in self.readiness_entries if entry.certificate_ready)

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
    readiness_entry: Any = None
    selected_case_kinds: tuple[str, ...] = ()
    deferred_case_kinds: tuple[str, ...] = ()


def load_fixed_point_selected_root_proof_readiness_coverage(
    path: Path | str = DEFAULT_COVERAGE,
) -> FixedPointSelectedRootProofReadinessCoverageManifest:
    """Load the selected-root proof-readiness coverage manifest."""

    coverage_path = Path(path)
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    readiness_paths = data.get("readiness_paths")
    if not isinstance(readiness_paths, dict):
        raise ValueError("readiness_paths must be an object")
    if not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in readiness_paths.items()
    ):
        raise ValueError("readiness_paths must map text to text")
    return FixedPointSelectedRootProofReadinessCoverageManifest(
        path=coverage_path,
        schema_version=_required_int(data, "schema_version"),
        coverage_id=_required_text(data, "coverage_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_frontier_selector_path=_required_text(
            data,
            "fixed_point_frontier_selector_path",
        ),
        readiness_paths=dict(readiness_paths),
        expected_selected_case_kinds=tuple(
            _required_text_list(data, "expected_selected_case_kinds")
        ),
        expected_deferred_case_kinds=tuple(
            _required_text_list(data, "expected_deferred_case_kinds")
        ),
        expected_selected_count=_required_int(data, "expected_selected_count"),
        expected_deferred_count=_required_int(data, "expected_deferred_count"),
        expected_readiness_count=_required_int(data, "expected_readiness_count"),
        expected_missing_readiness_count=_required_int(
            data,
            "expected_missing_readiness_count",
        ),
        expected_certificate_ready_count=_required_int(
            data,
            "expected_certificate_ready_count",
        ),
        expected_readiness_status=_required_text(data, "expected_readiness_status"),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_selected_root_proof_readiness_coverage(
    manifest: FixedPointSelectedRootProofReadinessCoverageManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSelectedRootProofReadinessCoverageReport:
    """Validate selected-root proof-readiness coverage."""

    checked_willard_map_path = Path(willard_map_path)
    selector_path = _resolve_path(
        manifest.path,
        manifest.fixed_point_frontier_selector_path,
    )
    readiness_paths = {
        case_kind: _resolve_path(manifest.path, path)
        for case_kind, path in manifest.readiness_paths.items()
    }
    results: list[FixedPointSelectedRootProofReadinessCoverageValidation] = [
        _accepted("manifest", f"loaded {manifest.coverage_id}")
    ]
    results.extend(_validate_manifest(manifest))

    selector_report = _load_selector(selector_path, checked_willard_map_path)
    readiness_reports = {
        case_kind: _load_readiness(
            case_kind,
            readiness_paths.get(case_kind, Path("")),
            checked_willard_map_path,
        )
        for case_kind in REQUIRED_SELECTED_CASE_KINDS
    }
    results.extend(_validate_dependencies(selector_report, readiness_reports))

    selected_case_kinds = tuple(getattr(selector_report, "selected_case_kinds", ()))
    deferred_case_kinds = tuple(getattr(selector_report, "deferred_case_kinds", ()))
    readiness_entries = tuple(
        entry
        for case_kind in REQUIRED_SELECTED_CASE_KINDS
        for entry in (_readiness_entry(case_kind, readiness_reports[case_kind]),)
        if entry.accepted
    )
    readiness_case_kinds = tuple(entry.case_kind for entry in readiness_entries)
    missing_case_kinds = tuple(
        case_kind
        for case_kind in selected_case_kinds
        if case_kind not in readiness_case_kinds
    )
    proof_boundary_preserved = (
        bool(getattr(selector_report, "accepted", False))
        and selected_case_kinds == REQUIRED_SELECTED_CASE_KINDS
        and deferred_case_kinds == REQUIRED_DEFERRED_CASE_KINDS
        and not missing_case_kinds
        and all(entry.proof_open for entry in readiness_entries)
        and _non_claims_are_guarded(manifest.non_claims)
    )
    results.extend(
        _validate_coverage(
            manifest,
            selected_case_kinds,
            deferred_case_kinds,
            readiness_entries,
            missing_case_kinds,
            proof_boundary_preserved,
        )
    )

    return FixedPointSelectedRootProofReadinessCoverageReport(
        manifest=manifest,
        fixed_point_frontier_selector_path=selector_path,
        readiness_paths=readiness_paths,
        willard_map_path=checked_willard_map_path,
        selector_accepted=bool(getattr(selector_report, "accepted", False)),
        selected_case_kinds=selected_case_kinds,
        deferred_case_kinds=deferred_case_kinds,
        readiness_entries=readiness_entries,
        missing_case_kinds=missing_case_kinds,
        proof_boundary_preserved=proof_boundary_preserved,
        results=tuple(results),
    )


def fixed_point_selected_root_proof_readiness_coverage_payload(
    report: FixedPointSelectedRootProofReadinessCoverageReport,
) -> dict[str, Any]:
    """Return a JSON-ready selected-root coverage payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "coverage_manifest": str(report.manifest.path),
        "coverage_id": report.manifest.coverage_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_frontier_selector_path": str(
            report.fixed_point_frontier_selector_path
        ),
        "readiness_paths": {
            key: str(value) for key, value in report.readiness_paths.items()
        },
        "willard_map": str(report.willard_map_path),
        "observed_selector_accepted": report.selector_accepted,
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "selected_case_kinds": list(report.selected_case_kinds),
        "selected_case_count": report.selected_case_count,
        "deferred_case_kinds": list(report.deferred_case_kinds),
        "deferred_case_count": report.deferred_case_count,
        "readiness_count": report.readiness_count,
        "missing_readiness_count": report.missing_readiness_count,
        "certificate_ready_count": report.certificate_ready_count,
        "missing_case_kinds": list(report.missing_case_kinds),
        "readiness_entries": [
            _readiness_entry_payload(entry) for entry in report.readiness_entries
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


def format_fixed_point_selected_root_proof_readiness_coverage_report(
    report: FixedPointSelectedRootProofReadinessCoverageReport,
) -> str:
    """Format a concise text report for selected-root coverage."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point selected-root proof-readiness coverage: {status}",
        f"Coverage: {report.manifest.coverage_id}",
        f"Selector accepted: {str(report.selector_accepted).lower()}",
        f"Selected roots: {report.selected_case_count}",
        f"Deferred cases: {report.deferred_case_count}",
        f"Readiness entries: {report.readiness_count}",
        f"Missing readiness: {_joined_or_none(report.missing_case_kinds)}",
        f"Certificate-ready handoffs: {report.certificate_ready_count}",
        "Readiness coverage: "
        + _joined_or_none(tuple(entry.case_kind for entry in report.readiness_entries)),
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


def run_fixed_point_selected_root_proof_readiness_coverage_cli(
    argv: list[str] | None = None,
) -> int:
    """Run selected-root proof-readiness coverage validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_selected_root_proof_readiness_coverage"
        ),
        description=(
            "Validate certificate-ready/proof-open coverage for selected "
            "AS fixed-point construction root obligations."
        ),
    )
    parser.add_argument(
        "--coverage",
        default=str(DEFAULT_COVERAGE),
        help="Path to the selected-root proof-readiness coverage manifest.",
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

    manifest = load_fixed_point_selected_root_proof_readiness_coverage(
        args.coverage
    )
    report = validate_fixed_point_selected_root_proof_readiness_coverage(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_selected_root_proof_readiness_coverage_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_selected_root_proof_readiness_coverage_report(
                report
            )
        )
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


def _load_selector(path: Path, willard_map_path: Path) -> Any:
    """Load and validate the fixed-point frontier selector."""

    try:
        manifest = load_fixed_point_frontier_selector(path)
        return validate_fixed_point_frontier_selector(manifest, willard_map_path)
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-frontier-selector-load",),
        )


def _load_readiness(case_kind: str, path: Path, willard_map_path: Path) -> Any:
    """Load and validate one selected-root proof-readiness handoff."""

    if case_kind not in _READINESS_VALIDATORS:
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-selected-root-readiness-unknown-case",),
        )
    loader, validator = _READINESS_VALIDATORS[case_kind]
    try:
        manifest = loader(path)
        return validator(manifest, willard_map_path)
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                f"fixed-point-selected-root-readiness-{case_kind}-load",
            ),
        )


def _validate_manifest(
    manifest: FixedPointSelectedRootProofReadinessCoverageManifest,
) -> list[FixedPointSelectedRootProofReadinessCoverageValidation]:
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
            "fixed_point_frontier_selector_path",
            manifest.fixed_point_frontier_selector_path == EXPECTED_SELECTOR_PATH,
            f"{EXPECTED_SELECTOR_PATH} referenced",
        ),
        _check(
            "readiness_paths",
            manifest.readiness_paths == EXPECTED_READINESS_PATHS,
            "readiness paths match",
            "readiness path mismatch",
        ),
        _check(
            "expected_selected_case_kinds",
            manifest.expected_selected_case_kinds == REQUIRED_SELECTED_CASE_KINDS,
            "selected case kinds match",
            "selected case kind mismatch",
        ),
        _check(
            "expected_deferred_case_kinds",
            manifest.expected_deferred_case_kinds == REQUIRED_DEFERRED_CASE_KINDS,
            "deferred case kinds match",
            "deferred case kind mismatch",
        ),
        _check(
            "expected_selected_count",
            manifest.expected_selected_count == len(REQUIRED_SELECTED_CASE_KINDS),
            "selected count matches",
        ),
        _check(
            "expected_deferred_count",
            manifest.expected_deferred_count == len(REQUIRED_DEFERRED_CASE_KINDS),
            "deferred count matches",
        ),
        _check(
            "expected_readiness_count",
            manifest.expected_readiness_count == len(REQUIRED_SELECTED_CASE_KINDS),
            "readiness count matches",
        ),
        _check(
            "expected_missing_readiness_count",
            manifest.expected_missing_readiness_count == 0,
            "missing readiness count matches",
        ),
        _check(
            "expected_certificate_ready_count",
            (
                manifest.expected_certificate_ready_count
                == len(REQUIRED_SELECTED_CASE_KINDS)
            ),
            "certificate-ready count matches",
        ),
        _check(
            "expected_readiness_status",
            manifest.expected_readiness_status == REQUIRED_READINESS_STATUS,
            "readiness status matches",
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
    selector_report: Any,
    readiness_reports: dict[str, Any],
) -> list[FixedPointSelectedRootProofReadinessCoverageValidation]:
    """Validate that the selector and selected-root readiness dependencies accept."""

    results = [
        _check(
            "selector.accepted",
            bool(getattr(selector_report, "accepted", False)),
            "selector accepted",
            "selector rejected",
        )
    ]
    for case_kind in REQUIRED_SELECTED_CASE_KINDS:
        report = readiness_reports[case_kind]
        results.append(
            _check(
                f"readiness.{case_kind}.accepted",
                bool(getattr(report, "accepted", False)),
                "readiness accepted",
                "readiness rejected",
            )
        )
    return results


def _readiness_entry(
    case_kind: str,
    report: Any,
) -> SelectedRootReadinessCoverageEntry:
    """Extract the common readiness-entry shape from one dependency report."""

    entry = getattr(report, "readiness_entry", None)
    observed_case_kind = str(getattr(entry, "case_kind", ""))
    readiness_status = str(getattr(entry, "readiness_status", ""))
    certificate_ready = bool(getattr(entry, "certificate_ready", False))
    accepted = (
        bool(getattr(report, "accepted", False))
        and observed_case_kind == case_kind
        and readiness_status == REQUIRED_READINESS_STATUS
        and certificate_ready
        and bool(getattr(report, "proof_boundary_preserved", False))
    )
    return SelectedRootReadinessCoverageEntry(
        case_kind=observed_case_kind,
        readiness_id=str(getattr(getattr(report, "manifest", None), "readiness_id", "")),
        readiness_status=readiness_status,
        certificate_ready=certificate_ready,
        accepted=accepted,
        proof_boundary_preserved=bool(
            getattr(report, "proof_boundary_preserved", False)
        ),
        failed_subjects=tuple(getattr(report, "failed_subjects", ())),
    )


def _validate_coverage(
    manifest: FixedPointSelectedRootProofReadinessCoverageManifest,
    selected_case_kinds: tuple[str, ...],
    deferred_case_kinds: tuple[str, ...],
    readiness_entries: tuple[SelectedRootReadinessCoverageEntry, ...],
    missing_case_kinds: tuple[str, ...],
    proof_boundary_preserved: bool,
) -> list[FixedPointSelectedRootProofReadinessCoverageValidation]:
    """Validate selected-root coverage facts against the checked manifest."""

    readiness_case_kinds = tuple(entry.case_kind for entry in readiness_entries)
    return [
        _check(
            "selection.selected_case_kinds",
            selected_case_kinds == manifest.expected_selected_case_kinds,
            "selected case kinds match",
            "selected case kind mismatch",
        ),
        _check(
            "selection.deferred_case_kinds",
            deferred_case_kinds == manifest.expected_deferred_case_kinds,
            "deferred case kinds match",
            "deferred case kind mismatch",
        ),
        _check(
            "selection.selected_count",
            len(selected_case_kinds) == manifest.expected_selected_count,
            "selected count matches",
            "selected count mismatch",
        ),
        _check(
            "selection.deferred_count",
            len(deferred_case_kinds) == manifest.expected_deferred_count,
            "deferred count matches",
            "deferred count mismatch",
        ),
        _check(
            "readiness.case_kinds",
            readiness_case_kinds == manifest.expected_selected_case_kinds,
            "readiness case kinds match",
            "readiness case kind mismatch",
        ),
        _check(
            "readiness.count",
            len(readiness_entries) == manifest.expected_readiness_count,
            "readiness count matches",
            "readiness count mismatch",
        ),
        _check(
            "readiness.missing_count",
            len(missing_case_kinds) == manifest.expected_missing_readiness_count,
            "missing readiness count matches",
            "missing readiness count mismatch",
        ),
        _check(
            "readiness.certificate_ready_count",
            sum(1 for entry in readiness_entries if entry.certificate_ready)
            == manifest.expected_certificate_ready_count,
            "certificate-ready count matches",
            "certificate-ready count mismatch",
        ),
        _check(
            "readiness.statuses",
            all(
                entry.readiness_status == manifest.expected_readiness_status
                for entry in readiness_entries
            ),
            "readiness statuses match",
            "readiness status mismatch",
        ),
        _check(
            "readiness.proof_open",
            all(entry.proof_open for entry in readiness_entries),
            "all readiness entries remain proof-open",
            "readiness proof-open mismatch",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
            "proof boundary not preserved",
        ),
    ]


def _readiness_entry_payload(entry: SelectedRootReadinessCoverageEntry) -> dict[str, Any]:
    """Return the JSON shape for one selected-root readiness entry."""

    return {
        "case_kind": entry.case_kind,
        "readiness_id": entry.readiness_id,
        "readiness_status": entry.readiness_status,
        "certificate_ready": entry.certificate_ready,
        "proof_open": entry.proof_open,
        "accepted": entry.accepted,
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
) -> FixedPointSelectedRootProofReadinessCoverageValidation:
    """Build a validation result."""

    return FixedPointSelectedRootProofReadinessCoverageValidation(
        subject=subject,
        accepted=accepted,
        detail=ok_detail if accepted else (fail_detail or ok_detail),
    )


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointSelectedRootProofReadinessCoverageValidation:
    """Build an accepted validation result."""

    return FixedPointSelectedRootProofReadinessCoverageValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    """Map detailed validation subjects to compact failure labels."""

    if subject.startswith("selector.accepted") or subject.startswith("readiness."):
        return "fixed-point-selected-root-proof-readiness-coverage-dependencies"
    if subject.startswith("selection."):
        return "fixed-point-selected-root-proof-readiness-coverage-selection"
    if subject.startswith("proof_boundary") or subject.startswith(
        "non_claim_promotion_boundary"
    ):
        return "fixed-point-selected-root-proof-readiness-coverage-proof-boundary"
    return "fixed-point-selected-root-proof-readiness-coverage-manifest"


def _joined_or_none(values: tuple[str, ...]) -> str:
    """Render a tuple for text output."""

    return ", ".join(values) if values else "none"


def main() -> int:
    """Module entry point."""

    return run_fixed_point_selected_root_proof_readiness_coverage_cli()


if __name__ == "__main__":
    raise SystemExit(main())
