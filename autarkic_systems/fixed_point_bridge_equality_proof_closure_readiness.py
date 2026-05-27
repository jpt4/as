"""Proof-closure readiness for the fixed-point bridge-equality case.

ADR-0311 composes the expanded predecessor certificate coverage, the compact
bridge-equality frontier status, and the bridge-equality finite certificate.
The result is intentionally narrow: it says the bridge-equality case is
certificate-ready, but it also preserves that all predecessor proof blockers
are still open and bridge equality has not been proved.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_bridge_equality_certificate import (
    load_fixed_point_bridge_equality_certificate,
    validate_fixed_point_bridge_equality_certificate,
)
from autarkic_systems.fixed_point_bridge_equality_frontier_status import (
    load_fixed_point_bridge_equality_frontier_status,
    validate_fixed_point_bridge_equality_frontier_status,
)
from autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage import (
    load_fixed_point_expanded_available_predecessor_certificate_coverage,
    validate_fixed_point_expanded_available_predecessor_certificate_coverage,
)


DEFAULT_READINESS = Path("claims/fixed_point_bridge_equality_proof_closure_readiness.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CASE_KIND = "bridge-equality-proof"
REQUIRED_READINESS_STATUS = "blocked-certificate-ready-proof-open"
REQUIRED_PREDECESSOR_CASE_KINDS = (
    "diagonal-instance-closure",
    "substitution-representability-proof",
    "substitution-graph-correctness-proof",
)
REQUIRED_OPEN_PROOF_BLOCKERS = REQUIRED_PREDECESSOR_CASE_KINDS
REQUIRED_NON_CLAIMS = (
    "no diagonal-instance closure proof",
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "expanded_available_predecessor_certificate_coverage_path": (
        "claims/fixed_point_expanded_available_predecessor_certificate_coverage.json"
    ),
    "bridge_equality_frontier_status_path": (
        "claims/fixed_point_bridge_equality_frontier_status.json"
    ),
    "bridge_equality_certificate_path": (
        "claims/fixed_point_bridge_equality_certificate.json"
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
class FixedPointBridgeEqualityProofClosureReadinessManifest:
    """Loaded manifest for bridge-equality proof-closure readiness."""

    path: Path
    schema_version: int
    readiness_id: str
    reviewed_at: str
    purpose: str
    expanded_available_predecessor_certificate_coverage_path: str
    bridge_equality_frontier_status_path: str
    bridge_equality_certificate_path: str
    expected_readiness_case_kind: str
    expected_readiness_status: str
    expected_predecessor_case_kinds: tuple[str, ...]
    expected_certificate_covered_predecessor_case_kinds: tuple[str, ...]
    expected_missing_certificate_predecessor_case_kinds: tuple[str, ...]
    expected_open_proof_blocker_case_kinds: tuple[str, ...]
    expected_available_predecessor_certificate_count: int
    expected_missing_certificate_predecessor_count: int
    expected_open_proof_blocker_count: int
    expected_bridge_equality_certificate_step_count: int
    expected_bridge_equality_frontier_status: str
    expected_bridge_equality_frontier_blocker: str
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityProofClosureReadinessEntry:
    """Readiness state for the still-open bridge-equality proof case."""

    case_kind: str
    readiness_status: str
    predecessor_case_kinds: tuple[str, ...]
    certificate_covered_predecessor_case_kinds: tuple[str, ...]
    missing_certificate_predecessor_case_kinds: tuple[str, ...]
    open_proof_blocker_case_kinds: tuple[str, ...]

    @property
    def predecessor_count(self) -> int:
        """Return the number of predecessor proof cases."""

        return len(self.predecessor_case_kinds)

    @property
    def available_predecessor_certificate_count(self) -> int:
        """Return how many predecessor cases have certificate support."""

        return len(self.certificate_covered_predecessor_case_kinds)

    @property
    def missing_certificate_predecessor_count(self) -> int:
        """Return how many predecessor cases lack certificate support."""

        return len(self.missing_certificate_predecessor_case_kinds)

    @property
    def open_proof_blocker_count(self) -> int:
        """Return how many predecessor proofs remain open blockers."""

        return len(self.open_proof_blocker_case_kinds)

    @property
    def accepted(self) -> bool:
        """Return whether this readiness entry has the expected blocked status."""

        return (
            self.case_kind == REQUIRED_CASE_KIND
            and self.readiness_status == REQUIRED_READINESS_STATUS
            and self.missing_certificate_predecessor_count == 0
            and self.open_proof_blocker_count > 0
        )


@dataclass(frozen=True)
class FixedPointBridgeEqualityProofClosureReadinessValidation:
    """One validation result for bridge-equality proof-closure readiness."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityProofClosureReadinessReport:
    """Validation report for bridge-equality proof-closure readiness."""

    manifest: FixedPointBridgeEqualityProofClosureReadinessManifest
    expanded_available_predecessor_certificate_coverage_path: Path
    bridge_equality_frontier_status_path: Path
    bridge_equality_certificate_path: Path
    willard_map_path: Path
    expanded_coverage_accepted: bool
    bridge_frontier_accepted: bool
    bridge_certificate_accepted: bool
    bridge_equality_frontier_status: str
    bridge_equality_frontier_blocker: str
    bridge_equality_certificate_step_count: int
    proof_boundary_preserved: bool
    readiness_entry: FixedPointBridgeEqualityProofClosureReadinessEntry
    results: tuple[FixedPointBridgeEqualityProofClosureReadinessValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every readiness validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return compact failure subjects for automation and reports."""

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
    coverage_entries: tuple[Any, ...] = ()
    certificates: tuple[Any, ...] = ()
    frontier_status: str = ""
    frontier_blocked_by: str = ""
    certificate_step_count: int = 0


def load_fixed_point_bridge_equality_proof_closure_readiness(
    path: Path | str = DEFAULT_READINESS,
) -> FixedPointBridgeEqualityProofClosureReadinessManifest:
    """Load the bridge-equality proof-closure readiness manifest."""

    readiness_path = Path(path)
    data = json.loads(readiness_path.read_text(encoding="utf-8"))
    return FixedPointBridgeEqualityProofClosureReadinessManifest(
        path=readiness_path,
        schema_version=_required_int(data, "schema_version"),
        readiness_id=_required_text(data, "readiness_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        expanded_available_predecessor_certificate_coverage_path=_required_text(
            data,
            "expanded_available_predecessor_certificate_coverage_path",
        ),
        bridge_equality_frontier_status_path=_required_text(
            data,
            "bridge_equality_frontier_status_path",
        ),
        bridge_equality_certificate_path=_required_text(
            data,
            "bridge_equality_certificate_path",
        ),
        expected_readiness_case_kind=_required_text(
            data,
            "expected_readiness_case_kind",
        ),
        expected_readiness_status=_required_text(data, "expected_readiness_status"),
        expected_predecessor_case_kinds=tuple(
            _required_text_list(data, "expected_predecessor_case_kinds")
        ),
        expected_certificate_covered_predecessor_case_kinds=tuple(
            _required_text_list(
                data,
                "expected_certificate_covered_predecessor_case_kinds",
            )
        ),
        expected_missing_certificate_predecessor_case_kinds=tuple(
            _required_text_list(
                data,
                "expected_missing_certificate_predecessor_case_kinds",
            )
        ),
        expected_open_proof_blocker_case_kinds=tuple(
            _required_text_list(data, "expected_open_proof_blocker_case_kinds")
        ),
        expected_available_predecessor_certificate_count=_required_int(
            data,
            "expected_available_predecessor_certificate_count",
        ),
        expected_missing_certificate_predecessor_count=_required_int(
            data,
            "expected_missing_certificate_predecessor_count",
        ),
        expected_open_proof_blocker_count=_required_int(
            data,
            "expected_open_proof_blocker_count",
        ),
        expected_bridge_equality_certificate_step_count=_required_int(
            data,
            "expected_bridge_equality_certificate_step_count",
        ),
        expected_bridge_equality_frontier_status=_required_text(
            data,
            "expected_bridge_equality_frontier_status",
        ),
        expected_bridge_equality_frontier_blocker=_required_text(
            data,
            "expected_bridge_equality_frontier_blocker",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_bridge_equality_proof_closure_readiness(
    manifest: FixedPointBridgeEqualityProofClosureReadinessManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointBridgeEqualityProofClosureReadinessReport:
    """Validate bridge-equality proof-closure readiness."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointBridgeEqualityProofClosureReadinessValidation] = [
        _accepted("manifest", f"loaded {manifest.readiness_id}")
    ]
    results.extend(_validate_manifest(manifest))

    expanded_coverage_report = _load_expanded_coverage(
        paths["expanded_available_predecessor_certificate_coverage_path"],
        checked_willard_map_path,
    )
    bridge_frontier_report = _load_bridge_frontier(
        paths["bridge_equality_frontier_status_path"],
    )
    bridge_certificate_report = _load_bridge_certificate(
        paths["bridge_equality_certificate_path"],
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(
            expanded_coverage_report,
            bridge_frontier_report,
            bridge_certificate_report,
        )
    )

    readiness_entry = _derive_readiness_entry(expanded_coverage_report)
    proof_boundary_preserved = (
        bool(getattr(expanded_coverage_report, "proof_boundary_preserved", False))
        and bool(getattr(bridge_frontier_report, "accepted", False))
        and bool(getattr(bridge_certificate_report, "accepted", False))
        and readiness_entry.open_proof_blocker_count > 0
    )
    results.extend(
        _validate_readiness(
            manifest,
            readiness_entry,
            bridge_frontier_report,
            bridge_certificate_report,
            proof_boundary_preserved,
        )
    )

    return FixedPointBridgeEqualityProofClosureReadinessReport(
        manifest=manifest,
        expanded_available_predecessor_certificate_coverage_path=paths[
            "expanded_available_predecessor_certificate_coverage_path"
        ],
        bridge_equality_frontier_status_path=paths[
            "bridge_equality_frontier_status_path"
        ],
        bridge_equality_certificate_path=paths["bridge_equality_certificate_path"],
        willard_map_path=checked_willard_map_path,
        expanded_coverage_accepted=bool(getattr(expanded_coverage_report, "accepted", False)),
        bridge_frontier_accepted=bool(getattr(bridge_frontier_report, "accepted", False)),
        bridge_certificate_accepted=bool(
            getattr(bridge_certificate_report, "accepted", False)
        ),
        bridge_equality_frontier_status=getattr(
            bridge_frontier_report,
            "frontier_status",
            "",
        ),
        bridge_equality_frontier_blocker=getattr(
            bridge_frontier_report,
            "frontier_blocked_by",
            "",
        ),
        bridge_equality_certificate_step_count=int(
            getattr(bridge_certificate_report, "certificate_step_count", 0)
        ),
        proof_boundary_preserved=proof_boundary_preserved,
        readiness_entry=readiness_entry,
        results=tuple(results),
    )


def fixed_point_bridge_equality_proof_closure_readiness_payload(
    report: FixedPointBridgeEqualityProofClosureReadinessReport,
) -> dict[str, Any]:
    """Return a JSON-ready proof-closure readiness payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "readiness_manifest": str(report.manifest.path),
        "readiness_id": report.manifest.readiness_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "expanded_available_predecessor_certificate_coverage_path": str(
            report.expanded_available_predecessor_certificate_coverage_path
        ),
        "bridge_equality_frontier_status_path": str(
            report.bridge_equality_frontier_status_path
        ),
        "bridge_equality_certificate_path": str(
            report.bridge_equality_certificate_path
        ),
        "willard_map": str(report.willard_map_path),
        "observed_expanded_coverage_accepted": report.expanded_coverage_accepted,
        "observed_bridge_frontier_accepted": report.bridge_frontier_accepted,
        "observed_bridge_certificate_accepted": report.bridge_certificate_accepted,
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "bridge_equality_frontier_status": report.bridge_equality_frontier_status,
        "bridge_equality_frontier_blocker": report.bridge_equality_frontier_blocker,
        "bridge_equality_certificate_step_count": (
            report.bridge_equality_certificate_step_count
        ),
        "readiness_entry": _readiness_entry_payload(report.readiness_entry),
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


def format_fixed_point_bridge_equality_proof_closure_readiness_report(
    report: FixedPointBridgeEqualityProofClosureReadinessReport,
) -> str:
    """Format a concise bridge-equality proof-closure readiness report."""

    status = "accepted" if report.accepted else "rejected"
    entry = report.readiness_entry
    lines = [
        f"Fixed-point bridge equality proof-closure readiness: {status}",
        f"Readiness: {report.manifest.readiness_id}",
        f"Case: {entry.case_kind}",
        f"Readiness status: {entry.readiness_status}",
        "Available predecessor certificates: "
        + str(entry.available_predecessor_certificate_count),
        "Missing predecessor certificates: "
        + _joined_or_none(entry.missing_certificate_predecessor_case_kinds),
        "Open proof blockers: " + _joined_or_none(entry.open_proof_blocker_case_kinds),
        (
            "Bridge frontier: "
            + report.bridge_equality_frontier_status
            + " by "
            + report.bridge_equality_frontier_blocker
        ),
        "Bridge certificate steps: "
        + str(report.bridge_equality_certificate_step_count),
        "Proof boundary preserved: " + str(report.proof_boundary_preserved).lower(),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_bridge_equality_proof_closure_readiness_cli(
    argv: list[str] | None = None,
) -> int:
    """Run bridge-equality proof-closure readiness validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_bridge_equality_proof_closure_readiness"
        ),
        description=(
            "Validate certificate-ready/proof-open readiness for the AS "
            "fixed-point bridge-equality proof case."
        ),
    )
    parser.add_argument(
        "--readiness",
        default=str(DEFAULT_READINESS),
        help="Path to the bridge-equality proof-closure readiness manifest.",
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

    manifest = load_fixed_point_bridge_equality_proof_closure_readiness(
        args.readiness
    )
    report = validate_fixed_point_bridge_equality_proof_closure_readiness(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_bridge_equality_proof_closure_readiness_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_bridge_equality_proof_closure_readiness_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointBridgeEqualityProofClosureReadinessManifest,
) -> dict[str, Path]:
    """Return dependency paths resolved relative to the manifest location."""

    return {
        "expanded_available_predecessor_certificate_coverage_path": _resolve_path(
            manifest.path,
            manifest.expanded_available_predecessor_certificate_coverage_path,
        ),
        "bridge_equality_frontier_status_path": _resolve_path(
            manifest.path,
            manifest.bridge_equality_frontier_status_path,
        ),
        "bridge_equality_certificate_path": _resolve_path(
            manifest.path,
            manifest.bridge_equality_certificate_path,
        ),
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


def _load_expanded_coverage(path: Path, willard_map_path: Path) -> Any:
    """Load and validate expanded available predecessor certificate coverage."""

    try:
        manifest = load_fixed_point_expanded_available_predecessor_certificate_coverage(
            path
        )
        return validate_fixed_point_expanded_available_predecessor_certificate_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-expanded-available-predecessor-coverage-load",
            ),
        )


def _load_bridge_frontier(path: Path) -> Any:
    """Load and validate bridge-equality frontier status."""

    try:
        manifest = load_fixed_point_bridge_equality_frontier_status(path)
        return validate_fixed_point_bridge_equality_frontier_status(manifest)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-bridge-equality-frontier-load",),
        )


def _load_bridge_certificate(path: Path, willard_map_path: Path) -> Any:
    """Load and validate bridge-equality finite certificate support."""

    try:
        manifest = load_fixed_point_bridge_equality_certificate(path)
        return validate_fixed_point_bridge_equality_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-bridge-equality-certificate-load",),
        )


def _validate_manifest(
    manifest: FixedPointBridgeEqualityProofClosureReadinessManifest,
) -> list[FixedPointBridgeEqualityProofClosureReadinessValidation]:
    """Validate manifest-local constants and non-claim guardrails."""

    return [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "readiness_id",
            (
                manifest.readiness_id
                == "as-fixed-point-bridge-equality-proof-closure-readiness-v1"
            ),
            "readiness id matches",
        ),
        *[
            _check(
                key,
                getattr(manifest, key) == expected,
                f"{expected} referenced",
            )
            for key, expected in EXPECTED_DEPENDENCY_PATHS.items()
        ],
        _check(
            "expected_readiness_case_kind",
            manifest.expected_readiness_case_kind == REQUIRED_CASE_KIND,
            "case kind matches",
        ),
        _check(
            "expected_readiness_status",
            manifest.expected_readiness_status == REQUIRED_READINESS_STATUS,
            "readiness status matches",
        ),
        _check(
            "expected_predecessor_case_kinds",
            manifest.expected_predecessor_case_kinds == REQUIRED_PREDECESSOR_CASE_KINDS,
            "predecessors match",
        ),
        _check(
            "expected_certificate_covered_predecessor_case_kinds",
            (
                manifest.expected_certificate_covered_predecessor_case_kinds
                == REQUIRED_PREDECESSOR_CASE_KINDS
            ),
            "covered predecessors match",
        ),
        _check(
            "expected_missing_certificate_predecessor_case_kinds",
            manifest.expected_missing_certificate_predecessor_case_kinds == (),
            "no missing predecessor certificates expected",
        ),
        _check(
            "expected_open_proof_blocker_case_kinds",
            manifest.expected_open_proof_blocker_case_kinds
            == REQUIRED_OPEN_PROOF_BLOCKERS,
            "open proof blockers match",
        ),
        _check(
            "expected_available_predecessor_certificate_count",
            manifest.expected_available_predecessor_certificate_count == 3,
            "three predecessor certificates expected",
        ),
        _check(
            "expected_missing_certificate_predecessor_count",
            manifest.expected_missing_certificate_predecessor_count == 0,
            "zero missing predecessor certificates expected",
        ),
        _check(
            "expected_open_proof_blocker_count",
            manifest.expected_open_proof_blocker_count == 3,
            "three open proof blockers expected",
        ),
        _check(
            "expected_bridge_equality_certificate_step_count",
            manifest.expected_bridge_equality_certificate_step_count == 6,
            "six bridge certificate steps expected",
        ),
        _check(
            "expected_bridge_equality_frontier_status",
            manifest.expected_bridge_equality_frontier_status == "blocked",
            "bridge frontier remains blocked",
        ),
        _check(
            "expected_bridge_equality_frontier_blocker",
            manifest.expected_bridge_equality_frontier_blocker
            == "bridge-equality-proof",
            "bridge frontier blocker preserved",
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
    expanded_coverage_report: Any,
    bridge_frontier_report: Any,
    bridge_certificate_report: Any,
) -> list[FixedPointBridgeEqualityProofClosureReadinessValidation]:
    """Validate that dependency reports accepted before readiness derivation."""

    return [
        _check(
            "expanded_available_predecessor_certificate_coverage",
            bool(getattr(expanded_coverage_report, "accepted", False)),
            "expanded coverage accepted",
            "expanded coverage rejected: "
            + _joined_or_none(getattr(expanded_coverage_report, "failed_subjects", ())),
        ),
        _check(
            "bridge_equality_frontier_status",
            bool(getattr(bridge_frontier_report, "accepted", False)),
            "bridge frontier accepted",
            "bridge frontier rejected: "
            + _joined_or_none(getattr(bridge_frontier_report, "failed_subjects", ())),
        ),
        _check(
            "bridge_equality_certificate",
            bool(getattr(bridge_certificate_report, "accepted", False)),
            "bridge certificate accepted",
            "bridge certificate rejected: "
            + _joined_or_none(
                getattr(bridge_certificate_report, "failed_subjects", ())
            ),
        ),
    ]


def _derive_readiness_entry(
    expanded_coverage_report: Any,
) -> FixedPointBridgeEqualityProofClosureReadinessEntry:
    """Derive the bridge-equality readiness entry from expanded coverage."""

    coverage_entry = None
    for entry in getattr(expanded_coverage_report, "coverage_entries", ()):
        if getattr(entry, "deferred_case_kind", "") == REQUIRED_CASE_KIND:
            coverage_entry = entry
            break
    if coverage_entry is None:
        return FixedPointBridgeEqualityProofClosureReadinessEntry(
            case_kind=REQUIRED_CASE_KIND,
            readiness_status=REQUIRED_READINESS_STATUS,
            predecessor_case_kinds=(),
            certificate_covered_predecessor_case_kinds=(),
            missing_certificate_predecessor_case_kinds=(),
            open_proof_blocker_case_kinds=(),
        )

    return FixedPointBridgeEqualityProofClosureReadinessEntry(
        case_kind=getattr(coverage_entry, "deferred_case_kind", ""),
        readiness_status=REQUIRED_READINESS_STATUS,
        predecessor_case_kinds=tuple(getattr(coverage_entry, "predecessor_case_kinds", ())),
        certificate_covered_predecessor_case_kinds=tuple(
            getattr(coverage_entry, "certificate_covered_predecessor_case_kinds", ())
        ),
        missing_certificate_predecessor_case_kinds=tuple(
            getattr(coverage_entry, "missing_certificate_predecessor_case_kinds", ())
        ),
        open_proof_blocker_case_kinds=tuple(
            getattr(coverage_entry, "open_proof_blocker_case_kinds", ())
        ),
    )


def _validate_readiness(
    manifest: FixedPointBridgeEqualityProofClosureReadinessManifest,
    entry: FixedPointBridgeEqualityProofClosureReadinessEntry,
    bridge_frontier_report: Any,
    bridge_certificate_report: Any,
    proof_boundary_preserved: bool,
) -> list[FixedPointBridgeEqualityProofClosureReadinessValidation]:
    """Validate derived bridge-equality readiness against manifest expectations."""

    return [
        _check(
            "readiness_case_kind",
            entry.case_kind == manifest.expected_readiness_case_kind,
            "readiness case kind matches",
        ),
        _check(
            "readiness_status",
            entry.readiness_status == manifest.expected_readiness_status,
            "readiness status matches",
        ),
        _check(
            "predecessor_case_kinds",
            entry.predecessor_case_kinds == manifest.expected_predecessor_case_kinds,
            "predecessors match",
        ),
        _check(
            "certificate_covered_predecessors",
            (
                entry.certificate_covered_predecessor_case_kinds
                == manifest.expected_certificate_covered_predecessor_case_kinds
            ),
            "covered predecessors match",
        ),
        _check(
            "missing_certificate_predecessors",
            (
                entry.missing_certificate_predecessor_case_kinds
                == manifest.expected_missing_certificate_predecessor_case_kinds
            ),
            "missing predecessor certificates match",
            "missing predecessor certificate mismatch",
        ),
        _check(
            "open_proof_blockers",
            (
                entry.open_proof_blocker_case_kinds
                == manifest.expected_open_proof_blocker_case_kinds
                and entry.open_proof_blocker_count
                == manifest.expected_open_proof_blocker_count
            ),
            "open proof blockers match",
            "open proof blocker mismatch",
        ),
        _check(
            "available_predecessor_certificate_count",
            (
                entry.available_predecessor_certificate_count
                == manifest.expected_available_predecessor_certificate_count
            ),
            "available predecessor certificate count matches",
        ),
        _check(
            "missing_certificate_predecessor_count",
            (
                entry.missing_certificate_predecessor_count
                == manifest.expected_missing_certificate_predecessor_count
            ),
            "missing predecessor certificate count matches",
        ),
        _check(
            "bridge_equality_frontier_status",
            (
                getattr(bridge_frontier_report, "frontier_status", "")
                == manifest.expected_bridge_equality_frontier_status
            ),
            "bridge frontier status matches",
        ),
        _check(
            "bridge_equality_frontier_blocker",
            (
                getattr(bridge_frontier_report, "frontier_blocked_by", "")
                == manifest.expected_bridge_equality_frontier_blocker
            ),
            "bridge frontier blocker matches",
        ),
        _check(
            "bridge_equality_certificate_step_count",
            (
                getattr(bridge_certificate_report, "certificate_step_count", 0)
                == manifest.expected_bridge_equality_certificate_step_count
            ),
            "bridge certificate step count matches",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
        ),
        _check(
            "readiness_entry",
            entry.accepted,
            "readiness entry remains certificate-ready and proof-open",
        ),
    ]


def _readiness_entry_payload(
    entry: FixedPointBridgeEqualityProofClosureReadinessEntry,
) -> dict[str, Any]:
    """Return a JSON-ready readiness entry."""

    return {
        "case_kind": entry.case_kind,
        "readiness_status": entry.readiness_status,
        "predecessor_case_kinds": list(entry.predecessor_case_kinds),
        "predecessor_count": entry.predecessor_count,
        "certificate_covered_predecessor_case_kinds": list(
            entry.certificate_covered_predecessor_case_kinds
        ),
        "available_predecessor_certificate_count": (
            entry.available_predecessor_certificate_count
        ),
        "missing_certificate_predecessor_case_kinds": list(
            entry.missing_certificate_predecessor_case_kinds
        ),
        "missing_certificate_predecessor_count": (
            entry.missing_certificate_predecessor_count
        ),
        "open_proof_blocker_case_kinds": list(entry.open_proof_blocker_case_kinds),
        "open_proof_blocker_count": entry.open_proof_blocker_count,
        "accepted": entry.accepted,
    }


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
) -> FixedPointBridgeEqualityProofClosureReadinessValidation:
    """Return an accepted validation result."""

    return FixedPointBridgeEqualityProofClosureReadinessValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _check(
    subject: str,
    condition: bool,
    accepted_detail: str,
    rejected_detail: str | None = None,
) -> FixedPointBridgeEqualityProofClosureReadinessValidation:
    """Return a validation result from a boolean condition."""

    return FixedPointBridgeEqualityProofClosureReadinessValidation(
        subject=subject,
        accepted=condition,
        detail=accepted_detail if condition else rejected_detail or accepted_detail,
    )


def _non_claims_are_guarded(non_claims: tuple[str, ...]) -> bool:
    """Return whether every proof-promotion phrase is explicitly negated."""

    return all(f"no {claim}" in non_claims for claim in PROOF_PROMOTION_NON_CLAIMS)


def _failed_subject_for_result(subject: str) -> str:
    """Map verbose result subjects to stable failure subjects."""

    if subject in {
        "expanded_available_predecessor_certificate_coverage",
        "bridge_equality_frontier_status",
        "bridge_equality_certificate",
    }:
        return "fixed-point-bridge-equality-proof-closure-readiness-dependencies"
    if subject == "open_proof_blockers":
        return "fixed-point-bridge-equality-proof-closure-readiness-open-blockers"
    if subject in {
        "readiness_case_kind",
        "readiness_status",
        "predecessor_case_kinds",
        "certificate_covered_predecessors",
        "missing_certificate_predecessors",
        "available_predecessor_certificate_count",
        "missing_certificate_predecessor_count",
        "bridge_equality_frontier_status",
        "bridge_equality_frontier_blocker",
        "bridge_equality_certificate_step_count",
        "readiness_entry",
    }:
        return "fixed-point-bridge-equality-proof-closure-readiness"
    if subject in {"non_claims", "non_claim_promotion_boundary"}:
        return "fixed-point-bridge-equality-proof-closure-readiness-non-claim"
    if subject == "proof_boundary":
        return "fixed-point-bridge-equality-proof-closure-readiness-boundary"
    if subject.startswith("expected_") or subject in {"readiness_id", "schema_version"}:
        return "fixed-point-bridge-equality-proof-closure-readiness-manifest"
    return (
        "fixed-point-bridge-equality-proof-closure-readiness-"
        + subject.replace("_", "-")
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    """Return a comma-joined list or ``none`` for empty sequences."""

    if not values:
        return "none"
    return ", ".join(values)


def main() -> int:
    """Module entrypoint."""

    return run_fixed_point_bridge_equality_proof_closure_readiness_cli()


if __name__ == "__main__":
    raise SystemExit(main())
