"""Finite alignment for the fixed-point bridge-equality construction case.

This module checks that the current bridge-equality proof case is aligned with
the checked fixed-point equation bridge, substitution-witness bridge,
substitution graph correctness bridge, and formula-schema witness relation. It
does not prove the bridge equality, lift a fixed-point equation, or establish
self-consistency.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_equation_bridge import (
    FixedPointEquationBridgeObservation,
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)
from autarkic_systems.fixed_point_substitution_graph_correctness_bridge import (
    load_fixed_point_substitution_graph_correctness_bridge,
    validate_fixed_point_substitution_graph_correctness_bridge,
)
from autarkic_systems.fixed_point_substitution_witness_bridge import (
    load_fixed_point_substitution_witness_bridge,
    validate_fixed_point_substitution_witness_bridge,
)
from autarkic_systems.substitution_graph_formula_schema_relation import (
    SubstitutionGraphFormulaSchemaRelationPoint,
    load_substitution_graph_formula_schema_relation,
    validate_substitution_graph_formula_schema_relation,
)


DEFAULT_ALIGNMENT = Path("claims/fixed_point_bridge_equality_alignment.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = ("bridge-equality-alignment",)
REQUIRED_FUTURE_WORK = (
    "bridge-equality-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
REQUIRED_CONSTRUCTION_DEPENDENCIES = {
    "fixed_point_equation_bridge",
    "substitution_representability",
    "substitution_graph_correctness_cases",
    "bridge_equality_alignment",
}
OUTER_FORMULA_WRAPPER_DELTA = 5


@dataclass(frozen=True)
class FixedPointBridgeEqualityAlignmentManifest:
    """Loaded manifest for finite bridge-equality alignment evidence."""

    path: Path
    schema_version: int
    alignment_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_construction_cases_path: str
    fixed_point_equation_bridge_targets_path: str
    substitution_witness_bridge_path: str
    substitution_graph_correctness_bridge_path: str
    formula_schema_relation_path: str
    expected_alignment_count: int
    expected_bridge_equation_code_length: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityAlignmentValidation:
    """One validation result for bridge-equality alignment evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityAlignment:
    """One finite bridge-equality alignment check."""

    alignment_id: str
    source_kind: str
    target_id: str
    construction_case_id: str
    equation_bridge_id: str
    witness_bridge_id: str
    graph_correctness_bridge_id: str
    schema_relation_point_id: str
    bridge_equation_code_length: int
    schema_instance_code_length: int
    bridge_left_term_code_length: int
    witness_output_code_length: int
    bridge_right_term_code_length: int
    direct_target_code_length: int
    construction_case_is_open: bool
    construction_case_requires_alignment: bool
    bridge_equation_matches_schema_instance: bool
    left_term_matches_witness_output_quote: bool
    right_term_quotes_diagonal_instance: bool
    route_ids_match: bool
    all_dependencies_accepted: bool


@dataclass(frozen=True)
class FixedPointBridgeEqualityAlignmentReport:
    """Validation report over finite bridge-equality alignment evidence."""

    manifest: FixedPointBridgeEqualityAlignmentManifest
    fixed_point_construction_cases_path: Path
    fixed_point_equation_bridge_targets_path: Path
    substitution_witness_bridge_path: Path
    substitution_graph_correctness_bridge_path: Path
    formula_schema_relation_path: Path
    willard_map_path: Path
    results: tuple[FixedPointBridgeEqualityAlignmentValidation, ...]
    alignments: tuple[FixedPointBridgeEqualityAlignment, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every bridge-equality alignment validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def alignment_count(self) -> int:
        """Return the number of checked bridge-equality alignments."""

        return len(self.alignments)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed alignment counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for alignment in self.alignments:
            counts[alignment.source_kind] = (
                counts.get(alignment.source_kind, 0) + 1
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


def load_fixed_point_bridge_equality_alignment(
    path: Path | str = DEFAULT_ALIGNMENT,
) -> FixedPointBridgeEqualityAlignmentManifest:
    """Load the bridge-equality alignment manifest from JSON."""

    alignment_path = Path(path)
    data = json.loads(alignment_path.read_text(encoding="utf-8"))
    return FixedPointBridgeEqualityAlignmentManifest(
        path=alignment_path,
        schema_version=_required_int(data, "schema_version"),
        alignment_set_id=_required_text(data, "alignment_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_construction_cases_path=_required_text(
            data,
            "fixed_point_construction_cases_path",
        ),
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        substitution_witness_bridge_path=_required_text(
            data,
            "substitution_witness_bridge_path",
        ),
        substitution_graph_correctness_bridge_path=_required_text(
            data,
            "substitution_graph_correctness_bridge_path",
        ),
        formula_schema_relation_path=_required_text(
            data,
            "formula_schema_relation_path",
        ),
        expected_alignment_count=_required_int(data, "expected_alignment_count"),
        expected_bridge_equation_code_length=_required_int(
            data,
            "expected_bridge_equation_code_length",
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_bridge_equality_alignment(
    manifest: FixedPointBridgeEqualityAlignmentManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointBridgeEqualityAlignmentReport:
    """Validate finite bridge-equality alignment evidence."""

    checked_willard_map_path = Path(willard_map_path)
    checked_construction_cases_path = Path(manifest.fixed_point_construction_cases_path)
    checked_equation_bridge_path = Path(
        manifest.fixed_point_equation_bridge_targets_path
    )
    checked_witness_bridge_path = Path(manifest.substitution_witness_bridge_path)
    checked_graph_bridge_path = Path(
        manifest.substitution_graph_correctness_bridge_path
    )
    checked_schema_relation_path = Path(manifest.formula_schema_relation_path)

    construction_cases = load_fixed_point_construction_cases(
        checked_construction_cases_path
    )
    equation_bridge = load_fixed_point_equation_bridge_targets(
        checked_equation_bridge_path
    )
    equation_bridge_report = validate_fixed_point_equation_bridge_targets(
        equation_bridge,
        willard_map_path=checked_willard_map_path,
    )
    witness_bridge = load_fixed_point_substitution_witness_bridge(
        checked_witness_bridge_path
    )
    witness_bridge_report = validate_fixed_point_substitution_witness_bridge(
        witness_bridge,
        checked_willard_map_path,
    )
    graph_bridge = load_fixed_point_substitution_graph_correctness_bridge(
        checked_graph_bridge_path
    )
    graph_bridge_report = validate_fixed_point_substitution_graph_correctness_bridge(
        graph_bridge,
        checked_willard_map_path,
    )
    schema_relation = load_substitution_graph_formula_schema_relation(
        checked_schema_relation_path
    )
    schema_relation_report = validate_substitution_graph_formula_schema_relation(
        schema_relation,
        checked_willard_map_path,
    )

    results: list[FixedPointBridgeEqualityAlignmentValidation] = [
        _accepted("manifest", f"loaded {manifest.alignment_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(_validate_manifest_lists(manifest))
    results.extend(
        _validate_dependency_reports(
            equation_bridge_report,
            witness_bridge_report,
            graph_bridge_report,
            schema_relation_report,
        )
    )

    alignments: tuple[FixedPointBridgeEqualityAlignment, ...] = ()
    try:
        alignments = _derive_alignments(
            construction_cases,
            equation_bridge_report.accepted,
            equation_bridge_report.observations,
            witness_bridge_report.accepted,
            witness_bridge_report.bridges,
            graph_bridge_report.accepted,
            graph_bridge_report.bridges,
            schema_relation_report.accepted,
            schema_relation_report.relation_points,
        )
    except ValueError as exc:
        results.append(_rejected("alignments", str(exc)))
    results.extend(_validate_alignment_set(manifest, alignments))

    return FixedPointBridgeEqualityAlignmentReport(
        manifest=manifest,
        fixed_point_construction_cases_path=checked_construction_cases_path,
        fixed_point_equation_bridge_targets_path=checked_equation_bridge_path,
        substitution_witness_bridge_path=checked_witness_bridge_path,
        substitution_graph_correctness_bridge_path=checked_graph_bridge_path,
        formula_schema_relation_path=checked_schema_relation_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        alignments=alignments,
    )


def fixed_point_bridge_equality_alignment_payload(
    report: FixedPointBridgeEqualityAlignmentReport,
) -> dict[str, Any]:
    """Return a JSON-ready bridge-equality alignment payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "alignment_manifest": str(report.manifest.path),
        "alignment_set_id": report.manifest.alignment_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "substitution_witness_bridge_path": str(
            report.substitution_witness_bridge_path
        ),
        "substitution_graph_correctness_bridge_path": str(
            report.substitution_graph_correctness_bridge_path
        ),
        "formula_schema_relation_path": str(report.formula_schema_relation_path),
        "willard_map": str(report.willard_map_path),
        "expected_alignment_count": report.manifest.expected_alignment_count,
        "alignment_count": report.alignment_count,
        "expected_bridge_equation_code_length": (
            report.manifest.expected_bridge_equation_code_length
        ),
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "alignments": [
            {
                "alignment_id": alignment.alignment_id,
                "source_kind": alignment.source_kind,
                "target_id": alignment.target_id,
                "construction_case_id": alignment.construction_case_id,
                "equation_bridge_id": alignment.equation_bridge_id,
                "witness_bridge_id": alignment.witness_bridge_id,
                "graph_correctness_bridge_id": (
                    alignment.graph_correctness_bridge_id
                ),
                "schema_relation_point_id": alignment.schema_relation_point_id,
                "observed_bridge_equation_code_length": (
                    alignment.bridge_equation_code_length
                ),
                "observed_schema_instance_code_length": (
                    alignment.schema_instance_code_length
                ),
                "observed_bridge_left_term_code_length": (
                    alignment.bridge_left_term_code_length
                ),
                "observed_witness_output_code_length": (
                    alignment.witness_output_code_length
                ),
                "observed_bridge_right_term_code_length": (
                    alignment.bridge_right_term_code_length
                ),
                "observed_direct_target_code_length": (
                    alignment.direct_target_code_length
                ),
                "observed_construction_case_is_open": (
                    alignment.construction_case_is_open
                ),
                "observed_construction_case_requires_alignment": (
                    alignment.construction_case_requires_alignment
                ),
                "observed_bridge_equation_matches_schema_instance": (
                    alignment.bridge_equation_matches_schema_instance
                ),
                "observed_left_term_matches_witness_output_quote": (
                    alignment.left_term_matches_witness_output_quote
                ),
                "observed_right_term_quotes_diagonal_instance": (
                    alignment.right_term_quotes_diagonal_instance
                ),
                "observed_route_ids_match": alignment.route_ids_match,
                "observed_all_dependencies_accepted": (
                    alignment.all_dependencies_accepted
                ),
            }
            for alignment in report.alignments
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


def format_fixed_point_bridge_equality_alignment_report(
    report: FixedPointBridgeEqualityAlignmentReport,
) -> str:
    """Format a concise bridge-equality alignment report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        alignment.alignment_id
        for alignment in report.alignments
        if not _alignment_accepted(alignment)
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Fixed-point bridge equality alignment: {status}",
        f"Alignment set: {report.manifest.alignment_set_id}",
        f"Bridge-equality alignments: {report.alignment_count}",
        f"Source kinds: {source_counts}",
        f"Alignment failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_bridge_equality_alignment_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite bridge-equality alignment validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_bridge_equality_alignment",
        description="Validate AS fixed-point bridge-equality alignment evidence.",
    )
    parser.add_argument(
        "--alignment",
        default=str(DEFAULT_ALIGNMENT),
        help="Path to the bridge-equality alignment manifest.",
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

    manifest = load_fixed_point_bridge_equality_alignment(args.alignment)
    report = validate_fixed_point_bridge_equality_alignment(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            fixed_point_bridge_equality_alignment_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_fixed_point_bridge_equality_alignment_report(report))
    return 0 if report.accepted else 1


def _derive_alignments(
    construction_cases: Any,
    equation_bridge_accepted: bool,
    equation_observations: tuple[FixedPointEquationBridgeObservation, ...],
    witness_bridge_accepted: bool,
    witness_bridges: tuple[Any, ...],
    graph_bridge_accepted: bool,
    graph_bridges: tuple[Any, ...],
    schema_relation_accepted: bool,
    schema_relation_points: tuple[SubstitutionGraphFormulaSchemaRelationPoint, ...],
) -> tuple[FixedPointBridgeEqualityAlignment, ...]:
    construction_case = _find_case(construction_cases.cases, "bridge-equality-proof")
    equation_observation = _first_or_none(equation_observations)
    witness_bridge = _first_or_none(witness_bridges)
    graph_bridge = _first_or_none(graph_bridges)
    if equation_observation is None:
        raise ValueError("missing fixed-point equation bridge observation")
    if witness_bridge is None:
        raise ValueError("missing substitution witness bridge")
    if graph_bridge is None:
        raise ValueError("missing graph correctness bridge")
    relation_point = _find_witness_relation(
        schema_relation_points,
        equation_observation.witness_id,
    )
    route_ids_match = (
        construction_case.target_id
        == equation_observation.target_id
        == witness_bridge.target_id
        == graph_bridge.fixed_point_target_id
        and equation_observation.bridge_id == witness_bridge.equation_bridge_id
        and equation_observation.witness_id == witness_bridge.witness_id
        and relation_point.source_id == witness_bridge.witness_id
    )
    dependencies_accepted = (
        equation_bridge_accepted
        and witness_bridge_accepted
        and graph_bridge_accepted
        and schema_relation_accepted
    )
    return (
        FixedPointBridgeEqualityAlignment(
            alignment_id="AS-FIXED-POINT-BRIDGE-EQUALITY-ALIGNMENT",
            source_kind="bridge-equality-alignment",
            target_id=construction_case.target_id,
            construction_case_id=construction_case.case_id,
            equation_bridge_id=equation_observation.bridge_id,
            witness_bridge_id=witness_bridge.bridge_id,
            graph_correctness_bridge_id=graph_bridge.bridge_id,
            schema_relation_point_id=relation_point.point_id,
            bridge_equation_code_length=(
                equation_observation.bridge_equation_code_length
            ),
            schema_instance_code_length=relation_point.schema_instance_code_length,
            bridge_left_term_code_length=(
                equation_observation.bridge_left_term_code_length
            ),
            witness_output_code_length=witness_bridge.witness_output_code_length,
            bridge_right_term_code_length=(
                equation_observation.bridge_right_term_code_length
            ),
            direct_target_code_length=equation_observation.direct_target_code_length,
            construction_case_is_open=construction_case.status == "proof-case-open",
            construction_case_requires_alignment=(
                REQUIRED_CONSTRUCTION_DEPENDENCIES.issubset(
                    set(construction_case.required_dependency_subjects)
                )
            ),
            bridge_equation_matches_schema_instance=(
                equation_observation.bridge_equation_closed
                and relation_point.schema_instance_closed
                and equation_observation.bridge_equation_code_length
                == relation_point.schema_instance_code_length
            ),
            left_term_matches_witness_output_quote=(
                equation_observation.bridge_left_term_code_length
                + OUTER_FORMULA_WRAPPER_DELTA
                == witness_bridge.witness_output_code_length
                == relation_point.output_code_length
            ),
            right_term_quotes_diagonal_instance=(
                equation_observation.direct_slot_quotes_diagonal_instance
                and equation_observation.bridge_right_term_code_length
                + OUTER_FORMULA_WRAPPER_DELTA
                == equation_observation.direct_target_code_length
            ),
            route_ids_match=route_ids_match,
            all_dependencies_accepted=dependencies_accepted,
        ),
    )


def _validate_references(
    manifest: FixedPointBridgeEqualityAlignmentManifest,
) -> list[FixedPointBridgeEqualityAlignmentValidation]:
    expected = (
        (
            "fixed_point_construction_cases_path",
            manifest.fixed_point_construction_cases_path,
            "claims/fixed_point_construction_cases.json",
        ),
        (
            "fixed_point_equation_bridge_targets_path",
            manifest.fixed_point_equation_bridge_targets_path,
            "claims/fixed_point_equation_bridge_targets.json",
        ),
        (
            "substitution_witness_bridge_path",
            manifest.substitution_witness_bridge_path,
            "claims/fixed_point_substitution_witness_bridge.json",
        ),
        (
            "substitution_graph_correctness_bridge_path",
            manifest.substitution_graph_correctness_bridge_path,
            "claims/fixed_point_substitution_graph_correctness_bridge.json",
        ),
        (
            "formula_schema_relation_path",
            manifest.formula_schema_relation_path,
            "claims/substitution_graph_formula_schema_relation.json",
        ),
    )
    results: list[FixedPointBridgeEqualityAlignmentValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_manifest_lists(
    manifest: FixedPointBridgeEqualityAlignmentManifest,
) -> list[FixedPointBridgeEqualityAlignmentValidation]:
    results: list[FixedPointBridgeEqualityAlignmentValidation] = []
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
    equation_bridge_report: Any,
    witness_bridge_report: Any,
    graph_bridge_report: Any,
    schema_relation_report: Any,
) -> list[FixedPointBridgeEqualityAlignmentValidation]:
    checks = (
        (
            "fixed_point_equation_bridge",
            equation_bridge_report,
            "fixed-point equation bridge",
        ),
        (
            "substitution_witness_bridge",
            witness_bridge_report,
            "fixed-point substitution witness bridge",
        ),
        (
            "substitution_graph_correctness_bridge",
            graph_bridge_report,
            "fixed-point substitution graph correctness bridge",
        ),
        (
            "formula_schema_relation",
            schema_relation_report,
            "substitution graph formula-schema relation",
        ),
    )
    results: list[FixedPointBridgeEqualityAlignmentValidation] = []
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


def _validate_alignment_set(
    manifest: FixedPointBridgeEqualityAlignmentManifest,
    alignments: tuple[FixedPointBridgeEqualityAlignment, ...],
) -> list[FixedPointBridgeEqualityAlignmentValidation]:
    results: list[FixedPointBridgeEqualityAlignmentValidation] = []
    if len(alignments) == manifest.expected_alignment_count:
        results.append(
            _accepted(
                "expected_alignment_count",
                f"alignment count {len(alignments)} matches manifest",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_alignment_count",
                "alignment count mismatch: expected "
                f"{manifest.expected_alignment_count} but found {len(alignments)}",
            )
        )

    if len(alignments) != 1:
        return results
    alignment = alignments[0]
    if (
        alignment.bridge_equation_code_length
        == manifest.expected_bridge_equation_code_length
    ):
        results.append(
            _accepted(
                "expected_bridge_equation_code_length",
                "bridge equation length matches manifest",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_bridge_equation_code_length",
                "bridge equation length mismatch: expected "
                f"{manifest.expected_bridge_equation_code_length} but found "
                f"{alignment.bridge_equation_code_length}",
            )
        )

    bool_checks = (
        (
            "alignment.construction_case_is_open",
            alignment.construction_case_is_open,
            "construction case remains open",
            "construction case is not open",
        ),
        (
            "alignment.construction_case_requires_alignment",
            alignment.construction_case_requires_alignment,
            "construction case requires bridge-equality alignment",
            "construction case does not require bridge-equality alignment",
        ),
        (
            "alignment.bridge_equation_matches_schema_instance",
            alignment.bridge_equation_matches_schema_instance,
            "bridge equation and schema instance lengths align",
            "bridge equation and schema instance lengths diverge",
        ),
        (
            "alignment.left_term_matches_witness_output_quote",
            alignment.left_term_matches_witness_output_quote,
            "left bridge term matches witness output quote boundary",
            "left bridge term does not match witness output quote boundary",
        ),
        (
            "alignment.right_term_quotes_diagonal_instance",
            alignment.right_term_quotes_diagonal_instance,
            "right bridge term quotes the diagonal instance",
            "right bridge term does not quote the diagonal instance",
        ),
        (
            "alignment.route_ids_match",
            alignment.route_ids_match,
            "target and witness route ids match",
            "target or witness route ids diverge",
        ),
        (
            "alignment.all_dependencies_accepted",
            alignment.all_dependencies_accepted,
            "all dependency surfaces accepted",
            "one or more dependency surfaces rejected",
        ),
    )
    for subject, accepted, ok_detail, fail_detail in bool_checks:
        if accepted:
            results.append(_accepted(subject, ok_detail))
        else:
            results.append(_rejected(subject, fail_detail))
    return results


def _alignment_accepted(alignment: FixedPointBridgeEqualityAlignment) -> bool:
    return (
        alignment.construction_case_is_open
        and alignment.construction_case_requires_alignment
        and alignment.bridge_equation_matches_schema_instance
        and alignment.left_term_matches_witness_output_quote
        and alignment.right_term_quotes_diagonal_instance
        and alignment.route_ids_match
        and alignment.all_dependencies_accepted
    )


def _find_case(cases: tuple[Any, ...], case_kind: str) -> Any:
    for case in cases:
        if case.case_kind == case_kind:
            return case
    raise ValueError(f"missing construction case kind: {case_kind}")


def _find_witness_relation(
    points: tuple[SubstitutionGraphFormulaSchemaRelationPoint, ...],
    witness_id: str,
) -> SubstitutionGraphFormulaSchemaRelationPoint:
    for point in points:
        if point.source_kind == "witness-instance" and point.source_id == witness_id:
            return point
    raise ValueError(f"missing witness formula-schema relation point: {witness_id}")


def _first_or_none(items: tuple[Any, ...]) -> Any | None:
    if not items:
        return None
    return items[0]


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointBridgeEqualityAlignmentValidation:
    return FixedPointBridgeEqualityAlignmentValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointBridgeEqualityAlignmentValidation:
    return FixedPointBridgeEqualityAlignmentValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_alignment_count":
        return "fixed-point-bridge-equality-alignment-count"
    if subject == "expected_bridge_equation_code_length":
        return "fixed-point-bridge-equality-alignment-length"
    if subject == "non_claims":
        return "fixed-point-bridge-equality-alignment-non-claim"
    if subject == "required_future_work":
        return "fixed-point-bridge-equality-alignment-future-work"
    if subject == "required_source_kinds":
        return "fixed-point-bridge-equality-alignment-source-kind"
    if subject == "next_as_action":
        return "fixed-point-bridge-equality-alignment-next-action"
    if subject == "alignments":
        return "fixed-point-bridge-equality-alignment-derivation"
    if subject.startswith("alignment."):
        return "fixed-point-bridge-equality-alignment-check"
    if subject.endswith("_path"):
        return "fixed-point-bridge-equality-alignment-path"
    return subject


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return value


def _joined_or_none(items: tuple[str, ...]) -> str:
    if not items:
        return "none"
    return ", ".join(items)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_bridge_equality_alignment_cli())
