"""Compact status surface for the AS fixed-point construction frontier.

The surrounding modules validate finite support artifacts for the current
fixed-point construction stack. This module only gathers those artifacts into a
fail-closed frontier report. It deliberately preserves the blocked boundary and
does not promote any construction case to a proved fixed-point equation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.fixed_point_bridge_equality_frontier_status import (
    load_fixed_point_bridge_equality_frontier_status,
    validate_fixed_point_bridge_equality_frontier_status,
)
from autarkic_systems.fixed_point_bridge_equality_alignment import (
    load_fixed_point_bridge_equality_alignment,
)
from autarkic_systems.fixed_point_bridge_equality_certificate import (
    load_fixed_point_bridge_equality_certificate,
)
from autarkic_systems.fixed_point_bridge_equality_evaluation import (
    load_fixed_point_bridge_equality_evaluation,
)
from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status import (
    load_fixed_point_diagonal_instance_closure_frontier_status,
    validate_fixed_point_diagonal_instance_closure_frontier_status,
)
from autarkic_systems.fixed_point_diagonal_instance_candidate_surface import (
    load_fixed_point_diagonal_instance_candidate_surface,
)
from autarkic_systems.fixed_point_equation_lifting_frontier_status import (
    load_fixed_point_equation_lifting_frontier_status,
    validate_fixed_point_equation_lifting_frontier_status,
)
from autarkic_systems.fixed_point_equation_lifting_alignment import (
    load_fixed_point_equation_lifting_alignment,
)
from autarkic_systems.fixed_point_substitution_representability_frontier_status import (
    load_fixed_point_substitution_representability_frontier_status,
    validate_fixed_point_substitution_representability_frontier_status,
)
from autarkic_systems.fixed_point_substitution_graph_correctness_bridge import (
    load_fixed_point_substitution_graph_correctness_bridge,
)
from autarkic_systems.fixed_point_substitution_witness_bridge import (
    load_fixed_point_substitution_witness_bridge,
)
from autarkic_systems.substitution_graph_correctness_frontier_status import (
    load_substitution_graph_correctness_frontier_status,
    validate_substitution_graph_correctness_frontier_status,
)


DEFAULT_STATUS = Path("claims/fixed_point_construction_frontier_status.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "fixed-point-construction"
REQUIRED_CASE_STATUS = "proof-case-open"
REQUIRED_DEPENDENCY_SUBJECTS = (
    "fixed_point_construction_cases",
    "diagonal_instance_candidate_surface",
    "substitution_witness_bridge",
    "substitution_graph_correctness_bridge",
    "bridge_equality_alignment",
    "bridge_equality_evaluation",
    "bridge_equality_certificate",
    "equation_lifting_alignment",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "fixed_point_construction_cases_path": "claims/fixed_point_construction_cases.json",
    "diagonal_instance_candidate_surface_path": (
        "claims/fixed_point_diagonal_instance_candidate_surface.json"
    ),
    "substitution_witness_bridge_path": (
        "claims/fixed_point_substitution_witness_bridge.json"
    ),
    "substitution_graph_correctness_bridge_path": (
        "claims/fixed_point_substitution_graph_correctness_bridge.json"
    ),
    "bridge_equality_alignment_path": (
        "claims/fixed_point_bridge_equality_alignment.json"
    ),
    "bridge_equality_evaluation_path": (
        "claims/fixed_point_bridge_equality_evaluation.json"
    ),
    "bridge_equality_certificate_path": (
        "claims/fixed_point_bridge_equality_certificate.json"
    ),
    "equation_lifting_alignment_path": (
        "claims/fixed_point_equation_lifting_alignment.json"
    ),
}
SUPPORT_BY_CASE_KIND = {
    "diagonal-instance-closure": ("diagonal_instance_candidate_surface",),
    "substitution-representability-proof": ("substitution_witness_bridge",),
    "substitution-graph-correctness-proof": (
        "substitution_graph_correctness_bridge",
    ),
    "bridge-equality-proof": (
        "bridge_equality_alignment",
        "bridge_equality_evaluation",
        "bridge_equality_certificate",
    ),
    "fixed-point-equation-lifting": ("equation_lifting_alignment",),
}
REQUIRED_CASE_STATUS_PATHS = {
    "diagonal-instance-closure": (
        "claims/fixed_point_diagonal_instance_closure_frontier_status.json"
    ),
    "substitution-representability-proof": (
        "claims/fixed_point_substitution_representability_frontier_status.json"
    ),
    "substitution-graph-correctness-proof": (
        "claims/substitution_graph_correctness_frontier_status.json"
    ),
    "bridge-equality-proof": (
        "claims/fixed_point_bridge_equality_frontier_status.json"
    ),
    "fixed-point-equation-lifting": (
        "claims/fixed_point_equation_lifting_frontier_status.json"
    ),
}
EXPECTED_CASE_STATUS_BLOCKERS = {
    "diagonal-instance-closure": "diagonal-instance-closure",
    "substitution-representability-proof": "substitution-representability-proof",
    "substitution-graph-correctness-proof": "substitution-graph-correctness",
    "bridge-equality-proof": "bridge-equality-proof",
    "fixed-point-equation-lifting": "fixed-point-equation-lifting",
}
_CASE_STATUS_VALIDATORS: dict[
    str,
    tuple[Callable[[Path | str], Any], Callable[[Any], Any]],
] = {
    "diagonal-instance-closure": (
        load_fixed_point_diagonal_instance_closure_frontier_status,
        validate_fixed_point_diagonal_instance_closure_frontier_status,
    ),
    "substitution-representability-proof": (
        load_fixed_point_substitution_representability_frontier_status,
        validate_fixed_point_substitution_representability_frontier_status,
    ),
    "substitution-graph-correctness-proof": (
        load_substitution_graph_correctness_frontier_status,
        validate_substitution_graph_correctness_frontier_status,
    ),
    "bridge-equality-proof": (
        load_fixed_point_bridge_equality_frontier_status,
        validate_fixed_point_bridge_equality_frontier_status,
    ),
    "fixed-point-equation-lifting": (
        load_fixed_point_equation_lifting_frontier_status,
        validate_fixed_point_equation_lifting_frontier_status,
    ),
}


@dataclass(frozen=True)
class FixedPointConstructionFrontierStatusManifest:
    """Loaded compact manifest for the fixed-point construction frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    fixed_point_construction_cases_path: str
    diagonal_instance_candidate_surface_path: str
    substitution_witness_bridge_path: str
    substitution_graph_correctness_bridge_path: str
    bridge_equality_alignment_path: str
    bridge_equality_evaluation_path: str
    bridge_equality_certificate_path: str
    equation_lifting_alignment_path: str
    case_status_paths: dict[str, str]
    non_claims: tuple[str, ...]
    next_as_action: str

    def __hash__(self) -> int:
        """Hash manifests with dict-valued status paths for validation caching."""

        return hash((
            self.path,
            self.schema_version,
            self.status_set_id,
            self.reviewed_at,
            self.purpose,
            self.frontier_status,
            self.frontier_blocked_by,
            self.fixed_point_construction_cases_path,
            self.diagonal_instance_candidate_surface_path,
            self.substitution_witness_bridge_path,
            self.substitution_graph_correctness_bridge_path,
            self.bridge_equality_alignment_path,
            self.bridge_equality_evaluation_path,
            self.bridge_equality_certificate_path,
            self.equation_lifting_alignment_path,
            tuple(sorted(self.case_status_paths.items())),
            self.non_claims,
            self.next_as_action,
        ))


@dataclass(frozen=True)
class FixedPointConstructionFrontierStatusValidation:
    """One validation result for the frontier status report."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointConstructionFrontierSupportSurface:
    """Observed state of one finite support surface."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class FixedPointConstructionFrontierCaseSupport:
    """Per-case view of finite support while the proof case remains open."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    finite_support_subjects: tuple[str, ...]
    finite_support_accepted: bool


@dataclass(frozen=True)
class FixedPointConstructionFrontierCaseStatusRollup:
    """One compact construction-case status observed by the aggregate status."""

    case_kind: str
    path: Path
    accepted: bool
    frontier_status: str
    expected_frontier_blocker: str
    frontier_blocked_by: str
    construction_case_id: str
    construction_case_status: str
    failed_subjects: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class FixedPointConstructionFrontierStatusReport:
    """Validation report for the compact construction frontier status."""

    manifest: FixedPointConstructionFrontierStatusManifest
    willard_map_path: Path
    fixed_point_construction_cases_path: Path
    diagonal_instance_candidate_surface_path: Path
    substitution_witness_bridge_path: Path
    substitution_graph_correctness_bridge_path: Path
    bridge_equality_alignment_path: Path
    bridge_equality_evaluation_path: Path
    bridge_equality_certificate_path: Path
    equation_lifting_alignment_path: Path
    results: tuple[FixedPointConstructionFrontierStatusValidation, ...]
    support_surfaces: tuple[FixedPointConstructionFrontierSupportSurface, ...]
    case_supports: tuple[FixedPointConstructionFrontierCaseSupport, ...]
    case_status_rollup: tuple[
        FixedPointConstructionFrontierCaseStatusRollup,
        ...
    ]

    @property
    def accepted(self) -> bool:
        """Return whether every frontier status validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the manifest frontier status for payloads and tests."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the blocker that this status surface preserves."""

        return self.manifest.frontier_blocked_by

    @property
    def case_count(self) -> int:
        """Return the number of observed construction cases."""

        return len(self.case_supports)

    @property
    def open_case_count(self) -> int:
        """Return the number of construction cases still explicitly open."""

        return sum(1 for case in self.case_supports if case.status == "proof-case-open")

    @property
    def support_surface_count(self) -> int:
        """Return the number of required support surfaces inspected."""

        return len(self.support_surfaces)

    @property
    def case_status_count(self) -> int:
        """Return the number of observed compact case-status handoffs."""

        return len(self.case_status_rollup)

    @property
    def accepted_case_status_count(self) -> int:
        """Return the number of compact case-status handoffs that accepted."""

        return sum(1 for status in self.case_status_rollup if status.accepted)

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
    """Small report shim used when a dependency cannot even be loaded."""

    accepted: bool
    failed_subjects: tuple[str, ...]


def load_fixed_point_construction_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> FixedPointConstructionFrontierStatusManifest:
    """Load the fixed-point construction frontier status manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return FixedPointConstructionFrontierStatusManifest(
        path=status_path,
        schema_version=_required_int(data, "schema_version"),
        status_set_id=_required_text(data, "status_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        frontier_status=_required_text(data, "frontier_status"),
        frontier_blocked_by=_required_text(data, "frontier_blocked_by"),
        fixed_point_construction_cases_path=_required_text(
            data,
            "fixed_point_construction_cases_path",
        ),
        diagonal_instance_candidate_surface_path=_required_text(
            data,
            "diagonal_instance_candidate_surface_path",
        ),
        substitution_witness_bridge_path=_required_text(
            data,
            "substitution_witness_bridge_path",
        ),
        substitution_graph_correctness_bridge_path=_required_text(
            data,
            "substitution_graph_correctness_bridge_path",
        ),
        bridge_equality_alignment_path=_required_text(
            data,
            "bridge_equality_alignment_path",
        ),
        bridge_equality_evaluation_path=_required_text(
            data,
            "bridge_equality_evaluation_path",
        ),
        bridge_equality_certificate_path=_required_text(
            data,
            "bridge_equality_certificate_path",
        ),
        equation_lifting_alignment_path=_required_text(
            data,
            "equation_lifting_alignment_path",
        ),
        case_status_paths=_required_text_map(data, "case_status_paths"),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_construction_frontier_status(
    manifest: FixedPointConstructionFrontierStatusManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointConstructionFrontierStatusReport:
    """Validate the compact fixed-point construction frontier status."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)

    construction_cases, construction_case_report = _load_dependency_manifest(
        "fixed_point_construction_cases",
        paths["fixed_point_construction_cases_path"],
        load_fixed_point_construction_cases,
        "fixed-point-construction-cases-load",
    )
    dependency_reports = {
        "fixed_point_construction_cases": construction_case_report,
        "diagonal_instance_candidate_surface": _load_dependency_manifest(
            "diagonal_instance_candidate_surface",
            paths["diagonal_instance_candidate_surface_path"],
            load_fixed_point_diagonal_instance_candidate_surface,
            "fixed-point-diagonal-instance-candidate-surface-load",
        )[1],
        "substitution_witness_bridge": _load_dependency_manifest(
            "substitution_witness_bridge",
            paths["substitution_witness_bridge_path"],
            load_fixed_point_substitution_witness_bridge,
            "fixed-point-substitution-witness-bridge-load",
        )[1],
        "substitution_graph_correctness_bridge": _load_dependency_manifest(
            "substitution_graph_correctness_bridge",
            paths["substitution_graph_correctness_bridge_path"],
            load_fixed_point_substitution_graph_correctness_bridge,
            "fixed-point-substitution-graph-correctness-bridge-load",
        )[1],
        "bridge_equality_alignment": _load_dependency_manifest(
            "bridge_equality_alignment",
            paths["bridge_equality_alignment_path"],
            load_fixed_point_bridge_equality_alignment,
            "fixed-point-bridge-equality-alignment-load",
        )[1],
        "bridge_equality_evaluation": _load_dependency_manifest(
            "bridge_equality_evaluation",
            paths["bridge_equality_evaluation_path"],
            load_fixed_point_bridge_equality_evaluation,
            "fixed-point-bridge-equality-evaluation-load",
        )[1],
        "bridge_equality_certificate": _load_dependency_manifest(
            "bridge_equality_certificate",
            paths["bridge_equality_certificate_path"],
            load_fixed_point_bridge_equality_certificate,
            "fixed-point-bridge-equality-certificate-load",
        )[1],
        "equation_lifting_alignment": _load_dependency_manifest(
            "equation_lifting_alignment",
            paths["equation_lifting_alignment_path"],
            load_fixed_point_equation_lifting_alignment,
            "fixed-point-equation-lifting-alignment-load",
        )[1],
    }

    results: list[FixedPointConstructionFrontierStatusValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))
    support_surfaces = _support_surfaces(paths, dependency_reports)
    results.extend(_validate_support_surfaces(support_surfaces))
    case_supports, case_results = _case_supports(
        construction_cases,
        frozenset(
            surface.subject for surface in support_surfaces if surface.accepted
        ),
    )
    results.extend(case_results)
    case_status_rollup, case_status_results = _case_status_rollup(
        manifest.case_status_paths,
        {case.case_kind: case for case in case_supports},
    )
    results.extend(case_status_results)

    return FixedPointConstructionFrontierStatusReport(
        manifest=manifest,
        willard_map_path=checked_willard_map_path,
        fixed_point_construction_cases_path=paths["fixed_point_construction_cases_path"],
        diagonal_instance_candidate_surface_path=paths[
            "diagonal_instance_candidate_surface_path"
        ],
        substitution_witness_bridge_path=paths["substitution_witness_bridge_path"],
        substitution_graph_correctness_bridge_path=paths[
            "substitution_graph_correctness_bridge_path"
        ],
        bridge_equality_alignment_path=paths["bridge_equality_alignment_path"],
        bridge_equality_evaluation_path=paths["bridge_equality_evaluation_path"],
        bridge_equality_certificate_path=paths["bridge_equality_certificate_path"],
        equation_lifting_alignment_path=paths["equation_lifting_alignment_path"],
        results=tuple(results),
        support_surfaces=tuple(support_surfaces),
        case_supports=tuple(case_supports),
        case_status_rollup=tuple(case_status_rollup),
    )


def fixed_point_construction_frontier_status_payload(
    report: FixedPointConstructionFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready fixed-point construction frontier payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "status_manifest": str(report.manifest.path),
        "status_set_id": report.manifest.status_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_status": report.frontier_status,
        "frontier_blocked_by": report.frontier_blocked_by,
        "willard_map": str(report.willard_map_path),
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "diagonal_instance_candidate_surface_path": str(
            report.diagonal_instance_candidate_surface_path
        ),
        "substitution_witness_bridge_path": str(
            report.substitution_witness_bridge_path
        ),
        "substitution_graph_correctness_bridge_path": str(
            report.substitution_graph_correctness_bridge_path
        ),
        "bridge_equality_alignment_path": str(report.bridge_equality_alignment_path),
        "bridge_equality_evaluation_path": str(report.bridge_equality_evaluation_path),
        "bridge_equality_certificate_path": str(
            report.bridge_equality_certificate_path
        ),
        "equation_lifting_alignment_path": str(report.equation_lifting_alignment_path),
        "case_status_paths": dict(report.manifest.case_status_paths),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "support_surface_count": report.support_surface_count,
        "case_count": report.case_count,
        "open_case_count": report.open_case_count,
        "case_status_count": report.case_status_count,
        "accepted_case_status_count": report.accepted_case_status_count,
        "failed_subjects": list(report.failed_subjects),
        "support_surfaces": [
            {
                "subject": surface.subject,
                "path": str(surface.path),
                "accepted": surface.accepted,
                "failed_subjects": list(surface.failed_subjects),
                "detail": surface.detail,
            }
            for surface in report.support_surfaces
        ],
        "case_supports": [
            {
                "case_id": case.case_id,
                "case_kind": case.case_kind,
                "target_id": case.target_id,
                "status": case.status,
                "finite_support_subjects": list(case.finite_support_subjects),
                "finite_support_accepted": case.finite_support_accepted,
            }
            for case in report.case_supports
        ],
        "case_status_rollup": [
            {
                "case_kind": status.case_kind,
                "path": str(status.path),
                "accepted": status.accepted,
                "frontier_status": status.frontier_status,
                "expected_frontier_blocker": status.expected_frontier_blocker,
                "frontier_blocked_by": status.frontier_blocked_by,
                "construction_case_id": status.construction_case_id,
                "construction_case_status": status.construction_case_status,
                "failed_subjects": list(status.failed_subjects),
                "detail": status.detail,
            }
            for status in report.case_status_rollup
        ],
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


def format_fixed_point_construction_frontier_status_report(
    report: FixedPointConstructionFrontierStatusReport,
) -> str:
    """Format a concise human-readable frontier status report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point construction frontier status: {status}",
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Open construction cases: {report.open_case_count}/{report.case_count}",
        f"Support surfaces: {report.support_surface_count}",
        (
            "Compact construction-case status rollup: "
            f"{report.accepted_case_status_count}/{report.case_status_count}"
        ),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        lines.append(f"- {surface.subject}: {prefix} ({surface.path})")
    lines.append("Compact construction-case statuses:")
    for status_report in report.case_status_rollup:
        prefix = "accepted" if status_report.accepted else "rejected"
        lines.append(f"- {status_report.case_kind}: {prefix} ({status_report.path})")
        lines.append(f"  Frontier status: {status_report.frontier_status}")
        lines.append(f"  Expected blocker: {status_report.expected_frontier_blocker}")
        lines.append(f"  Blocked by: {status_report.frontier_blocked_by}")
        lines.append(f"  Construction case: {status_report.construction_case_id}")
        lines.append(
            f"  Construction case status: "
            f"{status_report.construction_case_status}"
        )
        lines.append(
            f"  Failed subjects: {_joined_or_none(status_report.failed_subjects)}"
        )
    lines.append("Construction cases:")
    for case in report.case_supports:
        lines.extend([
            f"- {case.case_id}",
            f"  Kind: {case.case_kind}",
            f"  Status: {case.status}",
            f"  Finite support: {_joined_or_none(case.finite_support_subjects)}",
            f"  Support accepted: {case.finite_support_accepted}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_construction_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point construction frontier status validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_construction_frontier_status",
        description="Validate the AS fixed-point construction frontier status.",
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the fixed-point construction frontier status manifest.",
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

    manifest = load_fixed_point_construction_frontier_status(args.status)
    report = validate_fixed_point_construction_frontier_status(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            fixed_point_construction_frontier_status_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_fixed_point_construction_frontier_status_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointConstructionFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "fixed_point_construction_cases_path": Path(
            manifest.fixed_point_construction_cases_path
        ),
        "diagonal_instance_candidate_surface_path": Path(
            manifest.diagonal_instance_candidate_surface_path
        ),
        "substitution_witness_bridge_path": Path(
            manifest.substitution_witness_bridge_path
        ),
        "substitution_graph_correctness_bridge_path": Path(
            manifest.substitution_graph_correctness_bridge_path
        ),
        "bridge_equality_alignment_path": Path(
            manifest.bridge_equality_alignment_path
        ),
        "bridge_equality_evaluation_path": Path(
            manifest.bridge_equality_evaluation_path
        ),
        "bridge_equality_certificate_path": Path(
            manifest.bridge_equality_certificate_path
        ),
        "equation_lifting_alignment_path": Path(
            manifest.equation_lifting_alignment_path
        ),
    }


def _load_dependency_manifest(
    subject: str,
    path: Path,
    loader: Callable[[Path], Any],
    load_failure_subject: str,
) -> tuple[Any | None, Any]:
    try:
        loaded = loader(path)
        return loaded, _validate_loaded_support_manifest(subject, loaded)
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _DependencyFailure(False, (load_failure_subject,))


def _validate_loaded_support_manifest(subject: str, loaded: Any) -> _DependencyFailure:
    """Check cheap status invariants for an already factored support surface.

    The individual support modules own the expensive evidence derivations. This
    frontier layer only verifies that the expected compact surface is present
    and still carries its non-promotional boundary.
    """

    failures: list[str] = []
    if subject == "fixed_point_construction_cases":
        cases = tuple(loaded.cases)
        if loaded.case_set_id != "as-fixed-point-construction-cases-v1":
            failures.append("fixed-point-construction-cases-id")
        if len(cases) != 5:
            failures.append("fixed-point-construction-cases-count")
        if any(case.status != "proof-case-open" for case in cases):
            failures.append("fixed-point-construction-frontier-case-status")
        for case in cases:
            missing = [item for item in REQUIRED_NON_CLAIMS if item not in case.non_claims]
            if missing:
                failures.append("fixed-point-construction-cases-non-claim")
                break
    elif subject == "diagonal_instance_candidate_surface":
        _require_attr_value(
            loaded,
            "candidate_surface_set_id",
            "as-fixed-point-diagonal-instance-candidate-surface-v1",
            "fixed-point-diagonal-instance-candidate-surface-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_candidate_count",
            1,
            "fixed-point-diagonal-instance-candidate-surface-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-diagonal-instance-candidate-surface-non-claim")
    elif subject == "substitution_witness_bridge":
        _require_attr_value(
            loaded,
            "bridge_set_id",
            "as-fixed-point-substitution-witness-bridge-v1",
            "fixed-point-substitution-witness-bridge-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_bridge_count",
            1,
            "fixed-point-substitution-witness-bridge-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-substitution-witness-bridge-non-claim")
    elif subject == "substitution_graph_correctness_bridge":
        _require_attr_value(
            loaded,
            "bridge_set_id",
            "as-fixed-point-substitution-graph-correctness-bridge-v1",
            "fixed-point-substitution-graph-correctness-bridge-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_bridge_count",
            1,
            "fixed-point-substitution-graph-correctness-bridge-count",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_correctness_case_count",
            5,
            "fixed-point-substitution-graph-correctness-bridge-case-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-substitution-graph-correctness-bridge-non-claim")
    elif subject == "bridge_equality_alignment":
        _require_attr_value(
            loaded,
            "alignment_set_id",
            "as-fixed-point-bridge-equality-alignment-v1",
            "fixed-point-bridge-equality-alignment-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_alignment_count",
            1,
            "fixed-point-bridge-equality-alignment-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-bridge-equality-alignment-non-claim")
    elif subject == "bridge_equality_evaluation":
        _require_attr_value(
            loaded,
            "evaluation_set_id",
            "as-fixed-point-bridge-equality-evaluation-v1",
            "fixed-point-bridge-equality-evaluation-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_evaluation_count",
            1,
            "fixed-point-bridge-equality-evaluation-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-bridge-equality-evaluation-non-claim")
    elif subject == "bridge_equality_certificate":
        _require_attr_value(
            loaded,
            "certificate_set_id",
            "as-fixed-point-bridge-equality-certificate-v1",
            "fixed-point-bridge-equality-certificate-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_certificate_count",
            1,
            "fixed-point-bridge-equality-certificate-count",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_evaluation_output_code_length",
            296,
            "fixed-point-bridge-equality-certificate-output-length",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-bridge-equality-certificate-non-claim")
    elif subject == "equation_lifting_alignment":
        _require_attr_value(
            loaded,
            "alignment_set_id",
            "as-fixed-point-equation-lifting-alignment-v1",
            "fixed-point-equation-lifting-alignment-id",
            failures,
        )
        _require_attr_value(
            loaded,
            "expected_alignment_count",
            1,
            "fixed-point-equation-lifting-alignment-count",
            failures,
        )
        _require_non_claims(loaded, failures, "fixed-point-equation-lifting-alignment-non-claim")
    else:
        failures.append("fixed-point-construction-frontier-unknown-support")

    return _DependencyFailure(not failures, tuple(failures))


def _require_attr_value(
    loaded: Any,
    attr: str,
    expected: Any,
    failure: str,
    failures: list[str],
) -> None:
    if getattr(loaded, attr, None) != expected:
        failures.append(failure)


def _require_non_claims(
    loaded: Any,
    failures: list[str],
    failure: str,
) -> None:
    non_claims = tuple(getattr(loaded, "non_claims", ()))
    if not non_claims:
        failures.append(failure)
        return
    if any(claim in non_claims for claim in (
        "fixed-point-equation-proved",
        "self-consistency-theorem-proved",
    )):
        failures.append(failure)


def _support_surfaces(
    paths: dict[str, Path],
    dependency_reports: dict[str, Any],
) -> list[FixedPointConstructionFrontierSupportSurface]:
    path_by_subject = {
        "fixed_point_construction_cases": paths["fixed_point_construction_cases_path"],
        "diagonal_instance_candidate_surface": paths[
            "diagonal_instance_candidate_surface_path"
        ],
        "substitution_witness_bridge": paths["substitution_witness_bridge_path"],
        "substitution_graph_correctness_bridge": paths[
            "substitution_graph_correctness_bridge_path"
        ],
        "bridge_equality_alignment": paths["bridge_equality_alignment_path"],
        "bridge_equality_evaluation": paths["bridge_equality_evaluation_path"],
        "bridge_equality_certificate": paths["bridge_equality_certificate_path"],
        "equation_lifting_alignment": paths["equation_lifting_alignment_path"],
    }
    surfaces: list[FixedPointConstructionFrontierSupportSurface] = []
    for subject in REQUIRED_DEPENDENCY_SUBJECTS:
        report = dependency_reports[subject]
        failed_subjects = tuple(report.failed_subjects)
        accepted = bool(report.accepted)
        detail = "accepted" if accepted else "rejected: " + _joined_or_none(failed_subjects)
        surfaces.append(
            FixedPointConstructionFrontierSupportSurface(
                subject=subject,
                path=path_by_subject[subject],
                accepted=accepted,
                failed_subjects=failed_subjects,
                detail=detail,
            )
        )
    return surfaces


def _validate_manifest(
    manifest: FixedPointConstructionFrontierStatusManifest,
) -> list[FixedPointConstructionFrontierStatusValidation]:
    results: list[FixedPointConstructionFrontierStatusValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.status_set_id == "as-fixed-point-construction-frontier-status-v1":
        results.append(_accepted("status_set_id", "status set id matches"))
    else:
        results.append(_rejected("status_set_id", "unexpected status set id"))

    if manifest.frontier_status == REQUIRED_FRONTIER_STATUS:
        results.append(_accepted("frontier_status", "frontier remains blocked"))
    elif manifest.frontier_status == "fixed-point-equation-proved":
        results.append(
            _rejected(
                "frontier_status",
                "overclaiming frontier status: fixed-point-equation-proved",
            )
        )
    else:
        results.append(
            _rejected(
                "frontier_status",
                "unsupported frontier status: " + manifest.frontier_status,
            )
        )

    if manifest.frontier_blocked_by == REQUIRED_FRONTIER_BLOCKER:
        results.append(_accepted("frontier_blocked_by", "blocked by fixed-point-construction"))
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                "expected fixed-point-construction blocker",
            )
        )

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    results.extend(_validate_case_status_paths(manifest.case_status_paths))

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in manifest.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_case_status_paths(
    paths: dict[str, str],
) -> list[FixedPointConstructionFrontierStatusValidation]:
    results: list[FixedPointConstructionFrontierStatusValidation] = []
    missing = [
        case_kind for case_kind in REQUIRED_CASE_STATUS_PATHS if case_kind not in paths
    ]
    extra = [
        case_kind for case_kind in paths if case_kind not in REQUIRED_CASE_STATUS_PATHS
    ]
    mismatched = [
        (
            case_kind,
            REQUIRED_CASE_STATUS_PATHS[case_kind],
            paths[case_kind],
        )
        for case_kind in REQUIRED_CASE_STATUS_PATHS
        if case_kind in paths
        and paths[case_kind] != REQUIRED_CASE_STATUS_PATHS[case_kind]
    ]
    if not missing and not extra and not mismatched:
        return [_accepted("case_status_paths", "compact case-status paths match")]

    detail: list[str] = []
    if missing:
        detail.append("missing case-status paths: " + ", ".join(missing))
    if extra:
        detail.append("unexpected case-status paths: " + ", ".join(extra))
    if mismatched:
        detail.append(
            "case-status path mismatches: "
            + "; ".join(
                f"{case_kind} expected {expected} but found {actual}"
                for case_kind, expected, actual in mismatched
            )
        )
    results.append(_rejected("case_status_paths", "; ".join(detail)))
    return results


def _validate_support_surfaces(
    surfaces: list[FixedPointConstructionFrontierSupportSurface],
) -> list[FixedPointConstructionFrontierStatusValidation]:
    results: list[FixedPointConstructionFrontierStatusValidation] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_DEPENDENCY_SUBJECTS:
        results.append(_accepted("support_surfaces", "required support surfaces present"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    for surface in surfaces:
        if surface.accepted:
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _case_supports(
    construction_cases: Any | None,
    accepted_support_subjects: frozenset[str],
) -> tuple[
    list[FixedPointConstructionFrontierCaseSupport],
    list[FixedPointConstructionFrontierStatusValidation],
]:
    if construction_cases is None:
        return [], [_rejected("cases", "construction cases could not be loaded")]

    case_supports: list[FixedPointConstructionFrontierCaseSupport] = []
    results: list[FixedPointConstructionFrontierStatusValidation] = []
    cases = tuple(construction_cases.cases)
    if len(cases) == 5:
        results.append(_accepted("cases", "five construction cases observed"))
    else:
        results.append(_rejected("cases", f"expected 5 construction cases, found {len(cases)}"))

    for case in cases:
        finite_support_subjects = SUPPORT_BY_CASE_KIND.get(case.case_kind, ())
        finite_support_accepted = all(
            subject in accepted_support_subjects for subject in finite_support_subjects
        )
        case_supports.append(
            FixedPointConstructionFrontierCaseSupport(
                case_id=case.case_id,
                case_kind=case.case_kind,
                target_id=case.target_id,
                status=case.status,
                finite_support_subjects=finite_support_subjects,
                finite_support_accepted=finite_support_accepted,
            )
        )

        if case.status == "proof-case-open":
            results.append(_accepted(f"{case.case_id}.status", "construction case remains open"))
        else:
            results.append(
                _rejected(
                    f"{case.case_id}.status",
                    f"construction case is not open: {case.status}",
                )
            )

        if not finite_support_subjects:
            results.append(_rejected(f"{case.case_id}.finite_support", "no finite support mapping"))
        elif finite_support_accepted:
            results.append(_accepted(f"{case.case_id}.finite_support", "finite support accepted"))
        else:
            missing = [
                subject
                for subject in finite_support_subjects
                if subject not in accepted_support_subjects
            ]
            results.append(
                _rejected(
                    f"{case.case_id}.finite_support",
                    "support surfaces rejected: " + ", ".join(missing),
                )
            )
    return case_supports, results


def _case_status_rollup(
    paths: dict[str, str],
    construction_cases_by_kind: dict[str, FixedPointConstructionFrontierCaseSupport],
) -> tuple[
    list[FixedPointConstructionFrontierCaseStatusRollup],
    list[FixedPointConstructionFrontierStatusValidation],
]:
    rollup: list[FixedPointConstructionFrontierCaseStatusRollup] = []
    results: list[FixedPointConstructionFrontierStatusValidation] = []

    # The compact handoffs own their local validation. The aggregate only
    # enforces the cross-status contract: accepted, blocked, and still open.
    for case_kind, expected_path in REQUIRED_CASE_STATUS_PATHS.items():
        subject = f"case_status.{case_kind}"
        expected_blocker = EXPECTED_CASE_STATUS_BLOCKERS[case_kind]
        construction_case = construction_cases_by_kind.get(case_kind)
        construction_case_id = _aggregate_case_value(construction_case, "case_id")
        construction_case_status = _aggregate_case_value(construction_case, "status")
        path_text = paths.get(case_kind)
        if not path_text:
            results.append(_rejected(f"{subject}.path", "missing case-status path"))
            rollup.append(
                FixedPointConstructionFrontierCaseStatusRollup(
                    case_kind=case_kind,
                    path=Path("<missing>"),
                    accepted=False,
                    frontier_status="missing",
                    expected_frontier_blocker=expected_blocker,
                    frontier_blocked_by="missing",
                    construction_case_id=construction_case_id,
                    construction_case_status=construction_case_status,
                    failed_subjects=("case-status-path-missing",),
                    detail=f"missing case-status path: expected {expected_path}",
                )
            )
            continue

        path = Path(path_text)
        load_status, validate_status = _CASE_STATUS_VALIDATORS[case_kind]
        try:
            status_manifest = load_status(path)
            status_report = validate_status(status_manifest)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            detail = f"case status missing or invalid: {exc}"
            results.append(_rejected(f"{subject}.load", detail))
            rollup.append(
                FixedPointConstructionFrontierCaseStatusRollup(
                    case_kind=case_kind,
                    path=path,
                    accepted=False,
                    frontier_status="missing",
                    expected_frontier_blocker=expected_blocker,
                    frontier_blocked_by="missing",
                    construction_case_id=construction_case_id,
                    construction_case_status=construction_case_status,
                    failed_subjects=("case-status-load",),
                    detail=detail,
                )
            )
            continue

        compact_case = _case_status_report_case(status_report)
        if compact_case is not None:
            construction_case_id = _case_status_case_value(compact_case, "case_id")
            construction_case_status = _case_status_case_value(
                compact_case,
                "status",
            )
        compact_case_kind = _case_status_case_value(compact_case, "case_kind")
        failed_subjects = tuple(getattr(status_report, "failed_subjects", ()))
        frontier_status = str(getattr(status_report, "frontier_status", "missing"))
        frontier_blocked_by = str(
            getattr(status_report, "frontier_blocked_by", "missing")
        )

        case_results = _validate_case_status_report(
            case_kind=case_kind,
            expected_blocker=expected_blocker,
            report=status_report,
            frontier_status=frontier_status,
            frontier_blocked_by=frontier_blocked_by,
            compact_case_kind=compact_case_kind,
            construction_case_status=construction_case_status,
            failed_subjects=failed_subjects,
        )
        results.extend(case_results)
        accepted = all(result.accepted for result in case_results)
        if accepted:
            detail = "accepted compact construction-case status"
        else:
            detail = "rejected compact construction-case status"
        rollup.append(
            FixedPointConstructionFrontierCaseStatusRollup(
                case_kind=case_kind,
                path=path,
                accepted=accepted,
                frontier_status=frontier_status,
                expected_frontier_blocker=expected_blocker,
                frontier_blocked_by=frontier_blocked_by,
                construction_case_id=construction_case_id,
                construction_case_status=construction_case_status,
                failed_subjects=failed_subjects,
                detail=detail,
            )
        )
    return rollup, results


def _validate_case_status_report(
    *,
    case_kind: str,
    expected_blocker: str,
    report: Any,
    frontier_status: str,
    frontier_blocked_by: str,
    compact_case_kind: str,
    construction_case_status: str,
    failed_subjects: tuple[str, ...],
) -> list[FixedPointConstructionFrontierStatusValidation]:
    subject = f"case_status.{case_kind}"
    results: list[FixedPointConstructionFrontierStatusValidation] = []
    if bool(getattr(report, "accepted", False)):
        results.append(_accepted(f"{subject}.accepted", "case status accepted"))
    else:
        results.append(
            _rejected(
                f"{subject}.accepted",
                "case status validator rejected: "
                + _case_status_failure_detail(failed_subjects),
            )
        )

    if frontier_status == REQUIRED_FRONTIER_STATUS:
        results.append(_accepted(f"{subject}.frontier_status", "frontier blocked"))
    else:
        results.append(
            _rejected(
                f"{subject}.frontier_status",
                f"expected blocked but found {frontier_status}",
            )
        )

    if frontier_blocked_by == expected_blocker:
        results.append(
            _accepted(f"{subject}.frontier_blocked_by", "blocker matches handoff")
        )
    else:
        results.append(
            _rejected(
                f"{subject}.frontier_blocked_by",
                f"expected {expected_blocker} blocker but found {frontier_blocked_by}",
            )
        )

    if compact_case_kind in {"missing", case_kind}:
        results.append(_accepted(f"{subject}.case_kind", "case kind matches"))
    else:
        results.append(
            _rejected(
                f"{subject}.case_kind",
                f"expected {case_kind} case kind but found {compact_case_kind}",
            )
        )

    if construction_case_status == REQUIRED_CASE_STATUS:
        results.append(
            _accepted(
                f"{subject}.construction_case_status",
                "construction case remains open",
            )
        )
    else:
        results.append(
            _rejected(
                f"{subject}.construction_case_status",
                f"expected proof-case-open but found {construction_case_status}",
            )
        )

    if compact_case_kind == "missing":
        open_case_count = getattr(report, "open_case_count", None)
        case_count = getattr(report, "case_count", None)
        if open_case_count == case_count and case_count:
            results.append(
                _accepted(
                    f"{subject}.open_cases",
                    "compact handoff cases remain open",
                )
            )
        else:
            results.append(
                _rejected(
                    f"{subject}.open_cases",
                    "compact handoff does not expose all cases open",
                )
            )
    return results


def _case_status_report_case(report: Any) -> Any | None:
    construction_case = getattr(report, "construction_case", None)
    if construction_case is not None:
        return construction_case
    proof_case = getattr(report, "proof_case", None)
    if proof_case is not None:
        return proof_case
    return getattr(report, "case", None)


def _case_status_case_value(case: Any | None, field: str) -> str:
    if case is None:
        return "missing"
    return str(getattr(case, field, "missing"))


def _aggregate_case_value(
    case: FixedPointConstructionFrontierCaseSupport | None,
    field: str,
) -> str:
    if case is None:
        return "missing"
    return str(getattr(case, field, "missing"))


def _case_status_failure_detail(failed_subjects: tuple[str, ...]) -> str:
    if failed_subjects:
        return ", ".join(failed_subjects)
    return "unknown failure"


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "fixed-point-construction-frontier-status"
    if subject.endswith(".status"):
        return "fixed-point-construction-frontier-case-status"
    if subject == "non_claims":
        return "fixed-point-construction-frontier-non-claim"
    if subject == "case_status_paths" or subject.startswith("case_status."):
        return "fixed-point-construction-frontier-case-status-rollup"
    if subject in REQUIRED_DEPENDENCY_SUBJECTS or subject.endswith("_path"):
        return "fixed-point-construction-frontier-dependency"
    if subject.endswith(".finite_support") or subject in {"cases", "support_surfaces"}:
        return "fixed-point-construction-frontier-support"
    return "fixed-point-construction-frontier"


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"required list field missing: {key}")
    return value


def _required_text_map(item: dict[str, Any], key: str) -> dict[str, str]:
    value = item.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"required object field missing: {key}")
    result: dict[str, str] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"{key} contains non-text key")
        if not isinstance(map_value, str) or not map_value.strip():
            raise ValueError(f"{key} contains non-text value")
        result[map_key] = map_value
    return result


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    values = _required_list(item, key)
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        result.append(value)
    return result


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointConstructionFrontierStatusValidation:
    return FixedPointConstructionFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointConstructionFrontierStatusValidation:
    return FixedPointConstructionFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_construction_frontier_status_cli())
