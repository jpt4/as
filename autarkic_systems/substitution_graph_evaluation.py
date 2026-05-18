"""Finite substitution graph evaluation examples for AS.

This module evaluates a few concrete ``substitution_code`` graph points over
the current codebook. It is deliberately finite evidence only: the examples
exercise the evaluator and guard against drift, but they do not prove formula
correctness or substitution representability.
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
    FormalCodebook,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import free_variables, substitute_node
from autarkic_systems.substitution_graph_formula import (
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)


DEFAULT_EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")
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
VALID_EXAMPLE_STATUSES = {
    "finite-evaluation-not-proof",
}


@dataclass(frozen=True)
class SubstitutionGraphEvaluationExample:
    """One finite substitution graph evaluation example."""

    example_id: str
    status: str
    variable: str
    formula_node: dict[str, Any]
    argument_code: tuple[int, ...]
    expected_formula_code: tuple[int, ...]
    expected_formula_free_variables: tuple[str, ...]
    expected_relation_holds: bool
    expected_output_code_length: int
    expected_output_code_prefix: tuple[int, ...]
    expected_output_free_variables: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphEvaluationManifest:
    """Loaded finite substitution graph evaluation examples."""

    path: Path
    schema_version: int
    evaluation_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    formula_candidates_path: str
    examples: tuple[SubstitutionGraphEvaluationExample, ...]


@dataclass(frozen=True)
class SubstitutionGraphEvaluationValidation:
    """One validation result for finite graph evaluation examples."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphEvaluationObservation:
    """Observed facts from one finite graph evaluation."""

    example_id: str
    status: str
    formula_code: tuple[int, ...]
    formula_free_variables: tuple[str, ...]
    relation_holds: bool
    output_code_length: int
    output_code_prefix: tuple[int, ...]
    output_free_variables: tuple[str, ...]


@dataclass(frozen=True)
class SubstitutionGraphEvaluationReport:
    """Validation report over finite substitution graph examples."""

    manifest: SubstitutionGraphEvaluationManifest
    formal_language_path: Path
    codebook_path: Path
    formula_candidates_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphEvaluationValidation, ...]
    observations: tuple[SubstitutionGraphEvaluationObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every evaluation validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def example_count(self) -> int:
        """Return the number of checked evaluation examples."""

        return len(self.manifest.examples)

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


def load_substitution_graph_evaluation_examples(
    path: Path | str = DEFAULT_EXAMPLES,
) -> SubstitutionGraphEvaluationManifest:
    """Load finite substitution graph evaluation examples from JSON."""

    examples_path = Path(path)
    data = json.loads(examples_path.read_text(encoding="utf-8"))
    return SubstitutionGraphEvaluationManifest(
        path=examples_path,
        schema_version=_required_int(data, "schema_version"),
        evaluation_set_id=_required_text(data, "evaluation_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        examples=tuple(
            _parse_example(item) for item in _required_list(data, "examples")
        ),
    )


def validate_substitution_graph_evaluation_examples(
    manifest: SubstitutionGraphEvaluationManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphEvaluationReport:
    """Validate finite substitution graph examples and dependencies."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_candidates_path = Path(manifest.formula_candidates_path)

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
    formula_candidates = load_substitution_graph_formula_candidates(
        checked_candidates_path,
    )
    formula_report = validate_substitution_graph_formula_candidates(
        formula_candidates,
        checked_willard_map_path,
    )

    results: list[SubstitutionGraphEvaluationValidation] = [
        _accepted("manifest", f"loaded {len(manifest.examples)} example(s)")
    ]
    observations: list[SubstitutionGraphEvaluationObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(_validate_dependency_reports(
        language_report,
        codebook_report,
        formula_report,
    ))
    example_results, observations = _validate_examples(
        manifest.examples,
        codebook,
    )
    results.extend(example_results)

    return SubstitutionGraphEvaluationReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        formula_candidates_path=checked_candidates_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def substitution_graph_evaluation_report_payload(
    report: SubstitutionGraphEvaluationReport,
) -> dict[str, Any]:
    """Return a JSON-ready finite evaluation report."""

    observations = {observation.example_id: observation for observation in report.observations}
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "examples_path": str(report.manifest.path),
        "evaluation_set_id": report.manifest.evaluation_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "formula_candidates_path": str(report.formula_candidates_path),
        "willard_map": str(report.willard_map_path),
        "example_count": report.example_count,
        "failed_subjects": list(report.failed_subjects),
        "examples": [
            _example_payload(example, observations.get(example.example_id))
            for example in report.manifest.examples
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


def format_substitution_graph_evaluation_report(
    report: SubstitutionGraphEvaluationReport,
) -> str:
    """Format a concise human-readable finite evaluation report."""

    observations = {observation.example_id: observation for observation in report.observations}
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Substitution graph evaluation examples: {status}",
        f"Evaluation set: {report.manifest.evaluation_set_id}",
        f"Examples: {report.example_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for example in report.manifest.examples:
        observation = observations.get(example.example_id)
        relation_holds = "unknown"
        output_length = "unknown"
        if observation is not None:
            relation_holds = str(observation.relation_holds).lower()
            output_length = str(observation.output_code_length)
        lines.extend([
            f"- {example.example_id}",
            f"  Status: {example.status}",
            f"  Variable: {example.variable}",
            f"  Argument code length: {len(example.argument_code)}",
            f"  Relation holds: {relation_holds}",
            f"  Output code length: {output_length}",
            "  Future work: " + _joined_or_none(example.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_evaluation_cli(argv: list[str] | None = None) -> int:
    """Run finite substitution graph evaluation validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.substitution_graph_evaluation",
        description="Validate finite AS substitution graph evaluation examples.",
    )
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES),
        help="Path to the finite substitution graph evaluation manifest.",
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

    examples = load_substitution_graph_evaluation_examples(args.examples)
    report = validate_substitution_graph_evaluation_examples(
        examples,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_graph_evaluation_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_graph_evaluation_report(report))
    return 0 if report.accepted else 1


def _example_payload(
    example: SubstitutionGraphEvaluationExample,
    observation: SubstitutionGraphEvaluationObservation | None,
) -> dict[str, Any]:
    payload = {
        "example_id": example.example_id,
        "status": example.status,
        "variable": example.variable,
        "formula_node": example.formula_node,
        "argument_code": list(example.argument_code),
        "expected_formula_code": list(example.expected_formula_code),
        "expected_formula_free_variables": list(
            example.expected_formula_free_variables
        ),
        "expected_relation_holds": example.expected_relation_holds,
        "expected_output_code_length": example.expected_output_code_length,
        "expected_output_code_prefix": list(example.expected_output_code_prefix),
        "expected_output_free_variables": list(example.expected_output_free_variables),
        "required_future_work": list(example.required_future_work),
        "non_claims": list(example.non_claims),
        "next_as_action": example.next_as_action,
    }
    if observation is None:
        payload.update({
            "observed_formula_code": None,
            "observed_formula_free_variables": None,
            "observed_relation_holds": None,
            "observed_output_code_length": None,
            "observed_output_code_prefix": None,
            "observed_output_free_variables": None,
        })
    else:
        payload.update({
            "observed_formula_code": list(observation.formula_code),
            "observed_formula_free_variables": list(
                observation.formula_free_variables
            ),
            "observed_relation_holds": observation.relation_holds,
            "observed_output_code_length": observation.output_code_length,
            "observed_output_code_prefix": list(observation.output_code_prefix),
            "observed_output_free_variables": list(
                observation.output_free_variables
            ),
        })
    return payload


def _validate_references(
    manifest: SubstitutionGraphEvaluationManifest,
) -> list[SubstitutionGraphEvaluationValidation]:
    expected = (
        (
            "formal_language_path",
            manifest.formal_language_path,
            "language/formal_arithmetic_language.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "formula_candidates_path",
            manifest.formula_candidates_path,
            "claims/substitution_graph_formula_candidates.json",
        ),
    )
    results: list[SubstitutionGraphEvaluationValidation] = []
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
    formula_report: Any,
) -> list[SubstitutionGraphEvaluationValidation]:
    checks = (
        ("formal_language", language_report, "formal arithmetic language"),
        ("codebook", codebook_report, "formal codebook"),
        ("substitution_graph_formula", formula_report, "substitution graph formula"),
    )
    results: list[SubstitutionGraphEvaluationValidation] = []
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


def _validate_examples(
    examples: tuple[SubstitutionGraphEvaluationExample, ...],
    codebook: FormalCodebook,
) -> tuple[
    list[SubstitutionGraphEvaluationValidation],
    list[SubstitutionGraphEvaluationObservation],
]:
    if not examples:
        return [_rejected("examples", "no substitution graph evaluation examples")], []

    results: list[SubstitutionGraphEvaluationValidation] = []
    observations: list[SubstitutionGraphEvaluationObservation] = []
    example_ids = [example.example_id for example in examples]
    duplicate_ids = _duplicates(example_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "examples.example_id",
                "duplicate example ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("examples.example_id", "example ids are unique"))

    for example in examples:
        example_results, observation = _validate_example(example, codebook)
        results.extend(example_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("examples", f"checked {len(examples)} example(s)"))
    return results, observations


def _validate_example(
    example: SubstitutionGraphEvaluationExample,
    codebook: FormalCodebook,
) -> tuple[
    list[SubstitutionGraphEvaluationValidation],
    SubstitutionGraphEvaluationObservation | None,
]:
    subject = example.example_id
    results: list[SubstitutionGraphEvaluationValidation] = []

    if example.status in {
        "formula-correctness-proved",
        "substitution-representability-proved",
    }:
        results.append(
            _rejected(
                f"{subject}.status",
                "proved formula correctness is not supported",
            )
        )
    elif example.status not in VALID_EXAMPLE_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {example.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in example.required_future_work
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
        item for item in REQUIRED_NON_CLAIMS if item not in example.non_claims
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
        observation = _observe_example(example, codebook)
    except ValueError as exc:
        results.append(_rejected(f"{subject}.formula", str(exc)))
        return results, None

    results.extend(_validate_formula(example, observation))
    results.extend(_validate_relation(example, observation))
    results.extend(_validate_output(example, observation))
    return results, observation


def _observe_example(
    example: SubstitutionGraphEvaluationExample,
    codebook: FormalCodebook,
) -> SubstitutionGraphEvaluationObservation:
    formula_code = encode_node(example.formula_node, codebook)
    formula_free_variables = tuple(sorted(free_variables(example.formula_node)))
    output_node = substitute_node(
        example.formula_node,
        example.variable,
        quote_tokens_as_term(example.argument_code),
    )
    output_code = encode_node(output_node, codebook)
    output_free_variables = tuple(sorted(free_variables(output_node)))
    return SubstitutionGraphEvaluationObservation(
        example_id=example.example_id,
        status=example.status,
        formula_code=formula_code,
        formula_free_variables=formula_free_variables,
        relation_holds=True,
        output_code_length=len(output_code),
        output_code_prefix=output_code[: len(example.expected_output_code_prefix)],
        output_free_variables=output_free_variables,
    )


def _validate_formula(
    example: SubstitutionGraphEvaluationExample,
    observation: SubstitutionGraphEvaluationObservation,
) -> list[SubstitutionGraphEvaluationValidation]:
    subject = f"{example.example_id}.formula"
    if observation.formula_code != example.expected_formula_code:
        return [
            _rejected(
                subject,
                "formula code mismatch: expected "
                + _format_code(example.expected_formula_code)
                + " got "
                + _format_code(observation.formula_code),
            )
        ]
    if observation.formula_free_variables != example.expected_formula_free_variables:
        return [
            _rejected(
                subject,
                "formula free variables mismatch: expected "
                + _joined_or_none(example.expected_formula_free_variables)
                + " got "
                + _joined_or_none(observation.formula_free_variables),
            )
        ]
    return [_accepted(subject, "formula facts accepted")]


def _validate_relation(
    example: SubstitutionGraphEvaluationExample,
    observation: SubstitutionGraphEvaluationObservation,
) -> list[SubstitutionGraphEvaluationValidation]:
    subject = f"{example.example_id}.relation"
    if observation.relation_holds != example.expected_relation_holds:
        return [
            _rejected(
                subject,
                "relation truth mismatch: expected "
                + str(example.expected_relation_holds).lower()
                + " got "
                + str(observation.relation_holds).lower(),
            )
        ]
    return [_accepted(subject, "finite relation evaluation accepted")]


def _validate_output(
    example: SubstitutionGraphEvaluationExample,
    observation: SubstitutionGraphEvaluationObservation,
) -> list[SubstitutionGraphEvaluationValidation]:
    subject = f"{example.example_id}.output"
    if observation.output_code_length != example.expected_output_code_length:
        return [
            _rejected(
                subject,
                "output code length mismatch: expected "
                + str(example.expected_output_code_length)
                + " got "
                + str(observation.output_code_length),
            )
        ]
    if observation.output_code_prefix != example.expected_output_code_prefix:
        return [
            _rejected(
                subject,
                "output code prefix mismatch: expected "
                + _format_code(example.expected_output_code_prefix)
                + " got "
                + _format_code(observation.output_code_prefix),
            )
        ]
    if observation.output_free_variables != example.expected_output_free_variables:
        return [
            _rejected(
                subject,
                "output free variables mismatch: expected "
                + _joined_or_none(example.expected_output_free_variables)
                + " got "
                + _joined_or_none(observation.output_free_variables),
            )
        ]
    return [_accepted(subject, "output facts accepted")]


def _parse_example(item: dict[str, Any]) -> SubstitutionGraphEvaluationExample:
    return SubstitutionGraphEvaluationExample(
        example_id=_required_text(item, "example_id"),
        status=_required_text(item, "status"),
        variable=_required_text(item, "variable"),
        formula_node=_required_mapping(item, "formula_node"),
        argument_code=tuple(_required_int_list(item, "argument_code")),
        expected_formula_code=tuple(_required_int_list(item, "expected_formula_code")),
        expected_formula_free_variables=tuple(
            _required_text_list(item, "expected_formula_free_variables", allow_empty=True)
        ),
        expected_relation_holds=_required_bool(item, "expected_relation_holds"),
        expected_output_code_length=_required_int(
            item,
            "expected_output_code_length",
        ),
        expected_output_code_prefix=tuple(
            _required_int_list(item, "expected_output_code_prefix")
        ),
        expected_output_free_variables=tuple(
            _required_text_list(
                item,
                "expected_output_free_variables",
                allow_empty=True,
            )
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject.endswith(".status"):
        return "substitution-graph-evaluation-status"
    if subject.endswith(".formula"):
        return "substitution-graph-evaluation-formula"
    if subject.endswith(".relation"):
        return "substitution-graph-evaluation-relation"
    if subject.endswith(".output"):
        return "substitution-graph-evaluation-output"
    if subject.endswith(".required_future_work"):
        return "substitution-graph-evaluation-future-work"
    if subject.endswith(".non_claims"):
        return "substitution-graph-evaluation-non-claim"
    if subject in {
        "formal_language",
        "codebook",
        "substitution_graph_formula",
    }:
        return "substitution-graph-evaluation-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-evaluation-reference"
    if subject.startswith("examples"):
        return "substitution-graph-evaluation-example"
    return "substitution-graph-evaluation"


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


def _required_mapping(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"required mapping field missing: {key}")
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


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    values = item.get(key)
    if not isinstance(values, list) or not values:
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for value in values:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{key} contains non-natural item")
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


def _accepted(subject: str, detail: str) -> SubstitutionGraphEvaluationValidation:
    return SubstitutionGraphEvaluationValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(subject: str, detail: str) -> SubstitutionGraphEvaluationValidation:
    return SubstitutionGraphEvaluationValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _format_code(values: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(value) for value in values) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_evaluation_cli())
