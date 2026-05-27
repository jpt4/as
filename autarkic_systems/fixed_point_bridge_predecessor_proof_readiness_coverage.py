"""Coverage handoff for bridge-equality predecessor proof readiness.

ADR-0315 checks that the three open predecessor proof blockers named by the
bridge-equality readiness surface each have an accepted
certificate-ready/proof-open readiness handoff. The module deliberately keeps
bridge equality blocked; it is coverage metadata, not a proof of any
predecessor, bridge equality, the fixed-point equation, or self-consistency.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.fixed_point_bridge_equality_proof_closure_readiness import (
    load_fixed_point_bridge_equality_proof_closure_readiness,
    validate_fixed_point_bridge_equality_proof_closure_readiness,
)
from autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness import (
    load_fixed_point_diagonal_instance_closure_proof_readiness,
    validate_fixed_point_diagonal_instance_closure_proof_readiness,
)
from autarkic_systems.fixed_point_substitution_graph_correctness_proof_readiness import (
    load_fixed_point_substitution_graph_correctness_proof_readiness,
    validate_fixed_point_substitution_graph_correctness_proof_readiness,
)
from autarkic_systems.fixed_point_substitution_representability_proof_readiness import (
    load_fixed_point_substitution_representability_proof_readiness,
    validate_fixed_point_substitution_representability_proof_readiness,
)


DEFAULT_COVERAGE = Path(
    "claims/fixed_point_bridge_predecessor_proof_readiness_coverage.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_COVERAGE_ID = (
    "as-fixed-point-bridge-predecessor-proof-readiness-coverage-v1"
)
REQUIRED_BRIDGE_CASE_KIND = "bridge-equality-proof"
REQUIRED_READINESS_STATUS = "blocked-certificate-ready-proof-open"
REQUIRED_PREDECESSOR_CASE_KINDS = (
    "diagonal-instance-closure",
    "substitution-representability-proof",
    "substitution-graph-correctness-proof",
)
REQUIRED_NON_CLAIMS = (
    "no diagonal-instance closure proof",
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_BRIDGE_READINESS_PATH = (
    "claims/fixed_point_bridge_equality_proof_closure_readiness.json"
)
EXPECTED_PREDECESSOR_PATHS = {
    "diagonal-instance-closure": (
        "claims/fixed_point_diagonal_instance_closure_proof_readiness.json"
    ),
    "substitution-representability-proof": (
        "claims/fixed_point_substitution_representability_proof_readiness.json"
    ),
    "substitution-graph-correctness-proof": (
        "claims/fixed_point_substitution_graph_correctness_proof_readiness.json"
    ),
}
PROOF_PROMOTION_NON_CLAIMS = {
    "diagonal-instance closure proof",
    "substitution representability proof",
    "substitution graph correctness proof",
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "self-consistency theorem",
}


@dataclass(frozen=True)
class FixedPointBridgePredecessorProofReadinessCoverageManifest:
    """Loaded manifest for bridge predecessor readiness coverage."""

    path: Path
    schema_version: int
    coverage_id: str
    reviewed_at: str
    purpose: str
    bridge_equality_readiness_path: str
    predecessor_readiness_paths: dict[str, str]
    expected_bridge_case_kind: str
    expected_bridge_readiness_status: str
    expected_predecessor_case_kinds: tuple[str, ...]
    expected_predecessor_readiness_status: str
    expected_predecessor_readiness_count: int
    expected_missing_predecessor_readiness_count: int
    expected_certificate_ready_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointBridgePredecessorReadinessEntry:
    """One observed predecessor proof-readiness handoff."""

    case_kind: str
    readiness_id: str
    readiness_status: str
    certificate_ready: bool
    accepted: bool
    proof_boundary_preserved: bool
    failed_subjects: tuple[str, ...]

    @property
    def proof_open(self) -> bool:
        """Return whether the predecessor remains proof-open."""

        return self.readiness_status == REQUIRED_READINESS_STATUS


@dataclass(frozen=True)
class FixedPointBridgePredecessorProofReadinessCoverageValidation:
    """One validation result for the aggregate coverage surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointBridgePredecessorProofReadinessCoverageReport:
    """Validation report for bridge predecessor proof-readiness coverage."""

    manifest: FixedPointBridgePredecessorProofReadinessCoverageManifest
    bridge_equality_readiness_path: Path
    predecessor_readiness_paths: dict[str, Path]
    willard_map_path: Path
    bridge_readiness_accepted: bool
    bridge_case_kind: str
    bridge_readiness_status: str
    bridge_open_proof_blocker_case_kinds: tuple[str, ...]
    predecessor_entries: tuple[FixedPointBridgePredecessorReadinessEntry, ...]
    missing_predecessor_case_kinds: tuple[str, ...]
    proof_boundary_preserved: bool
    results: tuple[
        FixedPointBridgePredecessorProofReadinessCoverageValidation,
        ...,
    ]

    @property
    def accepted(self) -> bool:
        """Return whether every coverage validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def predecessor_readiness_count(self) -> int:
        """Return the number of observed predecessor readiness entries."""

        return len(self.predecessor_entries)

    @property
    def missing_predecessor_readiness_count(self) -> int:
        """Return how many expected predecessor readiness handoffs are missing."""

        return len(self.missing_predecessor_case_kinds)

    @property
    def certificate_ready_count(self) -> int:
        """Return the number of certificate-ready predecessor handoffs."""

        return sum(1 for entry in self.predecessor_entries if entry.certificate_ready)

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


def load_fixed_point_bridge_predecessor_proof_readiness_coverage(
    path: Path | str = DEFAULT_COVERAGE,
) -> FixedPointBridgePredecessorProofReadinessCoverageManifest:
    """Load the bridge predecessor proof-readiness coverage manifest."""

    coverage_path = Path(path)
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    predecessor_paths = data.get("predecessor_readiness_paths")
    if not isinstance(predecessor_paths, dict):
        raise ValueError("predecessor_readiness_paths must be an object")
    if not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in predecessor_paths.items()
    ):
        raise ValueError("predecessor_readiness_paths must map text to text")
    return FixedPointBridgePredecessorProofReadinessCoverageManifest(
        path=coverage_path,
        schema_version=_required_int(data, "schema_version"),
        coverage_id=_required_text(data, "coverage_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        bridge_equality_readiness_path=_required_text(
            data,
            "bridge_equality_readiness_path",
        ),
        predecessor_readiness_paths=dict(predecessor_paths),
        expected_bridge_case_kind=_required_text(data, "expected_bridge_case_kind"),
        expected_bridge_readiness_status=_required_text(
            data,
            "expected_bridge_readiness_status",
        ),
        expected_predecessor_case_kinds=tuple(
            _required_text_list(data, "expected_predecessor_case_kinds")
        ),
        expected_predecessor_readiness_status=_required_text(
            data,
            "expected_predecessor_readiness_status",
        ),
        expected_predecessor_readiness_count=_required_int(
            data,
            "expected_predecessor_readiness_count",
        ),
        expected_missing_predecessor_readiness_count=_required_int(
            data,
            "expected_missing_predecessor_readiness_count",
        ),
        expected_certificate_ready_count=_required_int(
            data,
            "expected_certificate_ready_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_bridge_predecessor_proof_readiness_coverage(
    manifest: FixedPointBridgePredecessorProofReadinessCoverageManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointBridgePredecessorProofReadinessCoverageReport:
    """Validate bridge predecessor proof-readiness coverage."""

    checked_willard_map_path = Path(willard_map_path)
    bridge_path = _resolve_path(manifest.path, manifest.bridge_equality_readiness_path)
    predecessor_paths = {
        case_kind: _resolve_path(manifest.path, path)
        for case_kind, path in manifest.predecessor_readiness_paths.items()
    }
    results: list[
        FixedPointBridgePredecessorProofReadinessCoverageValidation
    ] = [_accepted("manifest", f"loaded {manifest.coverage_id}")]
    results.extend(_validate_manifest(manifest))

    bridge_report = _load_bridge_readiness(bridge_path, checked_willard_map_path)
    predecessor_reports = {
        case_kind: _load_predecessor_readiness(
            case_kind,
            predecessor_paths.get(case_kind, Path()),
            checked_willard_map_path,
        )
        for case_kind in manifest.expected_predecessor_case_kinds
    }
    results.extend(_validate_dependencies(bridge_report, predecessor_reports))

    bridge_entry = getattr(bridge_report, "readiness_entry", None)
    bridge_case_kind = str(getattr(bridge_entry, "case_kind", ""))
    bridge_readiness_status = str(getattr(bridge_entry, "readiness_status", ""))
    bridge_blockers = tuple(
        getattr(bridge_entry, "open_proof_blocker_case_kinds", ())
    )
    predecessor_entries = tuple(
        _readiness_entry(case_kind, predecessor_reports[case_kind])
        for case_kind in manifest.expected_predecessor_case_kinds
        if bool(getattr(predecessor_reports[case_kind], "accepted", False))
    )
    observed_case_kinds = tuple(entry.case_kind for entry in predecessor_entries)
    missing_predecessors = tuple(
        case_kind
        for case_kind in manifest.expected_predecessor_case_kinds
        if case_kind not in observed_case_kinds
    )
    proof_boundary_preserved = (
        bool(getattr(bridge_report, "accepted", False))
        and bool(getattr(bridge_report, "proof_boundary_preserved", False))
        and bridge_case_kind == manifest.expected_bridge_case_kind
        and bridge_readiness_status == manifest.expected_bridge_readiness_status
        and bridge_blockers == manifest.expected_predecessor_case_kinds
        and missing_predecessors == ()
        and all(entry.accepted for entry in predecessor_entries)
        and all(entry.proof_boundary_preserved for entry in predecessor_entries)
        and all(entry.proof_open for entry in predecessor_entries)
    )
    results.extend(
        _validate_coverage(
            manifest,
            bridge_case_kind,
            bridge_readiness_status,
            bridge_blockers,
            predecessor_entries,
            missing_predecessors,
            proof_boundary_preserved,
        )
    )

    return FixedPointBridgePredecessorProofReadinessCoverageReport(
        manifest=manifest,
        bridge_equality_readiness_path=bridge_path,
        predecessor_readiness_paths=predecessor_paths,
        willard_map_path=checked_willard_map_path,
        bridge_readiness_accepted=bool(getattr(bridge_report, "accepted", False)),
        bridge_case_kind=bridge_case_kind,
        bridge_readiness_status=bridge_readiness_status,
        bridge_open_proof_blocker_case_kinds=bridge_blockers,
        predecessor_entries=predecessor_entries,
        missing_predecessor_case_kinds=missing_predecessors,
        proof_boundary_preserved=proof_boundary_preserved,
        results=tuple(results),
    )


def fixed_point_bridge_predecessor_proof_readiness_coverage_payload(
    report: FixedPointBridgePredecessorProofReadinessCoverageReport,
) -> dict[str, Any]:
    """Return a JSON-ready coverage payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "coverage_manifest": str(report.manifest.path),
        "coverage_id": report.manifest.coverage_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "bridge_equality_readiness_path": str(report.bridge_equality_readiness_path),
        "predecessor_readiness_paths": {
            key: str(value)
            for key, value in report.predecessor_readiness_paths.items()
        },
        "willard_map": str(report.willard_map_path),
        "observed_bridge_readiness_accepted": report.bridge_readiness_accepted,
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "bridge_case_kind": report.bridge_case_kind,
        "bridge_readiness_status": report.bridge_readiness_status,
        "bridge_open_proof_blocker_case_kinds": list(
            report.bridge_open_proof_blocker_case_kinds
        ),
        "predecessor_readiness_count": report.predecessor_readiness_count,
        "missing_predecessor_readiness_count": (
            report.missing_predecessor_readiness_count
        ),
        "missing_predecessor_case_kinds": list(report.missing_predecessor_case_kinds),
        "certificate_ready_count": report.certificate_ready_count,
        "predecessor_readiness_entries": [
            _predecessor_entry_payload(entry) for entry in report.predecessor_entries
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


def format_fixed_point_bridge_predecessor_proof_readiness_coverage_report(
    report: FixedPointBridgePredecessorProofReadinessCoverageReport,
) -> str:
    """Format a concise text report for the aggregate readiness coverage."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point bridge predecessor proof-readiness coverage: {status}",
        f"Coverage: {report.manifest.coverage_id}",
        f"Bridge case: {report.bridge_case_kind}",
        f"Bridge readiness status: {report.bridge_readiness_status}",
        "Open proof blockers: "
        + _joined_or_none(report.bridge_open_proof_blocker_case_kinds),
        f"Predecessor readiness entries: {report.predecessor_readiness_count}",
        "Missing predecessor readiness: "
        + _joined_or_none(report.missing_predecessor_case_kinds),
        f"Certificate-ready predecessors: {report.certificate_ready_count}",
        "Proof boundary preserved: "
        + str(report.proof_boundary_preserved).lower(),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Predecessors:")
    for entry in report.predecessor_entries:
        lines.append(
            f"- {entry.case_kind}: {entry.readiness_status}; "
            f"certificate_ready={str(entry.certificate_ready).lower()}"
        )
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_bridge_predecessor_proof_readiness_coverage_cli(
    argv: list[str] | None = None,
) -> int:
    """Run bridge predecessor proof-readiness coverage validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_bridge_predecessor_proof_readiness_coverage"
        ),
        description=(
            "Validate aggregate proof-readiness coverage for bridge-equality "
            "predecessor blockers."
        ),
    )
    parser.add_argument(
        "--coverage",
        default=str(DEFAULT_COVERAGE),
        help="Path to the bridge predecessor readiness coverage manifest.",
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

    manifest = load_fixed_point_bridge_predecessor_proof_readiness_coverage(
        args.coverage
    )
    report = validate_fixed_point_bridge_predecessor_proof_readiness_coverage(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_bridge_predecessor_proof_readiness_coverage_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_bridge_predecessor_proof_readiness_coverage_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _load_bridge_readiness(path: Path, willard_map_path: Path) -> Any:
    """Load and validate the bridge-equality readiness dependency."""

    try:
        manifest = load_fixed_point_bridge_equality_proof_closure_readiness(path)
        return validate_fixed_point_bridge_equality_proof_closure_readiness(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-bridge-equality-readiness-load",),
        )


def _load_predecessor_readiness(
    case_kind: str,
    path: Path,
    willard_map_path: Path,
) -> Any:
    """Load and validate one predecessor readiness dependency."""

    loaders: dict[str, tuple[Callable[[Path], Any], Callable[[Any, Path], Any]]] = {
        "diagonal-instance-closure": (
            load_fixed_point_diagonal_instance_closure_proof_readiness,
            validate_fixed_point_diagonal_instance_closure_proof_readiness,
        ),
        "substitution-representability-proof": (
            load_fixed_point_substitution_representability_proof_readiness,
            validate_fixed_point_substitution_representability_proof_readiness,
        ),
        "substitution-graph-correctness-proof": (
            load_fixed_point_substitution_graph_correctness_proof_readiness,
            validate_fixed_point_substitution_graph_correctness_proof_readiness,
        ),
    }
    if case_kind not in loaders:
        return _DependencyFailure(False, ("unknown-predecessor-readiness",))
    load_manifest, validate_manifest = loaders[case_kind]
    try:
        manifest = load_manifest(path)
        return validate_manifest(manifest, willard_map_path)
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(f"{case_kind}-readiness-load",),
        )


def _validate_manifest(
    manifest: FixedPointBridgePredecessorProofReadinessCoverageManifest,
) -> list[FixedPointBridgePredecessorProofReadinessCoverageValidation]:
    """Validate manifest constants and proof-boundary guardrails."""

    return [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "coverage_id",
            manifest.coverage_id == REQUIRED_COVERAGE_ID,
            "coverage id matches",
            "unexpected coverage id",
        ),
        _check(
            "bridge_equality_readiness_path",
            manifest.bridge_equality_readiness_path == EXPECTED_BRIDGE_READINESS_PATH,
            "bridge readiness path matches",
        ),
        _check(
            "predecessor_readiness_paths",
            manifest.predecessor_readiness_paths == EXPECTED_PREDECESSOR_PATHS,
            "predecessor readiness paths match",
            "predecessor readiness path mismatch",
        ),
        _check(
            "expected_bridge_case_kind",
            manifest.expected_bridge_case_kind == REQUIRED_BRIDGE_CASE_KIND,
            "bridge case kind matches",
        ),
        _check(
            "expected_bridge_readiness_status",
            manifest.expected_bridge_readiness_status == REQUIRED_READINESS_STATUS,
            "bridge readiness status matches",
        ),
        _check(
            "expected_predecessor_case_kinds",
            manifest.expected_predecessor_case_kinds
            == REQUIRED_PREDECESSOR_CASE_KINDS,
            "predecessor case kinds match",
            "predecessor case kind mismatch",
        ),
        _check(
            "expected_predecessor_readiness_status",
            manifest.expected_predecessor_readiness_status
            == REQUIRED_READINESS_STATUS,
            "predecessor readiness status matches",
        ),
        _check(
            "expected_predecessor_readiness_count",
            manifest.expected_predecessor_readiness_count
            == len(REQUIRED_PREDECESSOR_CASE_KINDS),
            "predecessor readiness count matches",
        ),
        _check(
            "expected_missing_predecessor_readiness_count",
            manifest.expected_missing_predecessor_readiness_count == 0,
            "missing predecessor readiness count matches",
        ),
        _check(
            "expected_certificate_ready_count",
            manifest.expected_certificate_ready_count
            == len(REQUIRED_PREDECESSOR_CASE_KINDS),
            "certificate-ready count matches",
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
    ]


def _validate_dependencies(
    bridge_report: Any,
    predecessor_reports: dict[str, Any],
) -> list[FixedPointBridgePredecessorProofReadinessCoverageValidation]:
    """Validate all dependencies accepted before deriving coverage."""

    results = [
        _check(
            "bridge_equality_readiness",
            bool(getattr(bridge_report, "accepted", False)),
            "bridge readiness accepted",
            "bridge readiness rejected: "
            + _joined_or_none(getattr(bridge_report, "failed_subjects", ())),
        )
    ]
    for case_kind, report in predecessor_reports.items():
        results.append(
            _check(
                f"predecessor_readiness:{case_kind}",
                bool(getattr(report, "accepted", False)),
                f"{case_kind} readiness accepted",
                f"{case_kind} readiness rejected: "
                + _joined_or_none(getattr(report, "failed_subjects", ())),
            )
        )
    return results


def _validate_coverage(
    manifest: FixedPointBridgePredecessorProofReadinessCoverageManifest,
    bridge_case_kind: str,
    bridge_readiness_status: str,
    bridge_blockers: tuple[str, ...],
    predecessor_entries: tuple[FixedPointBridgePredecessorReadinessEntry, ...],
    missing_predecessors: tuple[str, ...],
    proof_boundary_preserved: bool,
) -> list[FixedPointBridgePredecessorProofReadinessCoverageValidation]:
    """Validate observed bridge predecessor readiness coverage."""

    observed_case_kinds = tuple(entry.case_kind for entry in predecessor_entries)
    return [
        _check(
            "bridge_case_kind",
            bridge_case_kind == manifest.expected_bridge_case_kind,
            "bridge case kind matches",
        ),
        _check(
            "bridge_readiness_status",
            bridge_readiness_status == manifest.expected_bridge_readiness_status,
            "bridge readiness status matches",
        ),
        _check(
            "bridge_open_proof_blockers",
            bridge_blockers == manifest.expected_predecessor_case_kinds,
            "bridge open proof blockers match predecessor cases",
            "bridge open proof blocker mismatch",
        ),
        _check(
            "predecessor_case_kinds",
            observed_case_kinds == manifest.expected_predecessor_case_kinds,
            "predecessor case kinds match",
            "predecessor case kind mismatch",
        ),
        _check(
            "predecessor_readiness_count",
            len(predecessor_entries)
            == manifest.expected_predecessor_readiness_count,
            "predecessor readiness count matches",
            "predecessor readiness count mismatch",
        ),
        _check(
            "missing_predecessor_readiness_count",
            len(missing_predecessors)
            == manifest.expected_missing_predecessor_readiness_count,
            "missing predecessor readiness count matches",
            "missing predecessor readiness count mismatch",
        ),
        _check(
            "certificate_ready_count",
            sum(1 for entry in predecessor_entries if entry.certificate_ready)
            == manifest.expected_certificate_ready_count,
            "certificate-ready count matches",
            "certificate-ready count mismatch",
        ),
        _check(
            "predecessor_readiness_status",
            all(
                entry.readiness_status
                == manifest.expected_predecessor_readiness_status
                for entry in predecessor_entries
            ),
            "predecessor readiness statuses match",
            "predecessor readiness status mismatch",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
        ),
    ]


def _readiness_entry(
    case_kind: str,
    report: Any,
) -> FixedPointBridgePredecessorReadinessEntry:
    """Extract the common readiness fields from a predecessor report."""

    entry = getattr(report, "readiness_entry", None)
    return FixedPointBridgePredecessorReadinessEntry(
        case_kind=str(getattr(entry, "case_kind", case_kind)),
        readiness_id=str(getattr(getattr(report, "manifest", None), "readiness_id", "")),
        readiness_status=str(getattr(entry, "readiness_status", "")),
        certificate_ready=bool(getattr(entry, "certificate_ready", False)),
        accepted=bool(getattr(entry, "accepted", False))
        and bool(getattr(report, "accepted", False)),
        proof_boundary_preserved=bool(
            getattr(report, "proof_boundary_preserved", False)
        ),
        failed_subjects=tuple(getattr(report, "failed_subjects", ())),
    )


def _predecessor_entry_payload(
    entry: FixedPointBridgePredecessorReadinessEntry,
) -> dict[str, Any]:
    """Return a JSON-ready predecessor readiness entry."""

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


def _resolve_path(base_path: Path, value: str) -> Path:
    """Resolve a manifest-local path while preserving root-relative paths."""

    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    candidate = base_path.parent / path
    if candidate.exists():
        return candidate
    return path


def _required_text(data: dict[str, Any], key: str) -> str:
    """Return a required non-empty text field."""

    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    """Return a required integer field."""

    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    """Return a required list of non-empty text values."""

    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{key} must contain non-empty text")
    return value


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointBridgePredecessorProofReadinessCoverageValidation:
    """Return an accepted validation result."""

    return FixedPointBridgePredecessorProofReadinessCoverageValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _check(
    subject: str,
    condition: bool,
    accepted_detail: str,
    rejected_detail: str | None = None,
) -> FixedPointBridgePredecessorProofReadinessCoverageValidation:
    """Return a validation result from a boolean condition."""

    return FixedPointBridgePredecessorProofReadinessCoverageValidation(
        subject=subject,
        accepted=condition,
        detail=accepted_detail if condition else rejected_detail or accepted_detail,
    )


def _non_claims_are_guarded(non_claims: tuple[str, ...]) -> bool:
    """Return whether every proof-promotion phrase is explicitly negated."""

    return all(f"no {claim}" in non_claims for claim in PROOF_PROMOTION_NON_CLAIMS)


def _failed_subject_for_result(subject: str) -> str:
    """Map verbose result subjects to stable failure subjects."""

    if subject == "bridge_equality_readiness" or subject.startswith(
        "predecessor_readiness:"
    ):
        return "fixed-point-bridge-predecessor-proof-readiness-coverage-dependencies"
    if subject in {
        "expected_predecessor_case_kinds",
        "predecessor_case_kinds",
        "bridge_open_proof_blockers",
        "predecessor_readiness_count",
        "missing_predecessor_readiness_count",
        "certificate_ready_count",
        "predecessor_readiness_status",
    }:
        return "fixed-point-bridge-predecessor-proof-readiness-coverage-predecessors"
    if subject in {"non_claims", "non_claim_promotion_boundary"}:
        return "fixed-point-bridge-predecessor-proof-readiness-coverage-non-claim"
    if subject == "proof_boundary":
        return "fixed-point-bridge-predecessor-proof-readiness-coverage-boundary"
    if subject.startswith("expected_") or subject in {
        "coverage_id",
        "schema_version",
        "bridge_equality_readiness_path",
        "predecessor_readiness_paths",
    }:
        return "fixed-point-bridge-predecessor-proof-readiness-coverage-manifest"
    return (
        "fixed-point-bridge-predecessor-proof-readiness-coverage-"
        + subject.replace("_", "-").replace(":", "-")
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    """Return a comma-joined list or ``none`` for empty sequences."""

    if not values:
        return "none"
    return ", ".join(values)


def main() -> int:
    """Module entrypoint."""

    return run_fixed_point_bridge_predecessor_proof_readiness_coverage_cli()


if __name__ == "__main__":
    raise SystemExit(main())
