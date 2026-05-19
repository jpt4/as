"""Finite bridge from the current substitution witness to fixed-point surfaces.

This module checks that the existing substitution witness, diagonal
construction, fixed-point equation bridge, diagonal-instance closure, and
substitution graph correctness case map all name the same finite
self-application route. It does not prove substitution representability,
bridge equality, a fixed-point equation, or self-consistency.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.diagonal_construction import (
    DiagonalConstructionTarget,
    build_diagonal_instance_code,
    build_diagonal_seed_node,
    load_diagonal_construction_targets,
    validate_diagonal_construction_targets,
)
from autarkic_systems.fixed_point import (
    FixedPointTarget,
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.fixed_point_diagonal_instance_closure import (
    FixedPointDiagonalInstanceClosure,
    load_fixed_point_diagonal_instance_closure,
    validate_fixed_point_diagonal_instance_closure,
)
from autarkic_systems.fixed_point_equation_bridge import (
    FixedPointEquationBridgeObservation,
    FixedPointEquationBridgeTarget,
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)
from autarkic_systems.formal_code import (
    FormalCodebook,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.substitution_graph_correctness_cases import (
    load_substitution_graph_correctness_cases,
    validate_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_representability import (
    SubstitutionRepresentabilityObservation,
    SubstitutionRepresentabilityWitness,
    build_substitution_witness_output_code,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


DEFAULT_BRIDGE = Path("claims/fixed_point_substitution_witness_bridge.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = ("substitution-witness-bridge",)
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


@dataclass(frozen=True)
class FixedPointSubstitutionWitnessBridgeManifest:
    """Loaded manifest for finite substitution-witness bridge evidence."""

    path: Path
    schema_version: int
    bridge_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    fixed_point_targets_path: str
    diagonal_construction_targets_path: str
    substitution_representability_targets_path: str
    substitution_graph_correctness_cases_path: str
    fixed_point_equation_bridge_targets_path: str
    diagonal_instance_closure_path: str
    expected_bridge_count: int
    expected_witness_output_code_length: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSubstitutionWitnessBridgeValidation:
    """One validation result for substitution-witness bridge evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionWitnessBridge:
    """One finite witness-to-bridge alignment point."""

    bridge_id: str
    source_kind: str
    target_id: str
    construction_id: str
    witness_id: str
    equation_bridge_id: str
    closure_id: str
    formula_code_length: int
    argument_code_length: int
    witness_output_code_length: int
    route_ids_match: bool
    self_application_inputs_match: bool
    seed_code_matches_witness_formula: bool
    witness_output_matches_diagonal_instance: bool
    bridge_observation_matches_witness: bool
    closure_observation_matches_bridge: bool
    correctness_cases_accepted: bool
    witness_output_closed: bool


@dataclass(frozen=True)
class FixedPointSubstitutionWitnessBridgeReport:
    """Validation report over finite substitution-witness bridge evidence."""

    manifest: FixedPointSubstitutionWitnessBridgeManifest
    formal_language_path: Path
    codebook_path: Path
    fixed_point_targets_path: Path
    diagonal_construction_targets_path: Path
    substitution_representability_targets_path: Path
    substitution_graph_correctness_cases_path: Path
    fixed_point_equation_bridge_targets_path: Path
    diagonal_instance_closure_path: Path
    willard_map_path: Path
    results: tuple[FixedPointSubstitutionWitnessBridgeValidation, ...]
    bridges: tuple[FixedPointSubstitutionWitnessBridge, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every witness-bridge validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def bridge_count(self) -> int:
        """Return the number of checked witness bridges."""

        return len(self.bridges)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed bridge counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for bridge in self.bridges:
            counts[bridge.source_kind] = counts.get(bridge.source_kind, 0) + 1
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


def load_fixed_point_substitution_witness_bridge(
    path: Path | str = DEFAULT_BRIDGE,
) -> FixedPointSubstitutionWitnessBridgeManifest:
    """Load the substitution-witness bridge manifest from JSON."""

    bridge_path = Path(path)
    data = json.loads(bridge_path.read_text(encoding="utf-8"))
    return FixedPointSubstitutionWitnessBridgeManifest(
        path=bridge_path,
        schema_version=_required_int(data, "schema_version"),
        bridge_set_id=_required_text(data, "bridge_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        diagonal_construction_targets_path=_required_text(
            data,
            "diagonal_construction_targets_path",
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
        diagonal_instance_closure_path=_required_text(
            data,
            "diagonal_instance_closure_path",
        ),
        expected_bridge_count=_required_int(data, "expected_bridge_count"),
        expected_witness_output_code_length=_required_int(
            data,
            "expected_witness_output_code_length",
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_substitution_witness_bridge(
    manifest: FixedPointSubstitutionWitnessBridgeManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSubstitutionWitnessBridgeReport:
    """Validate finite substitution-witness bridge evidence."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_diagonal_path = Path(manifest.diagonal_construction_targets_path)
    checked_witness_path = Path(manifest.substitution_representability_targets_path)
    checked_cases_path = Path(manifest.substitution_graph_correctness_cases_path)
    checked_equation_bridge_path = Path(manifest.fixed_point_equation_bridge_targets_path)
    checked_closure_path = Path(manifest.diagonal_instance_closure_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    fixed_points = load_fixed_point_targets(checked_fixed_point_path)
    fixed_point_report = validate_fixed_point_targets(
        fixed_points,
        checked_willard_map_path,
        checked_language_path,
    )
    diagonals = load_diagonal_construction_targets(checked_diagonal_path)
    diagonal_report = validate_diagonal_construction_targets(
        diagonals,
        checked_language_path,
        checked_willard_map_path,
    )
    witnesses = load_substitution_representability_targets(checked_witness_path)
    witness_report = validate_substitution_representability_targets(
        witnesses,
        checked_language_path,
        checked_willard_map_path,
    )
    correctness_cases = load_substitution_graph_correctness_cases(checked_cases_path)
    correctness_case_report = validate_substitution_graph_correctness_cases(
        correctness_cases,
        checked_willard_map_path,
    )
    equation_bridges = load_fixed_point_equation_bridge_targets(
        checked_equation_bridge_path
    )
    equation_bridge_report = validate_fixed_point_equation_bridge_targets(
        equation_bridges,
        checked_language_path,
        checked_willard_map_path,
    )
    closures = load_fixed_point_diagonal_instance_closure(checked_closure_path)
    closure_report = validate_fixed_point_diagonal_instance_closure(
        closures,
        checked_willard_map_path,
    )

    results: list[FixedPointSubstitutionWitnessBridgeValidation] = [
        _accepted("manifest", "loaded substitution-witness bridge manifest")
    ]
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            codebook_report,
            fixed_point_report,
            diagonal_report,
            witness_report,
            correctness_case_report,
            equation_bridge_report,
            closure_report,
        )
    )
    bridges: tuple[FixedPointSubstitutionWitnessBridge, ...] = ()
    if all(
        report.accepted
        for report in (
            codebook_report,
            fixed_point_report,
            diagonal_report,
            witness_report,
            correctness_case_report,
            equation_bridge_report,
            closure_report,
        )
    ):
        bridge_results, bridges = _validate_bridges(
            manifest,
            codebook,
            fixed_points.targets,
            diagonals.constructions,
            witnesses.witnesses,
            witness_report.observations,
            equation_bridges.bridges,
            equation_bridge_report.observations,
            closure_report.closures,
            correctness_case_report.accepted,
            checked_witness_path,
            checked_diagonal_path,
            checked_fixed_point_path,
            checked_codebook_path,
        )
        results.extend(bridge_results)
    else:
        results.append(
            _rejected(
                "bridges.dependencies",
                "accepted dependencies are required before bridge checks",
            )
        )

    return FixedPointSubstitutionWitnessBridgeReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        fixed_point_targets_path=checked_fixed_point_path,
        diagonal_construction_targets_path=checked_diagonal_path,
        substitution_representability_targets_path=checked_witness_path,
        substitution_graph_correctness_cases_path=checked_cases_path,
        fixed_point_equation_bridge_targets_path=checked_equation_bridge_path,
        diagonal_instance_closure_path=checked_closure_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        bridges=bridges,
    )


def fixed_point_substitution_witness_bridge_payload(
    report: FixedPointSubstitutionWitnessBridgeReport,
) -> dict[str, Any]:
    """Return a JSON-ready substitution-witness bridge payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "bridge_manifest": str(report.manifest.path),
        "bridge_set_id": report.manifest.bridge_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "diagonal_construction_targets_path": str(
            report.diagonal_construction_targets_path
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
        "diagonal_instance_closure_path": str(report.diagonal_instance_closure_path),
        "willard_map": str(report.willard_map_path),
        "expected_bridge_count": report.manifest.expected_bridge_count,
        "bridge_count": report.bridge_count,
        "source_kind_counts": report.source_kind_counts,
        "failed_subjects": list(report.failed_subjects),
        "bridges": [_bridge_payload(bridge) for bridge in report.bridges],
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


def format_fixed_point_substitution_witness_bridge_report(
    report: FixedPointSubstitutionWitnessBridgeReport,
) -> str:
    """Format a concise human-readable witness-bridge report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point substitution witness bridge: {status}",
        f"Bridge set: {report.manifest.bridge_set_id}",
        f"Witness bridges: {report.bridge_count}",
        "Source kinds: "
        + ", ".join(
            f"{kind}={count}" for kind, count in report.source_kind_counts.items()
        ),
        f"Bridge failures: {_joined_or_none(report.failed_subjects)}",
    ]
    for bridge in report.bridges:
        lines.extend([
            f"- {bridge.bridge_id}",
            f"  Target: {bridge.target_id}",
            f"  Construction: {bridge.construction_id}",
            f"  Witness: {bridge.witness_id}",
            f"  Equation bridge: {bridge.equation_bridge_id}",
            f"  Witness output length: {bridge.witness_output_code_length}",
            f"  Self-application: {bridge.self_application_inputs_match}",
            f"  Correctness cases accepted: {bridge.correctness_cases_accepted}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_substitution_witness_bridge_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point substitution-witness bridge validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_substitution_witness_bridge",
        description="Validate AS fixed-point substitution-witness bridge evidence.",
    )
    parser.add_argument(
        "--bridge",
        default=str(DEFAULT_BRIDGE),
        help="Path to the fixed-point substitution-witness bridge manifest.",
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

    manifest = load_fixed_point_substitution_witness_bridge(args.bridge)
    report = validate_fixed_point_substitution_witness_bridge(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(fixed_point_substitution_witness_bridge_payload(report), sort_keys=True))
    else:
        print(format_fixed_point_substitution_witness_bridge_report(report))
    return 0 if report.accepted else 1


def _validate_references(
    manifest: FixedPointSubstitutionWitnessBridgeManifest,
) -> list[FixedPointSubstitutionWitnessBridgeValidation]:
    expected = (
        ("formal_language_path", manifest.formal_language_path, "language/formal_arithmetic_language.json"),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        ("fixed_point_targets_path", manifest.fixed_point_targets_path, "claims/fixed_point_targets.json"),
        (
            "diagonal_construction_targets_path",
            manifest.diagonal_construction_targets_path,
            "claims/diagonal_construction_targets.json",
        ),
        (
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
        (
            "substitution_graph_correctness_cases_path",
            manifest.substitution_graph_correctness_cases_path,
            "claims/substitution_graph_correctness_cases.json",
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
    results: list[FixedPointSubstitutionWitnessBridgeValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(_rejected(subject, f"expected {expected_value} but found {actual}"))
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    codebook_report: Any,
    fixed_point_report: Any,
    diagonal_report: Any,
    witness_report: Any,
    correctness_case_report: Any,
    equation_bridge_report: Any,
    closure_report: Any,
) -> list[FixedPointSubstitutionWitnessBridgeValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("fixed_point", fixed_point_report, "fixed-point target"),
        ("diagonal_construction", diagonal_report, "diagonal construction"),
        ("substitution_representability", witness_report, "substitution witness"),
        (
            "substitution_graph_correctness_cases",
            correctness_case_report,
            "substitution graph correctness cases",
        ),
        (
            "fixed_point_equation_bridge",
            equation_bridge_report,
            "fixed-point equation bridge",
        ),
        ("diagonal_instance_closure", closure_report, "diagonal-instance closure"),
    )
    results: list[FixedPointSubstitutionWitnessBridgeValidation] = []
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


def _validate_bridges(
    manifest: FixedPointSubstitutionWitnessBridgeManifest,
    codebook: FormalCodebook,
    fixed_points: tuple[FixedPointTarget, ...],
    diagonals: tuple[DiagonalConstructionTarget, ...],
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_observations: tuple[SubstitutionRepresentabilityObservation, ...],
    equation_bridges: tuple[FixedPointEquationBridgeTarget, ...],
    equation_observations: tuple[FixedPointEquationBridgeObservation, ...],
    closures: tuple[FixedPointDiagonalInstanceClosure, ...],
    correctness_cases_accepted: bool,
    witness_targets_path: Path,
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    codebook_path: Path,
) -> tuple[
    list[FixedPointSubstitutionWitnessBridgeValidation],
    tuple[FixedPointSubstitutionWitnessBridge, ...],
]:
    results: list[FixedPointSubstitutionWitnessBridgeValidation] = []
    built: list[FixedPointSubstitutionWitnessBridge] = []
    witness_observations_by_id = {
        observation.witness_id: observation for observation in witness_observations
    }
    equation_observations_by_id = {
        observation.bridge_id: observation for observation in equation_observations
    }
    closures_by_bridge = {closure.bridge_id: closure for closure in closures}
    for equation_bridge in equation_bridges:
        witness = _find_by_id(witnesses, "witness_id", equation_bridge.witness_id)
        target = _find_by_id(fixed_points, "target_id", equation_bridge.target_id)
        construction = _find_by_id(
            diagonals,
            "construction_id",
            equation_bridge.construction_id,
        )
        witness_observation = witness_observations_by_id[witness.witness_id]
        equation_observation = equation_observations_by_id[equation_bridge.bridge_id]
        closure = closures_by_bridge[equation_bridge.bridge_id]
        built.append(
            _build_bridge(
                target,
                construction,
                witness,
                witness_observation,
                equation_bridge,
                equation_observation,
                closure,
                correctness_cases_accepted,
                codebook,
                witness_targets_path,
                diagonal_targets_path,
                fixed_point_targets_path,
                codebook_path,
            )
        )

    if len(built) != manifest.expected_bridge_count:
        results.append(
            _rejected(
                "bridge_count",
                "bridge count mismatch: expected "
                + str(manifest.expected_bridge_count)
                + " got "
                + str(len(built)),
            )
        )
    else:
        results.append(_accepted("bridge_count", f"checked {len(built)} bridge(s)"))

    if manifest.required_source_kinds != REQUIRED_SOURCE_KINDS:
        results.append(
            _rejected(
                "required_source_kinds",
                "source kinds mismatch: " + ", ".join(manifest.required_source_kinds),
            )
        )
    else:
        results.append(_accepted("required_source_kinds", "source kinds are current"))

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
            _rejected("non_claims", "missing non-claims: " + ", ".join(missing_non_claims))
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))

    for bridge in built:
        results.extend(
            _validate_bridge(
                bridge,
                manifest.expected_witness_output_code_length,
            )
        )
    return results, tuple(built)


def _build_bridge(
    target: FixedPointTarget,
    construction: DiagonalConstructionTarget,
    witness: SubstitutionRepresentabilityWitness,
    witness_observation: SubstitutionRepresentabilityObservation,
    equation_bridge: FixedPointEquationBridgeTarget,
    equation_observation: FixedPointEquationBridgeObservation,
    closure: FixedPointDiagonalInstanceClosure,
    correctness_cases_accepted: bool,
    codebook: FormalCodebook,
    witness_targets_path: Path,
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    codebook_path: Path,
) -> FixedPointSubstitutionWitnessBridge:
    seed_code = encode_node(build_diagonal_seed_node(target), codebook)
    witness_output_code = build_substitution_witness_output_code(
        witness_id=witness.witness_id,
        targets_path=witness_targets_path,
        diagonal_targets_path=diagonal_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    diagonal_instance_code = build_diagonal_instance_code(
        construction_id=construction.construction_id,
        targets_path=diagonal_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    return FixedPointSubstitutionWitnessBridge(
        bridge_id="AS-FIXED-POINT-SUBSTITUTION-WITNESS-BRIDGE",
        source_kind="substitution-witness-bridge",
        target_id=target.target_id,
        construction_id=construction.construction_id,
        witness_id=witness.witness_id,
        equation_bridge_id=equation_bridge.bridge_id,
        closure_id=closure.closure_id,
        formula_code_length=len(witness_observation.formula_code),
        argument_code_length=len(witness_observation.argument_code),
        witness_output_code_length=len(witness_output_code),
        route_ids_match=(
            witness.target_id
            == target.target_id
            == equation_bridge.target_id
            == closure.target_id
            and witness.construction_id
            == construction.construction_id
            == equation_bridge.construction_id
            == closure.construction_id
        ),
        self_application_inputs_match=(
            witness_observation.formula_code == witness_observation.argument_code
            and witness.variable == target.template_variable
        ),
        seed_code_matches_witness_formula=(
            seed_code
            == witness_observation.formula_code
            == witness_observation.argument_code
        ),
        witness_output_matches_diagonal_instance=(
            witness_output_code == diagonal_instance_code
            and witness_observation.output_code_length == len(diagonal_instance_code)
        ),
        bridge_observation_matches_witness=(
            equation_bridge.witness_id == witness.witness_id
            and equation_observation.witness_output_matches_diagonal
            and equation_observation.diagonal_instance_code_length
            == len(witness_output_code)
        ),
        closure_observation_matches_bridge=(
            closure.bridge_id == equation_bridge.bridge_id
            and closure.bridge_matches_diagonal_instance
            and closure.diagonal_instance_code_length == len(witness_output_code)
        ),
        correctness_cases_accepted=correctness_cases_accepted,
        witness_output_closed=(witness_observation.output_free_variables == ()),
    )


def _validate_bridge(
    bridge: FixedPointSubstitutionWitnessBridge,
    expected_witness_output_length: int,
) -> list[FixedPointSubstitutionWitnessBridgeValidation]:
    subject = bridge.bridge_id
    results: list[FixedPointSubstitutionWitnessBridgeValidation] = []
    if bridge.witness_output_code_length != expected_witness_output_length:
        results.append(
            _rejected(
                f"{subject}.length",
                "witness output length mismatch: expected "
                + str(expected_witness_output_length)
                + " got "
                + str(bridge.witness_output_code_length),
            )
        )
    else:
        results.append(_accepted(f"{subject}.length", "witness output length is current"))

    bool_checks = (
        ("route", bridge.route_ids_match, "route ids match"),
        ("self_application", bridge.self_application_inputs_match, "self-application inputs match"),
        ("seed", bridge.seed_code_matches_witness_formula, "seed code matches witness"),
        ("output", bridge.witness_output_matches_diagonal_instance, "witness output matches diagonal instance"),
        ("equation_bridge", bridge.bridge_observation_matches_witness, "equation bridge matches witness"),
        ("closure", bridge.closure_observation_matches_bridge, "closure matches bridge"),
        ("correctness_cases", bridge.correctness_cases_accepted, "correctness cases accepted"),
        ("closed_output", bridge.witness_output_closed, "witness output is closed"),
    )
    for suffix, accepted, detail in bool_checks:
        if accepted:
            results.append(_accepted(f"{subject}.{suffix}", detail))
        else:
            results.append(_rejected(f"{subject}.{suffix}", detail + " failed"))
    return results


def _bridge_payload(bridge: FixedPointSubstitutionWitnessBridge) -> dict[str, Any]:
    return {
        "bridge_id": bridge.bridge_id,
        "source_kind": bridge.source_kind,
        "target_id": bridge.target_id,
        "construction_id": bridge.construction_id,
        "witness_id": bridge.witness_id,
        "equation_bridge_id": bridge.equation_bridge_id,
        "closure_id": bridge.closure_id,
        "formula_code_length": bridge.formula_code_length,
        "argument_code_length": bridge.argument_code_length,
        "observed_witness_output_code_length": bridge.witness_output_code_length,
        "observed_route_ids_match": bridge.route_ids_match,
        "observed_self_application_inputs_match": bridge.self_application_inputs_match,
        "observed_seed_code_matches_witness_formula": (
            bridge.seed_code_matches_witness_formula
        ),
        "observed_witness_output_matches_diagonal_instance": (
            bridge.witness_output_matches_diagonal_instance
        ),
        "observed_bridge_observation_matches_witness": (
            bridge.bridge_observation_matches_witness
        ),
        "observed_closure_observation_matches_bridge": (
            bridge.closure_observation_matches_bridge
        ),
        "observed_correctness_cases_accepted": bridge.correctness_cases_accepted,
        "observed_witness_output_closed": bridge.witness_output_closed,
    }


def _find_by_id(items: tuple[Any, ...], id_attr: str, expected_id: str) -> Any:
    for item in items:
        if getattr(item, id_attr) == expected_id:
            return item
    raise ValueError(f"missing {id_attr}: {expected_id}")


def _failed_subject_for_result(subject: str) -> str:
    if subject == "bridge_count":
        return "fixed-point-substitution-witness-bridge-count"
    if subject.endswith(".length"):
        return "fixed-point-substitution-witness-bridge-length"
    if subject == "non_claims":
        return "fixed-point-substitution-witness-bridge-non-claim"
    if subject == "required_future_work":
        return "fixed-point-substitution-witness-bridge-future-work"
    if subject == "required_source_kinds":
        return "fixed-point-substitution-witness-bridge-source-kind"
    if subject == "next_as_action":
        return "fixed-point-substitution-witness-bridge-next-action"
    if subject.endswith("_path"):
        return "fixed-point-substitution-witness-bridge-reference"
    if subject in {
        "codebook",
        "fixed_point",
        "diagonal_construction",
        "substitution_representability",
        "substitution_graph_correctness_cases",
        "fixed_point_equation_bridge",
        "diagonal_instance_closure",
    }:
        return "fixed-point-substitution-witness-bridge-dependency"
    return "fixed-point-substitution-witness-bridge"


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
) -> FixedPointSubstitutionWitnessBridgeValidation:
    return FixedPointSubstitutionWitnessBridgeValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointSubstitutionWitnessBridgeValidation:
    return FixedPointSubstitutionWitnessBridgeValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_substitution_witness_bridge_cli())
