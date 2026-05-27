"""Proof-readiness handoff for the fixed-point equation-lifting case.

ADR-0316 composes the compact equation-lifting frontier status with the
bridge-equality proof-closure readiness handoff and the bridge predecessor
readiness coverage check. The result is deliberately modest: it records that
the terminal equation-lifting case is certificate-ready as a handoff while the
construction case remains proof-open. It does not prove bridge equality, the
fixed-point equation, an arithmetized proof predicate, or self-consistency.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_bridge_equality_proof_closure_readiness import (
    load_fixed_point_bridge_equality_proof_closure_readiness,
    validate_fixed_point_bridge_equality_proof_closure_readiness,
)
from autarkic_systems.fixed_point_bridge_predecessor_proof_readiness_coverage import (
    load_fixed_point_bridge_predecessor_proof_readiness_coverage,
    validate_fixed_point_bridge_predecessor_proof_readiness_coverage,
)
from autarkic_systems.fixed_point_equation_lifting_frontier_status import (
    load_fixed_point_equation_lifting_frontier_status,
    validate_fixed_point_equation_lifting_frontier_status,
)


DEFAULT_READINESS = Path("claims/fixed_point_equation_lifting_proof_readiness.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_READINESS_ID = "as-fixed-point-equation-lifting-proof-readiness-v1"
REQUIRED_CASE_ID = "AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING"
REQUIRED_CASE_KIND = "fixed-point-equation-lifting"
REQUIRED_READINESS_STATUS = "blocked-certificate-ready-proof-open"
REQUIRED_CONSTRUCTION_CASE_STATUS = "proof-case-open"
REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "fixed-point-equation-lifting"
REQUIRED_SUPPORT_SURFACE_COUNT = 4
REQUIRED_DIRECT_TARGET_CODE_LENGTH = 4528
REQUIRED_BRIDGE_EQUATION_CODE_LENGTH = 4815
REQUIRED_PREDECESSOR_CASE_KINDS = ("bridge-equality-proof",)
REQUIRED_NON_CLAIMS = (
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "equation_lifting_frontier_status_path": (
        "claims/fixed_point_equation_lifting_frontier_status.json"
    ),
    "bridge_equality_readiness_path": (
        "claims/fixed_point_bridge_equality_proof_closure_readiness.json"
    ),
    "bridge_predecessor_readiness_coverage_path": (
        "claims/fixed_point_bridge_predecessor_proof_readiness_coverage.json"
    ),
}
PROOF_PROMOTION_NON_CLAIMS = {
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "self-consistency theorem",
}


@dataclass(frozen=True)
class FixedPointEquationLiftingProofReadinessManifest:
    """Loaded manifest for the equation-lifting readiness handoff."""

    path: Path
    schema_version: int
    readiness_id: str
    reviewed_at: str
    purpose: str
    equation_lifting_frontier_status_path: str
    bridge_equality_readiness_path: str
    bridge_predecessor_readiness_coverage_path: str
    expected_readiness_case_id: str
    expected_readiness_case_kind: str
    expected_readiness_status: str
    expected_construction_case_status: str
    expected_frontier_status: str
    expected_frontier_blocker: str
    expected_support_surface_count: int
    expected_direct_target_code_length: int
    expected_bridge_equation_code_length: int
    expected_predecessor_case_kinds: tuple[str, ...]
    expected_predecessor_readiness_count: int
    expected_missing_predecessor_readiness_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointEquationLiftingProofReadinessEntry:
    """Derived readiness state for the equation-lifting terminal case."""

    case_id: str
    case_kind: str
    construction_case_status: str
    readiness_status: str
    certificate_ready: bool
    predecessor_case_kinds: tuple[str, ...]
    missing_predecessor_case_kinds: tuple[str, ...]
    open_proof_blocker: str

    @property
    def accepted(self) -> bool:
        """Return whether this entry is certificate-ready and proof-open."""

        return (
            self.case_id == REQUIRED_CASE_ID
            and self.case_kind == REQUIRED_CASE_KIND
            and self.construction_case_status == REQUIRED_CONSTRUCTION_CASE_STATUS
            and self.readiness_status == REQUIRED_READINESS_STATUS
            and self.certificate_ready
            and self.predecessor_case_kinds == REQUIRED_PREDECESSOR_CASE_KINDS
            and not self.missing_predecessor_case_kinds
            and self.open_proof_blocker == REQUIRED_FRONTIER_BLOCKER
        )


@dataclass(frozen=True)
class FixedPointEquationLiftingProofReadinessValidation:
    """One validation result for equation-lifting proof readiness."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointEquationLiftingProofReadinessReport:
    """Validation report for equation-lifting proof readiness."""

    manifest: FixedPointEquationLiftingProofReadinessManifest
    equation_lifting_frontier_status_path: Path
    bridge_equality_readiness_path: Path
    bridge_predecessor_readiness_coverage_path: Path
    willard_map_path: Path
    frontier_accepted: bool
    bridge_readiness_accepted: bool
    bridge_predecessor_coverage_accepted: bool
    frontier_status: str
    frontier_blocker: str
    support_surface_count: int
    direct_target_code_length: int
    bridge_equation_code_length: int
    predecessor_readiness_count: int
    missing_predecessor_readiness_count: int
    proof_boundary_preserved: bool
    readiness_entry: FixedPointEquationLiftingProofReadinessEntry
    results: tuple[FixedPointEquationLiftingProofReadinessValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every readiness validation passed."""

        return all(result.accepted for result in self.results)

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
    frontier_status: str = ""
    frontier_blocked_by: str = ""
    support_surface_count: int = 0
    support_facts: dict[str, dict[str, Any]] | None = None
    construction_case: Any | None = None
    readiness_entry: Any = None
    bridge_case_kind: str = ""
    bridge_readiness_status: str = ""
    bridge_open_proof_blocker_case_kinds: tuple[str, ...] = ()


def load_fixed_point_equation_lifting_proof_readiness(
    path: Path | str = DEFAULT_READINESS,
) -> FixedPointEquationLiftingProofReadinessManifest:
    """Load the equation-lifting proof-readiness manifest."""

    readiness_path = Path(path)
    data = json.loads(readiness_path.read_text(encoding="utf-8"))
    return FixedPointEquationLiftingProofReadinessManifest(
        path=readiness_path,
        schema_version=_required_int(data, "schema_version"),
        readiness_id=_required_text(data, "readiness_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        equation_lifting_frontier_status_path=_required_text(
            data,
            "equation_lifting_frontier_status_path",
        ),
        bridge_equality_readiness_path=_required_text(
            data,
            "bridge_equality_readiness_path",
        ),
        bridge_predecessor_readiness_coverage_path=_required_text(
            data,
            "bridge_predecessor_readiness_coverage_path",
        ),
        expected_readiness_case_id=_required_text(
            data,
            "expected_readiness_case_id",
        ),
        expected_readiness_case_kind=_required_text(
            data,
            "expected_readiness_case_kind",
        ),
        expected_readiness_status=_required_text(
            data,
            "expected_readiness_status",
        ),
        expected_construction_case_status=_required_text(
            data,
            "expected_construction_case_status",
        ),
        expected_frontier_status=_required_text(data, "expected_frontier_status"),
        expected_frontier_blocker=_required_text(data, "expected_frontier_blocker"),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        expected_direct_target_code_length=_required_int(
            data,
            "expected_direct_target_code_length",
        ),
        expected_bridge_equation_code_length=_required_int(
            data,
            "expected_bridge_equation_code_length",
        ),
        expected_predecessor_case_kinds=tuple(
            _required_text_list(data, "expected_predecessor_case_kinds")
        ),
        expected_predecessor_readiness_count=_required_int(
            data,
            "expected_predecessor_readiness_count",
        ),
        expected_missing_predecessor_readiness_count=_required_int(
            data,
            "expected_missing_predecessor_readiness_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_equation_lifting_proof_readiness(
    manifest: FixedPointEquationLiftingProofReadinessManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointEquationLiftingProofReadinessReport:
    """Validate certificate-ready/proof-open readiness for equation lifting."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointEquationLiftingProofReadinessValidation] = [
        _accepted("manifest", f"loaded {manifest.readiness_id}")
    ]
    results.extend(_validate_manifest(manifest))

    frontier_report = _load_frontier(
        paths["equation_lifting_frontier_status_path"]
    )
    bridge_readiness_report = _load_bridge_readiness(
        paths["bridge_equality_readiness_path"],
        checked_willard_map_path,
    )
    bridge_coverage_report = _load_bridge_predecessor_coverage(
        paths["bridge_predecessor_readiness_coverage_path"],
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(
            frontier_report,
            bridge_readiness_report,
            bridge_coverage_report,
        )
    )

    support_facts = getattr(frontier_report, "support_facts", {}) or {}
    direct_target_code_length = _support_fact_int(
        support_facts,
        "fixed_point_equation_bridge",
        "direct_target_code_length",
    )
    bridge_equation_code_length = _support_fact_int(
        support_facts,
        "fixed_point_equation_bridge",
        "bridge_equation_code_length",
    )
    readiness_entry = _derive_readiness_entry(
        frontier_report,
        bridge_readiness_report,
        bridge_coverage_report,
    )
    proof_boundary_preserved = (
        bool(getattr(frontier_report, "accepted", False))
        and bool(getattr(bridge_readiness_report, "accepted", False))
        and bool(getattr(bridge_coverage_report, "accepted", False))
        and readiness_entry.construction_case_status
        == REQUIRED_CONSTRUCTION_CASE_STATUS
        and readiness_entry.open_proof_blocker == REQUIRED_FRONTIER_BLOCKER
        and _non_claims_are_guarded(manifest.non_claims)
    )
    results.extend(
        _validate_readiness(
            manifest,
            frontier_report,
            bridge_readiness_report,
            bridge_coverage_report,
            readiness_entry,
            direct_target_code_length,
            bridge_equation_code_length,
            proof_boundary_preserved,
        )
    )

    return FixedPointEquationLiftingProofReadinessReport(
        manifest=manifest,
        equation_lifting_frontier_status_path=paths[
            "equation_lifting_frontier_status_path"
        ],
        bridge_equality_readiness_path=paths["bridge_equality_readiness_path"],
        bridge_predecessor_readiness_coverage_path=paths[
            "bridge_predecessor_readiness_coverage_path"
        ],
        willard_map_path=checked_willard_map_path,
        frontier_accepted=bool(getattr(frontier_report, "accepted", False)),
        bridge_readiness_accepted=bool(
            getattr(bridge_readiness_report, "accepted", False)
        ),
        bridge_predecessor_coverage_accepted=bool(
            getattr(bridge_coverage_report, "accepted", False)
        ),
        frontier_status=str(getattr(frontier_report, "frontier_status", "")),
        frontier_blocker=str(getattr(frontier_report, "frontier_blocked_by", "")),
        support_surface_count=int(getattr(frontier_report, "support_surface_count", 0)),
        direct_target_code_length=direct_target_code_length,
        bridge_equation_code_length=bridge_equation_code_length,
        predecessor_readiness_count=len(readiness_entry.predecessor_case_kinds),
        missing_predecessor_readiness_count=len(
            readiness_entry.missing_predecessor_case_kinds
        ),
        proof_boundary_preserved=proof_boundary_preserved,
        readiness_entry=readiness_entry,
        results=tuple(results),
    )


def fixed_point_equation_lifting_proof_readiness_payload(
    report: FixedPointEquationLiftingProofReadinessReport,
) -> dict[str, Any]:
    """Return a JSON-ready proof-readiness payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "readiness_manifest": str(report.manifest.path),
        "readiness_id": report.manifest.readiness_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "equation_lifting_frontier_status_path": str(
            report.equation_lifting_frontier_status_path
        ),
        "bridge_equality_readiness_path": str(
            report.bridge_equality_readiness_path
        ),
        "bridge_predecessor_readiness_coverage_path": str(
            report.bridge_predecessor_readiness_coverage_path
        ),
        "willard_map": str(report.willard_map_path),
        "observed_frontier_accepted": report.frontier_accepted,
        "observed_bridge_readiness_accepted": report.bridge_readiness_accepted,
        "observed_bridge_predecessor_coverage_accepted": (
            report.bridge_predecessor_coverage_accepted
        ),
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "frontier_status": report.frontier_status,
        "frontier_blocker": report.frontier_blocker,
        "support_surface_count": report.support_surface_count,
        "direct_target_code_length": report.direct_target_code_length,
        "bridge_equation_code_length": report.bridge_equation_code_length,
        "predecessor_readiness_count": report.predecessor_readiness_count,
        "missing_predecessor_readiness_count": (
            report.missing_predecessor_readiness_count
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


def format_fixed_point_equation_lifting_proof_readiness_report(
    report: FixedPointEquationLiftingProofReadinessReport,
) -> str:
    """Format a concise text report for the proof-readiness handoff."""

    status = "accepted" if report.accepted else "rejected"
    entry = report.readiness_entry
    lines = [
        f"Fixed-point equation lifting proof readiness: {status}",
        f"Readiness: {report.manifest.readiness_id}",
        f"Construction case: {entry.case_id}",
        f"Case kind: {entry.case_kind}",
        f"Readiness status: {entry.readiness_status}",
        f"Frontier: {report.frontier_status} by {report.frontier_blocker}",
        f"Construction case status: {entry.construction_case_status}",
        f"Certificate ready: {str(entry.certificate_ready).lower()}",
        f"Support surfaces: {report.support_surface_count}",
        f"Direct target code length: {report.direct_target_code_length}",
        f"Bridge equation code length: {report.bridge_equation_code_length}",
        "Predecessor readiness: "
        + _joined_or_none(entry.predecessor_case_kinds),
        "Missing predecessor readiness: "
        + _joined_or_none(entry.missing_predecessor_case_kinds),
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


def run_fixed_point_equation_lifting_proof_readiness_cli(
    argv: list[str] | None = None,
) -> int:
    """Run equation-lifting proof-readiness validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_equation_lifting_proof_readiness"
        ),
        description=(
            "Validate certificate-ready/proof-open readiness for the AS "
            "fixed-point equation-lifting terminal case."
        ),
    )
    parser.add_argument(
        "--readiness",
        default=str(DEFAULT_READINESS),
        help="Path to the equation-lifting proof-readiness manifest.",
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

    manifest = load_fixed_point_equation_lifting_proof_readiness(args.readiness)
    report = validate_fixed_point_equation_lifting_proof_readiness(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_equation_lifting_proof_readiness_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_equation_lifting_proof_readiness_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointEquationLiftingProofReadinessManifest,
) -> dict[str, Path]:
    """Return dependency paths resolved relative to the manifest location."""

    return {
        "equation_lifting_frontier_status_path": _resolve_path(
            manifest.path,
            manifest.equation_lifting_frontier_status_path,
        ),
        "bridge_equality_readiness_path": _resolve_path(
            manifest.path,
            manifest.bridge_equality_readiness_path,
        ),
        "bridge_predecessor_readiness_coverage_path": _resolve_path(
            manifest.path,
            manifest.bridge_predecessor_readiness_coverage_path,
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


def _load_frontier(path: Path) -> Any:
    """Load and validate the equation-lifting frontier status."""

    try:
        manifest = load_fixed_point_equation_lifting_frontier_status(path)
        return validate_fixed_point_equation_lifting_frontier_status(manifest)
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-equation-lifting-frontier-status-load",),
            support_facts={},
        )


def _load_bridge_readiness(path: Path, willard_map_path: Path) -> Any:
    """Load and validate the bridge-equality proof-closure readiness surface."""

    try:
        manifest = load_fixed_point_bridge_equality_proof_closure_readiness(path)
        return validate_fixed_point_bridge_equality_proof_closure_readiness(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-bridge-equality-proof-closure-readiness-load",
            ),
        )


def _load_bridge_predecessor_coverage(path: Path, willard_map_path: Path) -> Any:
    """Load and validate bridge predecessor readiness coverage."""

    try:
        manifest = load_fixed_point_bridge_predecessor_proof_readiness_coverage(path)
        return validate_fixed_point_bridge_predecessor_proof_readiness_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-bridge-predecessor-proof-readiness-coverage-load",
            ),
        )


def _validate_manifest(
    manifest: FixedPointEquationLiftingProofReadinessManifest,
) -> list[FixedPointEquationLiftingProofReadinessValidation]:
    """Validate manifest-local constants and proof-boundary guardrails."""

    return [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "readiness_id",
            manifest.readiness_id == REQUIRED_READINESS_ID,
            "readiness id matches",
            "unexpected readiness id",
        ),
        *[
            _check(
                key,
                getattr(manifest, key) == expected,
                f"{expected} referenced",
                f"expected {expected} but found {getattr(manifest, key)}",
            )
            for key, expected in EXPECTED_DEPENDENCY_PATHS.items()
        ],
        _check(
            "expected_readiness_case_id",
            manifest.expected_readiness_case_id == REQUIRED_CASE_ID,
            "case id matches",
        ),
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
            "expected_construction_case_status",
            (
                manifest.expected_construction_case_status
                == REQUIRED_CONSTRUCTION_CASE_STATUS
            ),
            "construction case status matches",
        ),
        _check(
            "expected_frontier_status",
            manifest.expected_frontier_status == REQUIRED_FRONTIER_STATUS,
            "frontier status matches",
        ),
        _check(
            "expected_frontier_blocker",
            manifest.expected_frontier_blocker == REQUIRED_FRONTIER_BLOCKER,
            "frontier blocker matches",
        ),
        _check(
            "expected_support_surface_count",
            manifest.expected_support_surface_count == REQUIRED_SUPPORT_SURFACE_COUNT,
            "support surface count matches",
        ),
        _check(
            "expected_direct_target_code_length",
            (
                manifest.expected_direct_target_code_length
                == REQUIRED_DIRECT_TARGET_CODE_LENGTH
            ),
            "direct target code length matches",
        ),
        _check(
            "expected_bridge_equation_code_length",
            (
                manifest.expected_bridge_equation_code_length
                == REQUIRED_BRIDGE_EQUATION_CODE_LENGTH
            ),
            "bridge equation code length matches",
        ),
        _check(
            "expected_predecessor_case_kinds",
            manifest.expected_predecessor_case_kinds == REQUIRED_PREDECESSOR_CASE_KINDS,
            "predecessor case kinds match",
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
    frontier_report: Any,
    bridge_readiness_report: Any,
    bridge_coverage_report: Any,
) -> list[FixedPointEquationLiftingProofReadinessValidation]:
    """Validate that dependency reports accepted before readiness derivation."""

    return [
        _check(
            "equation_lifting_frontier_status.accepted",
            bool(getattr(frontier_report, "accepted", False)),
            "frontier accepted",
            "frontier rejected",
        ),
        _check(
            "bridge_equality_readiness.accepted",
            bool(getattr(bridge_readiness_report, "accepted", False)),
            "bridge readiness accepted",
            "bridge readiness rejected",
        ),
        _check(
            "bridge_predecessor_readiness_coverage.accepted",
            bool(getattr(bridge_coverage_report, "accepted", False)),
            "bridge predecessor coverage accepted",
            "bridge predecessor coverage rejected",
        ),
    ]


def _derive_readiness_entry(
    frontier_report: Any,
    bridge_readiness_report: Any,
    bridge_coverage_report: Any,
) -> FixedPointEquationLiftingProofReadinessEntry:
    """Build the readiness entry from frontier and predecessor handoffs."""

    construction_case = getattr(frontier_report, "construction_case", None)
    case_id = str(getattr(construction_case, "case_id", ""))
    case_kind = str(getattr(construction_case, "case_kind", ""))
    case_status = str(getattr(construction_case, "status", ""))
    bridge_entry = getattr(bridge_readiness_report, "readiness_entry", None)
    bridge_case_kind = str(getattr(bridge_entry, "case_kind", ""))
    bridge_ready = (
        bool(getattr(bridge_readiness_report, "accepted", False))
        and bridge_case_kind == "bridge-equality-proof"
        and str(getattr(bridge_entry, "readiness_status", ""))
        == REQUIRED_READINESS_STATUS
    )
    coverage_ready = (
        bool(getattr(bridge_coverage_report, "accepted", False))
        and str(getattr(bridge_coverage_report, "bridge_case_kind", ""))
        == "bridge-equality-proof"
        and str(getattr(bridge_coverage_report, "bridge_readiness_status", ""))
        == REQUIRED_READINESS_STATUS
        and getattr(
            bridge_coverage_report,
            "missing_predecessor_readiness_count",
            1,
        )
        == 0
    )
    predecessor_case_kinds = (
        REQUIRED_PREDECESSOR_CASE_KINDS if bridge_ready and coverage_ready else ()
    )
    missing_predecessor_case_kinds = (
        ()
        if predecessor_case_kinds == REQUIRED_PREDECESSOR_CASE_KINDS
        else REQUIRED_PREDECESSOR_CASE_KINDS
    )
    certificate_ready = (
        bool(getattr(frontier_report, "accepted", False))
        and bridge_ready
        and coverage_ready
    )
    return FixedPointEquationLiftingProofReadinessEntry(
        case_id=case_id,
        case_kind=case_kind,
        construction_case_status=case_status,
        readiness_status=REQUIRED_READINESS_STATUS,
        certificate_ready=certificate_ready,
        predecessor_case_kinds=predecessor_case_kinds,
        missing_predecessor_case_kinds=missing_predecessor_case_kinds,
        open_proof_blocker=str(getattr(frontier_report, "frontier_blocked_by", "")),
    )


def _validate_readiness(
    manifest: FixedPointEquationLiftingProofReadinessManifest,
    frontier_report: Any,
    bridge_readiness_report: Any,
    bridge_coverage_report: Any,
    readiness_entry: FixedPointEquationLiftingProofReadinessEntry,
    direct_target_code_length: int,
    bridge_equation_code_length: int,
    proof_boundary_preserved: bool,
) -> list[FixedPointEquationLiftingProofReadinessValidation]:
    """Validate derived readiness facts against the checked manifest."""

    support_surface_count = int(getattr(frontier_report, "support_surface_count", 0))
    return [
        _check(
            "readiness_entry.case",
            (
                readiness_entry.case_id == manifest.expected_readiness_case_id
                and readiness_entry.case_kind == manifest.expected_readiness_case_kind
            ),
            "readiness case matches",
            "readiness case mismatch",
        ),
        _check(
            "readiness_entry.status",
            readiness_entry.readiness_status == manifest.expected_readiness_status,
            "readiness status matches",
            "readiness status mismatch",
        ),
        _check(
            "readiness_entry.construction_case_status",
            (
                readiness_entry.construction_case_status
                == manifest.expected_construction_case_status
            ),
            "construction case remains open",
            "construction case status mismatch",
        ),
        _check(
            "frontier.status",
            str(getattr(frontier_report, "frontier_status", ""))
            == manifest.expected_frontier_status,
            "frontier status matches",
            "frontier status mismatch",
        ),
        _check(
            "frontier.blocker",
            str(getattr(frontier_report, "frontier_blocked_by", ""))
            == manifest.expected_frontier_blocker,
            "frontier blocker matches",
            "frontier blocker mismatch",
        ),
        _check(
            "support.surface_count",
            support_surface_count == manifest.expected_support_surface_count,
            "support surface count matches",
            "support surface count mismatch",
        ),
        _check(
            "support.direct_target_code_length",
            direct_target_code_length == manifest.expected_direct_target_code_length,
            "direct target code length matches",
            "direct target code length mismatch",
        ),
        _check(
            "support.bridge_equation_code_length",
            (
                bridge_equation_code_length
                == manifest.expected_bridge_equation_code_length
            ),
            "bridge equation code length matches",
            "bridge equation code length mismatch",
        ),
        _check(
            "predecessors.case_kinds",
            readiness_entry.predecessor_case_kinds
            == manifest.expected_predecessor_case_kinds,
            "predecessor case kinds match",
            "predecessor case kind mismatch",
        ),
        _check(
            "predecessors.readiness_count",
            (
                len(readiness_entry.predecessor_case_kinds)
                == manifest.expected_predecessor_readiness_count
            ),
            "predecessor readiness count matches",
            "predecessor readiness count mismatch",
        ),
        _check(
            "predecessors.missing_count",
            (
                len(readiness_entry.missing_predecessor_case_kinds)
                == manifest.expected_missing_predecessor_readiness_count
            ),
            "missing predecessor readiness count matches",
            "missing predecessor readiness count mismatch",
        ),
        _check(
            "bridge_readiness.status",
            str(
                getattr(
                    getattr(bridge_readiness_report, "readiness_entry", None),
                    "readiness_status",
                    "",
                )
            )
            == REQUIRED_READINESS_STATUS,
            "bridge readiness remains proof-open",
            "bridge readiness status mismatch",
        ),
        _check(
            "bridge_predecessor_coverage.missing_count",
            getattr(
                bridge_coverage_report,
                "missing_predecessor_readiness_count",
                1,
            )
            == 0,
            "bridge predecessor coverage has no missing readiness",
            "bridge predecessor readiness coverage mismatch",
        ),
        _check(
            "readiness_entry.accepted",
            readiness_entry.accepted,
            "readiness entry accepted",
            "readiness entry rejected",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
            "proof boundary not preserved",
        ),
    ]


def _support_fact_int(
    support_facts: dict[str, dict[str, Any]],
    subject: str,
    field: str,
) -> int:
    """Read an integer support fact from a nested support-facts mapping."""

    value = support_facts.get(subject, {}).get(field, 0)
    return value if isinstance(value, int) else 0


def _readiness_entry_payload(
    entry: FixedPointEquationLiftingProofReadinessEntry,
) -> dict[str, Any]:
    """Return the JSON shape for a readiness entry."""

    return {
        "accepted": entry.accepted,
        "case_id": entry.case_id,
        "case_kind": entry.case_kind,
        "construction_case_status": entry.construction_case_status,
        "readiness_status": entry.readiness_status,
        "certificate_ready": entry.certificate_ready,
        "predecessor_case_kinds": list(entry.predecessor_case_kinds),
        "missing_predecessor_case_kinds": list(
            entry.missing_predecessor_case_kinds
        ),
        "open_proof_blocker": entry.open_proof_blocker,
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
) -> FixedPointEquationLiftingProofReadinessValidation:
    """Build a validation result."""

    return FixedPointEquationLiftingProofReadinessValidation(
        subject=subject,
        accepted=accepted,
        detail=ok_detail if accepted else (fail_detail or ok_detail),
    )


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointEquationLiftingProofReadinessValidation:
    """Build an accepted validation result."""

    return FixedPointEquationLiftingProofReadinessValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    """Map detailed validation subjects to compact failure labels."""

    if subject.startswith(
        (
            "equation_lifting_frontier_status",
            "bridge_equality_readiness",
            "bridge_predecessor_readiness_coverage",
        )
    ):
        return "fixed-point-equation-lifting-proof-readiness-dependencies"
    if subject.startswith("support."):
        return "fixed-point-equation-lifting-proof-readiness-support"
    if subject.startswith("predecessors.") or subject.startswith("bridge_"):
        return "fixed-point-equation-lifting-proof-readiness-predecessors"
    if subject.startswith("proof_boundary") or subject.startswith(
        "non_claim_promotion_boundary"
    ):
        return "fixed-point-equation-lifting-proof-readiness-proof-boundary"
    return "fixed-point-equation-lifting-proof-readiness-manifest"


def _joined_or_none(values: tuple[str, ...]) -> str:
    """Render a tuple for text output."""

    return ", ".join(values) if values else "none"


def main() -> int:
    """Module entry point."""

    return run_fixed_point_equation_lifting_proof_readiness_cli()


if __name__ == "__main__":
    raise SystemExit(main())
