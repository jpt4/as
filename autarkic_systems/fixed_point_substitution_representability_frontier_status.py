"""Compact fixed-point substitution representability frontier status.

The fixed-point construction case map has a dedicated
``substitution-representability-proof`` case. This module gives that case a
small fail-closed status surface: it checks that the current manifests still
name the intended dependencies, that the construction case is still open, and
that the witness bridge is present as finite support. It intentionally avoids
promoting any support surface into a proof.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_equation_bridge import (
    load_fixed_point_equation_bridge_targets,
)
from autarkic_systems.fixed_point_substitution_witness_bridge import (
    load_fixed_point_substitution_witness_bridge,
)
from autarkic_systems.substitution_graph_correctness_cases import (
    load_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_representability import (
    load_substitution_representability_targets,
)


DEFAULT_STATUS = Path(
    "claims/fixed_point_substitution_representability_frontier_status.json"
)

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "substitution-representability-proof"
REQUIRED_CONSTRUCTION_CASE_KIND = "substitution-representability-proof"
REQUIRED_CONSTRUCTION_CASE_STATUS = "proof-case-open"
REQUIRED_CASE_DEPENDENCY_SUBJECTS = (
    "substitution_representability",
    "substitution_graph_correctness_cases",
    "fixed_point_equation_bridge",
    "substitution_witness_bridge",
)
REQUIRED_SUPPORT_SUBJECTS = (
    "fixed_point_construction_cases",
    "substitution_representability_target",
    "substitution_graph_correctness_cases",
    "fixed_point_equation_bridge",
    "substitution_witness_bridge",
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
    "substitution_representability_targets_path": (
        "claims/substitution_representability_targets.json"
    ),
    "substitution_graph_correctness_cases_path": (
        "claims/substitution_graph_correctness_cases.json"
    ),
    "fixed_point_equation_bridge_targets_path": (
        "claims/fixed_point_equation_bridge_targets.json"
    ),
    "substitution_witness_bridge_path": (
        "claims/fixed_point_substitution_witness_bridge.json"
    ),
}
PROOF_PROMOTION_FRONTIER_STATUSES = {
    "substitution-representability-proved",
    "substitution-representability-proof-closed",
    "fixed-point-equation-proved",
    "self-consistency-proved",
}


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityFrontierStatusManifest:
    """Loaded compact manifest for the substitution representability frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    fixed_point_construction_cases_path: str
    substitution_representability_targets_path: str
    substitution_graph_correctness_cases_path: str
    fixed_point_equation_bridge_targets_path: str
    substitution_witness_bridge_path: str
    required_construction_case_kind: str
    required_construction_case_status: str
    expected_support_surface_count: int
    expected_substitution_witness_bridge_count: int
    expected_witness_output_code_length: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityFrontierStatusValidation:
    """One validation result for the compact frontier status."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilitySupportSurface:
    """Observed compact facts for one dependency surface."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str
    facts: dict[str, Any]


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityConstructionCaseStatus:
    """Status of the construction case owned by this frontier."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    non_claims: tuple[str, ...]


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityFrontierStatusReport:
    """Validation report for the compact substitution representability frontier."""

    manifest: FixedPointSubstitutionRepresentabilityFrontierStatusManifest
    fixed_point_construction_cases_path: Path
    substitution_representability_targets_path: Path
    substitution_graph_correctness_cases_path: Path
    fixed_point_equation_bridge_targets_path: Path
    substitution_witness_bridge_path: Path
    construction_case: (
        FixedPointSubstitutionRepresentabilityConstructionCaseStatus | None
    )
    results: tuple[
        FixedPointSubstitutionRepresentabilityFrontierStatusValidation,
        ...,
    ]
    support_surfaces: tuple[
        FixedPointSubstitutionRepresentabilitySupportSurface,
        ...,
    ]

    @property
    def accepted(self) -> bool:
        """Return whether every compact frontier validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the preserved aggregate frontier status."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the proof obligation that still blocks the frontier."""

        return self.manifest.frontier_blocked_by

    @property
    def construction_case_id(self) -> str:
        """Return the active construction case id, if it was observed."""

        if self.construction_case is None:
            return ""
        return self.construction_case.case_id

    @property
    def construction_case_kind(self) -> str:
        """Return the active construction case kind, if it was observed."""

        if self.construction_case is None:
            return ""
        return self.construction_case.case_kind

    @property
    def construction_case_status(self) -> str:
        """Return the active construction case status, if it was observed."""

        if self.construction_case is None:
            return ""
        return self.construction_case.status

    @property
    def support_surface_count(self) -> int:
        """Return the number of compact support surfaces inspected."""

        return len(self.support_surfaces)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return compact failure subjects for automation."""

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
    """Small report shim used when a support manifest cannot be loaded."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]


def load_fixed_point_substitution_representability_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> FixedPointSubstitutionRepresentabilityFrontierStatusManifest:
    """Load the compact substitution representability frontier manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return FixedPointSubstitutionRepresentabilityFrontierStatusManifest(
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
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        substitution_graph_correctness_cases_path=_required_text(
            data,
            "substitution_graph_correctness_cases_path",
        ),
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        substitution_witness_bridge_path=_required_text(
            data,
            "substitution_witness_bridge_path",
        ),
        required_construction_case_kind=_required_text(
            data,
            "required_construction_case_kind",
        ),
        required_construction_case_status=_required_text(
            data,
            "required_construction_case_status",
        ),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        expected_substitution_witness_bridge_count=_required_int(
            data,
            "expected_substitution_witness_bridge_count",
        ),
        expected_witness_output_code_length=_required_int(
            data,
            "expected_witness_output_code_length",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_substitution_representability_frontier_status(
    manifest: FixedPointSubstitutionRepresentabilityFrontierStatusManifest,
) -> FixedPointSubstitutionRepresentabilityFrontierStatusReport:
    """Validate compact status facts for the current representability frontier."""

    paths = _manifest_paths(manifest)

    construction_cases, construction_cases_report = _load_dependency_manifest(
        "fixed_point_construction_cases",
        paths["fixed_point_construction_cases_path"],
        load_fixed_point_construction_cases,
        "fixed-point-construction-cases-load",
    )
    dependency_reports = {
        "fixed_point_construction_cases": construction_cases_report,
        "substitution_representability_target": _load_dependency_manifest(
            "substitution_representability_target",
            paths["substitution_representability_targets_path"],
            load_substitution_representability_targets,
            "substitution-representability-target-load",
        )[1],
        "substitution_graph_correctness_cases": _load_dependency_manifest(
            "substitution_graph_correctness_cases",
            paths["substitution_graph_correctness_cases_path"],
            load_substitution_graph_correctness_cases,
            "substitution-graph-correctness-cases-load",
        )[1],
        "fixed_point_equation_bridge": _load_dependency_manifest(
            "fixed_point_equation_bridge",
            paths["fixed_point_equation_bridge_targets_path"],
            load_fixed_point_equation_bridge_targets,
            "fixed-point-equation-bridge-load",
        )[1],
        "substitution_witness_bridge": _load_dependency_manifest(
            "substitution_witness_bridge",
            paths["substitution_witness_bridge_path"],
            load_fixed_point_substitution_witness_bridge,
            "fixed-point-substitution-witness-bridge-load",
        )[1],
    }

    results: list[FixedPointSubstitutionRepresentabilityFrontierStatusValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    support_surfaces = _support_surfaces(paths, dependency_reports)
    results.extend(_validate_support_surfaces(manifest, support_surfaces))

    construction_case = _construction_case_status(construction_cases)
    results.extend(_validate_construction_case(construction_case))

    return FixedPointSubstitutionRepresentabilityFrontierStatusReport(
        manifest=manifest,
        fixed_point_construction_cases_path=paths["fixed_point_construction_cases_path"],
        substitution_representability_targets_path=paths[
            "substitution_representability_targets_path"
        ],
        substitution_graph_correctness_cases_path=paths[
            "substitution_graph_correctness_cases_path"
        ],
        fixed_point_equation_bridge_targets_path=paths[
            "fixed_point_equation_bridge_targets_path"
        ],
        substitution_witness_bridge_path=paths["substitution_witness_bridge_path"],
        construction_case=construction_case,
        results=tuple(results),
        support_surfaces=tuple(support_surfaces),
    )


def fixed_point_substitution_representability_frontier_status_payload(
    report: FixedPointSubstitutionRepresentabilityFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready compact frontier status payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "status_manifest": str(report.manifest.path),
        "status_set_id": report.manifest.status_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_status": report.frontier_status,
        "frontier_blocked_by": report.frontier_blocked_by,
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "substitution_graph_correctness_cases_path": str(
            report.substitution_graph_correctness_cases_path
        ),
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "substitution_witness_bridge_path": str(
            report.substitution_witness_bridge_path
        ),
        "required_construction_case_kind": (
            report.manifest.required_construction_case_kind
        ),
        "required_construction_case_status": (
            report.manifest.required_construction_case_status
        ),
        "construction_case_id": report.construction_case_id,
        "construction_case_kind": report.construction_case_kind,
        "construction_case_status": report.construction_case_status,
        "expected_support_surface_count": (
            report.manifest.expected_support_surface_count
        ),
        "support_surface_count": report.support_surface_count,
        "expected_substitution_witness_bridge_count": (
            report.manifest.expected_substitution_witness_bridge_count
        ),
        "expected_witness_output_code_length": (
            report.manifest.expected_witness_output_code_length
        ),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "support_surfaces": [
            {
                "subject": surface.subject,
                "path": str(surface.path),
                "accepted": surface.accepted,
                "failed_subjects": list(surface.failed_subjects),
                "detail": surface.detail,
                "facts": surface.facts,
            }
            for surface in report.support_surfaces
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


def format_fixed_point_substitution_representability_frontier_status_report(
    report: FixedPointSubstitutionRepresentabilityFrontierStatusReport,
) -> str:
    """Format a concise human-readable frontier status report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point substitution representability frontier status: {status}",
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Construction case: {_or_none(report.construction_case_id)}",
        f"Kind: {_or_none(report.construction_case_kind)}",
        f"Status: {_or_none(report.construction_case_status)}",
        f"Support surfaces: {report.support_surface_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        lines.append(f"- {surface.subject}: {prefix} ({surface.path})")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_substitution_representability_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point substitution representability frontier validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_substitution_representability_frontier_status"
        ),
        description=(
            "Validate the AS fixed-point substitution representability "
            "frontier status."
        ),
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the substitution representability frontier manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_substitution_representability_frontier_status(
        args.status
    )
    report = validate_fixed_point_substitution_representability_frontier_status(
        manifest
    )
    if args.format == "json":
        print(json.dumps(
            fixed_point_substitution_representability_frontier_status_payload(
                report
            ),
            sort_keys=True,
        ))
    else:
        print(
            format_fixed_point_substitution_representability_frontier_status_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointSubstitutionRepresentabilityFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "fixed_point_construction_cases_path": Path(
            manifest.fixed_point_construction_cases_path
        ),
        "substitution_representability_targets_path": Path(
            manifest.substitution_representability_targets_path
        ),
        "substitution_graph_correctness_cases_path": Path(
            manifest.substitution_graph_correctness_cases_path
        ),
        "fixed_point_equation_bridge_targets_path": Path(
            manifest.fixed_point_equation_bridge_targets_path
        ),
        "substitution_witness_bridge_path": Path(
            manifest.substitution_witness_bridge_path
        ),
    }


def _load_dependency_manifest(
    subject: str,
    path: Path,
    loader: Callable[[Path], Any],
    load_failure_subject: str,
) -> tuple[Any | None, _DependencyFailure]:
    try:
        loaded = loader(path)
        return loaded, _validate_loaded_support_manifest(subject, loaded)
    except (OSError, ValueError, json.JSONDecodeError, AttributeError):
        return None, _DependencyFailure(
            False,
            (load_failure_subject,),
            {"path": str(path)},
        )


def _validate_loaded_support_manifest(
    subject: str,
    loaded: Any,
) -> _DependencyFailure:
    """Check cheap manifest-level facts owned by this status surface."""

    failures: list[str] = []
    facts: dict[str, Any] = {}

    if subject == "fixed_point_construction_cases":
        cases = tuple(loaded.cases)
        target_case = _find_case_by_kind(cases, REQUIRED_CONSTRUCTION_CASE_KIND)
        facts = {
            "case_set_id": loaded.case_set_id,
            "case_count": len(cases),
            "construction_case_id": getattr(target_case, "case_id", ""),
            "construction_case_kind": getattr(target_case, "case_kind", ""),
            "construction_case_status": getattr(target_case, "status", ""),
        }
        _require_attr_value(
            loaded,
            "case_set_id",
            "as-fixed-point-construction-cases-v1",
            "fixed-point-construction-cases-id",
            failures,
        )
        if len(cases) != 5:
            failures.append("fixed-point-construction-cases-count")
        if target_case is None:
            failures.append("fixed-point-substitution-representability-case-missing")
        elif target_case.status != REQUIRED_CONSTRUCTION_CASE_STATUS:
            failures.append(
                "fixed-point-substitution-representability-frontier-case-status"
            )
    elif subject == "substitution_representability_target":
        witnesses = tuple(loaded.witnesses)
        witness = witnesses[0] if witnesses else None
        facts = {
            "witness_set_id": loaded.witness_set_id,
            "witness_count": len(witnesses),
            "witness_status": getattr(witness, "status", ""),
            "expected_output_code_length": getattr(
                witness,
                "expected_output_code_length",
                None,
            ),
            "non_claim_count": len(getattr(witness, "non_claims", ())),
        }
        _require_attr_value(
            loaded,
            "witness_set_id",
            "as-substitution-representability-witness-v1",
            "substitution-representability-target-id",
            failures,
        )
        if len(witnesses) != 1:
            failures.append("substitution-representability-target-count")
        if witness is None:
            failures.append("substitution-representability-target-witness")
        else:
            if witness.status != "representability-witness-not-proof":
                failures.append("substitution-representability-target-status")
            if witness.expected_output_code_length != 296:
                failures.append("substitution-representability-target-length")
            _require_explicit_non_claims(
                witness.non_claims,
                ("no substitution representability proof",),
                "substitution-representability-target-non-claim",
                failures,
            )
    elif subject == "substitution_graph_correctness_cases":
        cases = tuple(loaded.cases)
        facts = {
            "case_set_id": loaded.case_set_id,
            "case_count": len(cases),
            "open_case_count": sum(
                1 for case in cases if case.status == "proof-case-open"
            ),
        }
        _require_attr_value(
            loaded,
            "case_set_id",
            "as-substitution-graph-correctness-cases-v1",
            "substitution-graph-correctness-cases-id",
            failures,
        )
        if len(cases) != 5:
            failures.append("substitution-graph-correctness-cases-count")
        if any(case.status != "proof-case-open" for case in cases):
            failures.append("substitution-graph-correctness-cases-status")
        for case in cases:
            _require_explicit_non_claims(
                case.non_claims,
                ("no substitution representability proof",),
                "substitution-graph-correctness-cases-non-claim",
                failures,
            )
    elif subject == "fixed_point_equation_bridge":
        bridges = tuple(loaded.bridges)
        bridge = bridges[0] if bridges else None
        facts = {
            "bridge_set_id": loaded.bridge_set_id,
            "bridge_count": len(bridges),
            "bridge_status": getattr(bridge, "status", ""),
            "expected_diagonal_instance_code_length": getattr(
                bridge,
                "expected_diagonal_instance_code_length",
                None,
            ),
        }
        _require_attr_value(
            loaded,
            "bridge_set_id",
            "as-fixed-point-equation-bridge-v1",
            "fixed-point-equation-bridge-id",
            failures,
        )
        if len(bridges) != 1:
            failures.append("fixed-point-equation-bridge-count")
        if bridge is None:
            failures.append("fixed-point-equation-bridge-target")
        else:
            if bridge.status != "bridge-target-open":
                failures.append("fixed-point-equation-bridge-status")
            if bridge.expected_diagonal_instance_code_length != 296:
                failures.append("fixed-point-equation-bridge-length")
            _require_explicit_non_claims(
                bridge.non_claims,
                (
                    "no substitution representability proof",
                    "no fixed-point equation proof",
                ),
                "fixed-point-equation-bridge-non-claim",
                failures,
            )
    elif subject == "substitution_witness_bridge":
        facts = {
            "bridge_set_id": loaded.bridge_set_id,
            "expected_bridge_count": loaded.expected_bridge_count,
            "expected_witness_output_code_length": (
                loaded.expected_witness_output_code_length
            ),
            "non_claim_count": len(loaded.non_claims),
        }
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
        _require_attr_value(
            loaded,
            "expected_witness_output_code_length",
            296,
            "fixed-point-substitution-witness-bridge-length",
            failures,
        )
        _require_explicit_non_claims(
            loaded.non_claims,
            REQUIRED_NON_CLAIMS,
            "fixed-point-substitution-witness-bridge-non-claim",
            failures,
        )
    else:
        failures.append("fixed-point-substitution-representability-unknown-support")

    return _DependencyFailure(not failures, tuple(dict.fromkeys(failures)), facts)


def _support_surfaces(
    paths: dict[str, Path],
    dependency_reports: dict[str, _DependencyFailure],
) -> list[FixedPointSubstitutionRepresentabilitySupportSurface]:
    path_by_subject = {
        "fixed_point_construction_cases": paths["fixed_point_construction_cases_path"],
        "substitution_representability_target": paths[
            "substitution_representability_targets_path"
        ],
        "substitution_graph_correctness_cases": paths[
            "substitution_graph_correctness_cases_path"
        ],
        "fixed_point_equation_bridge": paths["fixed_point_equation_bridge_targets_path"],
        "substitution_witness_bridge": paths["substitution_witness_bridge_path"],
    }
    surfaces: list[FixedPointSubstitutionRepresentabilitySupportSurface] = []
    for subject in REQUIRED_SUPPORT_SUBJECTS:
        report = dependency_reports[subject]
        failed_subjects = report.failed_subjects
        accepted = report.accepted
        detail = "accepted" if accepted else "rejected: " + _joined_or_none(failed_subjects)
        surfaces.append(
            FixedPointSubstitutionRepresentabilitySupportSurface(
                subject=subject,
                path=path_by_subject[subject],
                accepted=accepted,
                failed_subjects=failed_subjects,
                detail=detail,
                facts=report.facts,
            )
        )
    return surfaces


def _validate_manifest(
    manifest: FixedPointSubstitutionRepresentabilityFrontierStatusManifest,
) -> list[FixedPointSubstitutionRepresentabilityFrontierStatusValidation]:
    results: list[FixedPointSubstitutionRepresentabilityFrontierStatusValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if (
        manifest.status_set_id
        == "as-fixed-point-substitution-representability-frontier-status-v1"
    ):
        results.append(_accepted("status_set_id", "status set id matches"))
    else:
        results.append(_rejected("status_set_id", "unexpected status set id"))

    if manifest.frontier_status == REQUIRED_FRONTIER_STATUS:
        results.append(_accepted("frontier_status", "frontier remains blocked"))
    elif manifest.frontier_status in PROOF_PROMOTION_FRONTIER_STATUSES:
        results.append(
            _rejected(
                "frontier_status",
                "proof-promotion frontier status: " + manifest.frontier_status,
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
        results.append(
            _accepted(
                "frontier_blocked_by",
                "blocked by substitution-representability-proof",
            )
        )
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                "expected substitution-representability-proof blocker",
            )
        )

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.required_construction_case_kind == REQUIRED_CONSTRUCTION_CASE_KIND:
        results.append(
            _accepted(
                "required_construction_case_kind",
                "substitution representability proof case selected",
            )
        )
    else:
        results.append(
            _rejected(
                "required_construction_case_kind",
                "wrong construction case kind",
            )
        )

    if manifest.required_construction_case_status == REQUIRED_CONSTRUCTION_CASE_STATUS:
        results.append(
            _accepted(
                "required_construction_case_status",
                "construction case must remain open",
            )
        )
    else:
        results.append(
            _rejected(
                "required_construction_case_status",
                "wrong construction case status boundary",
            )
        )

    if manifest.expected_support_surface_count == len(REQUIRED_SUPPORT_SUBJECTS):
        results.append(_accepted("expected_support_surface_count", "five supports"))
    else:
        results.append(
            _rejected(
                "expected_support_surface_count",
                "expected five support surfaces",
            )
        )

    if manifest.expected_substitution_witness_bridge_count == 1:
        results.append(
            _accepted(
                "expected_substitution_witness_bridge_count",
                "one witness bridge",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_substitution_witness_bridge_count",
                "expected one witness bridge",
            )
        )

    if manifest.expected_witness_output_code_length == 296:
        results.append(
            _accepted("expected_witness_output_code_length", "296-token witness output")
        )
    else:
        results.append(
            _rejected(
                "expected_witness_output_code_length",
                "expected 296-token witness output",
            )
        )

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in manifest.non_claims
    ]
    malformed_non_claims = [
        item for item in manifest.non_claims if not item.startswith("no ")
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    elif malformed_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "malformed non-claims: " + ", ".join(malformed_non_claims),
            )
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_support_surfaces(
    manifest: FixedPointSubstitutionRepresentabilityFrontierStatusManifest,
    surfaces: list[FixedPointSubstitutionRepresentabilitySupportSurface],
) -> list[FixedPointSubstitutionRepresentabilityFrontierStatusValidation]:
    results: list[FixedPointSubstitutionRepresentabilityFrontierStatusValidation] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "required support surfaces present"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    if len(surfaces) == manifest.expected_support_surface_count:
        results.append(_accepted("support_surface_count", "support count matches"))
    else:
        results.append(
            _rejected(
                "support_surface_count",
                "support count mismatch",
            )
        )

    for surface in surfaces:
        if surface.accepted:
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _construction_case_status(
    construction_cases: Any | None,
) -> FixedPointSubstitutionRepresentabilityConstructionCaseStatus | None:
    if construction_cases is None:
        return None

    case = _find_case_by_kind(
        tuple(construction_cases.cases),
        REQUIRED_CONSTRUCTION_CASE_KIND,
    )
    if case is None:
        return None
    return FixedPointSubstitutionRepresentabilityConstructionCaseStatus(
        case_id=case.case_id,
        case_kind=case.case_kind,
        target_id=case.target_id,
        status=case.status,
        required_dependency_subjects=tuple(case.required_dependency_subjects),
        non_claims=tuple(case.non_claims),
    )


def _validate_construction_case(
    construction_case: FixedPointSubstitutionRepresentabilityConstructionCaseStatus | None,
) -> list[FixedPointSubstitutionRepresentabilityFrontierStatusValidation]:
    results: list[FixedPointSubstitutionRepresentabilityFrontierStatusValidation] = []
    if construction_case is None:
        return [
            _rejected(
                "construction_case",
                "substitution representability construction case missing",
            )
        ]

    if construction_case.case_kind == REQUIRED_CONSTRUCTION_CASE_KIND:
        results.append(_accepted("construction_case.kind", "case kind matches"))
    else:
        results.append(_rejected("construction_case.kind", "wrong case kind"))

    if construction_case.status == REQUIRED_CONSTRUCTION_CASE_STATUS:
        results.append(
            _accepted("construction_case.status", "construction case remains open")
        )
    else:
        results.append(
            _rejected(
                "construction_case.status",
                f"construction case is not open: {construction_case.status}",
            )
        )

    if construction_case.required_dependency_subjects == REQUIRED_CASE_DEPENDENCY_SUBJECTS:
        results.append(
            _accepted(
                "construction_case.dependencies",
                "required dependencies match",
            )
        )
    else:
        results.append(
            _rejected(
                "construction_case.dependencies",
                "required dependencies changed",
            )
        )

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in construction_case.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "construction_case.non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(
            _accepted("construction_case.non_claims", "case non-claims explicit")
        )
    return results


def _find_case_by_kind(cases: tuple[Any, ...], case_kind: str) -> Any | None:
    matches = [case for case in cases if getattr(case, "case_kind", "") == case_kind]
    if len(matches) != 1:
        return None
    return matches[0]


def _require_attr_value(
    loaded: Any,
    attr: str,
    expected: Any,
    failure: str,
    failures: list[str],
) -> None:
    if getattr(loaded, attr, None) != expected:
        failures.append(failure)


def _require_explicit_non_claims(
    observed: tuple[str, ...],
    required: tuple[str, ...],
    failure: str,
    failures: list[str],
) -> None:
    if not observed:
        failures.append(failure)
        return
    if any(item not in observed for item in required):
        failures.append(failure)
        return
    if any(not item.startswith("no ") for item in observed):
        failures.append(failure)


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "fixed-point-substitution-representability-frontier-status"
    if subject == "non_claims" or subject.endswith(".non_claims"):
        return "fixed-point-substitution-representability-frontier-non-claim"
    if subject == "construction_case.status":
        return "fixed-point-substitution-representability-frontier-case-status"
    if subject.startswith("construction_case"):
        return "fixed-point-substitution-representability-frontier-case"
    if subject in REQUIRED_SUPPORT_SUBJECTS or subject.endswith("_path"):
        return "fixed-point-substitution-representability-frontier-dependency"
    if subject in {"support_surfaces", "support_surface_count"}:
        return "fixed-point-substitution-representability-frontier-support"
    return "fixed-point-substitution-representability-frontier"


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
) -> FixedPointSubstitutionRepresentabilityFrontierStatusValidation:
    return FixedPointSubstitutionRepresentabilityFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointSubstitutionRepresentabilityFrontierStatusValidation:
    return FixedPointSubstitutionRepresentabilityFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


def _or_none(value: str) -> str:
    if not value:
        return "none"
    return value


if __name__ == "__main__":
    raise SystemExit(
        run_fixed_point_substitution_representability_frontier_status_cli()
    )
