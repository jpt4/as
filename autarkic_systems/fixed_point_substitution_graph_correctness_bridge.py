"""Finite bridge for the fixed-point substitution graph correctness case.

The fixed-point construction case map now has a case for proving substitution
graph correctness. This module checks that the open construction case is
aligned with the accepted substitution graph correctness target, the accepted
case map beneath it, and the five finite graph-domain dependency surfaces
already checked by prior ADRs. It does not prove graph correctness, bridge
equality, a fixed-point equation, or self-consistency.
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
from autarkic_systems.substitution_graph_codebook_roundtrip import (
    load_substitution_graph_codebook_roundtrip,
    validate_substitution_graph_codebook_roundtrip,
)
from autarkic_systems.substitution_graph_correctness import (
    load_substitution_graph_correctness_targets,
    validate_substitution_graph_correctness_targets,
)
from autarkic_systems.substitution_graph_correctness_cases import (
    load_substitution_graph_correctness_cases,
    validate_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_graph_diagonal_witness_composition import (
    load_substitution_graph_diagonal_witness_composition,
    validate_substitution_graph_diagonal_witness_composition,
)
from autarkic_systems.substitution_graph_formula_schema_relation import (
    load_substitution_graph_formula_schema_relation,
    validate_substitution_graph_formula_schema_relation,
)
from autarkic_systems.substitution_graph_meta_substitution_semantics import (
    load_substitution_graph_meta_substitution_semantics,
    validate_substitution_graph_meta_substitution_semantics,
)
from autarkic_systems.substitution_graph_quotation_term_closure import (
    load_substitution_graph_quotation_term_closure,
    validate_substitution_graph_quotation_term_closure,
)


DEFAULT_BRIDGE = Path("claims/fixed_point_substitution_graph_correctness_bridge.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = ("graph-correctness-bridge",)
REQUIRED_CORRECTNESS_CASE_KINDS = (
    "codebook-roundtrip",
    "quotation-term-closure",
    "meta-substitution-semantics",
    "formula-schema-relation",
    "diagonal-witness-composition",
)
REQUIRED_FINITE_DEPENDENCY_SUBJECTS = (
    "codebook_roundtrip",
    "quotation_term_closure",
    "meta_substitution_semantics",
    "formula_schema_relation",
    "diagonal_witness_composition",
)
REQUIRED_FUTURE_WORK = (
    "substitution-graph-correctness-proof",
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


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessBridgeManifest:
    """Loaded manifest for finite graph-correctness bridge evidence."""

    path: Path
    schema_version: int
    bridge_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_construction_cases_path: str
    substitution_graph_correctness_targets_path: str
    substitution_graph_correctness_cases_path: str
    codebook_roundtrip_path: str
    quotation_term_closure_path: str
    meta_substitution_semantics_path: str
    formula_schema_relation_path: str
    diagonal_witness_composition_path: str
    expected_bridge_count: int
    expected_correctness_case_count: int
    required_source_kinds: tuple[str, ...]
    required_correctness_case_kinds: tuple[str, ...]
    required_finite_dependency_subjects: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessBridgeValidation:
    """One validation result for graph-correctness bridge evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessBridge:
    """One finite construction-to-graph-correctness alignment point."""

    bridge_id: str
    source_kind: str
    fixed_point_target_id: str
    construction_case_id: str
    correctness_target_id: str
    correctness_case_set_id: str
    correctness_case_count: int
    finite_dependency_count: int
    construction_case_is_open: bool
    construction_case_requires_correctness: bool
    correctness_target_accepted: bool
    correctness_cases_accepted: bool
    all_correctness_case_kinds_present: bool
    all_finite_dependencies_accepted: bool
    diagonal_composition_links_target: bool


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessBridgeReport:
    """Validation report over finite graph-correctness bridge evidence."""

    manifest: FixedPointSubstitutionGraphCorrectnessBridgeManifest
    fixed_point_construction_cases_path: Path
    substitution_graph_correctness_targets_path: Path
    substitution_graph_correctness_cases_path: Path
    codebook_roundtrip_path: Path
    quotation_term_closure_path: Path
    meta_substitution_semantics_path: Path
    formula_schema_relation_path: Path
    diagonal_witness_composition_path: Path
    willard_map_path: Path
    results: tuple[FixedPointSubstitutionGraphCorrectnessBridgeValidation, ...]
    bridges: tuple[FixedPointSubstitutionGraphCorrectnessBridge, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every graph-correctness bridge validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def bridge_count(self) -> int:
        """Return the number of checked graph-correctness bridges."""

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


def load_fixed_point_substitution_graph_correctness_bridge(
    path: Path | str = DEFAULT_BRIDGE,
) -> FixedPointSubstitutionGraphCorrectnessBridgeManifest:
    """Load the graph-correctness bridge manifest from JSON."""

    bridge_path = Path(path)
    data = json.loads(bridge_path.read_text(encoding="utf-8"))
    return FixedPointSubstitutionGraphCorrectnessBridgeManifest(
        path=bridge_path,
        schema_version=_required_int(data, "schema_version"),
        bridge_set_id=_required_text(data, "bridge_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_construction_cases_path=_required_text(
            data,
            "fixed_point_construction_cases_path",
        ),
        substitution_graph_correctness_targets_path=_required_text(
            data,
            "substitution_graph_correctness_targets_path",
        ),
        substitution_graph_correctness_cases_path=_required_text(
            data,
            "substitution_graph_correctness_cases_path",
        ),
        codebook_roundtrip_path=_required_text(data, "codebook_roundtrip_path"),
        quotation_term_closure_path=_required_text(
            data,
            "quotation_term_closure_path",
        ),
        meta_substitution_semantics_path=_required_text(
            data,
            "meta_substitution_semantics_path",
        ),
        formula_schema_relation_path=_required_text(
            data,
            "formula_schema_relation_path",
        ),
        diagonal_witness_composition_path=_required_text(
            data,
            "diagonal_witness_composition_path",
        ),
        expected_bridge_count=_required_int(data, "expected_bridge_count"),
        expected_correctness_case_count=_required_int(
            data,
            "expected_correctness_case_count",
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_correctness_case_kinds=tuple(
            _required_text_list(data, "required_correctness_case_kinds")
        ),
        required_finite_dependency_subjects=tuple(
            _required_text_list(data, "required_finite_dependency_subjects")
        ),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_substitution_graph_correctness_bridge(
    manifest: FixedPointSubstitutionGraphCorrectnessBridgeManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSubstitutionGraphCorrectnessBridgeReport:
    """Validate finite graph-correctness bridge evidence."""

    checked_willard_map_path = Path(willard_map_path)
    checked_construction_cases_path = Path(manifest.fixed_point_construction_cases_path)
    checked_correctness_path = Path(
        manifest.substitution_graph_correctness_targets_path
    )
    checked_correctness_cases_path = Path(
        manifest.substitution_graph_correctness_cases_path
    )
    checked_roundtrip_path = Path(manifest.codebook_roundtrip_path)
    checked_closure_path = Path(manifest.quotation_term_closure_path)
    checked_meta_substitution_path = Path(manifest.meta_substitution_semantics_path)
    checked_schema_relation_path = Path(manifest.formula_schema_relation_path)
    checked_diagonal_composition_path = Path(
        manifest.diagonal_witness_composition_path
    )

    construction_cases = load_fixed_point_construction_cases(
        checked_construction_cases_path
    )
    correctness_targets = load_substitution_graph_correctness_targets(
        checked_correctness_path
    )
    correctness_report = validate_substitution_graph_correctness_targets(
        correctness_targets,
        checked_willard_map_path,
    )
    correctness_cases = load_substitution_graph_correctness_cases(
        checked_correctness_cases_path
    )
    correctness_case_report = validate_substitution_graph_correctness_cases(
        correctness_cases,
        checked_willard_map_path,
    )
    roundtrip_manifest = load_substitution_graph_codebook_roundtrip(
        checked_roundtrip_path
    )
    roundtrip_report = validate_substitution_graph_codebook_roundtrip(
        roundtrip_manifest,
        checked_willard_map_path,
    )
    closure_manifest = load_substitution_graph_quotation_term_closure(
        checked_closure_path
    )
    closure_report = validate_substitution_graph_quotation_term_closure(
        closure_manifest,
        checked_willard_map_path,
    )
    meta_substitution_manifest = load_substitution_graph_meta_substitution_semantics(
        checked_meta_substitution_path
    )
    meta_substitution_report = validate_substitution_graph_meta_substitution_semantics(
        meta_substitution_manifest,
        checked_willard_map_path,
    )
    schema_relation_manifest = load_substitution_graph_formula_schema_relation(
        checked_schema_relation_path
    )
    schema_relation_report = validate_substitution_graph_formula_schema_relation(
        schema_relation_manifest,
        checked_willard_map_path,
    )
    diagonal_composition_manifest = (
        load_substitution_graph_diagonal_witness_composition(
            checked_diagonal_composition_path
        )
    )
    diagonal_composition_report = (
        validate_substitution_graph_diagonal_witness_composition(
            diagonal_composition_manifest,
            checked_willard_map_path,
        )
    )

    results: list[FixedPointSubstitutionGraphCorrectnessBridgeValidation] = [
        _accepted("manifest", f"loaded {manifest.bridge_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(_validate_manifest_lists(manifest))
    results.extend(
        _validate_dependency_reports(
            correctness_report,
            correctness_case_report,
            roundtrip_report,
            closure_report,
            meta_substitution_report,
            schema_relation_report,
            diagonal_composition_report,
        )
    )

    bridges: tuple[FixedPointSubstitutionGraphCorrectnessBridge, ...] = ()
    try:
        bridges = _derive_bridges(
            construction_cases,
            correctness_targets,
            correctness_report.accepted,
            correctness_cases,
            correctness_case_report.accepted,
            roundtrip_report.accepted,
            closure_report.accepted,
            meta_substitution_report.accepted,
            schema_relation_report.accepted,
            diagonal_composition_report.accepted,
            diagonal_composition_report.compositions,
        )
    except ValueError as exc:
        results.append(_rejected("bridges", str(exc)))
    results.extend(_validate_bridge_set(manifest, bridges))

    return FixedPointSubstitutionGraphCorrectnessBridgeReport(
        manifest=manifest,
        fixed_point_construction_cases_path=checked_construction_cases_path,
        substitution_graph_correctness_targets_path=checked_correctness_path,
        substitution_graph_correctness_cases_path=checked_correctness_cases_path,
        codebook_roundtrip_path=checked_roundtrip_path,
        quotation_term_closure_path=checked_closure_path,
        meta_substitution_semantics_path=checked_meta_substitution_path,
        formula_schema_relation_path=checked_schema_relation_path,
        diagonal_witness_composition_path=checked_diagonal_composition_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        bridges=bridges,
    )


def fixed_point_substitution_graph_correctness_bridge_payload(
    report: FixedPointSubstitutionGraphCorrectnessBridgeReport,
) -> dict[str, Any]:
    """Return a JSON-ready graph-correctness bridge payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "bridge_manifest": str(report.manifest.path),
        "bridge_set_id": report.manifest.bridge_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "substitution_graph_correctness_targets_path": str(
            report.substitution_graph_correctness_targets_path
        ),
        "substitution_graph_correctness_cases_path": str(
            report.substitution_graph_correctness_cases_path
        ),
        "codebook_roundtrip_path": str(report.codebook_roundtrip_path),
        "quotation_term_closure_path": str(report.quotation_term_closure_path),
        "meta_substitution_semantics_path": str(
            report.meta_substitution_semantics_path
        ),
        "formula_schema_relation_path": str(report.formula_schema_relation_path),
        "diagonal_witness_composition_path": str(
            report.diagonal_witness_composition_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_bridge_count": report.manifest.expected_bridge_count,
        "bridge_count": report.bridge_count,
        "expected_correctness_case_count": (
            report.manifest.expected_correctness_case_count
        ),
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_correctness_case_kinds": list(
            report.manifest.required_correctness_case_kinds
        ),
        "required_finite_dependency_subjects": list(
            report.manifest.required_finite_dependency_subjects
        ),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "bridges": [
            {
                "bridge_id": bridge.bridge_id,
                "source_kind": bridge.source_kind,
                "fixed_point_target_id": bridge.fixed_point_target_id,
                "construction_case_id": bridge.construction_case_id,
                "correctness_target_id": bridge.correctness_target_id,
                "correctness_case_set_id": bridge.correctness_case_set_id,
                "observed_correctness_case_count": (
                    bridge.correctness_case_count
                ),
                "observed_finite_dependency_count": (
                    bridge.finite_dependency_count
                ),
                "observed_construction_case_is_open": (
                    bridge.construction_case_is_open
                ),
                "observed_construction_case_requires_correctness": (
                    bridge.construction_case_requires_correctness
                ),
                "observed_correctness_target_accepted": (
                    bridge.correctness_target_accepted
                ),
                "observed_correctness_cases_accepted": (
                    bridge.correctness_cases_accepted
                ),
                "observed_all_correctness_case_kinds_present": (
                    bridge.all_correctness_case_kinds_present
                ),
                "observed_all_finite_dependencies_accepted": (
                    bridge.all_finite_dependencies_accepted
                ),
                "observed_diagonal_composition_links_target": (
                    bridge.diagonal_composition_links_target
                ),
            }
            for bridge in report.bridges
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


def format_fixed_point_substitution_graph_correctness_bridge_report(
    report: FixedPointSubstitutionGraphCorrectnessBridgeReport,
) -> str:
    """Format a concise graph-correctness bridge report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        bridge.bridge_id for bridge in report.bridges if not _bridge_accepted(bridge)
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Fixed-point substitution graph correctness bridge: {status}",
        f"Bridge set: {report.manifest.bridge_set_id}",
        f"Graph-correctness bridges: {report.bridge_count}",
        f"Source kinds: {source_counts}",
        f"Bridge failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_substitution_graph_correctness_bridge_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite graph-correctness bridge validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_substitution_graph_correctness_bridge"
        ),
        description="Validate fixed-point substitution graph correctness bridge.",
    )
    parser.add_argument(
        "--bridge",
        default=str(DEFAULT_BRIDGE),
        help="Path to the graph-correctness bridge manifest.",
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

    manifest = load_fixed_point_substitution_graph_correctness_bridge(args.bridge)
    report = validate_fixed_point_substitution_graph_correctness_bridge(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            fixed_point_substitution_graph_correctness_bridge_payload(report),
            sort_keys=True,
        ))
    else:
        print(format_fixed_point_substitution_graph_correctness_bridge_report(report))
    return 0 if report.accepted else 1


def _derive_bridges(
    construction_cases: Any,
    correctness_targets: Any,
    correctness_target_accepted: bool,
    correctness_cases: Any,
    correctness_cases_accepted: bool,
    roundtrip_accepted: bool,
    closure_accepted: bool,
    meta_substitution_accepted: bool,
    schema_relation_accepted: bool,
    diagonal_composition_accepted: bool,
    diagonal_compositions: tuple[Any, ...],
) -> tuple[FixedPointSubstitutionGraphCorrectnessBridge, ...]:
    construction_case = _find_case(
        construction_cases.cases,
        "substitution-graph-correctness-proof",
    )
    correctness_target = _first_or_none(correctness_targets.targets)
    diagonal_composition = _first_or_none(diagonal_compositions)
    correctness_target_id = ""
    if correctness_target is not None:
        correctness_target_id = correctness_target.target_id
    fixed_point_target_id = construction_case.target_id
    if diagonal_composition is not None:
        fixed_point_target_id = diagonal_composition.fixed_point_target_id

    required_dependencies = {
        "substitution_graph_correctness",
        "substitution_graph_correctness_cases",
        "substitution_graph_correctness_bridge",
    }
    observed_case_kinds = tuple(case.case_kind for case in correctness_cases.cases)
    finite_dependency_statuses = (
        roundtrip_accepted,
        closure_accepted,
        meta_substitution_accepted,
        schema_relation_accepted,
        diagonal_composition_accepted,
    )
    return (
        FixedPointSubstitutionGraphCorrectnessBridge(
            bridge_id="AS-FIXED-POINT-SUBSTITUTION-GRAPH-CORRECTNESS-BRIDGE",
            source_kind="graph-correctness-bridge",
            fixed_point_target_id=fixed_point_target_id,
            construction_case_id=construction_case.case_id,
            correctness_target_id=correctness_target_id,
            correctness_case_set_id=correctness_cases.case_set_id,
            correctness_case_count=len(correctness_cases.cases),
            finite_dependency_count=sum(1 for accepted in finite_dependency_statuses if accepted),
            construction_case_is_open=construction_case.status == "proof-case-open",
            construction_case_requires_correctness=required_dependencies.issubset(
                set(construction_case.required_dependency_subjects)
            ),
            correctness_target_accepted=correctness_target_accepted,
            correctness_cases_accepted=correctness_cases_accepted,
            all_correctness_case_kinds_present=(
                observed_case_kinds == REQUIRED_CORRECTNESS_CASE_KINDS
            ),
            all_finite_dependencies_accepted=all(finite_dependency_statuses),
            diagonal_composition_links_target=(
                diagonal_composition is not None
                and diagonal_composition.fixed_point_target_id
                == construction_case.target_id
                and diagonal_composition.correctness_target_id
                == correctness_target_id
                and diagonal_composition.target_chain_aligned
            ),
        ),
    )


def _validate_references(
    manifest: FixedPointSubstitutionGraphCorrectnessBridgeManifest,
) -> list[FixedPointSubstitutionGraphCorrectnessBridgeValidation]:
    expected = (
        (
            "fixed_point_construction_cases_path",
            manifest.fixed_point_construction_cases_path,
            "claims/fixed_point_construction_cases.json",
        ),
        (
            "substitution_graph_correctness_targets_path",
            manifest.substitution_graph_correctness_targets_path,
            "claims/substitution_graph_correctness_targets.json",
        ),
        (
            "substitution_graph_correctness_cases_path",
            manifest.substitution_graph_correctness_cases_path,
            "claims/substitution_graph_correctness_cases.json",
        ),
        (
            "codebook_roundtrip_path",
            manifest.codebook_roundtrip_path,
            "claims/substitution_graph_codebook_roundtrip.json",
        ),
        (
            "quotation_term_closure_path",
            manifest.quotation_term_closure_path,
            "claims/substitution_graph_quotation_term_closure.json",
        ),
        (
            "meta_substitution_semantics_path",
            manifest.meta_substitution_semantics_path,
            "claims/substitution_graph_meta_substitution_semantics.json",
        ),
        (
            "formula_schema_relation_path",
            manifest.formula_schema_relation_path,
            "claims/substitution_graph_formula_schema_relation.json",
        ),
        (
            "diagonal_witness_composition_path",
            manifest.diagonal_witness_composition_path,
            "claims/substitution_graph_diagonal_witness_composition.json",
        ),
    )
    results: list[FixedPointSubstitutionGraphCorrectnessBridgeValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_manifest_lists(
    manifest: FixedPointSubstitutionGraphCorrectnessBridgeManifest,
) -> list[FixedPointSubstitutionGraphCorrectnessBridgeValidation]:
    results: list[FixedPointSubstitutionGraphCorrectnessBridgeValidation] = []
    if manifest.required_source_kinds == REQUIRED_SOURCE_KINDS:
        results.append(_accepted("required_source_kinds", "source kinds match"))
    else:
        results.append(_rejected("required_source_kinds", "source kind mismatch"))

    if manifest.required_correctness_case_kinds == REQUIRED_CORRECTNESS_CASE_KINDS:
        results.append(
            _accepted("required_correctness_case_kinds", "case kinds match")
        )
    else:
        results.append(
            _rejected("required_correctness_case_kinds", "case kind mismatch")
        )

    if (
        manifest.required_finite_dependency_subjects
        == REQUIRED_FINITE_DEPENDENCY_SUBJECTS
    ):
        results.append(
            _accepted("required_finite_dependency_subjects", "finite subjects match")
        )
    else:
        results.append(
            _rejected(
                "required_finite_dependency_subjects",
                "finite dependency subject mismatch",
            )
        )

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
    correctness_report: Any,
    correctness_case_report: Any,
    roundtrip_report: Any,
    closure_report: Any,
    meta_substitution_report: Any,
    schema_relation_report: Any,
    diagonal_composition_report: Any,
) -> list[FixedPointSubstitutionGraphCorrectnessBridgeValidation]:
    checks = (
        (
            "substitution_graph_correctness",
            correctness_report,
            "substitution graph correctness target",
        ),
        (
            "substitution_graph_correctness_cases",
            correctness_case_report,
            "substitution graph correctness cases",
        ),
        ("codebook_roundtrip", roundtrip_report, "codebook roundtrip"),
        ("quotation_term_closure", closure_report, "quotation term closure"),
        (
            "meta_substitution_semantics",
            meta_substitution_report,
            "meta-substitution semantics",
        ),
        (
            "formula_schema_relation",
            schema_relation_report,
            "formula-schema relation",
        ),
        (
            "diagonal_witness_composition",
            diagonal_composition_report,
            "diagonal-witness composition",
        ),
    )
    results: list[FixedPointSubstitutionGraphCorrectnessBridgeValidation] = []
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


def _validate_bridge_set(
    manifest: FixedPointSubstitutionGraphCorrectnessBridgeManifest,
    bridges: tuple[FixedPointSubstitutionGraphCorrectnessBridge, ...],
) -> list[FixedPointSubstitutionGraphCorrectnessBridgeValidation]:
    results: list[FixedPointSubstitutionGraphCorrectnessBridgeValidation] = []
    if len(bridges) == manifest.expected_bridge_count:
        results.append(
            _accepted(
                "expected_bridge_count",
                f"bridge count {len(bridges)} matches manifest",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_bridge_count",
                "bridge count mismatch: expected "
                f"{manifest.expected_bridge_count} but found {len(bridges)}",
            )
        )

    if len(bridges) != 1:
        return results
    bridge = bridges[0]
    if bridge.correctness_case_count == manifest.expected_correctness_case_count:
        results.append(
            _accepted(
                "expected_correctness_case_count",
                f"correctness case count {bridge.correctness_case_count} matches",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_correctness_case_count",
                "correctness case count mismatch: expected "
                f"{manifest.expected_correctness_case_count} but found "
                f"{bridge.correctness_case_count}",
            )
        )

    bool_checks = (
        (
            "bridge.construction_case_is_open",
            bridge.construction_case_is_open,
            "construction case remains open",
            "construction case is not open",
        ),
        (
            "bridge.construction_case_requires_correctness",
            bridge.construction_case_requires_correctness,
            "construction case requires correctness bridge",
            "construction case does not require correctness bridge",
        ),
        (
            "bridge.correctness_target_accepted",
            bridge.correctness_target_accepted,
            "correctness target accepted",
            "correctness target rejected",
        ),
        (
            "bridge.correctness_cases_accepted",
            bridge.correctness_cases_accepted,
            "correctness cases accepted",
            "correctness cases rejected",
        ),
        (
            "bridge.all_correctness_case_kinds_present",
            bridge.all_correctness_case_kinds_present,
            "all correctness case kinds present",
            "missing correctness case kinds",
        ),
        (
            "bridge.all_finite_dependencies_accepted",
            bridge.all_finite_dependencies_accepted,
            "all finite dependencies accepted",
            "missing accepted finite dependencies",
        ),
        (
            "bridge.diagonal_composition_links_target",
            bridge.diagonal_composition_links_target,
            "diagonal composition links fixed-point and correctness targets",
            "diagonal composition target link mismatch",
        ),
    )
    for subject, accepted, ok_detail, fail_detail in bool_checks:
        if accepted:
            results.append(_accepted(subject, ok_detail))
        else:
            results.append(_rejected(subject, fail_detail))
    return results


def _bridge_accepted(bridge: FixedPointSubstitutionGraphCorrectnessBridge) -> bool:
    return (
        bridge.construction_case_is_open
        and bridge.construction_case_requires_correctness
        and bridge.correctness_target_accepted
        and bridge.correctness_cases_accepted
        and bridge.all_correctness_case_kinds_present
        and bridge.all_finite_dependencies_accepted
        and bridge.diagonal_composition_links_target
    )


def _find_case(cases: tuple[Any, ...], case_kind: str) -> Any:
    for case in cases:
        if case.case_kind == case_kind:
            return case
    raise ValueError(f"missing construction case kind: {case_kind}")


def _first_or_none(items: tuple[Any, ...]) -> Any | None:
    if not items:
        return None
    return items[0]


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointSubstitutionGraphCorrectnessBridgeValidation:
    return FixedPointSubstitutionGraphCorrectnessBridgeValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointSubstitutionGraphCorrectnessBridgeValidation:
    return FixedPointSubstitutionGraphCorrectnessBridgeValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_bridge_count":
        return "fixed-point-substitution-graph-correctness-bridge-count"
    if subject == "expected_correctness_case_count":
        return "fixed-point-substitution-graph-correctness-bridge-case-count"
    if subject == "non_claims":
        return "fixed-point-substitution-graph-correctness-bridge-non-claim"
    if subject == "required_future_work":
        return "fixed-point-substitution-graph-correctness-bridge-future-work"
    if subject == "required_source_kinds":
        return "fixed-point-substitution-graph-correctness-bridge-source-kind"
    if subject == "required_correctness_case_kinds":
        return "fixed-point-substitution-graph-correctness-bridge-case-kind"
    if subject == "required_finite_dependency_subjects":
        return "fixed-point-substitution-graph-correctness-bridge-finite-subject"
    if subject == "next_as_action":
        return "fixed-point-substitution-graph-correctness-bridge-next-action"
    if subject == "bridges":
        return "fixed-point-substitution-graph-correctness-bridge-derivation"
    if subject.startswith("bridge."):
        return "fixed-point-substitution-graph-correctness-bridge-alignment"
    if subject.endswith("_path"):
        return "fixed-point-substitution-graph-correctness-bridge-path"
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
    raise SystemExit(run_fixed_point_substitution_graph_correctness_bridge_cli())
