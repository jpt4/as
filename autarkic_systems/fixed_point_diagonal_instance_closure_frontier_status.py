"""Compact status surface for the diagonal-instance-closure frontier.

The first fixed-point construction case already has finite support surfaces
for the fixed-point target, diagonal construction, equation bridge,
diagonal-instance closure, and diagonal-instance candidate. This module gathers
those facts into a fail-closed handoff while keeping the proof case open. It is
not a substitution representability proof, graph correctness proof, bridge
equality proof, fixed-point equation proof, proof-predicate construction, or
self-consistency theorem.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.diagonal_construction import (
    load_diagonal_construction_targets,
    validate_diagonal_construction_targets,
)
from autarkic_systems.fixed_point import (
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_diagonal_instance_candidate_surface import (
    load_fixed_point_diagonal_instance_candidate_surface,
    validate_fixed_point_diagonal_instance_candidate_surface,
)
from autarkic_systems.fixed_point_diagonal_instance_closure import (
    load_fixed_point_diagonal_instance_closure,
    validate_fixed_point_diagonal_instance_closure,
)
from autarkic_systems.fixed_point_equation_bridge import (
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)


DEFAULT_STATUS = Path(
    "claims/fixed_point_diagonal_instance_closure_frontier_status.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "diagonal-instance-closure"
REQUIRED_CONSTRUCTION_CASE_ID = (
    "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE"
)
REQUIRED_CONSTRUCTION_CASE_KIND = "diagonal-instance-closure"
REQUIRED_CONSTRUCTION_CASE_STATUS = "proof-case-open"
EXPECTED_DIAGONAL_INSTANCE_CODE_LENGTH = 296
EXPECTED_DIAGONAL_CANDIDATE_COUNT = 1
REQUIRED_SUPPORT_SUBJECTS = (
    "fixed_point",
    "diagonal_construction",
    "fixed_point_equation_bridge",
    "diagonal_instance_closure",
    "diagonal_instance_candidate_surface",
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
    "fixed_point_targets_path": "claims/fixed_point_targets.json",
    "diagonal_construction_targets_path": (
        "claims/diagonal_construction_targets.json"
    ),
    "fixed_point_equation_bridge_targets_path": (
        "claims/fixed_point_equation_bridge_targets.json"
    ),
    "diagonal_instance_closure_path": (
        "claims/fixed_point_diagonal_instance_closure.json"
    ),
    "diagonal_instance_candidate_surface_path": (
        "claims/fixed_point_diagonal_instance_candidate_surface.json"
    ),
}
PROOF_PROMOTION_FRONTIER_STATUSES = {
    "diagonal-instance-closure-proved",
    "substitution-representability-proved",
    "substitution-graph-correctness-proved",
    "bridge-equality-proved",
    "fixed-point-equation-proved",
    "arithmetized-proof-predicate-proved",
    "self-consistency-proved",
    "self-consistency-theorem-proved",
}


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureFrontierStatusManifest:
    """Loaded compact manifest for the first fixed-point construction case."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    fixed_point_construction_cases_path: str
    fixed_point_targets_path: str
    diagonal_construction_targets_path: str
    fixed_point_equation_bridge_targets_path: str
    diagonal_instance_closure_path: str
    diagonal_instance_candidate_surface_path: str
    required_construction_case_id: str
    required_construction_case_kind: str
    required_construction_case_status: str
    expected_support_surface_count: int
    expected_diagonal_instance_code_length: int
    expected_diagonal_candidate_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureFrontierStatusValidation:
    """One validation result for the compact frontier surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureFrontierConstructionCase:
    """Compact view of the construction case owned by this handoff."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    non_claims: tuple[str, ...]


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureFrontierSupportSurface:
    """Observed compact state of one required support surface."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str
    facts: dict[str, Any]


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureFrontierStatusReport:
    """Validation report for the diagonal-instance-closure frontier."""

    manifest: FixedPointDiagonalInstanceClosureFrontierStatusManifest
    willard_map_path: Path
    fixed_point_construction_cases_path: Path
    fixed_point_targets_path: Path
    diagonal_construction_targets_path: Path
    fixed_point_equation_bridge_targets_path: Path
    diagonal_instance_closure_path: Path
    diagonal_instance_candidate_surface_path: Path
    construction_case: FixedPointDiagonalInstanceClosureFrontierConstructionCase
    support_surfaces: tuple[
        FixedPointDiagonalInstanceClosureFrontierSupportSurface,
        ...,
    ]
    support_facts: dict[str, dict[str, Any]]
    results: tuple[FixedPointDiagonalInstanceClosureFrontierStatusValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every compact validation result accepted."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the status preserved by this handoff."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the still-open proof case that blocks this frontier."""

        return self.manifest.frontier_blocked_by

    @property
    def support_surface_count(self) -> int:
        """Return the number of support surfaces inspected."""

        return len(self.support_surfaces)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return compact failure subjects for automation and handoff reports."""

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
    """Small normalized support result used by the frontier validator."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]


def load_fixed_point_diagonal_instance_closure_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> FixedPointDiagonalInstanceClosureFrontierStatusManifest:
    """Load the compact diagonal-instance-closure frontier manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return FixedPointDiagonalInstanceClosureFrontierStatusManifest(
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
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        diagonal_construction_targets_path=_required_text(
            data,
            "diagonal_construction_targets_path",
        ),
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        diagonal_instance_closure_path=_required_text(
            data,
            "diagonal_instance_closure_path",
        ),
        diagonal_instance_candidate_surface_path=_required_text(
            data,
            "diagonal_instance_candidate_surface_path",
        ),
        required_construction_case_id=_required_text(
            data,
            "required_construction_case_id",
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
        expected_diagonal_instance_code_length=_required_int(
            data,
            "expected_diagonal_instance_code_length",
        ),
        expected_diagonal_candidate_count=_required_int(
            data,
            "expected_diagonal_candidate_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_diagonal_instance_closure_frontier_status(
    manifest: FixedPointDiagonalInstanceClosureFrontierStatusManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointDiagonalInstanceClosureFrontierStatusReport:
    """Validate compact status facts for the first construction case."""

    paths = _manifest_paths(manifest)
    checked_willard_map_path = Path(willard_map_path)
    results: list[FixedPointDiagonalInstanceClosureFrontierStatusValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    construction_cases, construction_load = _load_support(
        paths["fixed_point_construction_cases_path"],
        load_fixed_point_construction_cases,
        _validate_construction_case_map,
        "fixed-point-construction-cases-load",
    )
    construction_case = _find_construction_case(construction_cases)
    results.extend(_validate_construction_case(construction_case))
    if not construction_load.accepted:
        results.append(
            _rejected(
                "fixed_point_construction_cases",
                "construction case map rejected: "
                + _joined_or_none(construction_load.failed_subjects),
            )
        )

    support_loads = {
        "fixed_point": _load_support(
            paths["fixed_point_targets_path"],
            load_fixed_point_targets,
            lambda loaded: _validate_fixed_point_support(
                loaded,
                checked_willard_map_path,
            ),
            "fixed-point-target-load",
        )[1],
        "diagonal_construction": _load_support(
            paths["diagonal_construction_targets_path"],
            load_diagonal_construction_targets,
            lambda loaded: _validate_diagonal_construction_support(
                loaded,
                checked_willard_map_path,
                manifest.expected_diagonal_instance_code_length,
            ),
            "diagonal-construction-load",
        )[1],
        "fixed_point_equation_bridge": _load_support(
            paths["fixed_point_equation_bridge_targets_path"],
            load_fixed_point_equation_bridge_targets,
            lambda loaded: _validate_equation_bridge_support(
                loaded,
                checked_willard_map_path,
                manifest.expected_diagonal_instance_code_length,
            ),
            "fixed-point-equation-bridge-load",
        )[1],
        "diagonal_instance_closure": _load_support(
            paths["diagonal_instance_closure_path"],
            load_fixed_point_diagonal_instance_closure,
            lambda loaded: _validate_diagonal_instance_closure_support(
                loaded,
                checked_willard_map_path,
                manifest.expected_diagonal_instance_code_length,
            ),
            "fixed-point-diagonal-instance-closure-load",
        )[1],
        "diagonal_instance_candidate_surface": _load_support(
            paths["diagonal_instance_candidate_surface_path"],
            load_fixed_point_diagonal_instance_candidate_surface,
            lambda loaded: _validate_diagonal_candidate_support(
                loaded,
                checked_willard_map_path,
                manifest.expected_diagonal_candidate_count,
                manifest.expected_diagonal_instance_code_length,
            ),
            "fixed-point-diagonal-instance-candidate-surface-load",
        )[1],
    }

    support_surfaces = _support_surfaces(paths, support_loads)
    results.extend(_validate_support_surfaces(manifest, support_surfaces))
    results.extend(_validate_case_support(construction_case, support_surfaces))

    return FixedPointDiagonalInstanceClosureFrontierStatusReport(
        manifest=manifest,
        willard_map_path=checked_willard_map_path,
        fixed_point_construction_cases_path=paths[
            "fixed_point_construction_cases_path"
        ],
        fixed_point_targets_path=paths["fixed_point_targets_path"],
        diagonal_construction_targets_path=paths[
            "diagonal_construction_targets_path"
        ],
        fixed_point_equation_bridge_targets_path=paths[
            "fixed_point_equation_bridge_targets_path"
        ],
        diagonal_instance_closure_path=paths["diagonal_instance_closure_path"],
        diagonal_instance_candidate_surface_path=paths[
            "diagonal_instance_candidate_surface_path"
        ],
        construction_case=construction_case,
        support_surfaces=tuple(support_surfaces),
        support_facts={
            subject: dict(load.facts) for subject, load in support_loads.items()
        },
        results=tuple(results),
    )


def fixed_point_diagonal_instance_closure_frontier_status_payload(
    report: FixedPointDiagonalInstanceClosureFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready diagonal-instance-closure frontier payload."""

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
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "diagonal_construction_targets_path": str(
            report.diagonal_construction_targets_path
        ),
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "diagonal_instance_closure_path": str(report.diagonal_instance_closure_path),
        "diagonal_instance_candidate_surface_path": str(
            report.diagonal_instance_candidate_surface_path
        ),
        "required_construction_case_id": (
            report.manifest.required_construction_case_id
        ),
        "required_construction_case_kind": (
            report.manifest.required_construction_case_kind
        ),
        "required_construction_case_status": (
            report.manifest.required_construction_case_status
        ),
        "expected_support_surface_count": (
            report.manifest.expected_support_surface_count
        ),
        "expected_diagonal_instance_code_length": (
            report.manifest.expected_diagonal_instance_code_length
        ),
        "expected_diagonal_candidate_count": (
            report.manifest.expected_diagonal_candidate_count
        ),
        "construction_case": {
            "case_id": report.construction_case.case_id,
            "case_kind": report.construction_case.case_kind,
            "target_id": report.construction_case.target_id,
            "status": report.construction_case.status,
            "required_dependency_subjects": list(
                report.construction_case.required_dependency_subjects
            ),
            "non_claims": list(report.construction_case.non_claims),
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
                "facts": surface.facts,
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


def format_fixed_point_diagonal_instance_closure_frontier_status_report(
    report: FixedPointDiagonalInstanceClosureFrontierStatusReport,
) -> str:
    """Format a concise text report for the frontier handoff."""

    status = "accepted" if report.accepted else "rejected"
    case = report.construction_case
    lines = [
        f"Fixed-point diagonal instance closure frontier status: {status}",
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


def run_fixed_point_diagonal_instance_closure_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run diagonal-instance-closure frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_diagonal_instance_closure_frontier_status"
        ),
        description=(
            "Validate the AS fixed-point diagonal-instance-closure "
            "frontier status."
        ),
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the diagonal-instance-closure frontier status manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_diagonal_instance_closure_frontier_status(
        args.status
    )
    report = validate_fixed_point_diagonal_instance_closure_frontier_status(
        manifest
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_diagonal_instance_closure_frontier_status_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_diagonal_instance_closure_frontier_status_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointDiagonalInstanceClosureFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "fixed_point_construction_cases_path": Path(
            manifest.fixed_point_construction_cases_path
        ),
        "fixed_point_targets_path": Path(manifest.fixed_point_targets_path),
        "diagonal_construction_targets_path": Path(
            manifest.diagonal_construction_targets_path
        ),
        "fixed_point_equation_bridge_targets_path": Path(
            manifest.fixed_point_equation_bridge_targets_path
        ),
        "diagonal_instance_closure_path": Path(
            manifest.diagonal_instance_closure_path
        ),
        "diagonal_instance_candidate_surface_path": Path(
            manifest.diagonal_instance_candidate_surface_path
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
    except (OSError, ValueError, json.JSONDecodeError, AttributeError):
        return None, _SupportLoad(
            accepted=False,
            failed_subjects=(load_failure_subject,),
            facts={"path": str(path)},
        )


def _validate_manifest(
    manifest: FixedPointDiagonalInstanceClosureFrontierStatusManifest,
) -> list[FixedPointDiagonalInstanceClosureFrontierStatusValidation]:
    results: list[FixedPointDiagonalInstanceClosureFrontierStatusValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if (
        manifest.status_set_id
        == "as-fixed-point-diagonal-instance-closure-frontier-status-v1"
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
            _accepted("frontier_blocked_by", "blocked by diagonal-instance-closure")
        )
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                "expected diagonal-instance-closure blocker",
            )
        )

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.required_construction_case_id == REQUIRED_CONSTRUCTION_CASE_ID:
        results.append(_accepted("required_construction_case_id", "case id matches"))
    else:
        results.append(_rejected("required_construction_case_id", "wrong case id"))

    if manifest.required_construction_case_kind == REQUIRED_CONSTRUCTION_CASE_KIND:
        results.append(
            _accepted(
                "required_construction_case_kind",
                "diagonal-instance-closure case selected",
            )
        )
    else:
        results.append(
            _rejected("required_construction_case_kind", "wrong construction case kind")
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

    if (
        manifest.expected_diagonal_instance_code_length
        == EXPECTED_DIAGONAL_INSTANCE_CODE_LENGTH
    ):
        results.append(
            _accepted(
                "expected_diagonal_instance_code_length",
                "296-token diagonal instance",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_diagonal_instance_code_length",
                "expected 296-token diagonal instance",
            )
        )

    if manifest.expected_diagonal_candidate_count == EXPECTED_DIAGONAL_CANDIDATE_COUNT:
        results.append(_accepted("expected_diagonal_candidate_count", "one candidate"))
    else:
        results.append(
            _rejected(
                "expected_diagonal_candidate_count",
                "expected one diagonal candidate",
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


def _validate_construction_case_map(loaded: Any) -> _SupportLoad:
    failures: list[str] = []
    cases = tuple(getattr(loaded, "cases", ()))
    case = _find_case_by_kind(cases, REQUIRED_CONSTRUCTION_CASE_KIND)
    if getattr(loaded, "case_set_id", None) != "as-fixed-point-construction-cases-v1":
        failures.append("fixed-point-construction-cases-id")
    if len(cases) != 5:
        failures.append("fixed-point-construction-cases-count")
    if case is None:
        failures.append("fixed-point-diagonal-instance-closure-case-missing")
    return _SupportLoad(
        accepted=not failures,
        failed_subjects=tuple(failures),
        facts={"case_count": len(cases)},
    )


def _find_construction_case(
    construction_cases: Any | None,
) -> FixedPointDiagonalInstanceClosureFrontierConstructionCase:
    if construction_cases is None:
        return FixedPointDiagonalInstanceClosureFrontierConstructionCase(
            case_id="missing",
            case_kind="missing",
            target_id="missing",
            status="missing",
            required_dependency_subjects=(),
            non_claims=(),
        )

    case = _find_case_by_kind(
        tuple(getattr(construction_cases, "cases", ())),
        REQUIRED_CONSTRUCTION_CASE_KIND,
    )
    if case is None:
        return FixedPointDiagonalInstanceClosureFrontierConstructionCase(
            case_id="missing",
            case_kind="missing",
            target_id="missing",
            status="missing",
            required_dependency_subjects=(),
            non_claims=(),
        )
    return FixedPointDiagonalInstanceClosureFrontierConstructionCase(
        case_id=case.case_id,
        case_kind=case.case_kind,
        target_id=case.target_id,
        status=case.status,
        required_dependency_subjects=tuple(case.required_dependency_subjects),
        non_claims=tuple(case.non_claims),
    )


def _validate_construction_case(
    case: FixedPointDiagonalInstanceClosureFrontierConstructionCase,
) -> list[FixedPointDiagonalInstanceClosureFrontierStatusValidation]:
    results: list[FixedPointDiagonalInstanceClosureFrontierStatusValidation] = []
    if case.case_id == REQUIRED_CONSTRUCTION_CASE_ID:
        results.append(_accepted("construction_case.case_id", "case id matches"))
    else:
        results.append(_rejected("construction_case.case_id", "case id mismatch"))

    if case.case_kind == REQUIRED_CONSTRUCTION_CASE_KIND:
        results.append(_accepted("construction_case.kind", "case kind matches"))
    else:
        results.append(_rejected("construction_case.kind", "case kind mismatch"))

    if case.status == REQUIRED_CONSTRUCTION_CASE_STATUS:
        results.append(
            _accepted("construction_case.status", "construction case remains open")
        )
    else:
        results.append(
            _rejected(
                "construction_case.status",
                f"construction case is not open: {case.status}",
            )
        )

    if case.required_dependency_subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(
            _accepted(
                "construction_case.required_dependency_subjects",
                "support subjects match construction case",
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

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in case.non_claims
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


def _validate_fixed_point_support(
    loaded: Any,
    willard_map_path: Path,
) -> _SupportLoad:
    report = validate_fixed_point_targets(loaded, willard_map_path)
    targets = tuple(getattr(loaded, "targets", ()))
    target = targets[0] if targets else None
    failures = list(report.failed_subjects)
    if getattr(loaded, "target_set_id", None) != "as-fixed-point-target-v1":
        failures.append("fixed-point-target-id")
    if len(targets) != 1:
        failures.append("fixed-point-target-count")
    facts = {
        "target_set_id": getattr(loaded, "target_set_id", ""),
        "target_count": len(targets),
        "failed_subjects": list(report.failed_subjects),
        "target_status": getattr(target, "status", ""),
        "expected_instance_code_length": len(
            getattr(target, "expected_instance_code", ())
        ),
    }
    return _SupportLoad(not failures, tuple(dict.fromkeys(failures)), facts)


def _validate_diagonal_construction_support(
    loaded: Any,
    willard_map_path: Path,
    expected_instance_length: int,
) -> _SupportLoad:
    report = validate_diagonal_construction_targets(
        loaded,
        willard_map_path=willard_map_path,
    )
    constructions = tuple(getattr(loaded, "constructions", ()))
    construction = constructions[0] if constructions else None
    failures = list(report.failed_subjects)
    if getattr(loaded, "construction_set_id", None) != (
        "as-diagonal-construction-target-v1"
    ):
        failures.append("diagonal-construction-id")
    if len(constructions) != 1:
        failures.append("diagonal-construction-count")
    observed_length = getattr(construction, "expected_instance_code_length", None)
    if observed_length != expected_instance_length:
        failures.append("diagonal-construction-instance-length")
    facts = {
        "construction_set_id": getattr(loaded, "construction_set_id", ""),
        "construction_count": len(constructions),
        "failed_subjects": list(report.failed_subjects),
        "construction_status": getattr(construction, "status", ""),
        "diagonal_instance_code_length": observed_length,
    }
    return _SupportLoad(not failures, tuple(dict.fromkeys(failures)), facts)


def _validate_equation_bridge_support(
    loaded: Any,
    willard_map_path: Path,
    expected_instance_length: int,
) -> _SupportLoad:
    report = validate_fixed_point_equation_bridge_targets(
        loaded,
        willard_map_path=willard_map_path,
    )
    bridges = tuple(getattr(loaded, "bridges", ()))
    bridge = bridges[0] if bridges else None
    failures = list(report.failed_subjects)
    if getattr(loaded, "bridge_set_id", None) != "as-fixed-point-equation-bridge-v1":
        failures.append("fixed-point-equation-bridge-id")
    if len(bridges) != 1:
        failures.append("fixed-point-equation-bridge-count")
    observed_length = getattr(bridge, "expected_diagonal_instance_code_length", None)
    if observed_length != expected_instance_length:
        failures.append("fixed-point-equation-bridge-diagonal-length")
    facts = {
        "bridge_set_id": getattr(loaded, "bridge_set_id", ""),
        "bridge_count": len(bridges),
        "failed_subjects": list(report.failed_subjects),
        "bridge_status": getattr(bridge, "status", ""),
        "diagonal_instance_code_length": observed_length,
        "bridge_equation_code_length": getattr(
            bridge,
            "expected_bridge_equation_code_length",
            None,
        ),
    }
    return _SupportLoad(not failures, tuple(dict.fromkeys(failures)), facts)


def _validate_diagonal_instance_closure_support(
    loaded: Any,
    willard_map_path: Path,
    expected_instance_length: int,
) -> _SupportLoad:
    report = validate_fixed_point_diagonal_instance_closure(
        loaded,
        willard_map_path,
    )
    closures = tuple(report.closures)
    closure = closures[0] if closures else None
    failures = list(report.failed_subjects)
    if getattr(loaded, "closure_set_id", None) != (
        "as-fixed-point-diagonal-instance-closure-v1"
    ):
        failures.append("fixed-point-diagonal-instance-closure-id")
    if report.closure_count != 1:
        failures.append("fixed-point-diagonal-instance-closure-count")
    observed_length = getattr(closure, "diagonal_instance_code_length", None)
    if observed_length != expected_instance_length:
        failures.append("fixed-point-diagonal-instance-closure-length")
    facts = {
        "closure_set_id": getattr(loaded, "closure_set_id", ""),
        "closure_count": report.closure_count,
        "failed_subjects": list(report.failed_subjects),
        "diagonal_instance_code_length": observed_length,
        "bridge_matches_diagonal_instance": getattr(
            closure,
            "bridge_matches_diagonal_instance",
            False,
        ),
        "bridge_target_closed": getattr(closure, "bridge_target_closed", False),
    }
    return _SupportLoad(not failures, tuple(dict.fromkeys(failures)), facts)


def _validate_diagonal_candidate_support(
    loaded: Any,
    willard_map_path: Path,
    expected_candidate_count: int,
    expected_instance_length: int,
) -> _SupportLoad:
    report = validate_fixed_point_diagonal_instance_candidate_surface(
        loaded,
        willard_map_path,
    )
    candidates = tuple(report.candidates)
    candidate = candidates[0] if candidates else None
    failures = list(report.failed_subjects)
    if getattr(loaded, "candidate_surface_set_id", None) != (
        "as-fixed-point-diagonal-instance-candidate-surface-v1"
    ):
        failures.append("fixed-point-diagonal-instance-candidate-surface-id")
    if report.candidate_count != expected_candidate_count:
        failures.append("fixed-point-diagonal-instance-candidate-surface-count")
    observed_length = getattr(candidate, "candidate_code_length", None)
    if observed_length != expected_instance_length:
        failures.append("fixed-point-diagonal-instance-candidate-surface-length")
    facts = {
        "candidate_surface_set_id": getattr(loaded, "candidate_surface_set_id", ""),
        "candidate_count": report.candidate_count,
        "failed_subjects": list(report.failed_subjects),
        "candidate_code_length": observed_length,
        "construction_case_is_open": getattr(
            candidate,
            "construction_case_is_open",
            False,
        ),
        "candidate_matches_bridge_observation": getattr(
            candidate,
            "candidate_matches_bridge_observation",
            False,
        ),
        "candidate_matches_closure": getattr(
            candidate,
            "candidate_matches_closure",
            False,
        ),
        "all_dependencies_accepted": getattr(
            candidate,
            "all_dependencies_accepted",
            False,
        ),
    }
    return _SupportLoad(not failures, tuple(dict.fromkeys(failures)), facts)


def _support_surfaces(
    paths: dict[str, Path],
    support_loads: dict[str, _SupportLoad],
) -> list[FixedPointDiagonalInstanceClosureFrontierSupportSurface]:
    path_by_subject = {
        "fixed_point": paths["fixed_point_targets_path"],
        "diagonal_construction": paths["diagonal_construction_targets_path"],
        "fixed_point_equation_bridge": paths[
            "fixed_point_equation_bridge_targets_path"
        ],
        "diagonal_instance_closure": paths["diagonal_instance_closure_path"],
        "diagonal_instance_candidate_surface": paths[
            "diagonal_instance_candidate_surface_path"
        ],
    }
    surfaces: list[FixedPointDiagonalInstanceClosureFrontierSupportSurface] = []
    for subject in REQUIRED_SUPPORT_SUBJECTS:
        load = support_loads[subject]
        surfaces.append(
            FixedPointDiagonalInstanceClosureFrontierSupportSurface(
                subject=subject,
                path=path_by_subject[subject],
                accepted=load.accepted,
                failed_subjects=load.failed_subjects,
                detail=_support_detail(subject, load),
                facts=load.facts,
            )
        )
    return surfaces


def _support_detail(subject: str, load: _SupportLoad) -> str:
    if not load.accepted:
        return "rejected: " + _joined_or_none(load.failed_subjects)
    if subject == "fixed_point":
        return "target count " + str(load.facts.get("target_count"))
    if subject == "diagonal_construction":
        return (
            "diagonal instance length "
            + str(load.facts.get("diagonal_instance_code_length"))
        )
    if subject == "fixed_point_equation_bridge":
        return (
            "diagonal instance length "
            + str(load.facts.get("diagonal_instance_code_length"))
        )
    if subject == "diagonal_instance_closure":
        return (
            "diagonal instance length "
            + str(load.facts.get("diagonal_instance_code_length"))
        )
    if subject == "diagonal_instance_candidate_surface":
        return "candidate count " + str(load.facts.get("candidate_count"))
    return "accepted"


def _validate_support_surfaces(
    manifest: FixedPointDiagonalInstanceClosureFrontierStatusManifest,
    surfaces: list[FixedPointDiagonalInstanceClosureFrontierSupportSurface],
) -> list[FixedPointDiagonalInstanceClosureFrontierStatusValidation]:
    results: list[FixedPointDiagonalInstanceClosureFrontierStatusValidation] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "required support surfaces present"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    if len(surfaces) == manifest.expected_support_surface_count:
        results.append(_accepted("support_surface_count", "support count matches"))
    else:
        results.append(_rejected("support_surface_count", "support count mismatch"))

    for surface in surfaces:
        if surface.accepted and surface.failed_subjects == ():
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _validate_case_support(
    case: FixedPointDiagonalInstanceClosureFrontierConstructionCase,
    surfaces: list[FixedPointDiagonalInstanceClosureFrontierSupportSurface],
) -> list[FixedPointDiagonalInstanceClosureFrontierStatusValidation]:
    accepted_subjects = {surface.subject for surface in surfaces if surface.accepted}
    missing = [
        subject for subject in case.required_dependency_subjects
        if subject not in accepted_subjects
    ]
    if missing:
        return [
            _rejected(
                "construction_case.support",
                "support surfaces rejected: " + ", ".join(missing),
            )
        ]
    return [_accepted("construction_case.support", "all required support accepted")]


def _find_case_by_kind(cases: tuple[Any, ...], case_kind: str) -> Any | None:
    matches = [case for case in cases if getattr(case, "case_kind", "") == case_kind]
    if len(matches) != 1:
        return None
    return matches[0]


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "fixed-point-diagonal-instance-closure-frontier-status"
    if subject == "non_claims" or subject == "construction_case.non_claims":
        return "fixed-point-diagonal-instance-closure-frontier-non-claim"
    if subject == "construction_case.status":
        return "fixed-point-diagonal-instance-closure-frontier-case-status"
    if subject == "construction_case.required_dependency_subjects":
        return "fixed-point-diagonal-instance-closure-frontier-support-subject"
    if subject.startswith("construction_case."):
        return "fixed-point-diagonal-instance-closure-frontier-case"
    if subject in REQUIRED_SUPPORT_SUBJECTS or subject.endswith("_path"):
        return "fixed-point-diagonal-instance-closure-frontier-dependency"
    if subject.startswith("expected_"):
        return "fixed-point-diagonal-instance-closure-frontier-expectation"
    if subject in {"support_surfaces", "support_surface_count"}:
        return "fixed-point-diagonal-instance-closure-frontier-support"
    if subject == "construction_case.support":
        return "fixed-point-diagonal-instance-closure-frontier-support"
    return "fixed-point-diagonal-instance-closure-frontier"


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


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceClosureFrontierStatusValidation:
    return FixedPointDiagonalInstanceClosureFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceClosureFrontierStatusValidation:
    return FixedPointDiagonalInstanceClosureFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


if __name__ == "__main__":
    raise SystemExit(
        run_fixed_point_diagonal_instance_closure_frontier_status_cli()
    )
