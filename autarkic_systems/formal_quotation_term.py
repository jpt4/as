"""Formal quotation term helpers for AS code-token sequences.

This module turns checked code-token sequences into nested formal term nodes:
``sequence_cons`` cells ending in ``sequence_nil``. The term surface is useful
for fixed-point work because it gives quotation a codebook-round-trippable term
shape, but it is still not a diagonal lemma or a proof that any sentence is a
fixed point of its own code.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_code import (
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation import (
    numeral_to_natural,
    quote_code_tokens,
)
from autarkic_systems.formal_quotation_sequence import (
    load_quotation_sequence_examples,
    validate_quotation_sequence_examples,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_EXAMPLES = Path("language/formal_quotation_term_examples.json")
DEFAULT_CODEBOOK = Path("language/formal_codebook.json")
DEFAULT_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
)
VALID_TERM_KIND = "nested-sequence-cons-term"
VALID_TERM_STATUS = "quotation-term-surface-only"


@dataclass(frozen=True)
class QuotationTermExample:
    """One checked quotation-term example."""

    example_id: str
    tokens: tuple[int, ...]
    expected_token_count: int
    expected_first_token_depth: int
    expected_last_token_depth: int
    status: str


@dataclass(frozen=True)
class QuotationTermExampleSet:
    """Loaded quotation-term examples."""

    path: Path
    schema_version: int
    term_set_id: str
    reviewed_at: str
    purpose: str
    codebook_path: str
    quotation_sequence_examples_path: str
    fixed_point_targets_path: str
    term_kind: str
    willard_anchor_ids: tuple[str, ...]
    examples: tuple[QuotationTermExample, ...]


@dataclass(frozen=True)
class QuotationTermValidation:
    """One validation result for the quotation-term surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class QuotationTermReport:
    """Validation report for quotation-term examples."""

    examples: QuotationTermExampleSet
    codebook_path: Path
    language_path: Path
    willard_map_path: Path
    results: tuple[QuotationTermValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every quotation-term validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def example_count(self) -> int:
        """Return the number of checked quotation-term examples."""

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


def quote_tokens_as_term(tokens: tuple[int, ...] | list[int]) -> dict[str, Any]:
    """Return a nested formal term quoting a non-empty token sequence."""

    numerals = quote_code_tokens(tokens)
    term: dict[str, Any] = {"kind": "sequence_nil"}
    for numeral in reversed(numerals):
        term = {
            "kind": "sequence_cons",
            "head": numeral,
            "tail": term,
        }
    return term


def load_quotation_term_examples(
    path: Path | str = DEFAULT_EXAMPLES,
) -> QuotationTermExampleSet:
    """Load checked quotation-term examples from JSON."""

    examples_path = Path(path)
    data = json.loads(examples_path.read_text(encoding="utf-8"))
    return QuotationTermExampleSet(
        path=examples_path,
        schema_version=_required_int(data, "schema_version"),
        term_set_id=_required_text(data, "term_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        codebook_path=_required_text(data, "codebook_path"),
        quotation_sequence_examples_path=_required_text(
            data,
            "quotation_sequence_examples_path",
        ),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        term_kind=_required_text(data, "term_kind"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        examples=tuple(
            _parse_example(item) for item in _required_list(data, "examples")
        ),
    )


def validate_quotation_term_examples(
    examples: QuotationTermExampleSet,
    codebook_path: Path | str = DEFAULT_CODEBOOK,
    language_path: Path | str = DEFAULT_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> QuotationTermReport:
    """Validate quotation-term examples against the codebook and dependencies."""

    checked_codebook_path = Path(codebook_path)
    checked_language_path = Path(language_path)
    checked_willard_map_path = Path(willard_map_path)
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    quotation_sequence = load_quotation_sequence_examples(
        examples.quotation_sequence_examples_path,
    )
    quotation_sequence_report = validate_quotation_sequence_examples(
        quotation_sequence,
        checked_codebook_path,
        checked_language_path,
        checked_willard_map_path,
    )
    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}

    results: list[QuotationTermValidation] = [
        _accepted("examples", f"loaded {len(examples.examples)} example(s)")
    ]
    results.extend(_validate_references(examples))
    results.extend(_validate_dependency_reports(codebook_report, quotation_sequence_report))
    results.extend(_validate_term_kind(examples))
    results.extend(_validate_willard_anchors(examples, known_anchor_ids))
    results.extend(_validate_examples(examples, codebook))

    return QuotationTermReport(
        examples=examples,
        codebook_path=checked_codebook_path,
        language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
    )


def quotation_term_report_payload(report: QuotationTermReport) -> dict[str, Any]:
    """Return a JSON-ready quotation-term validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.examples.schema_version,
        "examples_path": str(report.examples.path),
        "term_set_id": report.examples.term_set_id,
        "reviewed_at": report.examples.reviewed_at,
        "purpose": report.examples.purpose,
        "codebook_path": str(report.codebook_path),
        "quotation_sequence_examples_path": (
            report.examples.quotation_sequence_examples_path
        ),
        "fixed_point_targets_path": report.examples.fixed_point_targets_path,
        "language_path": str(report.language_path),
        "willard_map": str(report.willard_map_path),
        "term_kind": report.examples.term_kind,
        "willard_anchor_ids": list(report.examples.willard_anchor_ids),
        "example_count": report.example_count,
        "failed_subjects": list(report.failed_subjects),
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


def format_quotation_term_report(report: QuotationTermReport) -> str:
    """Format a concise human-readable quotation-term report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Formal quotation term: {status}",
        f"Examples: {report.examples.term_set_id}",
        f"Quotation sequence examples: {report.examples.quotation_sequence_examples_path}",
        f"Term kind: {report.examples.term_kind}",
        f"Example count: {report.example_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
        "Validation:",
    ]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_quotation_term_cli(argv: list[str] | None = None) -> int:
    """Run the quotation-term validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_quotation_term",
        description="Validate AS formal quotation-term examples.",
    )
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES),
        help="Path to the quotation-term example manifest.",
    )
    parser.add_argument(
        "--codebook",
        default=str(DEFAULT_CODEBOOK),
        help="Path to the formal codebook manifest.",
    )
    parser.add_argument(
        "--language",
        default=str(DEFAULT_LANGUAGE),
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

    examples = load_quotation_term_examples(args.examples)
    report = validate_quotation_term_examples(
        examples,
        args.codebook,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(quotation_term_report_payload(report), sort_keys=True))
    else:
        print(format_quotation_term_report(report))
    return 0 if report.accepted else 1


def _validate_references(
    examples: QuotationTermExampleSet,
) -> list[QuotationTermValidation]:
    expected = (
        ("codebook_path", examples.codebook_path, "language/formal_codebook.json"),
        (
            "quotation_sequence_examples_path",
            examples.quotation_sequence_examples_path,
            "language/formal_quotation_sequence_examples.json",
        ),
        (
            "fixed_point_targets_path",
            examples.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
    )
    results: list[QuotationTermValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    codebook_report: Any,
    quotation_sequence_report: Any,
) -> list[QuotationTermValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        (
            "quotation_sequence",
            quotation_sequence_report,
            "formal quotation sequence",
        ),
    )
    results: list[QuotationTermValidation] = []
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


def _validate_term_kind(
    examples: QuotationTermExampleSet,
) -> list[QuotationTermValidation]:
    if examples.term_kind == VALID_TERM_KIND:
        return [_accepted("term_kind", VALID_TERM_KIND)]
    return [_rejected("term_kind", f"unknown term kind: {examples.term_kind}")]


def _validate_willard_anchors(
    examples: QuotationTermExampleSet,
    known_anchor_ids: set[str],
) -> list[QuotationTermValidation]:
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
    examples: QuotationTermExampleSet,
    codebook: Any,
) -> list[QuotationTermValidation]:
    if not examples.examples:
        return [_rejected("examples", "quotation term examples must not be empty")]

    failures: list[QuotationTermValidation] = []
    for example in examples.examples:
        try:
            _validate_example(example, codebook)
        except ValueError as exc:
            failures.append(_rejected(f"example.{example.example_id}", str(exc)))
    if failures:
        return failures
    return [_accepted("examples", f"validated {len(examples.examples)} example(s)")]


def _validate_example(example: QuotationTermExample, codebook: Any) -> None:
    if example.status != VALID_TERM_STATUS:
        raise ValueError(f"unknown quotation term status: {example.status}")
    term = quote_tokens_as_term(example.tokens)
    encoded = encode_node(term, codebook)
    decoded = decode_code(encoded, codebook)
    if decoded != term:
        raise ValueError("quotation term code round trip mismatch")

    numerals = _sequence_term_numerals(term)
    token_count = len(numerals)
    if token_count != example.expected_token_count:
        raise ValueError(
            "expected token count mismatch: expected "
            + str(example.expected_token_count)
            + " got "
            + str(token_count)
        )
    first_depth = numeral_to_natural(numerals[0])
    if first_depth != example.expected_first_token_depth:
        raise ValueError(
            "expected first token depth mismatch: expected "
            + str(example.expected_first_token_depth)
            + " got "
            + str(first_depth)
        )
    last_depth = numeral_to_natural(numerals[-1])
    if last_depth != example.expected_last_token_depth:
        raise ValueError(
            "expected last token depth mismatch: expected "
            + str(example.expected_last_token_depth)
            + " got "
            + str(last_depth)
        )


def _sequence_term_numerals(term: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    numerals: list[dict[str, Any]] = []
    cursor = term
    while True:
        kind = cursor.get("kind")
        if kind == "sequence_nil":
            break
        if kind != "sequence_cons":
            raise ValueError(f"unexpected quotation term node: {kind}")
        head = cursor.get("head")
        tail = cursor.get("tail")
        if not isinstance(head, dict) or not isinstance(tail, dict):
            raise ValueError("sequence_cons must contain head and tail nodes")
        numerals.append(head)
        cursor = tail
    if not numerals:
        raise ValueError("quotation term must contain at least one numeral")
    return tuple(numerals)


def _parse_example(item: dict[str, Any]) -> QuotationTermExample:
    return QuotationTermExample(
        example_id=_required_text(item, "example_id"),
        tokens=tuple(_required_int_list(item, "tokens")),
        expected_token_count=_required_int(item, "expected_token_count"),
        expected_first_token_depth=_required_int(item, "expected_first_token_depth"),
        expected_last_token_depth=_required_int(item, "expected_last_token_depth"),
        status=_required_text(item, "status"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "formal-quotation-term-willard-anchor"
    if subject in {
        "codebook_path",
        "quotation_sequence_examples_path",
        "fixed_point_targets_path",
    }:
        return "formal-quotation-term-reference"
    if subject in {"codebook", "quotation_sequence", "term_kind"}:
        return "formal-quotation-term-manifest"
    if subject.startswith("example") or subject == "examples":
        return "formal-quotation-term-example"
    return "formal-quotation-term"


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


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> QuotationTermValidation:
    return QuotationTermValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> QuotationTermValidation:
    return QuotationTermValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_quotation_term_cli())
