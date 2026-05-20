"""Compact status surface for the fixed-point equation-lifting frontier.

The equation-lifting alignment module owns the deeper finite alignment check.
This module is only a handoff/status layer: it confirms that the construction
case stays open, the current compact support surfaces still accept, and the
manifest preserves the non-claims that prevent accidental proof promotion.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Callable

from autarkic_systems.fixed_point import (
    load_fixed_point_targets,
)
from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_equation_bridge import (
    load_fixed_point_equation_bridge_targets,
)
from autarkic_systems.fixed_point_equation_lifting_alignment import (
    load_fixed_point_equation_lifting_alignment,
)
from autarkic_systems.formal_code import (
    load_formal_codebook,
)


DEFAULT_STATUS = Path("claims/fixed_point_equation_lifting_frontier_status.json")

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "fixed-point-equation-lifting"
REQUIRED_CASE_ID = "AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING"
REQUIRED_CASE_KIND = "fixed-point-equation-lifting"
REQUIRED_CASE_STATUS = "proof-case-open"
EXPECTED_SUPPORT_SURFACE_COUNT = 4
EXPECTED_DIRECT_TARGET_CODE_LENGTH = 4528
EXPECTED_BRIDGE_EQUATION_CODE_LENGTH = 4815
REQUIRED_SUPPORT_SUBJECTS = (
    "fixed_point",
    "fixed_point_equation_bridge",
    "codebook",
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
    "fixed_point_targets_path": "claims/fixed_point_targets.json",
    "fixed_point_equation_bridge_targets_path": (
        "claims/fixed_point_equation_bridge_targets.json"
    ),
    "codebook_path": "language/formal_codebook.json",
    "equation_lifting_alignment_path": (
        "claims/fixed_point_equation_lifting_alignment.json"
    ),
}
PROOF_PROMOTION_STATUSES = {
    "substitution-representability-proved",
    "substitution-graph-correctness-proved",
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
class FixedPointEquationLiftingFrontierStatusManifest:
    """Loaded compact manifest for the equation-lifting frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    fixed_point_construction_cases_path: str
    fixed_point_targets_path: str
    fixed_point_equation_bridge_targets_path: str
    codebook_path: str
    equation_lifting_alignment_path: str
    expected_support_surface_count: int
    expected_direct_target_code_length: int
    expected_bridge_equation_code_length: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointEquationLiftingFrontierStatusValidation:
    """One validation result for the equation-lifting frontier."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointEquationLiftingFrontierConstructionCase:
    """Compact view of the equation-lifting construction case."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    non_claims: tuple[str, ...]


@dataclass(frozen=True)
class FixedPointEquationLiftingFrontierSupportSurface:
    """Observed compact state of one equation-lifting support surface."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class FixedPointEquationLiftingFrontierStatusReport:
    """Validation report for the compact equation-lifting frontier."""

    manifest: FixedPointEquationLiftingFrontierStatusManifest
    fixed_point_construction_cases_path: Path
    fixed_point_targets_path: Path
    fixed_point_equation_bridge_targets_path: Path
    codebook_path: Path
    equation_lifting_alignment_path: Path
    construction_case: FixedPointEquationLiftingFrontierConstructionCase
    support_surfaces: tuple[FixedPointEquationLiftingFrontierSupportSurface, ...]
    support_facts: dict[str, dict[str, Any]]
    results: tuple[FixedPointEquationLiftingFrontierStatusValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every equation-lifting frontier validation passed."""

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


def load_fixed_point_equation_lifting_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> FixedPointEquationLiftingFrontierStatusManifest:
    """Load the fixed-point equation-lifting frontier status manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return FixedPointEquationLiftingFrontierStatusManifest(
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
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        codebook_path=_required_text(data, "codebook_path"),
        equation_lifting_alignment_path=_required_text(
            data,
            "equation_lifting_alignment_path",
        ),
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
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_equation_lifting_frontier_status(
    manifest: FixedPointEquationLiftingFrontierStatusManifest,
) -> FixedPointEquationLiftingFrontierStatusReport:
    """Validate the compact equation-lifting frontier status."""

    paths = _manifest_paths(manifest)
    results: list[FixedPointEquationLiftingFrontierStatusValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    construction_cases, construction_load = _load_support(
        paths["fixed_point_construction_cases_path"],
        load_fixed_point_construction_cases,
        _validate_construction_case_map,
        "fixed-point-construction-cases-load",
    )
    equation_lifting_case = _find_equation_lifting_case(construction_cases)
    results.extend(_validate_equation_lifting_case(equation_lifting_case))

    support_loads = {
        "fixed_point": _load_support(
            paths["fixed_point_targets_path"],
            load_fixed_point_targets,
            _validate_fixed_point_targets_support,
            "fixed-point-target-load",
        )[1],
        "fixed_point_equation_bridge": _load_support(
            paths["fixed_point_equation_bridge_targets_path"],
            load_fixed_point_equation_bridge_targets,
            lambda loaded: _validate_equation_bridge_support(
                loaded,
                manifest.expected_direct_target_code_length,
                manifest.expected_bridge_equation_code_length,
            ),
            "fixed-point-equation-bridge-load",
        )[1],
        "codebook": _load_support(
            paths["codebook_path"],
            load_formal_codebook,
            _validate_codebook_support,
            "formal-codebook-load",
        )[1],
        "equation_lifting_alignment": _load_support(
            paths["equation_lifting_alignment_path"],
            load_fixed_point_equation_lifting_alignment,
            lambda loaded: _validate_equation_lifting_alignment_support(
                loaded,
                manifest.expected_direct_target_code_length,
            ),
            "fixed-point-equation-lifting-alignment-load",
        )[1],
    }

    support_surfaces = _support_surfaces(paths, support_loads)
    results.extend(_validate_support_surfaces(manifest, support_surfaces))
    results.extend(
        _validate_case_dependencies(equation_lifting_case, support_surfaces)
    )
    if not construction_load.accepted:
        results.append(
            _rejected(
                "fixed_point_construction_cases",
                "construction case map rejected: "
                + _joined_or_none(construction_load.failed_subjects),
            )
        )

    return FixedPointEquationLiftingFrontierStatusReport(
        manifest=manifest,
        fixed_point_construction_cases_path=paths[
            "fixed_point_construction_cases_path"
        ],
        fixed_point_targets_path=paths["fixed_point_targets_path"],
        fixed_point_equation_bridge_targets_path=paths[
            "fixed_point_equation_bridge_targets_path"
        ],
        codebook_path=paths["codebook_path"],
        equation_lifting_alignment_path=paths["equation_lifting_alignment_path"],
        construction_case=equation_lifting_case,
        support_surfaces=tuple(support_surfaces),
        support_facts={
            subject: dict(load.facts) for subject, load in support_loads.items()
        },
        results=tuple(results),
    )


def fixed_point_equation_lifting_frontier_status_payload(
    report: FixedPointEquationLiftingFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready equation-lifting frontier payload."""

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
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "codebook_path": str(report.codebook_path),
        "equation_lifting_alignment_path": str(
            report.equation_lifting_alignment_path
        ),
        "expected_support_surface_count": (
            report.manifest.expected_support_surface_count
        ),
        "expected_direct_target_code_length": (
            report.manifest.expected_direct_target_code_length
        ),
        "expected_bridge_equation_code_length": (
            report.manifest.expected_bridge_equation_code_length
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


def format_fixed_point_equation_lifting_frontier_status_report(
    report: FixedPointEquationLiftingFrontierStatusReport,
) -> str:
    """Format a concise human-readable equation-lifting frontier report."""

    status = "accepted" if report.accepted else "rejected"
    case = report.construction_case
    lines = [
        f"Fixed-point equation lifting frontier status: {status}",
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


def run_fixed_point_equation_lifting_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point equation-lifting frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_equation_lifting_frontier_status"
        ),
        description=(
            "Validate the AS fixed-point equation-lifting frontier status."
        ),
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the fixed-point equation-lifting frontier status manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_equation_lifting_frontier_status(args.status)
    report = validate_fixed_point_equation_lifting_frontier_status(manifest)
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_equation_lifting_frontier_status_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_equation_lifting_frontier_status_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointEquationLiftingFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "fixed_point_construction_cases_path": Path(
            manifest.fixed_point_construction_cases_path
        ),
        "fixed_point_targets_path": Path(manifest.fixed_point_targets_path),
        "fixed_point_equation_bridge_targets_path": Path(
            manifest.fixed_point_equation_bridge_targets_path
        ),
        "codebook_path": Path(manifest.codebook_path),
        "equation_lifting_alignment_path": Path(
            manifest.equation_lifting_alignment_path
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
    manifest: FixedPointEquationLiftingFrontierStatusManifest,
) -> list[FixedPointEquationLiftingFrontierStatusValidation]:
    results: list[FixedPointEquationLiftingFrontierStatusValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.status_set_id == (
        "as-fixed-point-equation-lifting-frontier-status-v1"
    ):
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
        results.append(
            _accepted(
                "frontier_blocked_by",
                "blocked by fixed-point-equation-lifting",
            )
        )
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                "expected fixed-point-equation-lifting blocker",
            )
        )

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.expected_support_surface_count == EXPECTED_SUPPORT_SURFACE_COUNT:
        results.append(_accepted("expected_support_surface_count", "4 checked"))
    else:
        results.append(
            _rejected("expected_support_surface_count", "expected 4 support surfaces")
        )

    if (
        manifest.expected_direct_target_code_length
        == EXPECTED_DIRECT_TARGET_CODE_LENGTH
    ):
        results.append(_accepted("expected_direct_target_code_length", "4528 checked"))
    else:
        results.append(
            _rejected(
                "expected_direct_target_code_length",
                "expected direct target length 4528",
            )
        )

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
    cases = tuple(getattr(loaded, "cases", ()))
    equation_lifting_case = _find_equation_lifting_case(loaded)
    if getattr(loaded, "case_set_id", None) != "as-fixed-point-construction-cases-v1":
        failures.append("fixed-point-construction-cases-id")
    if len(cases) != 5:
        failures.append("fixed-point-construction-cases-count")
    if equation_lifting_case.case_id != REQUIRED_CASE_ID:
        failures.append("fixed-point-equation-lifting-frontier-case")
    if equation_lifting_case.case_kind != REQUIRED_CASE_KIND:
        failures.append("fixed-point-equation-lifting-frontier-case-kind")
    return _SupportLoad(
        accepted=not failures,
        failed_subjects=_unique_tuple(failures),
        facts={"case_count": len(cases)},
    )


def _find_equation_lifting_case(
    construction_cases: Any | None,
) -> FixedPointEquationLiftingFrontierConstructionCase:
    if construction_cases is None:
        return FixedPointEquationLiftingFrontierConstructionCase(
            case_id="missing",
            case_kind="missing",
            target_id="missing",
            status="missing",
            required_dependency_subjects=(),
            non_claims=(),
        )
    for case in tuple(getattr(construction_cases, "cases", ())):
        if getattr(case, "case_kind", None) != REQUIRED_CASE_KIND:
            continue
        return FixedPointEquationLiftingFrontierConstructionCase(
            case_id=case.case_id,
            case_kind=case.case_kind,
            target_id=case.target_id,
            status=case.status,
            required_dependency_subjects=tuple(case.required_dependency_subjects),
            non_claims=tuple(case.non_claims),
        )
    return FixedPointEquationLiftingFrontierConstructionCase(
        case_id="missing",
        case_kind="missing",
        target_id="missing",
        status="missing",
        required_dependency_subjects=(),
        non_claims=(),
    )


def _validate_equation_lifting_case(
    case: FixedPointEquationLiftingFrontierConstructionCase,
) -> list[FixedPointEquationLiftingFrontierStatusValidation]:
    results: list[FixedPointEquationLiftingFrontierStatusValidation] = []
    if case.case_id == REQUIRED_CASE_ID:
        results.append(_accepted("construction_case.case_id", "equation lifting case id found"))
    else:
        results.append(_rejected("construction_case.case_id", "equation lifting case id missing"))

    if case.case_kind == REQUIRED_CASE_KIND:
        results.append(_accepted("construction_case.kind", "equation lifting case found"))
    else:
        results.append(_rejected("construction_case.kind", "equation lifting case missing"))

    if case.status == REQUIRED_CASE_STATUS:
        results.append(_accepted("construction_case.status", "construction case remains open"))
    else:
        results.append(
            _rejected(
                "construction_case.status",
                "construction case is not open: " + case.status,
            )
        )

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in case.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "construction_case.non_claims",
                "missing case non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("construction_case.non_claims", "case non-claims are explicit"))
    return results


def _validate_fixed_point_targets_support(loaded: Any) -> _SupportLoad:
    failures: list[str] = []
    targets = tuple(getattr(loaded, "targets", ()))
    target = targets[0] if targets else None
    facts: dict[str, Any] = {"target_count": len(targets)}
    if getattr(loaded, "target_set_id", None) != "as-fixed-point-target-v1":
        failures.append("fixed-point-target-id")
    if len(targets) != 1:
        failures.append("fixed-point-target-count")
    if target is not None:
        facts["target_id"] = target.target_id
        facts["sentence_class"] = target.sentence_class
        facts["instance_code_length"] = len(target.expected_instance_code)
        if target.status != "target-selected-not-constructed":
            failures.append("fixed-point-target-status")
        if target.sentence_class != "pi1":
            failures.append("fixed-point-target-sentence-class")
        if not _has_non_claims(target):
            failures.append("fixed-point-target-non-claim")
    return _SupportLoad(
        accepted=not failures,
        failed_subjects=_unique_tuple(failures),
        facts=facts,
    )


def _validate_equation_bridge_support(
    loaded: Any,
    expected_direct_target_length: int,
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
        facts["direct_target_code_length"] = bridge.expected_direct_target_code_length
        facts["bridge_equation_code_length"] = (
            bridge.expected_bridge_equation_code_length
        )
        if bridge.status != "bridge-target-open":
            failures.append("fixed-point-equation-bridge-status")
        if not _has_non_claims(bridge):
            failures.append("fixed-point-equation-bridge-non-claim")
        if bridge.expected_direct_target_code_length != expected_direct_target_length:
            failures.append("fixed-point-equation-bridge-direct-target-length")
        if bridge.expected_bridge_equation_code_length != expected_bridge_length:
            failures.append("fixed-point-equation-bridge-equation-length")
    return _SupportLoad(
        accepted=not failures,
        failed_subjects=_unique_tuple(failures),
        facts=facts,
    )


def _validate_codebook_support(loaded: Any) -> _SupportLoad:
    failures: list[str] = []
    facts = {
        "codebook_id": getattr(loaded, "codebook_id", "missing"),
        "example_count": len(tuple(getattr(loaded, "examples", ()))),
    }
    if getattr(loaded, "codebook_id", None) != "as-formal-codebook-v1":
        failures.append("formal-codebook-id")
    return _SupportLoad(
        accepted=not failures,
        failed_subjects=_unique_tuple(failures),
        facts=facts,
    )


def _validate_equation_lifting_alignment_support(
    loaded: Any,
    expected_direct_target_length: int,
) -> _SupportLoad:
    failures: list[str] = []
    facts: dict[str, Any] = {
        "alignment_count": getattr(loaded, "expected_alignment_count", None),
        "alignment_set_id": getattr(loaded, "alignment_set_id", "missing"),
        "direct_target_code_length": getattr(
            loaded,
            "expected_direct_target_code_length",
            None,
        ),
    }
    if getattr(loaded, "alignment_set_id", None) != (
        "as-fixed-point-equation-lifting-alignment-v1"
    ):
        failures.append("fixed-point-equation-lifting-alignment-id")
    if getattr(loaded, "expected_alignment_count", None) != 1:
        failures.append("fixed-point-equation-lifting-alignment-count")
    if (
        getattr(loaded, "expected_direct_target_code_length", None)
        != expected_direct_target_length
    ):
        failures.append("fixed-point-equation-lifting-alignment-length")
    if not _has_non_claims(loaded):
        failures.append("fixed-point-equation-lifting-alignment-non-claim")
    return _SupportLoad(
        accepted=not failures,
        failed_subjects=_unique_tuple(failures),
        facts=facts,
    )


def _support_surfaces(
    paths: dict[str, Path],
    support_loads: dict[str, _SupportLoad],
) -> list[FixedPointEquationLiftingFrontierSupportSurface]:
    path_by_subject = {
        "fixed_point": paths["fixed_point_targets_path"],
        "fixed_point_equation_bridge": paths[
            "fixed_point_equation_bridge_targets_path"
        ],
        "codebook": paths["codebook_path"],
        "equation_lifting_alignment": paths["equation_lifting_alignment_path"],
    }
    surfaces: list[FixedPointEquationLiftingFrontierSupportSurface] = []
    for subject in REQUIRED_SUPPORT_SUBJECTS:
        load = support_loads[subject]
        surfaces.append(
            FixedPointEquationLiftingFrontierSupportSurface(
                subject=subject,
                path=path_by_subject[subject],
                accepted=load.accepted,
                failed_subjects=load.failed_subjects,
                detail=_support_detail(subject, load),
            )
        )
    return surfaces


def _support_detail(subject: str, load: _SupportLoad) -> str:
    if not load.accepted:
        return "rejected: " + _joined_or_none(load.failed_subjects)
    if subject == "fixed_point":
        return (
            "target count "
            + str(load.facts.get("target_count"))
            + ", class "
            + str(load.facts.get("sentence_class"))
        )
    if subject == "fixed_point_equation_bridge":
        return (
            "direct target length "
            + str(load.facts.get("direct_target_code_length"))
            + ", bridge equation length "
            + str(load.facts.get("bridge_equation_code_length"))
        )
    if subject == "codebook":
        return "codebook examples " + str(load.facts.get("example_count"))
    if subject == "equation_lifting_alignment":
        return (
            "direct target length "
            + str(load.facts.get("direct_target_code_length"))
            + ", alignments "
            + str(load.facts.get("alignment_count"))
        )
    return "accepted"


def _validate_support_surfaces(
    manifest: FixedPointEquationLiftingFrontierStatusManifest,
    surfaces: list[FixedPointEquationLiftingFrontierSupportSurface],
) -> list[FixedPointEquationLiftingFrontierStatusValidation]:
    results: list[FixedPointEquationLiftingFrontierStatusValidation] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "required support surfaces present"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    if len(surfaces) == manifest.expected_support_surface_count:
        results.append(
            _accepted(
                "expected_support_surface_count",
                f"support surface count {len(surfaces)} matches manifest",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_support_surface_count",
                "support surface count mismatch: expected "
                f"{manifest.expected_support_surface_count} but found {len(surfaces)}",
            )
        )

    for surface in surfaces:
        if surface.accepted:
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _validate_case_dependencies(
    case: FixedPointEquationLiftingFrontierConstructionCase,
    surfaces: list[FixedPointEquationLiftingFrontierSupportSurface],
) -> list[FixedPointEquationLiftingFrontierStatusValidation]:
    results: list[FixedPointEquationLiftingFrontierStatusValidation] = []
    if tuple(case.required_dependency_subjects) == REQUIRED_SUPPORT_SUBJECTS:
        results.append(
            _accepted(
                "construction_case.required_dependency_subjects",
                "equation lifting dependencies match support surfaces",
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
        return "fixed-point-equation-lifting-frontier-status"
    if subject in {"non_claims", "construction_case.non_claims"}:
        return "fixed-point-equation-lifting-frontier-non-claim"
    if subject == "construction_case.status":
        return "fixed-point-equation-lifting-frontier-case-status"
    if subject in {
        "support_surfaces",
        "expected_support_surface_count",
        "construction_case.required_dependency_subjects",
        "construction_case.support",
    }:
        return "fixed-point-equation-lifting-frontier-support"
    if subject.startswith("construction_case.") and subject != (
        "construction_case.required_dependency_subjects"
    ):
        return "fixed-point-equation-lifting-frontier-case"
    if subject in REQUIRED_SUPPORT_SUBJECTS or subject.endswith("_path"):
        return "fixed-point-equation-lifting-frontier-dependency"
    if subject.startswith("expected_") and subject != "expected_support_surface_count":
        return "fixed-point-equation-lifting-frontier-length"
    if subject == "fixed_point_construction_cases":
        return "fixed-point-equation-lifting-frontier-dependency"
    return "fixed-point-equation-lifting-frontier"


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
) -> FixedPointEquationLiftingFrontierStatusValidation:
    return FixedPointEquationLiftingFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointEquationLiftingFrontierStatusValidation:
    return FixedPointEquationLiftingFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


def _unique_tuple(values: list[str]) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return tuple(result)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_equation_lifting_frontier_status_cli())
