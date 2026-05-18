"""Checked sentence-complement surface for AS formal code.

The Level-1 consistency target needs a transparent relation between a
statement class and its negation class. This module implements only the small
syntax surface needed now: complementing a ``pi1`` sentence yields a ``sigma1``
sentence with a negated body, and complementing a ``sigma1`` sentence yields a
``pi1`` sentence with a negated body. It does not prove that this operation is
arithmetically complete, simplify double negations, or establish consistency.
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
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_EXAMPLES = Path("language/formal_complement_examples.json")
DEFAULT_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_CODEBOOK = Path("language/formal_codebook.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D5.6-LEVEL-K-CONSISTENCY",
    "W2011-D5.7-SELFCONSK",
    "W2020-T4.4-T4.5-LEM-BOUNDARY",
)
VALID_COMPLEMENT_KIND = "sentence-wrapper-negation-surface"
VALID_COMPLEMENT_STATUS = "complement-surface-only"
COMPLEMENT_CLASSES = {
    "pi1": "sigma1",
    "sigma1": "pi1",
}


@dataclass(frozen=True)
class FormalComplementExample:
    """One checked sentence-complement example."""

    example_id: str
    source_sentence_class: str
    complement_sentence_class: str
    source_node: dict[str, Any]
    expected_complement_node: dict[str, Any]
    expected_source_code: tuple[int, ...]
    expected_complement_code: tuple[int, ...]
    status: str
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FormalComplementExampleSet:
    """Loaded complement examples."""

    path: Path
    schema_version: int
    complement_set_id: str
    reviewed_at: str
    purpose: str
    language_path: str
    codebook_path: str
    complement_kind: str
    willard_anchor_ids: tuple[str, ...]
    examples: tuple[FormalComplementExample, ...]


@dataclass(frozen=True)
class FormalComplementValidation:
    """One validation result for the formal complement surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FormalComplementReport:
    """Validation report for formal complement examples."""

    examples: FormalComplementExampleSet
    language_path: Path
    codebook_path: Path
    willard_map_path: Path
    results: tuple[FormalComplementValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every complement validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def example_count(self) -> int:
        """Return the number of checked complement examples."""

        return len(self.examples.examples)

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


def complement_sentence(node: dict[str, Any]) -> dict[str, Any]:
    """Return the surface complement of a pi1 or sigma1 sentence wrapper."""

    kind = _node_kind(node)
    if kind not in COMPLEMENT_CLASSES:
        raise ValueError(f"unsupported complement sentence class: {kind}")
    variable = node.get("variable")
    if not isinstance(variable, str) or not variable.strip():
        raise ValueError("sentence wrapper missing variable")
    return {
        "kind": COMPLEMENT_CLASSES[kind],
        "variable": variable,
        "body": {
            "kind": "not",
            "body": _required_node(node, "body"),
        },
    }


def load_formal_complement_examples(
    path: Path | str = DEFAULT_EXAMPLES,
) -> FormalComplementExampleSet:
    """Load checked complement examples from JSON."""

    examples_path = Path(path)
    data = json.loads(examples_path.read_text(encoding="utf-8"))
    return FormalComplementExampleSet(
        path=examples_path,
        schema_version=_required_int(data, "schema_version"),
        complement_set_id=_required_text(data, "complement_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        language_path=_required_text(data, "language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        complement_kind=_required_text(data, "complement_kind"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        examples=tuple(_parse_example(item) for item in _required_list(data, "examples")),
    )


def validate_formal_complement_examples(
    examples: FormalComplementExampleSet,
    language_path: Path | str = DEFAULT_LANGUAGE,
    codebook_path: Path | str = DEFAULT_CODEBOOK,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FormalComplementReport:
    """Validate complement examples against the language and codebook."""

    checked_language_path = Path(language_path)
    checked_codebook_path = Path(codebook_path)
    checked_willard_map_path = Path(willard_map_path)
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
    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}

    results: list[FormalComplementValidation] = [
        _accepted("examples", f"loaded {len(examples.examples)} example(s)")
    ]
    results.extend(_validate_references(examples))
    results.extend(_validate_dependency_reports(language_report, codebook_report))
    results.extend(_validate_complement_kind(examples))
    results.extend(_validate_willard_anchors(examples, known_anchor_ids))
    results.extend(_validate_examples(examples, language, codebook))

    return FormalComplementReport(
        examples=examples,
        language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
    )


def formal_complement_report_payload(report: FormalComplementReport) -> dict[str, Any]:
    """Return a JSON-ready complement validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.examples.schema_version,
        "examples_path": str(report.examples.path),
        "complement_set_id": report.examples.complement_set_id,
        "reviewed_at": report.examples.reviewed_at,
        "purpose": report.examples.purpose,
        "language_path": str(report.language_path),
        "codebook_path": str(report.codebook_path),
        "willard_map": str(report.willard_map_path),
        "complement_kind": report.examples.complement_kind,
        "willard_anchor_ids": list(report.examples.willard_anchor_ids),
        "example_count": report.example_count,
        "failed_subjects": list(report.failed_subjects),
        "examples": [
            {
                "example_id": example.example_id,
                "source_sentence_class": example.source_sentence_class,
                "complement_sentence_class": example.complement_sentence_class,
                "source_node": example.source_node,
                "expected_complement_node": example.expected_complement_node,
                "expected_source_code": list(example.expected_source_code),
                "expected_complement_code": list(example.expected_complement_code),
                "status": example.status,
                "non_claims": list(example.non_claims),
                "next_as_action": example.next_as_action,
            }
            for example in report.examples.examples
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


def format_formal_complement_report(report: FormalComplementReport) -> str:
    """Format a concise human-readable complement report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Formal complements: {status}",
        f"Complement set: {report.examples.complement_set_id}",
        f"Examples: {report.example_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for example in report.examples.examples:
        lines.extend([
            f"- {example.example_id}",
            f"  Classes: {example.source_sentence_class} -> {example.complement_sentence_class}",
            f"  Status: {example.status}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_formal_complement_cli(argv: list[str] | None = None) -> int:
    """Run the formal complement validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_complement",
        description="Validate AS formal sentence-complement examples.",
    )
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES),
        help="Path to the formal complement example manifest.",
    )
    parser.add_argument(
        "--language",
        default=str(DEFAULT_LANGUAGE),
        help="Path to the formal arithmetic language manifest.",
    )
    parser.add_argument(
        "--codebook",
        default=str(DEFAULT_CODEBOOK),
        help="Path to the formal codebook manifest.",
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

    examples = load_formal_complement_examples(args.examples)
    report = validate_formal_complement_examples(
        examples,
        args.language,
        args.codebook,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(formal_complement_report_payload(report), sort_keys=True))
    else:
        print(format_formal_complement_report(report))
    return 0 if report.accepted else 1


def _validate_references(
    examples: FormalComplementExampleSet,
) -> list[FormalComplementValidation]:
    expected = (
        ("language_path", examples.language_path, "language/formal_arithmetic_language.json"),
        ("codebook_path", examples.codebook_path, "language/formal_codebook.json"),
    )
    results: list[FormalComplementValidation] = []
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
) -> list[FormalComplementValidation]:
    results: list[FormalComplementValidation] = []
    if language_report.accepted:
        results.append(_accepted("language", "formal arithmetic language accepted"))
    else:
        results.append(
            _rejected(
                "language",
                "formal arithmetic language rejected: "
                + _joined_or_none(language_report.failed_subjects),
            )
        )
    if codebook_report.accepted:
        results.append(_accepted("codebook", "formal codebook accepted"))
    else:
        results.append(
            _rejected(
                "codebook",
                "formal codebook rejected: "
                + _joined_or_none(codebook_report.failed_subjects),
            )
        )
    return results


def _validate_complement_kind(
    examples: FormalComplementExampleSet,
) -> list[FormalComplementValidation]:
    if examples.complement_kind == VALID_COMPLEMENT_KIND:
        return [_accepted("complement_kind", VALID_COMPLEMENT_KIND)]
    return [
        _rejected(
            "complement_kind",
            f"unknown complement kind: {examples.complement_kind}",
        )
    ]


def _validate_willard_anchors(
    examples: FormalComplementExampleSet,
    known_anchor_ids: set[str],
) -> list[FormalComplementValidation]:
    unknown_anchor_ids = sorted(set(examples.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(examples.willard_anchor_ids)
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


def _validate_examples(
    examples: FormalComplementExampleSet,
    language: Any,
    codebook: Any,
) -> list[FormalComplementValidation]:
    if not examples.examples:
        return [_rejected("examples", "complement examples must not be empty")]

    results: list[FormalComplementValidation] = []
    example_ids = [example.example_id for example in examples.examples]
    duplicate_ids = _duplicates(example_ids)
    if duplicate_ids:
        results.append(
            _rejected("examples.example_id", "duplicate example ids: " + ", ".join(duplicate_ids))
        )
    else:
        results.append(_accepted("examples.example_id", "example ids are unique"))

    sentence_classes = set(language.sentence_classes)
    code_sentence_classes = set(codebook.sentence_tags)
    for example in examples.examples:
        results.extend(_validate_example(example, sentence_classes, code_sentence_classes, codebook))
    results.append(_accepted("examples", f"checked {len(examples.examples)} example(s)"))
    return results


def _validate_example(
    example: FormalComplementExample,
    sentence_classes: set[str],
    code_sentence_classes: set[str],
    codebook: Any,
) -> list[FormalComplementValidation]:
    subject = example.example_id
    results: list[FormalComplementValidation] = []

    if example.status == "complement-theorem-proved":
        results.append(
            _rejected(
                f"{subject}.status",
                "proved complement theorems are not supported",
            )
        )
    elif example.status != VALID_COMPLEMENT_STATUS:
        results.append(_rejected(f"{subject}.status", f"unknown status: {example.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    source_class = example.source_sentence_class
    complement_class = example.complement_sentence_class
    expected_complement_class = COMPLEMENT_CLASSES.get(source_class)
    if source_class not in sentence_classes or source_class not in code_sentence_classes:
        results.append(
            _rejected(
                f"{subject}.classes",
                f"unknown source sentence class: {source_class}",
            )
        )
    elif complement_class not in sentence_classes or complement_class not in code_sentence_classes:
        results.append(
            _rejected(
                f"{subject}.classes",
                f"unknown complement sentence class: {complement_class}",
            )
        )
    elif expected_complement_class != complement_class:
        results.append(
            _rejected(
                f"{subject}.classes",
                f"expected complement class {expected_complement_class} but found {complement_class}",
            )
        )
    else:
        results.append(_accepted(f"{subject}.classes", f"{source_class} complements to {complement_class}"))

    try:
        observed_complement = complement_sentence(example.source_node)
        observed_source_code = encode_node(example.source_node, codebook)
        observed_complement_code = encode_node(observed_complement, codebook)
    except ValueError as exc:
        results.append(_rejected(f"{subject}.example", str(exc)))
        return results

    if _node_kind(example.source_node) != source_class:
        results.append(
            _rejected(
                f"{subject}.classes",
                "source node kind does not match source sentence class",
            )
        )
    elif observed_complement != example.expected_complement_node:
        results.append(_rejected(f"{subject}.example", "expected complement node mismatch"))
    elif observed_source_code != example.expected_source_code:
        results.append(_rejected(f"{subject}.example", "expected source code mismatch"))
    elif observed_complement_code != example.expected_complement_code:
        results.append(_rejected(f"{subject}.example", "expected complement code mismatch"))
    else:
        results.append(_accepted(f"{subject}.example", "complement example matches codebook"))

    if not example.non_claims:
        results.append(_rejected(f"{subject}.non_claims", "non-claims must be explicit"))
    else:
        results.append(_accepted(f"{subject}.non_claims", "non-claims are explicit"))
    return results


def _parse_example(item: dict[str, Any]) -> FormalComplementExample:
    return FormalComplementExample(
        example_id=_required_text(item, "example_id"),
        source_sentence_class=_required_text(item, "source_sentence_class"),
        complement_sentence_class=_required_text(item, "complement_sentence_class"),
        source_node=_required_node(item, "source_node"),
        expected_complement_node=_required_node(item, "expected_complement_node"),
        expected_source_code=tuple(_required_int_list(item, "expected_source_code")),
        expected_complement_code=tuple(_required_int_list(item, "expected_complement_code")),
        status=_required_text(item, "status"),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "formal-complement-willard-anchor"
    if subject.endswith(".status"):
        return "formal-complement-status"
    if subject.endswith(".classes"):
        return "formal-complement-class"
    if subject.endswith(".example") or subject.startswith("examples"):
        return "formal-complement-example"
    if subject in {"language", "codebook"}:
        return "formal-complement-dependency"
    if subject in {"language_path", "codebook_path"}:
        return "formal-complement-reference"
    if subject == "complement_kind":
        return "formal-complement-manifest"
    return "formal-complement"


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
    text_values: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        text_values.append(value)
    return text_values


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    value = item.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for list_item in value:
        if not isinstance(list_item, int) or isinstance(list_item, bool):
            raise ValueError(f"{key} contains non-integer item")
        result.append(list_item)
    return result


def _required_node(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required node missing: {key}")
    return value


def _node_kind(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ValueError("node missing kind")
    return kind


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> FormalComplementValidation:
    return FormalComplementValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> FormalComplementValidation:
    return FormalComplementValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_formal_complement_cli())
