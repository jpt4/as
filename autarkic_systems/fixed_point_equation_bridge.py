"""Checked bridge target for the AS fixed-point equation gap.

The diagonal construction builds ``Phi(substitution_code(quote(seed),
quote(seed)))`` while the direct fixed-point target would be
``Phi(quote(diagonal_instance))``. This module makes that gap executable by
checking the shared target skeleton and naming the finite equality that still
has to be proved. It does not prove representability, a fixed-point equation,
or self-consistency.
"""

from __future__ import annotations

import argparse
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
    FixedPointTarget,
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.formal_code import (
    FormalCodebook,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import free_variables, substitute_node
from autarkic_systems.substitution_graph_correctness_cases import (
    load_substitution_graph_correctness_cases,
    validate_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_representability import (
    build_substitution_witness_output_code,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_BRIDGES = Path("claims/fixed_point_equation_bridge_targets.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.2-SELF-JUSTIFYING-GENAC",
)
VALID_BRIDGE_STATUSES = {"bridge-target-open"}
REQUIRED_FUTURE_WORK = (
    "substitution-representability-proof",
    "substitution-graph-correctness-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)


@dataclass(frozen=True)
class FixedPointEquationBridgeTarget:
    """One finite bridge target between diagonal and direct fixed-point forms."""

    bridge_id: str
    target_id: str
    construction_id: str
    witness_id: str
    correctness_case_id: str
    status: str
    expected_diagonal_instance_code_length: int
    expected_diagonal_instance_code_prefix: tuple[int, ...]
    expected_direct_target_code_length: int
    expected_direct_target_code_prefix: tuple[int, ...]
    expected_bridge_equation_code_length: int
    expected_bridge_equation_code_prefix: tuple[int, ...]
    expected_bridge_left_term_code_length: int
    expected_bridge_right_term_code_length: int
    expected_diagonal_equals_direct_target: bool
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointEquationBridgeManifest:
    """Loaded manifest for fixed-point equation bridge targets."""

    path: Path
    schema_version: int
    bridge_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_targets_path: str
    diagonal_construction_targets_path: str
    substitution_representability_targets_path: str
    substitution_graph_correctness_cases_path: str
    codebook_path: str
    willard_anchor_ids: tuple[str, ...]
    bridges: tuple[FixedPointEquationBridgeTarget, ...]


@dataclass(frozen=True)
class FixedPointEquationBridgeValidation:
    """One validation result for a fixed-point equation bridge target."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointEquationBridgeObservation:
    """Observed finite facts for one bridge target."""

    bridge_id: str
    target_id: str
    construction_id: str
    witness_id: str
    status: str
    diagonal_instance_code_length: int
    diagonal_instance_code_prefix: tuple[int, ...]
    direct_target_code_length: int
    direct_target_code_prefix: tuple[int, ...]
    bridge_equation_code_length: int
    bridge_equation_code_prefix: tuple[int, ...]
    bridge_left_term_code_length: int
    bridge_right_term_code_length: int
    diagonal_instance_closed: bool
    direct_target_closed: bool
    bridge_equation_closed: bool
    target_skeleton_matches: bool
    diagonal_slot_is_substitution_code: bool
    direct_slot_quotes_diagonal_instance: bool
    witness_output_matches_diagonal: bool
    diagonal_equals_direct_target: bool


@dataclass(frozen=True)
class FixedPointEquationBridgeReport:
    """Validation report over fixed-point equation bridge targets."""

    manifest: FixedPointEquationBridgeManifest
    fixed_point_targets_path: Path
    diagonal_construction_targets_path: Path
    substitution_representability_targets_path: Path
    substitution_graph_correctness_cases_path: Path
    codebook_path: Path
    formal_language_path: Path
    willard_map_path: Path
    results: tuple[FixedPointEquationBridgeValidation, ...]
    observations: tuple[FixedPointEquationBridgeObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every bridge validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def bridge_count(self) -> int:
        """Return the number of checked bridge targets."""

        return len(self.manifest.bridges)

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


def load_fixed_point_equation_bridge_targets(
    path: Path | str = DEFAULT_BRIDGES,
) -> FixedPointEquationBridgeManifest:
    """Load fixed-point equation bridge targets from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return FixedPointEquationBridgeManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        bridge_set_id=_required_text(data, "bridge_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
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
        codebook_path=_required_text(data, "codebook_path"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        bridges=tuple(_parse_bridge(item) for item in _required_list(data, "bridges")),
    )


def validate_fixed_point_equation_bridge_targets(
    manifest: FixedPointEquationBridgeManifest,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointEquationBridgeReport:
    """Validate fixed-point equation bridge targets and dependencies."""

    checked_language_path = Path(formal_language_path)
    checked_willard_map_path = Path(willard_map_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_diagonal_path = Path(manifest.diagonal_construction_targets_path)
    checked_witness_path = Path(manifest.substitution_representability_targets_path)
    checked_cases_path = Path(manifest.substitution_graph_correctness_cases_path)
    checked_codebook_path = Path(manifest.codebook_path)

    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    fixed_point_targets: Any = None
    diagonal_targets: Any = None
    correctness_cases: Any = None
    codebook: FormalCodebook | None = None
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
        witnesses = load_substitution_representability_targets(checked_witness_path)
        witness_report: Any = validate_substitution_representability_targets(
            witnesses,
            checked_language_path,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        witness_report = _DependencyFailure(False, ("substitution-witness-load",))

    try:
        correctness_cases = load_substitution_graph_correctness_cases(checked_cases_path)
        correctness_case_report: Any = validate_substitution_graph_correctness_cases(
            correctness_cases,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        correctness_case_report = _DependencyFailure(
            False,
            ("substitution-graph-correctness-cases-load",),
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

    results: list[FixedPointEquationBridgeValidation] = [
        _accepted("manifest", f"loaded {len(manifest.bridges)} bridge(s)")
    ]
    observations: list[FixedPointEquationBridgeObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    results.extend(
        _validate_dependency_reports(
            fixed_point_report,
            diagonal_report,
            witness_report,
            correctness_case_report,
            codebook_report,
        )
    )
    dependency_reports = (
        fixed_point_report,
        diagonal_report,
        witness_report,
        correctness_case_report,
        codebook_report,
    )
    if all(report.accepted for report in dependency_reports) and codebook is not None:
        bridge_results, observations = _validate_bridges(
            manifest.bridges,
            fixed_point_targets.targets,
            diagonal_targets.constructions,
            correctness_cases.cases,
            checked_diagonal_path,
            checked_fixed_point_path,
            checked_witness_path,
            checked_codebook_path,
            codebook,
        )
        results.extend(bridge_results)

    return FixedPointEquationBridgeReport(
        manifest=manifest,
        fixed_point_targets_path=checked_fixed_point_path,
        diagonal_construction_targets_path=checked_diagonal_path,
        substitution_representability_targets_path=checked_witness_path,
        substitution_graph_correctness_cases_path=checked_cases_path,
        codebook_path=checked_codebook_path,
        formal_language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def fixed_point_equation_bridge_payload(
    report: FixedPointEquationBridgeReport,
) -> dict[str, Any]:
    """Return a JSON-ready fixed-point equation bridge payload."""

    observations = {observation.bridge_id: observation for observation in report.observations}
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "bridge_manifest": str(report.manifest.path),
        "bridge_set_id": report.manifest.bridge_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
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
        "codebook_path": str(report.codebook_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
        "bridge_count": report.bridge_count,
        "failed_subjects": list(report.failed_subjects),
        "bridges": [
            _bridge_payload(bridge, observations.get(bridge.bridge_id))
            for bridge in report.manifest.bridges
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


def format_fixed_point_equation_bridge_report(
    report: FixedPointEquationBridgeReport,
) -> str:
    """Format a concise human-readable bridge target report."""

    observations = {observation.bridge_id: observation for observation in report.observations}
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point equation bridge targets: {status}",
        f"Bridge set: {report.manifest.bridge_set_id}",
        f"Bridges: {report.bridge_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for bridge in report.manifest.bridges:
        observation = observations.get(bridge.bridge_id)
        diagonal_length = "unknown"
        direct_length = "unknown"
        equation_length = "unknown"
        if observation is not None:
            diagonal_length = str(observation.diagonal_instance_code_length)
            direct_length = str(observation.direct_target_code_length)
            equation_length = str(observation.bridge_equation_code_length)
        lines.extend([
            f"- {bridge.bridge_id}",
            f"  Target: {bridge.target_id}",
            f"  Status: {bridge.status}",
            f"  Diagonal instance length: {diagonal_length}",
            f"  Direct target length: {direct_length}",
            f"  Bridge equation length: {equation_length}",
            "  Future work: " + _joined_or_none(bridge.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_equation_bridge_cli(argv: list[str] | None = None) -> int:
    """Run fixed-point equation bridge target validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_equation_bridge",
        description="Validate AS fixed-point equation bridge targets.",
    )
    parser.add_argument(
        "--bridges",
        default=str(DEFAULT_BRIDGES),
        help="Path to the fixed-point equation bridge manifest.",
    )
    parser.add_argument(
        "--language",
        default=str(DEFAULT_FORMAL_LANGUAGE),
        help="Path to the formal arithmetic language manifest.",
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

    manifest = load_fixed_point_equation_bridge_targets(args.bridges)
    report = validate_fixed_point_equation_bridge_targets(
        manifest,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(fixed_point_equation_bridge_payload(report), sort_keys=True))
    else:
        print(format_fixed_point_equation_bridge_report(report))
    return 0 if report.accepted else 1


def _bridge_payload(
    bridge: FixedPointEquationBridgeTarget,
    observation: FixedPointEquationBridgeObservation | None,
) -> dict[str, Any]:
    payload = {
        "bridge_id": bridge.bridge_id,
        "target_id": bridge.target_id,
        "construction_id": bridge.construction_id,
        "witness_id": bridge.witness_id,
        "correctness_case_id": bridge.correctness_case_id,
        "status": bridge.status,
        "expected_diagonal_instance_code_length": (
            bridge.expected_diagonal_instance_code_length
        ),
        "expected_diagonal_instance_code_prefix": list(
            bridge.expected_diagonal_instance_code_prefix
        ),
        "expected_direct_target_code_length": bridge.expected_direct_target_code_length,
        "expected_direct_target_code_prefix": list(
            bridge.expected_direct_target_code_prefix
        ),
        "expected_bridge_equation_code_length": (
            bridge.expected_bridge_equation_code_length
        ),
        "expected_bridge_equation_code_prefix": list(
            bridge.expected_bridge_equation_code_prefix
        ),
        "expected_bridge_left_term_code_length": (
            bridge.expected_bridge_left_term_code_length
        ),
        "expected_bridge_right_term_code_length": (
            bridge.expected_bridge_right_term_code_length
        ),
        "expected_diagonal_equals_direct_target": (
            bridge.expected_diagonal_equals_direct_target
        ),
        "required_future_work": list(bridge.required_future_work),
        "non_claims": list(bridge.non_claims),
        "next_as_action": bridge.next_as_action,
    }
    if observation is None:
        payload.update({
            "observed_diagonal_instance_code_length": None,
            "observed_direct_target_code_length": None,
            "observed_bridge_equation_code_length": None,
            "observed_bridge_left_term_code_length": None,
            "observed_bridge_right_term_code_length": None,
            "observed_diagonal_instance_closed": None,
            "observed_direct_target_closed": None,
            "observed_bridge_equation_closed": None,
            "observed_target_skeleton_matches": None,
            "observed_diagonal_slot_is_substitution_code": None,
            "observed_direct_slot_quotes_diagonal_instance": None,
            "observed_witness_output_matches_diagonal": None,
            "observed_diagonal_equals_direct_target": None,
        })
    else:
        payload.update({
            "observed_diagonal_instance_code_length": (
                observation.diagonal_instance_code_length
            ),
            "observed_diagonal_instance_code_prefix": list(
                observation.diagonal_instance_code_prefix
            ),
            "observed_direct_target_code_length": (
                observation.direct_target_code_length
            ),
            "observed_direct_target_code_prefix": list(
                observation.direct_target_code_prefix
            ),
            "observed_bridge_equation_code_length": (
                observation.bridge_equation_code_length
            ),
            "observed_bridge_equation_code_prefix": list(
                observation.bridge_equation_code_prefix
            ),
            "observed_bridge_left_term_code_length": (
                observation.bridge_left_term_code_length
            ),
            "observed_bridge_right_term_code_length": (
                observation.bridge_right_term_code_length
            ),
            "observed_diagonal_instance_closed": observation.diagonal_instance_closed,
            "observed_direct_target_closed": observation.direct_target_closed,
            "observed_bridge_equation_closed": observation.bridge_equation_closed,
            "observed_target_skeleton_matches": observation.target_skeleton_matches,
            "observed_diagonal_slot_is_substitution_code": (
                observation.diagonal_slot_is_substitution_code
            ),
            "observed_direct_slot_quotes_diagonal_instance": (
                observation.direct_slot_quotes_diagonal_instance
            ),
            "observed_witness_output_matches_diagonal": (
                observation.witness_output_matches_diagonal
            ),
            "observed_diagonal_equals_direct_target": (
                observation.diagonal_equals_direct_target
            ),
        })
    return payload


def _validate_references(
    manifest: FixedPointEquationBridgeManifest,
) -> list[FixedPointEquationBridgeValidation]:
    expected = (
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
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
        (
            "substitution_graph_correctness_cases_path",
            manifest.substitution_graph_correctness_cases_path,
            "claims/substitution_graph_correctness_cases.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
    )
    results: list[FixedPointEquationBridgeValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_willard_anchors(
    manifest: FixedPointEquationBridgeManifest,
    known_anchor_ids: set[str],
) -> list[FixedPointEquationBridgeValidation]:
    unknown_anchor_ids = sorted(set(manifest.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(manifest.willard_anchor_ids)
    )
    if unknown_anchor_ids:
        return [
            _rejected(
                "willard_anchors",
                "unknown Willard anchor IDs: " + ", ".join(unknown_anchor_ids),
            )
        ]
    if missing_required:
        return [
            _rejected(
                "willard_anchors",
                "missing required Willard anchors: " + ", ".join(missing_required),
            )
        ]
    return [_accepted("willard_anchors", "required anchors are present and known")]


def _validate_dependency_reports(
    fixed_point_report: Any,
    diagonal_report: Any,
    witness_report: Any,
    correctness_case_report: Any,
    codebook_report: Any,
) -> list[FixedPointEquationBridgeValidation]:
    checks = (
        ("fixed_point", fixed_point_report, "fixed-point target"),
        ("diagonal_construction", diagonal_report, "diagonal construction"),
        ("substitution_representability", witness_report, "substitution witness"),
        (
            "substitution_graph_correctness_cases",
            correctness_case_report,
            "substitution graph correctness cases",
        ),
        ("codebook", codebook_report, "formal codebook"),
    )
    results: list[FixedPointEquationBridgeValidation] = []
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
    bridges: tuple[FixedPointEquationBridgeTarget, ...],
    fixed_point_targets: tuple[FixedPointTarget, ...],
    constructions: tuple[Any, ...],
    correctness_cases: tuple[Any, ...],
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    witness_targets_path: Path,
    codebook_path: Path,
    codebook: FormalCodebook,
) -> tuple[list[FixedPointEquationBridgeValidation], list[FixedPointEquationBridgeObservation]]:
    if not bridges:
        return [_rejected("bridges", "no fixed-point equation bridge targets")], []

    results: list[FixedPointEquationBridgeValidation] = []
    observations: list[FixedPointEquationBridgeObservation] = []
    bridge_ids = [bridge.bridge_id for bridge in bridges]
    duplicate_ids = _duplicates(bridge_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "bridges.bridge_id",
                "duplicate bridge ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("bridges.bridge_id", "bridge ids are unique"))

    for bridge in bridges:
        bridge_results, observation = _validate_bridge(
            bridge,
            fixed_point_targets,
            constructions,
            correctness_cases,
            diagonal_targets_path,
            fixed_point_targets_path,
            witness_targets_path,
            codebook_path,
            codebook,
        )
        results.extend(bridge_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("bridges", f"checked {len(bridges)} bridge target(s)"))
    return results, observations


def _validate_bridge(
    bridge: FixedPointEquationBridgeTarget,
    fixed_point_targets: tuple[FixedPointTarget, ...],
    constructions: tuple[Any, ...],
    correctness_cases: tuple[Any, ...],
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    witness_targets_path: Path,
    codebook_path: Path,
    codebook: FormalCodebook,
) -> tuple[list[FixedPointEquationBridgeValidation], FixedPointEquationBridgeObservation | None]:
    subject = bridge.bridge_id
    results: list[FixedPointEquationBridgeValidation] = []

    if bridge.status == "fixed-point-equation-proved":
        results.append(
            _rejected(
                f"{subject}.status",
                "proved fixed-point equation bridges are not supported",
            )
        )
    elif bridge.status not in VALID_BRIDGE_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {bridge.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "bridge status preserves non-claim"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in bridge.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                f"{subject}.required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(_accepted(f"{subject}.required_future_work", "future work is explicit"))

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in bridge.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                f"{subject}.non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted(f"{subject}.non_claims", "non-claims are explicit"))

    try:
        target = _find_fixed_point_target(fixed_point_targets, bridge.target_id)
        construction = _find_by_id(
            constructions,
            "construction_id",
            bridge.construction_id,
            "diagonal construction",
        )
        _find_by_id(
            correctness_cases,
            "case_id",
            bridge.correctness_case_id,
            "correctness case",
        )
        if construction.target_id != target.target_id:
            raise ValueError("diagonal construction target does not match bridge target")
        observation = _bridge_observation(
            bridge,
            target,
            diagonal_targets_path,
            fixed_point_targets_path,
            witness_targets_path,
            codebook_path,
            codebook,
        )
    except ValueError as exc:
        results.append(_rejected(f"{subject}.bridge", str(exc)))
        return results, None

    if not observation.diagonal_instance_closed:
        results.append(_rejected(f"{subject}.closure", "diagonal instance is open"))
    elif not observation.direct_target_closed:
        results.append(_rejected(f"{subject}.closure", "direct target form is open"))
    elif not observation.bridge_equation_closed:
        results.append(_rejected(f"{subject}.closure", "bridge equation is open"))
    else:
        results.append(_accepted(f"{subject}.closure", "bridge surfaces are closed"))

    if not observation.target_skeleton_matches:
        results.append(_rejected(f"{subject}.skeleton", "target skeleton mismatch"))
    elif not observation.diagonal_slot_is_substitution_code:
        results.append(
            _rejected(
                f"{subject}.slot",
                "diagonal slot is not substitution_code(quote(seed), quote(seed))",
            )
        )
    elif not observation.direct_slot_quotes_diagonal_instance:
        results.append(
            _rejected(
                f"{subject}.slot",
                "direct target slot does not quote the diagonal instance",
            )
        )
    else:
        results.append(_accepted(f"{subject}.slot", "bridge slots accepted"))

    if not observation.witness_output_matches_diagonal:
        results.append(
            _rejected(
                f"{subject}.witness",
                "substitution witness output does not match diagonal instance",
            )
        )
    else:
        results.append(_accepted(f"{subject}.witness", "witness output matches diagonal"))

    if (
        observation.diagonal_instance_code_length
        != bridge.expected_diagonal_instance_code_length
    ):
        results.append(
            _rejected(
                f"{subject}.length",
                "diagonal instance length mismatch: expected "
                + str(bridge.expected_diagonal_instance_code_length)
                + " got "
                + str(observation.diagonal_instance_code_length),
            )
        )
    elif observation.diagonal_instance_code_prefix != (
        bridge.expected_diagonal_instance_code_prefix
    ):
        results.append(_rejected(f"{subject}.length", "diagonal instance prefix mismatch"))
    elif observation.direct_target_code_length != bridge.expected_direct_target_code_length:
        results.append(
            _rejected(
                f"{subject}.length",
                "direct target length mismatch: expected "
                + str(bridge.expected_direct_target_code_length)
                + " got "
                + str(observation.direct_target_code_length),
            )
        )
    elif observation.direct_target_code_prefix != bridge.expected_direct_target_code_prefix:
        results.append(_rejected(f"{subject}.length", "direct target prefix mismatch"))
    elif (
        observation.bridge_equation_code_length
        != bridge.expected_bridge_equation_code_length
    ):
        results.append(
            _rejected(
                f"{subject}.length",
                "bridge equation length mismatch: expected "
                + str(bridge.expected_bridge_equation_code_length)
                + " got "
                + str(observation.bridge_equation_code_length),
            )
        )
    elif observation.bridge_equation_code_prefix != (
        bridge.expected_bridge_equation_code_prefix
    ):
        results.append(_rejected(f"{subject}.length", "bridge equation prefix mismatch"))
    elif (
        observation.bridge_left_term_code_length
        != bridge.expected_bridge_left_term_code_length
    ):
        results.append(
            _rejected(
                f"{subject}.length",
                "bridge left term length mismatch: expected "
                + str(bridge.expected_bridge_left_term_code_length)
                + " got "
                + str(observation.bridge_left_term_code_length),
            )
        )
    elif (
        observation.bridge_right_term_code_length
        != bridge.expected_bridge_right_term_code_length
    ):
        results.append(
            _rejected(
                f"{subject}.length",
                "bridge right term length mismatch: expected "
                + str(bridge.expected_bridge_right_term_code_length)
                + " got "
                + str(observation.bridge_right_term_code_length),
            )
        )
    else:
        results.append(_accepted(f"{subject}.length", "bridge lengths are current"))

    if (
        observation.diagonal_equals_direct_target
        != bridge.expected_diagonal_equals_direct_target
    ):
        results.append(
            _rejected(
                f"{subject}.gap",
                "diagonal/direct syntactic gap mismatch",
            )
        )
    else:
        results.append(_accepted(f"{subject}.gap", "diagonal/direct syntactic gap recorded"))

    return results, observation


def _bridge_observation(
    bridge: FixedPointEquationBridgeTarget,
    target: FixedPointTarget,
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    witness_targets_path: Path,
    codebook_path: Path,
    codebook: FormalCodebook,
) -> FixedPointEquationBridgeObservation:
    seed_node = build_diagonal_seed_node(target)
    seed_code = encode_node(seed_node, codebook)
    seed_quote = quote_tokens_as_term(seed_code)
    diagonal_instance_node = substitute_node(seed_node, target.template_variable, seed_quote)
    diagonal_instance_code = build_diagonal_instance_code(
        construction_id=bridge.construction_id,
        targets_path=diagonal_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    direct_target_slot = quote_tokens_as_term(diagonal_instance_code)
    direct_target_node = substitute_node(
        target.template_node,
        target.template_variable,
        direct_target_slot,
    )
    diagonal_slot = _target_slot(diagonal_instance_node)
    direct_slot = _target_slot(direct_target_node)
    bridge_equation_node = {
        "kind": "equals",
        "left": diagonal_slot,
        "right": direct_slot,
    }
    bridge_left_code = encode_node(diagonal_slot, codebook)
    bridge_right_code = encode_node(direct_slot, codebook)
    bridge_equation_code = encode_node(bridge_equation_node, codebook)
    direct_target_code = encode_node(direct_target_node, codebook)
    witness_output_code = build_substitution_witness_output_code(
        witness_id=bridge.witness_id,
        targets_path=witness_targets_path,
        diagonal_targets_path=diagonal_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook_path,
    )
    return FixedPointEquationBridgeObservation(
        bridge_id=bridge.bridge_id,
        target_id=bridge.target_id,
        construction_id=bridge.construction_id,
        witness_id=bridge.witness_id,
        status=bridge.status,
        diagonal_instance_code_length=len(diagonal_instance_code),
        diagonal_instance_code_prefix=diagonal_instance_code[
            : len(bridge.expected_diagonal_instance_code_prefix)
        ],
        direct_target_code_length=len(direct_target_code),
        direct_target_code_prefix=direct_target_code[
            : len(bridge.expected_direct_target_code_prefix)
        ],
        bridge_equation_code_length=len(bridge_equation_code),
        bridge_equation_code_prefix=bridge_equation_code[
            : len(bridge.expected_bridge_equation_code_prefix)
        ],
        bridge_left_term_code_length=len(bridge_left_code),
        bridge_right_term_code_length=len(bridge_right_code),
        diagonal_instance_closed=not free_variables(diagonal_instance_node),
        direct_target_closed=not free_variables(direct_target_node),
        bridge_equation_closed=not free_variables(bridge_equation_node),
        target_skeleton_matches=_target_skeleton_matches(
            diagonal_instance_node,
            direct_target_node,
        ),
        diagonal_slot_is_substitution_code=(
            diagonal_slot
            == {
                "kind": "substitution_code",
                "left": seed_quote,
                "right": seed_quote,
            }
        ),
        direct_slot_quotes_diagonal_instance=(direct_slot == direct_target_slot),
        witness_output_matches_diagonal=(witness_output_code == diagonal_instance_code),
        diagonal_equals_direct_target=(diagonal_instance_code == direct_target_code),
    )


def _target_slot(node: dict[str, Any]) -> dict[str, Any]:
    if node.get("kind") not in {"pi1", "sigma1"}:
        raise ValueError("bridge target must be a pi1 or sigma1 sentence")
    body = node.get("body")
    if not isinstance(body, dict) or body.get("kind") != "less_than":
        raise ValueError("bridge target body must be less_than")
    right = body.get("right")
    if not isinstance(right, dict):
        raise ValueError("bridge target slot is not a term")
    return right


def _target_skeleton_matches(
    diagonal_node: dict[str, Any],
    direct_node: dict[str, Any],
) -> bool:
    try:
        if diagonal_node.get("kind") != direct_node.get("kind"):
            return False
        if diagonal_node.get("variable") != direct_node.get("variable"):
            return False
        diagonal_body = diagonal_node.get("body")
        direct_body = direct_node.get("body")
        if not isinstance(diagonal_body, dict) or not isinstance(direct_body, dict):
            return False
        if diagonal_body.get("kind") != direct_body.get("kind"):
            return False
        if diagonal_body.get("left") != direct_body.get("left"):
            return False
        _target_slot(diagonal_node)
        _target_slot(direct_node)
    except ValueError:
        return False
    return True


def _find_fixed_point_target(
    targets: tuple[FixedPointTarget, ...],
    target_id: str,
) -> FixedPointTarget:
    for target in targets:
        if target.target_id == target_id:
            return target
    raise ValueError(f"unknown fixed-point target: {target_id}")


def _find_by_id(
    items: tuple[Any, ...],
    attr: str,
    value: str,
    label: str,
) -> Any:
    for item in items:
        if getattr(item, attr) == value:
            return item
    raise ValueError(f"unknown {label}: {value}")


def _parse_bridge(item: dict[str, Any]) -> FixedPointEquationBridgeTarget:
    return FixedPointEquationBridgeTarget(
        bridge_id=_required_text(item, "bridge_id"),
        target_id=_required_text(item, "target_id"),
        construction_id=_required_text(item, "construction_id"),
        witness_id=_required_text(item, "witness_id"),
        correctness_case_id=_required_text(item, "correctness_case_id"),
        status=_required_text(item, "status"),
        expected_diagonal_instance_code_length=_required_int(
            item,
            "expected_diagonal_instance_code_length",
        ),
        expected_diagonal_instance_code_prefix=tuple(
            _required_int_list(item, "expected_diagonal_instance_code_prefix")
        ),
        expected_direct_target_code_length=_required_int(
            item,
            "expected_direct_target_code_length",
        ),
        expected_direct_target_code_prefix=tuple(
            _required_int_list(item, "expected_direct_target_code_prefix")
        ),
        expected_bridge_equation_code_length=_required_int(
            item,
            "expected_bridge_equation_code_length",
        ),
        expected_bridge_equation_code_prefix=tuple(
            _required_int_list(item, "expected_bridge_equation_code_prefix")
        ),
        expected_bridge_left_term_code_length=_required_int(
            item,
            "expected_bridge_left_term_code_length",
        ),
        expected_bridge_right_term_code_length=_required_int(
            item,
            "expected_bridge_right_term_code_length",
        ),
        expected_diagonal_equals_direct_target=_required_bool(
            item,
            "expected_diagonal_equals_direct_target",
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "fixed-point-equation-bridge-willard-anchor"
    if subject.endswith(".status"):
        return "fixed-point-equation-bridge-status"
    if subject.endswith(".length"):
        return "fixed-point-equation-bridge-length"
    if subject.endswith(".slot"):
        return "fixed-point-equation-bridge-slot"
    if subject.endswith(".skeleton"):
        return "fixed-point-equation-bridge-skeleton"
    if subject.endswith(".witness"):
        return "fixed-point-equation-bridge-witness"
    if subject.endswith(".closure"):
        return "fixed-point-equation-bridge-closure"
    if subject.endswith(".gap"):
        return "fixed-point-equation-bridge-gap"
    if subject.endswith(".required_future_work"):
        return "fixed-point-equation-bridge-future-work"
    if subject.endswith(".non_claims"):
        return "fixed-point-equation-bridge-non-claim"
    if subject.endswith(".bridge") or subject.startswith("bridges"):
        return "fixed-point-equation-bridge"
    if subject in {
        "fixed_point",
        "diagonal_construction",
        "substitution_representability",
        "substitution_graph_correctness_cases",
        "codebook",
    }:
        return "fixed-point-equation-bridge-dependency"
    if subject.endswith("_path"):
        return "fixed-point-equation-bridge-reference"
    return "fixed-point-equation-bridge"


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


def _required_bool(item: dict[str, Any], key: str) -> bool:
    value = item.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"required boolean field missing: {key}")
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
    values = item.get(key)
    if not isinstance(values, list) or not values:
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for value in values:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{key} contains non-integer item")
        result.append(value)
    return result


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointEquationBridgeValidation:
    return FixedPointEquationBridgeValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointEquationBridgeValidation:
    return FixedPointEquationBridgeValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_equation_bridge_cli())
