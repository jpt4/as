"""Finite candidate-surface evidence for the AS fixed-point construction.

This module names the current closed diagonal instance as the fixed-point
candidate surface carried by the first construction case. It checks finite
syntax, routing, and codebook facts only. It does not prove bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.diagonal_construction import (
    build_diagonal_instance_code,
    build_diagonal_seed_node,
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
from autarkic_systems.fixed_point_diagonal_instance_closure import (
    load_fixed_point_diagonal_instance_closure,
    validate_fixed_point_diagonal_instance_closure,
)
from autarkic_systems.fixed_point_equation_bridge import (
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)
from autarkic_systems.formal_code import (
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import free_variables, substitute_node


DEFAULT_CANDIDATE_SURFACE = Path(
    "claims/fixed_point_diagonal_instance_candidate_surface.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = ("diagonal-instance-candidate",)
REQUIRED_FUTURE_WORK = (
    "substitution-representability-proof",
    "substitution-graph-correctness-proof",
    "bridge-equality-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
REQUIRED_CONSTRUCTION_DEPENDENCIES = (
    "fixed_point",
    "diagonal_construction",
    "fixed_point_equation_bridge",
    "diagonal_instance_closure",
    "diagonal_instance_candidate_surface",
)


@dataclass(frozen=True)
class FixedPointDiagonalInstanceCandidateSurfaceManifest:
    """Loaded manifest for finite diagonal-instance candidate evidence."""

    path: Path
    schema_version: int
    candidate_surface_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_construction_cases_path: str
    formal_language_path: str
    codebook_path: str
    fixed_point_targets_path: str
    diagonal_construction_targets_path: str
    fixed_point_equation_bridge_targets_path: str
    diagonal_instance_closure_path: str
    expected_candidate_count: int
    expected_candidate_code_length: int
    expected_candidate_code_prefix: tuple[int, ...]
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceCandidateSurfaceValidation:
    """One validation result for diagonal-instance candidate evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceCandidateSurface:
    """One finite checked fixed-point candidate surface."""

    candidate_id: str
    source_kind: str
    target_id: str
    construction_case_id: str
    construction_id: str
    bridge_id: str
    closure_id: str
    template_variable: str
    seed_code_length: int
    candidate_code_length: int
    candidate_code_prefix: tuple[int, ...]
    candidate_free_variables: tuple[str, ...]
    construction_case_is_open: bool
    construction_case_requires_candidate: bool
    candidate_source_is_closed_instance: bool
    candidate_codebook_roundtrip: bool
    candidate_preserves_target_skeleton: bool
    candidate_slot_is_seed_self_application: bool
    candidate_matches_bridge_observation: bool
    candidate_matches_closure: bool
    all_dependencies_accepted: bool


@dataclass(frozen=True)
class FixedPointDiagonalInstanceCandidateSurfaceReport:
    """Validation report over finite diagonal-instance candidate evidence."""

    manifest: FixedPointDiagonalInstanceCandidateSurfaceManifest
    fixed_point_construction_cases_path: Path
    formal_language_path: Path
    codebook_path: Path
    fixed_point_targets_path: Path
    diagonal_construction_targets_path: Path
    fixed_point_equation_bridge_targets_path: Path
    diagonal_instance_closure_path: Path
    willard_map_path: Path
    results: tuple[FixedPointDiagonalInstanceCandidateSurfaceValidation, ...]
    candidates: tuple[FixedPointDiagonalInstanceCandidateSurface, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every candidate-surface validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def candidate_count(self) -> int:
        """Return the number of checked candidate surfaces."""

        return len(self.candidates)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed candidate counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for candidate in self.candidates:
            counts[candidate.source_kind] = (
                counts.get(candidate.source_kind, 0) + 1
            )
        return counts

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
    """Small report shim for dependencies that cannot be loaded."""

    accepted: bool
    failed_subjects: tuple[str, ...]


def load_fixed_point_diagonal_instance_candidate_surface(
    path: Path | str = DEFAULT_CANDIDATE_SURFACE,
) -> FixedPointDiagonalInstanceCandidateSurfaceManifest:
    """Load the diagonal-instance candidate-surface manifest from JSON."""

    surface_path = Path(path)
    data = json.loads(surface_path.read_text(encoding="utf-8"))
    return FixedPointDiagonalInstanceCandidateSurfaceManifest(
        path=surface_path,
        schema_version=_required_int(data, "schema_version"),
        candidate_surface_set_id=_required_text(data, "candidate_surface_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_construction_cases_path=_required_text(
            data,
            "fixed_point_construction_cases_path",
        ),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
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
        expected_candidate_count=_required_int(data, "expected_candidate_count"),
        expected_candidate_code_length=_required_int(
            data,
            "expected_candidate_code_length",
        ),
        expected_candidate_code_prefix=tuple(
            _required_int_list(data, "expected_candidate_code_prefix")
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_diagonal_instance_candidate_surface(
    manifest: FixedPointDiagonalInstanceCandidateSurfaceManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointDiagonalInstanceCandidateSurfaceReport:
    """Validate finite diagonal-instance candidate-surface evidence."""

    checked_willard_map_path = Path(willard_map_path)
    checked_construction_cases_path = Path(
        manifest.fixed_point_construction_cases_path
    )
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_diagonal_path = Path(manifest.diagonal_construction_targets_path)
    checked_bridge_path = Path(manifest.fixed_point_equation_bridge_targets_path)
    checked_closure_path = Path(manifest.diagonal_instance_closure_path)

    construction_cases: Any = None
    fixed_point_targets: Any = None
    diagonal_targets: Any = None
    bridge_targets: Any = None
    codebook: Any = None

    try:
        construction_cases = load_fixed_point_construction_cases(
            checked_construction_cases_path
        )
        construction_case_report: Any = _DependencyFailure(True, ())
    except (OSError, ValueError, json.JSONDecodeError):
        construction_case_report = _DependencyFailure(
            False,
            ("fixed-point-construction-cases-load",),
        )

    try:
        codebook = load_formal_codebook(checked_codebook_path)
        codebook_report: Any = validate_formal_codebook(
            codebook,
            checked_language_path,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        codebook_report = _DependencyFailure(False, ("codebook-load",))

    try:
        fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
        fixed_point_report: Any = validate_fixed_point_targets(
            fixed_point_targets,
            checked_willard_map_path,
            checked_language_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        fixed_point_report = _DependencyFailure(False, ("fixed-point-target-load",))

    try:
        diagonal_targets = load_diagonal_construction_targets(checked_diagonal_path)
        diagonal_report: Any = validate_diagonal_construction_targets(
            diagonal_targets,
            checked_language_path,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        diagonal_report = _DependencyFailure(False, ("diagonal-construction-load",))

    try:
        bridge_targets = load_fixed_point_equation_bridge_targets(checked_bridge_path)
        bridge_report: Any = validate_fixed_point_equation_bridge_targets(
            bridge_targets,
            checked_language_path,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        bridge_report = _DependencyFailure(
            False,
            ("fixed-point-equation-bridge-load",),
        )

    try:
        closure = load_fixed_point_diagonal_instance_closure(checked_closure_path)
        closure_report: Any = validate_fixed_point_diagonal_instance_closure(
            closure,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        closure_report = _DependencyFailure(False, ("diagonal-instance-closure-load",))

    results: list[FixedPointDiagonalInstanceCandidateSurfaceValidation] = [
        _accepted("manifest", f"loaded {manifest.candidate_surface_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(_validate_manifest_lists(manifest))
    results.extend(
        _validate_dependency_reports(
            construction_case_report,
            codebook_report,
            fixed_point_report,
            diagonal_report,
            bridge_report,
            closure_report,
        )
    )

    candidates: tuple[FixedPointDiagonalInstanceCandidateSurface, ...] = ()
    dependency_reports = (
        construction_case_report,
        codebook_report,
        fixed_point_report,
        diagonal_report,
        bridge_report,
        closure_report,
    )
    can_derive = (
        all(report.accepted for report in dependency_reports)
        and construction_cases is not None
        and codebook is not None
        and fixed_point_targets is not None
        and diagonal_targets is not None
        and bridge_targets is not None
    )
    if can_derive:
        try:
            candidates = _derive_candidates(
                construction_cases,
                fixed_point_targets.targets,
                diagonal_targets.constructions,
                bridge_targets,
                bridge_report.observations,
                closure_report.closures,
                checked_diagonal_path,
                checked_fixed_point_path,
                checked_codebook_path,
                codebook,
            )
        except ValueError as exc:
            results.append(_rejected("candidates", str(exc)))
    else:
        results.append(
            _rejected(
                "candidates",
                "dependency load or validation failed; candidate not derived",
            )
        )
    results.extend(_validate_candidate_set(manifest, candidates))

    return FixedPointDiagonalInstanceCandidateSurfaceReport(
        manifest=manifest,
        fixed_point_construction_cases_path=checked_construction_cases_path,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        fixed_point_targets_path=checked_fixed_point_path,
        diagonal_construction_targets_path=checked_diagonal_path,
        fixed_point_equation_bridge_targets_path=checked_bridge_path,
        diagonal_instance_closure_path=checked_closure_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        candidates=candidates,
    )


def fixed_point_diagonal_instance_candidate_surface_payload(
    report: FixedPointDiagonalInstanceCandidateSurfaceReport,
) -> dict[str, Any]:
    """Return a JSON-ready diagonal-instance candidate-surface payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "candidate_surface_manifest": str(report.manifest.path),
        "candidate_surface_set_id": report.manifest.candidate_surface_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "diagonal_construction_targets_path": str(
            report.diagonal_construction_targets_path
        ),
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "diagonal_instance_closure_path": str(report.diagonal_instance_closure_path),
        "willard_map": str(report.willard_map_path),
        "expected_candidate_count": report.manifest.expected_candidate_count,
        "candidate_count": report.candidate_count,
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "candidates": [
            _candidate_payload(candidate) for candidate in report.candidates
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


def format_fixed_point_diagonal_instance_candidate_surface_report(
    report: FixedPointDiagonalInstanceCandidateSurfaceReport,
) -> str:
    """Format a concise human-readable candidate-surface report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point diagonal instance candidate surface: {status}",
        f"Candidate surface set: {report.manifest.candidate_surface_set_id}",
        f"Candidate surfaces: {report.candidate_count}",
        "Source kinds: "
        + ", ".join(
            f"{kind}={count}" for kind, count in report.source_kind_counts.items()
        ),
        f"Candidate failures: {_joined_or_none(report.failed_subjects)}",
    ]
    for candidate in report.candidates:
        lines.extend([
            f"- {candidate.candidate_id}",
            f"  Target: {candidate.target_id}",
            f"  Construction case: {candidate.construction_case_id}",
            f"  Construction: {candidate.construction_id}",
            f"  Bridge: {candidate.bridge_id}",
            f"  Closure: {candidate.closure_id}",
            f"  Candidate code length: {candidate.candidate_code_length}",
            f"  construction_case_open={candidate.construction_case_is_open}",
            "  requires_candidate="
            + str(candidate.construction_case_requires_candidate),
            f"  candidate_closed={candidate.candidate_source_is_closed_instance}",
            f"  codebook_roundtrip={candidate.candidate_codebook_roundtrip}",
            "  target_skeleton_preserved="
            + str(candidate.candidate_preserves_target_skeleton),
            "  seed_self_application_slot="
            + str(candidate.candidate_slot_is_seed_self_application),
            f"  matches_bridge={candidate.candidate_matches_bridge_observation}",
            f"  matches_closure={candidate.candidate_matches_closure}",
            f"  dependencies_accepted={candidate.all_dependencies_accepted}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_diagonal_instance_candidate_surface_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point diagonal-instance candidate-surface validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_diagonal_instance_candidate_surface"
        ),
        description="Validate AS fixed-point diagonal-instance candidate evidence.",
    )
    parser.add_argument(
        "--candidate-surface",
        default=str(DEFAULT_CANDIDATE_SURFACE),
        help="Path to the fixed-point diagonal-instance candidate manifest.",
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

    manifest = load_fixed_point_diagonal_instance_candidate_surface(
        args.candidate_surface
    )
    report = validate_fixed_point_diagonal_instance_candidate_surface(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            fixed_point_diagonal_instance_candidate_surface_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_fixed_point_diagonal_instance_candidate_surface_report(report))
    return 0 if report.accepted else 1


def _derive_candidates(
    construction_cases: Any,
    fixed_point_targets: tuple[Any, ...],
    diagonal_constructions: tuple[Any, ...],
    bridge_manifest: Any,
    bridge_observations: tuple[Any, ...],
    closures: tuple[Any, ...],
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    codebook_path: Path,
    codebook: Any,
) -> tuple[FixedPointDiagonalInstanceCandidateSurface, ...]:
    construction_case = _find_case(
        construction_cases.cases,
        "diagonal-instance-closure",
    )
    target = _find_by_id(fixed_point_targets, "target_id", construction_case.target_id)
    bridge = _find_by_id(
        bridge_manifest.bridges,
        "target_id",
        construction_case.target_id,
    )
    construction = _find_by_id(
        diagonal_constructions,
        "construction_id",
        bridge.construction_id,
    )
    bridge_observation = _find_by_id(
        bridge_observations,
        "bridge_id",
        bridge.bridge_id,
    )
    closure = _find_closure(closures, construction_case.target_id, bridge.bridge_id)

    seed_node = build_diagonal_seed_node(target)
    seed_code = encode_node(seed_node, codebook)
    seed_quote = quote_tokens_as_term(seed_code)
    candidate_node = substitute_node(
        seed_node,
        target.template_variable,
        seed_quote,
    )
    candidate_code = build_diagonal_instance_code(
        construction_id=construction.construction_id,
        targets_path=diagonal_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    decoded_candidate = decode_code(candidate_code, codebook)
    candidate_prefix = candidate_code[: len(closure.diagonal_instance_code_prefix)]
    candidate_slot = _target_slot(candidate_node)
    expected_slot = {
        "kind": "substitution_code",
        "left": seed_quote,
        "right": seed_quote,
    }
    candidate_free_variables = tuple(sorted(free_variables(candidate_node)))
    bridge_prefix = candidate_code[
        : len(bridge_observation.diagonal_instance_code_prefix)
    ]
    closure_prefix = candidate_code[: len(closure.diagonal_instance_code_prefix)]

    return (
        FixedPointDiagonalInstanceCandidateSurface(
            candidate_id="AS-FIXED-POINT-DIAGONAL-INSTANCE-CANDIDATE-SURFACE",
            source_kind="diagonal-instance-candidate",
            target_id=target.target_id,
            construction_case_id=construction_case.case_id,
            construction_id=construction.construction_id,
            bridge_id=bridge.bridge_id,
            closure_id=closure.closure_id,
            template_variable=target.template_variable,
            seed_code_length=len(seed_code),
            candidate_code_length=len(candidate_code),
            candidate_code_prefix=candidate_prefix,
            candidate_free_variables=candidate_free_variables,
            construction_case_is_open=construction_case.status == "proof-case-open",
            construction_case_requires_candidate=(
                construction_case.required_dependency_subjects
                == REQUIRED_CONSTRUCTION_DEPENDENCIES
            ),
            candidate_source_is_closed_instance=(
                not candidate_free_variables and decoded_candidate == candidate_node
            ),
            candidate_codebook_roundtrip=(
                decoded_candidate == candidate_node
                and encode_node(decoded_candidate, codebook) == candidate_code
            ),
            candidate_preserves_target_skeleton=_target_skeleton_preserved(
                target.template_node,
                candidate_node,
            ),
            candidate_slot_is_seed_self_application=(candidate_slot == expected_slot),
            candidate_matches_bridge_observation=(
                bridge_observation.diagonal_instance_code_length
                == len(candidate_code)
                and bridge_observation.diagonal_instance_code_prefix == bridge_prefix
                and bridge_observation.diagonal_instance_closed
            ),
            candidate_matches_closure=(
                closure.diagonal_instance_code_length == len(candidate_code)
                and closure.diagonal_instance_code_prefix == closure_prefix
                and closure.diagonal_instance_closed
                and closure.codebook_roundtrip
                and closure.bridge_matches_diagonal_instance
            ),
            all_dependencies_accepted=True,
        ),
    )


def _validate_references(
    manifest: FixedPointDiagonalInstanceCandidateSurfaceManifest,
) -> list[FixedPointDiagonalInstanceCandidateSurfaceValidation]:
    expected = (
        (
            "fixed_point_construction_cases_path",
            manifest.fixed_point_construction_cases_path,
            "claims/fixed_point_construction_cases.json",
        ),
        (
            "formal_language_path",
            manifest.formal_language_path,
            "language/formal_arithmetic_language.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "fixed_point_targets_path",
            manifest.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
        (
            "diagonal_construction_targets_path",
            manifest.diagonal_construction_targets_path,
            "claims/diagonal_construction_targets.json",
        ),
        (
            "fixed_point_equation_bridge_targets_path",
            manifest.fixed_point_equation_bridge_targets_path,
            "claims/fixed_point_equation_bridge_targets.json",
        ),
        (
            "diagonal_instance_closure_path",
            manifest.diagonal_instance_closure_path,
            "claims/fixed_point_diagonal_instance_closure.json",
        ),
    )
    results: list[FixedPointDiagonalInstanceCandidateSurfaceValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_manifest_lists(
    manifest: FixedPointDiagonalInstanceCandidateSurfaceManifest,
) -> list[FixedPointDiagonalInstanceCandidateSurfaceValidation]:
    results: list[FixedPointDiagonalInstanceCandidateSurfaceValidation] = []
    if manifest.required_source_kinds == REQUIRED_SOURCE_KINDS:
        results.append(_accepted("required_source_kinds", "source kinds match"))
    else:
        results.append(_rejected("required_source_kinds", "source kind mismatch"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in manifest.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                "required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(_accepted("required_future_work", "future work is explicit"))

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


def _validate_dependency_reports(
    construction_case_report: Any,
    codebook_report: Any,
    fixed_point_report: Any,
    diagonal_report: Any,
    bridge_report: Any,
    closure_report: Any,
) -> list[FixedPointDiagonalInstanceCandidateSurfaceValidation]:
    checks = (
        ("fixed_point_construction_cases", construction_case_report, "construction cases"),
        ("codebook", codebook_report, "formal codebook"),
        ("fixed_point", fixed_point_report, "fixed-point target"),
        ("diagonal_construction", diagonal_report, "diagonal construction"),
        ("fixed_point_equation_bridge", bridge_report, "fixed-point equation bridge"),
        ("diagonal_instance_closure", closure_report, "diagonal instance closure"),
    )
    results: list[FixedPointDiagonalInstanceCandidateSurfaceValidation] = []
    for subject, report, label in checks:
        if report.accepted:
            results.append(_accepted(subject, f"{label} accepted"))
        else:
            results.append(
                _rejected(
                    subject,
                    f"{label} rejected: " + _joined_or_none(report.failed_subjects),
                )
            )
    return results


def _validate_candidate_set(
    manifest: FixedPointDiagonalInstanceCandidateSurfaceManifest,
    candidates: tuple[FixedPointDiagonalInstanceCandidateSurface, ...],
) -> list[FixedPointDiagonalInstanceCandidateSurfaceValidation]:
    results: list[FixedPointDiagonalInstanceCandidateSurfaceValidation] = []
    if manifest.expected_candidate_count != len(candidates):
        results.append(
            _rejected(
                "candidate_count",
                "candidate count mismatch: expected "
                + str(manifest.expected_candidate_count)
                + " got "
                + str(len(candidates)),
            )
        )
    else:
        results.append(
            _accepted("candidate_count", f"checked {len(candidates)} candidate(s)")
        )

    for candidate in candidates:
        results.extend(_validate_candidate(manifest, candidate))
    return results


def _validate_candidate(
    manifest: FixedPointDiagonalInstanceCandidateSurfaceManifest,
    candidate: FixedPointDiagonalInstanceCandidateSurface,
) -> list[FixedPointDiagonalInstanceCandidateSurfaceValidation]:
    subject = candidate.candidate_id
    results: list[FixedPointDiagonalInstanceCandidateSurfaceValidation] = []

    if candidate.source_kind not in manifest.required_source_kinds:
        results.append(_rejected(f"{subject}.source_kind", "source kind mismatch"))
    else:
        results.append(_accepted(f"{subject}.source_kind", "source kind accepted"))

    if candidate.candidate_code_length != manifest.expected_candidate_code_length:
        results.append(
            _rejected(
                f"{subject}.length",
                "candidate length mismatch: expected "
                + str(manifest.expected_candidate_code_length)
                + " got "
                + str(candidate.candidate_code_length),
            )
        )
    elif candidate.candidate_code_prefix != manifest.expected_candidate_code_prefix:
        results.append(_rejected(f"{subject}.length", "candidate prefix mismatch"))
    else:
        results.append(_accepted(f"{subject}.length", "candidate length is current"))

    if candidate.construction_case_is_open:
        results.append(_accepted(f"{subject}.case_status", "construction case open"))
    else:
        results.append(_rejected(f"{subject}.case_status", "construction case closed"))

    if candidate.construction_case_requires_candidate:
        results.append(_accepted(f"{subject}.case_dependency", "candidate required"))
    else:
        results.append(
            _rejected(f"{subject}.case_dependency", "candidate dependency missing")
        )

    bool_checks = (
        (
            "source",
            candidate.candidate_source_is_closed_instance,
            "candidate is the closed diagonal instance",
            "candidate is not the closed diagonal instance",
        ),
        (
            "roundtrip",
            candidate.candidate_codebook_roundtrip,
            "candidate codebook roundtrip accepted",
            "candidate codebook roundtrip mismatch",
        ),
        (
            "skeleton",
            candidate.candidate_preserves_target_skeleton,
            "candidate target skeleton preserved",
            "candidate target skeleton mismatch",
        ),
        (
            "slot",
            candidate.candidate_slot_is_seed_self_application,
            "candidate slot is seed self-application",
            "candidate slot mismatch",
        ),
        (
            "bridge",
            candidate.candidate_matches_bridge_observation,
            "candidate matches bridge observation",
            "candidate bridge mismatch",
        ),
        (
            "closure",
            candidate.candidate_matches_closure,
            "candidate matches closure observation",
            "candidate closure mismatch",
        ),
        (
            "dependencies",
            candidate.all_dependencies_accepted,
            "dependencies accepted",
            "dependency rejection propagated",
        ),
    )
    for suffix, accepted, ok_detail, fail_detail in bool_checks:
        if accepted:
            results.append(_accepted(f"{subject}.{suffix}", ok_detail))
        else:
            results.append(_rejected(f"{subject}.{suffix}", fail_detail))

    return results


def _candidate_payload(
    candidate: FixedPointDiagonalInstanceCandidateSurface,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "source_kind": candidate.source_kind,
        "target_id": candidate.target_id,
        "construction_case_id": candidate.construction_case_id,
        "construction_id": candidate.construction_id,
        "bridge_id": candidate.bridge_id,
        "closure_id": candidate.closure_id,
        "template_variable": candidate.template_variable,
        "seed_code_length": candidate.seed_code_length,
        "observed_candidate_code_length": candidate.candidate_code_length,
        "observed_candidate_code_prefix": list(candidate.candidate_code_prefix),
        "observed_candidate_free_variables": list(
            candidate.candidate_free_variables
        ),
        "observed_construction_case_is_open": (
            candidate.construction_case_is_open
        ),
        "observed_construction_case_requires_candidate": (
            candidate.construction_case_requires_candidate
        ),
        "observed_candidate_source_is_closed_instance": (
            candidate.candidate_source_is_closed_instance
        ),
        "observed_candidate_codebook_roundtrip": (
            candidate.candidate_codebook_roundtrip
        ),
        "observed_candidate_preserves_target_skeleton": (
            candidate.candidate_preserves_target_skeleton
        ),
        "observed_candidate_slot_is_seed_self_application": (
            candidate.candidate_slot_is_seed_self_application
        ),
        "observed_candidate_matches_bridge_observation": (
            candidate.candidate_matches_bridge_observation
        ),
        "observed_candidate_matches_closure": candidate.candidate_matches_closure,
        "observed_all_dependencies_accepted": candidate.all_dependencies_accepted,
    }


def _target_slot(node: dict[str, Any]) -> dict[str, Any]:
    body = node.get("body")
    if not isinstance(body, dict) or body.get("kind") != "less_than":
        raise ValueError("target body must be less_than")
    right = body.get("right")
    if not isinstance(right, dict):
        raise ValueError("target slot is not a term")
    return right


def _target_skeleton_preserved(
    template_node: dict[str, Any],
    candidate_node: dict[str, Any],
) -> bool:
    try:
        if template_node.get("kind") != candidate_node.get("kind"):
            return False
        if template_node.get("variable") != candidate_node.get("variable"):
            return False
        template_body = template_node.get("body")
        candidate_body = candidate_node.get("body")
        if not isinstance(template_body, dict) or not isinstance(candidate_body, dict):
            return False
        if template_body.get("kind") != candidate_body.get("kind"):
            return False
        if template_body.get("left") != candidate_body.get("left"):
            return False
        _target_slot(template_node)
        _target_slot(candidate_node)
    except ValueError:
        return False
    return True


def _find_case(cases: tuple[Any, ...], case_kind: str) -> Any:
    for case in cases:
        if case.case_kind == case_kind:
            return case
    raise ValueError(f"missing construction case: {case_kind}")


def _find_by_id(items: tuple[Any, ...], id_attr: str, expected_id: str) -> Any:
    for item in items:
        if getattr(item, id_attr) == expected_id:
            return item
    raise ValueError(f"missing {id_attr}: {expected_id}")


def _find_closure(closures: tuple[Any, ...], target_id: str, bridge_id: str) -> Any:
    for closure in closures:
        if closure.target_id == target_id and closure.bridge_id == bridge_id:
            return closure
    raise ValueError(f"missing closure for {target_id} / {bridge_id}")


def _failed_subject_for_result(subject: str) -> str:
    if subject == "candidate_count":
        return "fixed-point-diagonal-instance-candidate-surface-count"
    if subject.endswith(".length"):
        return "fixed-point-diagonal-instance-candidate-surface-length"
    if subject.endswith(".source_kind") or subject == "required_source_kinds":
        return "fixed-point-diagonal-instance-candidate-surface-source-kind"
    if subject.endswith(".case_status"):
        return "fixed-point-diagonal-instance-candidate-surface-case-status"
    if subject.endswith(".case_dependency"):
        return "fixed-point-diagonal-instance-candidate-surface-case-dependency"
    if subject.endswith(".source"):
        return "fixed-point-diagonal-instance-candidate-surface-source"
    if subject.endswith(".roundtrip"):
        return "fixed-point-diagonal-instance-candidate-surface-roundtrip"
    if subject.endswith(".skeleton"):
        return "fixed-point-diagonal-instance-candidate-surface-skeleton"
    if subject.endswith(".slot"):
        return "fixed-point-diagonal-instance-candidate-surface-slot"
    if subject.endswith(".bridge"):
        return "fixed-point-diagonal-instance-candidate-surface-bridge"
    if subject.endswith(".closure"):
        return "fixed-point-diagonal-instance-candidate-surface-closure"
    if subject in {
        "fixed_point_construction_cases",
        "codebook",
        "fixed_point",
        "diagonal_construction",
        "fixed_point_equation_bridge",
        "diagonal_instance_closure",
    }:
        return "fixed-point-diagonal-instance-candidate-surface-dependency"
    if subject.endswith("_path"):
        return "fixed-point-diagonal-instance-candidate-surface-reference"
    if subject == "required_future_work":
        return "fixed-point-diagonal-instance-candidate-surface-future-work"
    if subject == "non_claims":
        return "fixed-point-diagonal-instance-candidate-surface-non-claim"
    if subject == "next_as_action":
        return "fixed-point-diagonal-instance-candidate-surface-next-action"
    return "fixed-point-diagonal-instance-candidate-surface"


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


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    values = _required_list(item, key)
    result: list[int] = []
    for value in values:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{key} contains non-natural item")
        result.append(value)
    return result


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceCandidateSurfaceValidation:
    return FixedPointDiagonalInstanceCandidateSurfaceValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceCandidateSurfaceValidation:
    return FixedPointDiagonalInstanceCandidateSurfaceValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_diagonal_instance_candidate_surface_cli())
