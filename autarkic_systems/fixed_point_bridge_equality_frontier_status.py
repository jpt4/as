"""Compact status surface for the fixed-point bridge-equality frontier.

The bridge-equality alignment and evaluation modules own the deeper finite
derivations. This module only checks that those surfaces are present with the
expected compact facts while the construction case remains open and blocked.
It deliberately avoids promoting bridge equality, fixed-point equality, proof
predicates, or self-consistency.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.fixed_point_bridge_equality_alignment import (
    load_fixed_point_bridge_equality_alignment,
)
from autarkic_systems.fixed_point_bridge_equality_evaluation import (
    load_fixed_point_bridge_equality_evaluation,
)
from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_equation_bridge import (
    load_fixed_point_equation_bridge_targets,
)
from autarkic_systems.substitution_graph_correctness_cases import (
    load_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_representability import (
    load_substitution_representability_targets,
)


DEFAULT_STATUS = Path("claims/fixed_point_bridge_equality_frontier_status.json")

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "bridge-equality-proof"
REQUIRED_CASE_KIND = "bridge-equality-proof"
REQUIRED_CASE_STATUS = "proof-case-open"
EXPECTED_BRIDGE_EQUATION_CODE_LENGTH = 4815
EXPECTED_EVALUATION_OUTPUT_CODE_LENGTH = 296
REQUIRED_SUPPORT_SUBJECTS = (
    "fixed_point_equation_bridge",
    "substitution_representability",
    "substitution_graph_correctness_cases",
    "bridge_equality_alignment",
    "bridge_equality_evaluation",
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
    "fixed_point_equation_bridge_targets_path": (
        "claims/fixed_point_equation_bridge_targets.json"
    ),
    "substitution_representability_targets_path": (
        "claims/substitution_representability_targets.json"
    ),
    "substitution_graph_correctness_cases_path": (
        "claims/substitution_graph_correctness_cases.json"
    ),
    "bridge_equality_alignment_path": (
        "claims/fixed_point_bridge_equality_alignment.json"
    ),
    "bridge_equality_evaluation_path": (
        "claims/fixed_point_bridge_equality_evaluation.json"
    ),
}
PROOF_PROMOTION_STATUSES = {
    "bridge-equality-proved",
    "fixed-point-equation-proved",
    "arithmetized-proof-predicate-proved",
    "self-consistency-proved",
    "self-consistency-theorem-proved",
}
PROOF_PROMOTION_NON_CLAIMS = {
    "substitution representability proof",
    "substitution graph correctness proof",
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "self-consistency theorem",
}


@dataclass(frozen=True)
class FixedPointBridgeEqualityFrontierStatusManifest:
    """Loaded compact manifest for the bridge-equality frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    fixed_point_construction_cases_path: str
    fixed_point_equation_bridge_targets_path: str
    substitution_representability_targets_path: str
    substitution_graph_correctness_cases_path: str
    bridge_equality_alignment_path: str
    bridge_equality_evaluation_path: str
    expected_bridge_equation_code_length: int
    expected_evaluation_output_code_length: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityFrontierStatusValidation:
    """One validation result for the bridge-equality frontier."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityFrontierConstructionCase:
    """Compact view of the bridge-equality construction case."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]


@dataclass(frozen=True)
class FixedPointBridgeEqualityFrontierSupportSurface:
    """Observed compact state of one bridge-equality support surface."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityFrontierStatusReport:
    """Validation report for the compact bridge-equality frontier."""

    manifest: FixedPointBridgeEqualityFrontierStatusManifest
    fixed_point_construction_cases_path: Path
    fixed_point_equation_bridge_targets_path: Path
    substitution_representability_targets_path: Path
    substitution_graph_correctness_cases_path: Path
    bridge_equality_alignment_path: Path
    bridge_equality_evaluation_path: Path
    construction_case: FixedPointBridgeEqualityFrontierConstructionCase
    support_surfaces: tuple[FixedPointBridgeEqualityFrontierSupportSurface, ...]
    support_facts: dict[str, dict[str, Any]]
    results: tuple[FixedPointBridgeEqualityFrontierStatusValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every bridge-equality frontier validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the compact frontier status."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the blocker preserved by this status surface."""

        return self.manifest.frontier_blocked_by

    @property
    def support_surface_count(self) -> int:
        """Return the number of required support surfaces inspected."""

        return len(self.support_surfaces)

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
class _SupportLoad:
    """Compact support load result used by the frontier validator."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]


def load_fixed_point_bridge_equality_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> FixedPointBridgeEqualityFrontierStatusManifest:
    """Load the fixed-point bridge-equality frontier status manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return FixedPointBridgeEqualityFrontierStatusManifest(
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
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        substitution_graph_correctness_cases_path=_required_text(
            data,
            "substitution_graph_correctness_cases_path",
        ),
        bridge_equality_alignment_path=_required_text(
            data,
            "bridge_equality_alignment_path",
        ),
        bridge_equality_evaluation_path=_required_text(
            data,
            "bridge_equality_evaluation_path",
        ),
        expected_bridge_equation_code_length=_required_int(
            data,
            "expected_bridge_equation_code_length",
        ),
        expected_evaluation_output_code_length=_required_int(
            data,
            "expected_evaluation_output_code_length",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_bridge_equality_frontier_status(
    manifest: FixedPointBridgeEqualityFrontierStatusManifest,
) -> FixedPointBridgeEqualityFrontierStatusReport:
    """Validate the compact bridge-equality frontier status."""

    paths = _manifest_paths(manifest)
    results: list[FixedPointBridgeEqualityFrontierStatusValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    construction_cases, construction_load = _load_support(
        paths["fixed_point_construction_cases_path"],
        load_fixed_point_construction_cases,
        _validate_construction_case_map,
        "fixed-point-construction-cases-load",
    )
    bridge_case = _find_bridge_equality_case(construction_cases)
    results.extend(_validate_bridge_case(bridge_case))

    support_loads = {
        "fixed_point_equation_bridge": _load_support(
            paths["fixed_point_equation_bridge_targets_path"],
            load_fixed_point_equation_bridge_targets,
            lambda loaded: _validate_equation_bridge(
                loaded,
                manifest.expected_bridge_equation_code_length,
            ),
            "fixed-point-equation-bridge-load",
        )[1],
        "substitution_representability": _load_support(
            paths["substitution_representability_targets_path"],
            load_substitution_representability_targets,
            lambda loaded: _validate_substitution_representability(
                loaded,
                manifest.expected_evaluation_output_code_length,
            ),
            "substitution-representability-load",
        )[1],
        "substitution_graph_correctness_cases": _load_support(
            paths["substitution_graph_correctness_cases_path"],
            load_substitution_graph_correctness_cases,
            _validate_substitution_graph_correctness_cases,
            "substitution-graph-correctness-cases-load",
        )[1],
        "bridge_equality_alignment": _load_support(
            paths["bridge_equality_alignment_path"],
            load_fixed_point_bridge_equality_alignment,
            lambda loaded: _validate_bridge_equality_alignment(
                loaded,
                manifest.expected_bridge_equation_code_length,
            ),
            "fixed-point-bridge-equality-alignment-load",
        )[1],
        "bridge_equality_evaluation": _load_support(
            paths["bridge_equality_evaluation_path"],
            load_fixed_point_bridge_equality_evaluation,
            lambda loaded: _validate_bridge_equality_evaluation(
                loaded,
                manifest.expected_bridge_equation_code_length,
                manifest.expected_evaluation_output_code_length,
            ),
            "fixed-point-bridge-equality-evaluation-load",
        )[1],
    }

    support_surfaces = _support_surfaces(paths, support_loads)
    results.extend(_validate_support_surfaces(support_surfaces))
    results.extend(_validate_case_dependencies(bridge_case, support_surfaces))
    if not construction_load.accepted:
        results.append(
            _rejected(
                "fixed_point_construction_cases",
                "construction case map rejected: "
                + _joined_or_none(construction_load.failed_subjects),
            )
        )

    return FixedPointBridgeEqualityFrontierStatusReport(
        manifest=manifest,
        fixed_point_construction_cases_path=paths[
            "fixed_point_construction_cases_path"
        ],
        fixed_point_equation_bridge_targets_path=paths[
            "fixed_point_equation_bridge_targets_path"
        ],
        substitution_representability_targets_path=paths[
            "substitution_representability_targets_path"
        ],
        substitution_graph_correctness_cases_path=paths[
            "substitution_graph_correctness_cases_path"
        ],
        bridge_equality_alignment_path=paths["bridge_equality_alignment_path"],
        bridge_equality_evaluation_path=paths["bridge_equality_evaluation_path"],
        construction_case=bridge_case,
        support_surfaces=tuple(support_surfaces),
        support_facts={
            subject: dict(load.facts) for subject, load in support_loads.items()
        },
        results=tuple(results),
    )


def fixed_point_bridge_equality_frontier_status_payload(
    report: FixedPointBridgeEqualityFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready bridge-equality frontier payload."""

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
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "substitution_graph_correctness_cases_path": str(
            report.substitution_graph_correctness_cases_path
        ),
        "bridge_equality_alignment_path": str(report.bridge_equality_alignment_path),
        "bridge_equality_evaluation_path": str(report.bridge_equality_evaluation_path),
        "expected_bridge_equation_code_length": (
            report.manifest.expected_bridge_equation_code_length
        ),
        "expected_evaluation_output_code_length": (
            report.manifest.expected_evaluation_output_code_length
        ),
        "construction_case": {
            "case_id": report.construction_case.case_id,
            "case_kind": report.construction_case.case_kind,
            "target_id": report.construction_case.target_id,
            "status": report.construction_case.status,
            "required_dependency_subjects": list(
                report.construction_case.required_dependency_subjects
            ),
        },
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "support_surface_count": report.support_surface_count,
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
        "support_facts": report.support_facts,
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


def format_fixed_point_bridge_equality_frontier_status_report(
    report: FixedPointBridgeEqualityFrontierStatusReport,
) -> str:
    """Format a concise human-readable bridge-equality frontier report."""

    status = "accepted" if report.accepted else "rejected"
    case = report.construction_case
    lines = [
        f"Fixed-point bridge equality frontier status: {status}",
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Construction case: {case.case_id}",
        f"Case kind: {case.case_kind}",
        f"Case status: {case.status}",
        f"Support surfaces: {report.support_surface_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        lines.append(f"- {surface.subject}: {prefix} ({surface.path}) {surface.detail}")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_bridge_equality_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point bridge-equality frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_bridge_equality_frontier_status"
        ),
        description="Validate the AS fixed-point bridge-equality frontier status.",
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the fixed-point bridge-equality frontier status manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_bridge_equality_frontier_status(args.status)
    report = validate_fixed_point_bridge_equality_frontier_status(manifest)
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_bridge_equality_frontier_status_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_bridge_equality_frontier_status_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointBridgeEqualityFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "fixed_point_construction_cases_path": Path(
            manifest.fixed_point_construction_cases_path
        ),
        "fixed_point_equation_bridge_targets_path": Path(
            manifest.fixed_point_equation_bridge_targets_path
        ),
        "substitution_representability_targets_path": Path(
            manifest.substitution_representability_targets_path
        ),
        "substitution_graph_correctness_cases_path": Path(
            manifest.substitution_graph_correctness_cases_path
        ),
        "bridge_equality_alignment_path": Path(
            manifest.bridge_equality_alignment_path
        ),
        "bridge_equality_evaluation_path": Path(
            manifest.bridge_equality_evaluation_path
        ),
    }


def _load_support(
    path: Path,
    loader: Callable[[Path], Any],
    validator: Callable[[Any], _SupportLoad],
    load_failure_subject: str,
) -> tuple[Any | None, _SupportLoad]:
    try:
        loaded = loader(path)
        return loaded, validator(loaded)
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _SupportLoad(
            accepted=False,
            failed_subjects=(load_failure_subject,),
            facts={},
        )


def _validate_manifest(
    manifest: FixedPointBridgeEqualityFrontierStatusManifest,
) -> list[FixedPointBridgeEqualityFrontierStatusValidation]:
    results: list[FixedPointBridgeEqualityFrontierStatusValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.status_set_id == "as-fixed-point-bridge-equality-frontier-status-v1":
        results.append(_accepted("status_set_id", "status set id matches"))
    else:
        results.append(_rejected("status_set_id", "unexpected status set id"))

    if manifest.frontier_status == REQUIRED_FRONTIER_STATUS:
        results.append(_accepted("frontier_status", "frontier remains blocked"))
    elif manifest.frontier_status in PROOF_PROMOTION_STATUSES:
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
        results.append(_accepted("frontier_blocked_by", "blocked by bridge-equality-proof"))
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                "expected bridge-equality-proof blocker",
            )
        )

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if (
        manifest.expected_bridge_equation_code_length
        == EXPECTED_BRIDGE_EQUATION_CODE_LENGTH
    ):
        results.append(_accepted("expected_bridge_equation_code_length", "4815 checked"))
    else:
        results.append(
            _rejected(
                "expected_bridge_equation_code_length",
                "expected bridge equation length 4815",
            )
        )

    if (
        manifest.expected_evaluation_output_code_length
        == EXPECTED_EVALUATION_OUTPUT_CODE_LENGTH
    ):
        results.append(
            _accepted("expected_evaluation_output_code_length", "296 checked")
        )
    else:
        results.append(
            _rejected(
                "expected_evaluation_output_code_length",
                "expected evaluation output length 296",
            )
        )

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in manifest.non_claims
    ]
    proof_promotions = [
        item for item in manifest.non_claims if item in PROOF_PROMOTION_NON_CLAIMS
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    elif proof_promotions:
        results.append(
            _rejected(
                "non_claims",
                "proof-promotion non-claims: " + ", ".join(proof_promotions),
            )
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_construction_case_map(loaded: Any) -> _SupportLoad:
    failures: list[str] = []
    if getattr(loaded, "case_set_id", None) != "as-fixed-point-construction-cases-v1":
        failures.append("fixed-point-construction-cases-id")
    cases = tuple(getattr(loaded, "cases", ()))
    if len(cases) != 5:
        failures.append("fixed-point-construction-cases-count")
    if _find_bridge_equality_case(loaded).case_kind != REQUIRED_CASE_KIND:
        failures.append("fixed-point-bridge-equality-frontier-case")
    return _SupportLoad(
        accepted=not failures,
        failed_subjects=tuple(failures),
        facts={"case_count": len(cases)},
    )


def _find_bridge_equality_case(
    construction_cases: Any | None,
) -> FixedPointBridgeEqualityFrontierConstructionCase:
    if construction_cases is None:
        return FixedPointBridgeEqualityFrontierConstructionCase(
            case_id="missing",
            case_kind="missing",
            target_id="missing",
            status="missing",
            required_dependency_subjects=(),
        )
    for case in tuple(getattr(construction_cases, "cases", ())):
        if getattr(case, "case_kind", None) != REQUIRED_CASE_KIND:
            continue
        return FixedPointBridgeEqualityFrontierConstructionCase(
            case_id=case.case_id,
            case_kind=case.case_kind,
            target_id=case.target_id,
            status=case.status,
            required_dependency_subjects=tuple(case.required_dependency_subjects),
        )
    return FixedPointBridgeEqualityFrontierConstructionCase(
        case_id="missing",
        case_kind="missing",
        target_id="missing",
        status="missing",
        required_dependency_subjects=(),
    )


def _validate_bridge_case(
    case: FixedPointBridgeEqualityFrontierConstructionCase,
) -> list[FixedPointBridgeEqualityFrontierStatusValidation]:
    results: list[FixedPointBridgeEqualityFrontierStatusValidation] = []
    if case.case_kind == REQUIRED_CASE_KIND:
        results.append(_accepted("construction_case.kind", "bridge equality case found"))
    else:
        results.append(_rejected("construction_case.kind", "bridge equality case missing"))

    if case.status == REQUIRED_CASE_STATUS:
        results.append(_accepted("construction_case.status", "construction case remains open"))
    else:
        results.append(
            _rejected(
                "construction_case.status",
                "construction case is not open: " + case.status,
            )
        )
    return results


def _validate_equation_bridge(
    loaded: Any,
    expected_bridge_length: int,
) -> _SupportLoad:
    failures: list[str] = []
    bridges = tuple(getattr(loaded, "bridges", ()))
    bridge = bridges[0] if bridges else None
    facts: dict[str, Any] = {"bridge_count": len(bridges)}
    if getattr(loaded, "bridge_set_id", None) != "as-fixed-point-equation-bridge-v1":
        failures.append("fixed-point-equation-bridge-id")
    if len(bridges) != 1:
        failures.append("fixed-point-equation-bridge-count")
    if bridge is not None:
        facts["bridge_equation_code_length"] = (
            bridge.expected_bridge_equation_code_length
        )
        facts["diagonal_instance_code_length"] = (
            bridge.expected_diagonal_instance_code_length
        )
        if bridge.status != "bridge-target-open":
            failures.append("fixed-point-equation-bridge-status")
        if bridge.expected_bridge_equation_code_length != expected_bridge_length:
            failures.append("fixed-point-equation-bridge-length")
        if not _has_non_claims(bridge):
            failures.append("fixed-point-equation-bridge-non-claim")
    return _SupportLoad(not failures, tuple(failures), facts)


def _validate_substitution_representability(
    loaded: Any,
    expected_output_length: int,
) -> _SupportLoad:
    failures: list[str] = []
    witnesses = tuple(getattr(loaded, "witnesses", ()))
    witness = witnesses[0] if witnesses else None
    facts: dict[str, Any] = {"witness_count": len(witnesses)}
    if getattr(loaded, "witness_set_id", None) != (
        "as-substitution-representability-witness-v1"
    ):
        failures.append("substitution-representability-id")
    if len(witnesses) != 1:
        failures.append("substitution-representability-count")
    if witness is not None:
        facts["evaluation_output_code_length"] = witness.expected_output_code_length
        if witness.status != "representability-witness-not-proof":
            failures.append("substitution-representability-status")
        if witness.expected_output_code_length != expected_output_length:
            failures.append("substitution-representability-output-length")
        if not _has_non_claims(witness):
            failures.append("substitution-representability-non-claim")
    return _SupportLoad(not failures, tuple(failures), facts)


def _validate_substitution_graph_correctness_cases(loaded: Any) -> _SupportLoad:
    failures: list[str] = []
    cases = tuple(getattr(loaded, "cases", ()))
    if getattr(loaded, "case_set_id", None) != (
        "as-substitution-graph-correctness-cases-v1"
    ):
        failures.append("substitution-graph-correctness-cases-id")
    if len(cases) != 5:
        failures.append("substitution-graph-correctness-cases-count")
    if any(case.status != "proof-case-open" for case in cases):
        failures.append("substitution-graph-correctness-cases-status")
    if any(not _has_non_claims(case) for case in cases):
        failures.append("substitution-graph-correctness-cases-non-claim")
    return _SupportLoad(
        accepted=not failures,
        failed_subjects=tuple(failures),
        facts={"case_count": len(cases)},
    )


def _validate_bridge_equality_alignment(
    loaded: Any,
    expected_bridge_length: int,
) -> _SupportLoad:
    failures: list[str] = []
    facts = {
        "alignment_count": getattr(loaded, "expected_alignment_count", None),
        "bridge_equation_code_length": getattr(
            loaded,
            "expected_bridge_equation_code_length",
            None,
        ),
    }
    if getattr(loaded, "alignment_set_id", None) != (
        "as-fixed-point-bridge-equality-alignment-v1"
    ):
        failures.append("fixed-point-bridge-equality-alignment-id")
    if getattr(loaded, "expected_alignment_count", None) != 1:
        failures.append("fixed-point-bridge-equality-alignment-count")
    if (
        getattr(loaded, "expected_bridge_equation_code_length", None)
        != expected_bridge_length
    ):
        failures.append("fixed-point-bridge-equality-alignment-length")
    if not _has_non_claims(loaded):
        failures.append("fixed-point-bridge-equality-alignment-non-claim")
    return _SupportLoad(not failures, tuple(failures), facts)


def _validate_bridge_equality_evaluation(
    loaded: Any,
    expected_bridge_length: int,
    expected_output_length: int,
) -> _SupportLoad:
    failures: list[str] = []
    facts = {
        "evaluation_count": getattr(loaded, "expected_evaluation_count", None),
        "bridge_equation_code_length": getattr(
            loaded,
            "expected_bridge_equation_code_length",
            None,
        ),
        "evaluation_output_code_length": getattr(
            loaded,
            "expected_output_code_length",
            None,
        ),
    }
    if getattr(loaded, "evaluation_set_id", None) != (
        "as-fixed-point-bridge-equality-evaluation-v1"
    ):
        failures.append("fixed-point-bridge-equality-evaluation-id")
    if getattr(loaded, "expected_evaluation_count", None) != 1:
        failures.append("fixed-point-bridge-equality-evaluation-count")
    if (
        getattr(loaded, "expected_bridge_equation_code_length", None)
        != expected_bridge_length
    ):
        failures.append("fixed-point-bridge-equality-evaluation-bridge-length")
    if getattr(loaded, "expected_output_code_length", None) != expected_output_length:
        failures.append("fixed-point-bridge-equality-evaluation-output-length")
    if not _has_non_claims(loaded):
        failures.append("fixed-point-bridge-equality-evaluation-non-claim")
    return _SupportLoad(not failures, tuple(failures), facts)


def _support_surfaces(
    paths: dict[str, Path],
    support_loads: dict[str, _SupportLoad],
) -> list[FixedPointBridgeEqualityFrontierSupportSurface]:
    path_by_subject = {
        "fixed_point_equation_bridge": paths[
            "fixed_point_equation_bridge_targets_path"
        ],
        "substitution_representability": paths[
            "substitution_representability_targets_path"
        ],
        "substitution_graph_correctness_cases": paths[
            "substitution_graph_correctness_cases_path"
        ],
        "bridge_equality_alignment": paths["bridge_equality_alignment_path"],
        "bridge_equality_evaluation": paths["bridge_equality_evaluation_path"],
    }
    surfaces: list[FixedPointBridgeEqualityFrontierSupportSurface] = []
    for subject in REQUIRED_SUPPORT_SUBJECTS:
        load = support_loads[subject]
        detail = _support_detail(subject, load)
        surfaces.append(
            FixedPointBridgeEqualityFrontierSupportSurface(
                subject=subject,
                path=path_by_subject[subject],
                accepted=load.accepted,
                failed_subjects=load.failed_subjects,
                detail=detail,
            )
        )
    return surfaces


def _support_detail(subject: str, load: _SupportLoad) -> str:
    if not load.accepted:
        return "rejected: " + _joined_or_none(load.failed_subjects)
    if subject == "fixed_point_equation_bridge":
        return (
            "bridge equation length "
            + str(load.facts.get("bridge_equation_code_length"))
        )
    if subject == "substitution_representability":
        return (
            "witness output length "
            + str(load.facts.get("evaluation_output_code_length"))
        )
    if subject == "substitution_graph_correctness_cases":
        return "open proof cases " + str(load.facts.get("case_count"))
    if subject == "bridge_equality_alignment":
        return (
            "bridge equation length "
            + str(load.facts.get("bridge_equation_code_length"))
        )
    if subject == "bridge_equality_evaluation":
        return (
            "bridge equation length "
            + str(load.facts.get("bridge_equation_code_length"))
            + ", evaluation output length "
            + str(load.facts.get("evaluation_output_code_length"))
        )
    return "accepted"


def _validate_support_surfaces(
    surfaces: list[FixedPointBridgeEqualityFrontierSupportSurface],
) -> list[FixedPointBridgeEqualityFrontierStatusValidation]:
    results: list[FixedPointBridgeEqualityFrontierStatusValidation] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "required support surfaces present"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    for surface in surfaces:
        if surface.accepted:
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _validate_case_dependencies(
    case: FixedPointBridgeEqualityFrontierConstructionCase,
    surfaces: list[FixedPointBridgeEqualityFrontierSupportSurface],
) -> list[FixedPointBridgeEqualityFrontierStatusValidation]:
    results: list[FixedPointBridgeEqualityFrontierStatusValidation] = []
    if tuple(case.required_dependency_subjects) == REQUIRED_SUPPORT_SUBJECTS:
        results.append(
            _accepted(
                "construction_case.required_dependency_subjects",
                "bridge equality dependencies match support surfaces",
            )
        )
    else:
        results.append(
            _rejected(
                "construction_case.required_dependency_subjects",
                "expected "
                + ", ".join(REQUIRED_SUPPORT_SUBJECTS)
                + " but found "
                + _joined_or_none(case.required_dependency_subjects),
            )
        )

    accepted_subjects = {surface.subject for surface in surfaces if surface.accepted}
    missing = [
        subject
        for subject in REQUIRED_SUPPORT_SUBJECTS
        if subject not in accepted_subjects
    ]
    if missing:
        results.append(
            _rejected(
                "construction_case.support",
                "support surfaces rejected: " + ", ".join(missing),
            )
        )
    else:
        results.append(_accepted("construction_case.support", "all support accepted"))
    return results


def _has_non_claims(item: Any) -> bool:
    non_claims = tuple(getattr(item, "non_claims", ()))
    if not non_claims:
        return False
    return not any(claim in non_claims for claim in PROOF_PROMOTION_NON_CLAIMS)


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "fixed-point-bridge-equality-frontier-status"
    if subject == "non_claims":
        return "fixed-point-bridge-equality-frontier-non-claim"
    if subject == "construction_case.status":
        return "fixed-point-bridge-equality-frontier-case-status"
    if subject.startswith("construction_case."):
        return "fixed-point-bridge-equality-frontier-case"
    if subject in REQUIRED_SUPPORT_SUBJECTS or subject.endswith("_path"):
        return "fixed-point-bridge-equality-frontier-dependency"
    if subject.startswith("expected_"):
        return "fixed-point-bridge-equality-frontier-length"
    if subject in {"support_surfaces", "construction_case.support"}:
        return "fixed-point-bridge-equality-frontier-support"
    return "fixed-point-bridge-equality-frontier"


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
) -> FixedPointBridgeEqualityFrontierStatusValidation:
    return FixedPointBridgeEqualityFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointBridgeEqualityFrontierStatusValidation:
    return FixedPointBridgeEqualityFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_bridge_equality_frontier_status_cli())
