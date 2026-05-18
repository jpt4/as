"""Checked substitution graph correctness target surface for AS.

This module names the proof obligation that follows the existing substitution
graph surfaces: the checked delta0 formula schema must be proved correct for
the ``substitution_code`` graph. It validates the target boundary and its
dependencies, but it deliberately does not prove formula correctness,
substitution representability, a diagonal lemma, a fixed-point equation, or
self-consistency.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_arithmetic import (
    load_formal_arithmetic_language,
    validate_formal_arithmetic_language,
)
from autarkic_systems.formal_code import (
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.substitution_graph_evaluation import (
    SubstitutionGraphEvaluationObservation,
    load_substitution_graph_evaluation_examples,
    validate_substitution_graph_evaluation_examples,
)
from autarkic_systems.substitution_graph_formula import (
    SubstitutionGraphFormulaCandidate,
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)
from autarkic_systems.substitution_graph_target import (
    SubstitutionGraphObservation,
    load_substitution_graph_targets,
    validate_substitution_graph_targets,
)


DEFAULT_TARGETS = Path("claims/substitution_graph_correctness_targets.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_FUTURE_WORK = (
    "formula-correctness-proof",
    "substitution-representability-proof",
    "diagonal-lemma-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no self-consistency theorem",
)
VALID_TARGET_STATUSES = {
    "correctness-proof-not-constructed",
}
PROVED_STATUS_REJECTIONS = {
    "formula-correctness-proved",
    "substitution-representability-proved",
    "diagonal-lemma-proved",
    "fixed-point-equation-proved",
    "self-consistency-proved",
}


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessTarget:
    """One proof-obligation target for substitution graph formula correctness."""

    target_id: str
    graph_target_id: str
    formula_candidate_id: str
    relation_name: str
    formula_class: str
    status: str
    checked_evaluation_example_ids: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessManifest:
    """Loaded manifest for substitution graph correctness proof targets."""

    path: Path
    schema_version: int
    target_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    substitution_graph_targets_path: str
    formula_candidates_path: str
    evaluation_examples_path: str
    targets: tuple[SubstitutionGraphCorrectnessTarget, ...]


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessValidation:
    """One validation result for correctness proof targets."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessObservation:
    """Observed dependency facts for one correctness proof target."""

    target_id: str
    graph_target_id: str
    formula_candidate_id: str
    status: str
    graph_target_status: str
    formula_candidate_status: str
    checked_evaluation_example_count: int
    all_examples_hold: bool


@dataclass(frozen=True)
class SubstitutionGraphCorrectnessReport:
    """Validation report over substitution graph correctness proof targets."""

    manifest: SubstitutionGraphCorrectnessManifest
    formal_language_path: Path
    codebook_path: Path
    substitution_graph_targets_path: Path
    formula_candidates_path: Path
    evaluation_examples_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphCorrectnessValidation, ...]
    observations: tuple[SubstitutionGraphCorrectnessObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every correctness-target validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def target_count(self) -> int:
        """Return the number of checked correctness proof targets."""

        return len(self.manifest.targets)

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


def load_substitution_graph_correctness_targets(
    path: Path | str = DEFAULT_TARGETS,
) -> SubstitutionGraphCorrectnessManifest:
    """Load substitution graph correctness proof targets from JSON."""

    targets_path = Path(path)
    data = json.loads(targets_path.read_text(encoding="utf-8"))
    return SubstitutionGraphCorrectnessManifest(
        path=targets_path,
        schema_version=_required_int(data, "schema_version"),
        target_set_id=_required_text(data, "target_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        substitution_graph_targets_path=_required_text(
            data,
            "substitution_graph_targets_path",
        ),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        evaluation_examples_path=_required_text(data, "evaluation_examples_path"),
        targets=tuple(
            _parse_target(item) for item in _required_list(data, "targets")
        ),
    )


def validate_substitution_graph_correctness_targets(
    manifest: SubstitutionGraphCorrectnessManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphCorrectnessReport:
    """Validate correctness targets and all referenced proof-route surfaces."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_graph_targets_path = Path(manifest.substitution_graph_targets_path)
    checked_formula_candidates_path = Path(manifest.formula_candidates_path)
    checked_evaluation_examples_path = Path(manifest.evaluation_examples_path)

    language = load_formal_arithmetic_language(checked_language_path)
    language_report = validate_formal_arithmetic_language(
        language,
        checked_willard_map_path,
    )
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    graph_targets = load_substitution_graph_targets(checked_graph_targets_path)
    graph_report = validate_substitution_graph_targets(
        graph_targets,
        checked_willard_map_path,
    )
    formula_candidates = load_substitution_graph_formula_candidates(
        checked_formula_candidates_path,
    )
    formula_report = validate_substitution_graph_formula_candidates(
        formula_candidates,
        checked_willard_map_path,
    )
    evaluation_examples = load_substitution_graph_evaluation_examples(
        checked_evaluation_examples_path,
    )
    evaluation_report = validate_substitution_graph_evaluation_examples(
        evaluation_examples,
        checked_willard_map_path,
    )

    results: list[SubstitutionGraphCorrectnessValidation] = [
        _accepted("manifest", f"loaded {len(manifest.targets)} target(s)")
    ]
    observations: list[SubstitutionGraphCorrectnessObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            language_report,
            codebook_report,
            graph_report,
            formula_report,
            evaluation_report,
        )
    )
    target_results, observations = _validate_targets(
        manifest.targets,
        graph_report.observations,
        formula_candidates.candidates,
        formula_report.observations,
        evaluation_report.observations,
    )
    results.extend(target_results)

    return SubstitutionGraphCorrectnessReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        substitution_graph_targets_path=checked_graph_targets_path,
        formula_candidates_path=checked_formula_candidates_path,
        evaluation_examples_path=checked_evaluation_examples_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def substitution_graph_correctness_report_payload(
    report: SubstitutionGraphCorrectnessReport,
) -> dict[str, Any]:
    """Return a JSON-ready correctness target report."""

    observations = {
        observation.target_id: observation
        for observation in report.observations
    }
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "target_manifest": str(report.manifest.path),
        "target_set_id": report.manifest.target_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "substitution_graph_targets_path": str(report.substitution_graph_targets_path),
        "formula_candidates_path": str(report.formula_candidates_path),
        "evaluation_examples_path": str(report.evaluation_examples_path),
        "willard_map": str(report.willard_map_path),
        "target_count": report.target_count,
        "failed_subjects": list(report.failed_subjects),
        "targets": [
            _target_payload(target, observations.get(target.target_id))
            for target in report.manifest.targets
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


def format_substitution_graph_correctness_report(
    report: SubstitutionGraphCorrectnessReport,
) -> str:
    """Format a concise human-readable correctness target report."""

    observations = {
        observation.target_id: observation
        for observation in report.observations
    }
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Substitution graph correctness targets: {status}",
        f"Target set: {report.manifest.target_set_id}",
        f"Targets: {report.target_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for target in report.manifest.targets:
        observation = observations.get(target.target_id)
        finite_examples = "unknown"
        examples_hold = "unknown"
        if observation is not None:
            finite_examples = str(observation.checked_evaluation_example_count)
            examples_hold = str(observation.all_examples_hold).lower()
        lines.extend([
            f"- {target.target_id}",
            f"  Graph target: {target.graph_target_id}",
            f"  Formula candidate: {target.formula_candidate_id}",
            f"  Relation: {target.relation_name}",
            f"  Formula class: {target.formula_class}",
            f"  Status: {target.status}",
            f"  Finite examples: {finite_examples}",
            f"  All examples hold: {examples_hold}",
            "  Future work: " + _joined_or_none(target.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_correctness_cli(argv: list[str] | None = None) -> int:
    """Run substitution graph correctness-target validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.substitution_graph_correctness",
        description="Validate AS substitution graph correctness proof targets.",
    )
    parser.add_argument(
        "--targets",
        default=str(DEFAULT_TARGETS),
        help="Path to the substitution graph correctness target manifest.",
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

    targets = load_substitution_graph_correctness_targets(args.targets)
    report = validate_substitution_graph_correctness_targets(
        targets,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_graph_correctness_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_graph_correctness_report(report))
    return 0 if report.accepted else 1


def _target_payload(
    target: SubstitutionGraphCorrectnessTarget,
    observation: SubstitutionGraphCorrectnessObservation | None,
) -> dict[str, Any]:
    payload = {
        "target_id": target.target_id,
        "graph_target_id": target.graph_target_id,
        "formula_candidate_id": target.formula_candidate_id,
        "relation_name": target.relation_name,
        "formula_class": target.formula_class,
        "status": target.status,
        "checked_evaluation_example_ids": list(target.checked_evaluation_example_ids),
        "required_future_work": list(target.required_future_work),
        "non_claims": list(target.non_claims),
        "next_as_action": target.next_as_action,
    }
    if observation is None:
        payload.update({
            "observed_graph_target_status": None,
            "observed_formula_candidate_status": None,
            "observed_evaluation_example_count": None,
            "observed_all_examples_hold": None,
        })
    else:
        payload.update({
            "observed_graph_target_status": observation.graph_target_status,
            "observed_formula_candidate_status": observation.formula_candidate_status,
            "observed_evaluation_example_count": (
                observation.checked_evaluation_example_count
            ),
            "observed_all_examples_hold": observation.all_examples_hold,
        })
    return payload


def _validate_references(
    manifest: SubstitutionGraphCorrectnessManifest,
) -> list[SubstitutionGraphCorrectnessValidation]:
    expected = (
        (
            "formal_language_path",
            manifest.formal_language_path,
            "language/formal_arithmetic_language.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "substitution_graph_targets_path",
            manifest.substitution_graph_targets_path,
            "claims/substitution_graph_targets.json",
        ),
        (
            "formula_candidates_path",
            manifest.formula_candidates_path,
            "claims/substitution_graph_formula_candidates.json",
        ),
        (
            "evaluation_examples_path",
            manifest.evaluation_examples_path,
            "claims/substitution_graph_evaluation_examples.json",
        ),
    )
    results: list[SubstitutionGraphCorrectnessValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    language_report: Any,
    codebook_report: Any,
    graph_report: Any,
    formula_report: Any,
    evaluation_report: Any,
) -> list[SubstitutionGraphCorrectnessValidation]:
    checks = (
        ("formal_language", language_report, "formal arithmetic language"),
        ("codebook", codebook_report, "formal codebook"),
        ("substitution_graph", graph_report, "substitution graph target"),
        ("substitution_graph_formula", formula_report, "substitution graph formula"),
        (
            "substitution_graph_evaluation",
            evaluation_report,
            "substitution graph evaluation examples",
        ),
    )
    results: list[SubstitutionGraphCorrectnessValidation] = []
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


def _validate_targets(
    targets: tuple[SubstitutionGraphCorrectnessTarget, ...],
    graph_observations: tuple[SubstitutionGraphObservation, ...],
    formula_candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    formula_observations: tuple[Any, ...],
    evaluation_observations: tuple[SubstitutionGraphEvaluationObservation, ...],
) -> tuple[
    list[SubstitutionGraphCorrectnessValidation],
    list[SubstitutionGraphCorrectnessObservation],
]:
    if not targets:
        return [_rejected("targets", "no substitution graph correctness targets")], []

    results: list[SubstitutionGraphCorrectnessValidation] = []
    observations: list[SubstitutionGraphCorrectnessObservation] = []
    target_ids = [target.target_id for target in targets]
    duplicate_ids = _duplicates(target_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "targets.target_id",
                "duplicate target ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("targets.target_id", "target ids are unique"))

    for target in targets:
        target_results, observation = _validate_target(
            target,
            graph_observations,
            formula_candidates,
            formula_observations,
            evaluation_observations,
        )
        results.extend(target_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("targets", f"checked {len(targets)} target(s)"))
    return results, observations


def _validate_target(
    target: SubstitutionGraphCorrectnessTarget,
    graph_observations: tuple[SubstitutionGraphObservation, ...],
    formula_candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    formula_observations: tuple[Any, ...],
    evaluation_observations: tuple[SubstitutionGraphEvaluationObservation, ...],
) -> tuple[
    list[SubstitutionGraphCorrectnessValidation],
    SubstitutionGraphCorrectnessObservation | None,
]:
    subject = target.target_id
    results: list[SubstitutionGraphCorrectnessValidation] = []

    if target.status in PROVED_STATUS_REJECTIONS:
        results.append(
            _rejected(
                f"{subject}.status",
                "proved formula correctness is not supported",
            )
        )
    elif target.status not in VALID_TARGET_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {target.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    if target.relation_name != "subst_code_graph":
        results.append(
            _rejected(f"{subject}.relation_name", "expected subst_code_graph")
        )
    else:
        results.append(_accepted(f"{subject}.relation_name", "relation target named"))

    if target.formula_class != "delta0":
        results.append(
            _rejected(f"{subject}.formula_class", "expected delta0 formula class")
        )
    else:
        results.append(_accepted(f"{subject}.formula_class", "delta0 proof target selected"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in target.required_future_work
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
        item for item in REQUIRED_NON_CLAIMS if item not in target.non_claims
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
        graph_observation = _find_graph_observation(
            graph_observations,
            target.graph_target_id,
        )
    except ValueError as exc:
        results.append(_rejected(f"{subject}.target", str(exc)))
        return results, None

    try:
        formula_candidate = _find_formula_candidate(
            formula_candidates,
            target.formula_candidate_id,
        )
        formula_observation = _find_formula_observation(
            formula_observations,
            target.formula_candidate_id,
        )
    except ValueError as exc:
        results.append(_rejected(f"{subject}.formula", str(exc)))
        return results, None

    results.extend(
        _validate_formula_candidate_tether(
            target,
            graph_observation,
            formula_candidate,
            formula_observation,
        )
    )

    example_results, matched_examples = _validate_evaluation_examples(
        target,
        evaluation_observations,
    )
    results.extend(example_results)
    if any(not result.accepted for result in example_results):
        return results, None

    all_examples_hold = all(example.relation_holds for example in matched_examples)
    observation = SubstitutionGraphCorrectnessObservation(
        target_id=target.target_id,
        graph_target_id=target.graph_target_id,
        formula_candidate_id=target.formula_candidate_id,
        status=target.status,
        graph_target_status=graph_observation.status,
        formula_candidate_status=formula_observation.status,
        checked_evaluation_example_count=len(matched_examples),
        all_examples_hold=all_examples_hold,
    )
    return results, observation


def _validate_formula_candidate_tether(
    target: SubstitutionGraphCorrectnessTarget,
    graph_observation: SubstitutionGraphObservation,
    formula_candidate: SubstitutionGraphFormulaCandidate,
    formula_observation: Any,
) -> list[SubstitutionGraphCorrectnessValidation]:
    subject = target.target_id
    results: list[SubstitutionGraphCorrectnessValidation] = []
    if formula_candidate.target_id != target.graph_target_id:
        results.append(
            _rejected(
                f"{subject}.formula",
                "formula target mismatch: expected "
                + target.graph_target_id
                + " but found "
                + formula_candidate.target_id,
            )
        )
    else:
        results.append(_accepted(f"{subject}.formula", "formula targets graph target"))

    if formula_observation.target_id != graph_observation.target_id:
        results.append(
            _rejected(
                f"{subject}.target",
                "formula observation mismatch: expected "
                + graph_observation.target_id
                + " but found "
                + formula_observation.target_id,
            )
        )
    else:
        results.append(_accepted(f"{subject}.target", "graph and formula observations agree"))

    if formula_candidate.relation_name != target.relation_name:
        results.append(
            _rejected(
                f"{subject}.relation_name",
                "formula relation mismatch: expected "
                + target.relation_name
                + " but found "
                + formula_candidate.relation_name,
            )
        )
    if formula_candidate.formula_class != target.formula_class:
        results.append(
            _rejected(
                f"{subject}.formula_class",
                "formula class mismatch: expected "
                + target.formula_class
                + " but found "
                + formula_candidate.formula_class,
            )
        )
    return results


def _validate_evaluation_examples(
    target: SubstitutionGraphCorrectnessTarget,
    observations: tuple[SubstitutionGraphEvaluationObservation, ...],
) -> tuple[
    list[SubstitutionGraphCorrectnessValidation],
    list[SubstitutionGraphEvaluationObservation],
]:
    subject = f"{target.target_id}.evaluation"
    results: list[SubstitutionGraphCorrectnessValidation] = []
    if not target.checked_evaluation_example_ids:
        return [_rejected(subject, "no finite evaluation examples listed")], []

    duplicate_ids = _duplicates(list(target.checked_evaluation_example_ids))
    if duplicate_ids:
        return [
            _rejected(
                subject,
                "duplicate evaluation example ids: " + ", ".join(duplicate_ids),
            )
        ], []

    matched: list[SubstitutionGraphEvaluationObservation] = []
    for example_id in target.checked_evaluation_example_ids:
        try:
            observation = _find_evaluation_observation(observations, example_id)
        except ValueError as exc:
            return [_rejected(subject, str(exc))], []
        matched.append(observation)

    failing_examples = [
        observation.example_id
        for observation in matched
        if not observation.relation_holds
    ]
    if failing_examples:
        results.append(
            _rejected(
                subject,
                "finite examples do not hold: " + ", ".join(failing_examples),
            )
        )
    else:
        results.append(_accepted(subject, f"{len(matched)} finite example(s) hold"))
    return results, matched


def _find_graph_observation(
    observations: tuple[SubstitutionGraphObservation, ...],
    target_id: str,
) -> SubstitutionGraphObservation:
    for observation in observations:
        if observation.target_id == target_id:
            return observation
    raise ValueError(f"unknown substitution graph target: {target_id}")


def _find_formula_candidate(
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    candidate_id: str,
) -> SubstitutionGraphFormulaCandidate:
    for candidate in candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    raise ValueError(f"unknown formula candidate: {candidate_id}")


def _find_formula_observation(
    observations: tuple[Any, ...],
    candidate_id: str,
) -> Any:
    for observation in observations:
        if observation.candidate_id == candidate_id:
            return observation
    raise ValueError(f"unknown formula candidate: {candidate_id}")


def _find_evaluation_observation(
    observations: tuple[SubstitutionGraphEvaluationObservation, ...],
    example_id: str,
) -> SubstitutionGraphEvaluationObservation:
    for observation in observations:
        if observation.example_id == example_id:
            return observation
    raise ValueError(f"unknown evaluation example: {example_id}")


def _parse_target(
    item: dict[str, Any],
) -> SubstitutionGraphCorrectnessTarget:
    return SubstitutionGraphCorrectnessTarget(
        target_id=_required_text(item, "target_id"),
        graph_target_id=_required_text(item, "graph_target_id"),
        formula_candidate_id=_required_text(item, "formula_candidate_id"),
        relation_name=_required_text(item, "relation_name"),
        formula_class=_required_text(item, "formula_class"),
        status=_required_text(item, "status"),
        checked_evaluation_example_ids=tuple(
            _required_text_list(item, "checked_evaluation_example_ids")
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject.endswith(".status"):
        return "substitution-graph-correctness-status"
    if subject.endswith(".relation_name"):
        return "substitution-graph-correctness-relation"
    if subject.endswith(".formula_class"):
        return "substitution-graph-correctness-formula-class"
    if subject.endswith(".target"):
        return "substitution-graph-correctness-target"
    if subject.endswith(".formula"):
        return "substitution-graph-correctness-formula"
    if subject.endswith(".evaluation"):
        return "substitution-graph-correctness-evaluation"
    if subject.endswith(".required_future_work"):
        return "substitution-graph-correctness-future-work"
    if subject.endswith(".non_claims"):
        return "substitution-graph-correctness-non-claim"
    if subject in {
        "formal_language",
        "codebook",
        "substitution_graph",
        "substitution_graph_formula",
        "substitution_graph_evaluation",
    }:
        return "substitution-graph-correctness-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-correctness-reference"
    if subject.startswith("targets"):
        return "substitution-graph-correctness-target"
    return "substitution-graph-correctness"


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


def _required_text_list(
    item: dict[str, Any],
    key: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    values = item.get(key)
    if not isinstance(values, list) or (not values and not allow_empty):
        raise ValueError(f"required list field missing: {key}")
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
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


def _accepted(subject: str, detail: str) -> SubstitutionGraphCorrectnessValidation:
    return SubstitutionGraphCorrectnessValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(subject: str, detail: str) -> SubstitutionGraphCorrectnessValidation:
    return SubstitutionGraphCorrectnessValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_correctness_cli())
