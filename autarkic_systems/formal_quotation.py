"""Formal quotation helpers for AS code-token numerals.

This module checks the first tiny piece of quotation machinery needed by
fixed-point work: turning natural-number code tokens into unary successor
numerals in the existing formal term language. It deliberately stops before
pair/list/sequence coding and does not construct a full quotation term for a
formula code.
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
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_EXAMPLES = Path("language/formal_quotation_examples.json")
DEFAULT_CODEBOOK = Path("language/formal_codebook.json")
DEFAULT_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
)
VALID_QUOTATION_KIND = "unary-successor-token-numerals"
VALID_SEQUENCE_STATUS = "token-numerals-only"


@dataclass(frozen=True)
class QuotationExample:
    """One checked quotation example for code-token numerals."""

    example_id: str
    token: int | None
    tokens: tuple[int, ...]
    expected_depth: int | None
    expected_code: tuple[int, ...]
    expected_token_count: int | None
    expected_first_token_depth: int | None
    expected_last_token_depth: int | None
    status: str | None


@dataclass(frozen=True)
class QuotationExampleSet:
    """Loaded quotation example manifest."""

    path: Path
    schema_version: int
    quotation_set_id: str
    reviewed_at: str
    purpose: str
    codebook_path: str
    fixed_point_targets_path: str
    quotation_kind: str
    willard_anchor_ids: tuple[str, ...]
    examples: tuple[QuotationExample, ...]


@dataclass(frozen=True)
class QuotationValidation:
    """One validation result for the quotation surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class QuotationReport:
    """Validation report for formal quotation examples."""

    examples: QuotationExampleSet
    codebook_path: Path
    language_path: Path
    willard_map_path: Path
    results: tuple[QuotationValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every quotation validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def example_count(self) -> int:
        """Return the number of checked quotation examples."""

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


def natural_to_numeral(value: int) -> dict[str, Any]:
    """Return the unary successor numeral for a natural number."""

    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("natural value must be an integer")
    if value < 0:
        raise ValueError("natural value must be nonnegative")
    node: dict[str, Any] = {"kind": "zero"}
    for _ in range(value):
        node = {"kind": "successor", "term": node}
    return node


def numeral_to_natural(node: dict[str, Any]) -> int:
    """Decode a unary successor numeral back to a natural number."""

    kind = _required_text(node, "kind")
    if kind == "zero":
        return 0
    if kind == "successor":
        return 1 + numeral_to_natural(_required_node(node, "term"))
    raise ValueError(f"node is not a unary numeral: {kind}")


def quote_code_tokens(tokens: tuple[int, ...] | list[int]) -> tuple[dict[str, Any], ...]:
    """Quote each code token as a unary successor numeral node."""

    if not isinstance(tokens, (tuple, list)) or not tokens:
        raise ValueError("code tokens must be a non-empty sequence")
    return tuple(natural_to_numeral(token) for token in tokens)


def load_quotation_examples(
    path: Path | str = DEFAULT_EXAMPLES,
) -> QuotationExampleSet:
    """Load checked quotation examples from JSON."""

    examples_path = Path(path)
    data = json.loads(examples_path.read_text(encoding="utf-8"))
    return QuotationExampleSet(
        path=examples_path,
        schema_version=_required_int(data, "schema_version"),
        quotation_set_id=_required_text(data, "quotation_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        codebook_path=_required_text(data, "codebook_path"),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        quotation_kind=_required_text(data, "quotation_kind"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        examples=tuple(
            _parse_example(item) for item in _required_list(data, "examples")
        ),
    )


def validate_quotation_examples(
    examples: QuotationExampleSet,
    codebook_path: Path | str = DEFAULT_CODEBOOK,
    language_path: Path | str = DEFAULT_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> QuotationReport:
    """Validate quotation examples against the formal codebook."""

    checked_codebook_path = Path(codebook_path)
    checked_language_path = Path(language_path)
    checked_willard_map_path = Path(willard_map_path)
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}

    results: list[QuotationValidation] = [
        _accepted("examples", f"loaded {len(examples.examples)} example(s)")
    ]
    results.extend(_validate_references(examples, checked_codebook_path))
    results.extend(_validate_codebook_report(codebook_report))
    results.extend(_validate_quotation_kind(examples))
    results.extend(_validate_willard_anchors(examples, known_anchor_ids))
    results.extend(_validate_examples(examples, codebook))

    return QuotationReport(
        examples=examples,
        codebook_path=checked_codebook_path,
        language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
    )


def quotation_report_payload(report: QuotationReport) -> dict[str, Any]:
    """Return a JSON-ready quotation validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.examples.schema_version,
        "examples_path": str(report.examples.path),
        "quotation_set_id": report.examples.quotation_set_id,
        "reviewed_at": report.examples.reviewed_at,
        "purpose": report.examples.purpose,
        "codebook_path": str(report.codebook_path),
        "fixed_point_targets_path": report.examples.fixed_point_targets_path,
        "language_path": str(report.language_path),
        "willard_map": str(report.willard_map_path),
        "quotation_kind": report.examples.quotation_kind,
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


def format_quotation_report(report: QuotationReport) -> str:
    """Format a concise human-readable quotation report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Formal quotation: {status}",
        f"Examples: {report.examples.quotation_set_id}",
        f"Codebook: {report.examples.codebook_path}",
        f"Quotation: {report.examples.quotation_kind}",
        f"Example count: {report.example_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
        "Validation:",
    ]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_quotation_cli(argv: list[str] | None = None) -> int:
    """Run the formal quotation validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_quotation",
        description="Validate AS formal quotation examples.",
    )
    parser.add_argument(
        "--examples",
        default=str(DEFAULT_EXAMPLES),
        help="Path to the formal quotation example manifest.",
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

    examples = load_quotation_examples(args.examples)
    report = validate_quotation_examples(
        examples,
        args.codebook,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(quotation_report_payload(report), sort_keys=True))
    else:
        print(format_quotation_report(report))
    return 0 if report.accepted else 1


def _validate_references(
    examples: QuotationExampleSet,
    codebook_path: Path,
) -> list[QuotationValidation]:
    results: list[QuotationValidation] = []
    if examples.codebook_path != str(codebook_path):
        results.append(
            _rejected(
                "codebook_path",
                f"expected {codebook_path} but found {examples.codebook_path}",
            )
        )
    else:
        results.append(_accepted("codebook_path", f"{codebook_path} referenced"))

    expected_fixed_point_path = "claims/fixed_point_targets.json"
    if examples.fixed_point_targets_path != expected_fixed_point_path:
        results.append(
            _rejected(
                "fixed_point_targets_path",
                "expected "
                + expected_fixed_point_path
                + " but found "
                + examples.fixed_point_targets_path,
            )
        )
    else:
        results.append(
            _accepted(
                "fixed_point_targets_path",
                expected_fixed_point_path + " referenced",
            )
        )
    return results


def _validate_codebook_report(codebook_report: Any) -> list[QuotationValidation]:
    if codebook_report.accepted:
        return [_accepted("codebook", "formal codebook accepted")]
    return [
        _rejected(
            "codebook",
            "formal codebook rejected: "
            + _joined_or_none(codebook_report.failed_subjects),
        )
    ]


def _validate_quotation_kind(
    examples: QuotationExampleSet,
) -> list[QuotationValidation]:
    if examples.quotation_kind == VALID_QUOTATION_KIND:
        return [_accepted("quotation_kind", VALID_QUOTATION_KIND)]
    return [
        _rejected(
            "quotation_kind",
            f"unknown quotation kind: {examples.quotation_kind}",
        )
    ]


def _validate_willard_anchors(
    examples: QuotationExampleSet,
    known_anchor_ids: set[str],
) -> list[QuotationValidation]:
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
    examples: QuotationExampleSet,
    codebook: Any,
) -> list[QuotationValidation]:
    if not examples.examples:
        return [_rejected("examples", "quotation examples must not be empty")]

    failures: list[QuotationValidation] = []
    for example in examples.examples:
        try:
            if example.token is not None:
                _validate_token_example(example, codebook)
            elif example.tokens:
                _validate_sequence_example(example)
            else:
                failures.append(
                    _rejected(f"example.{example.example_id}", "missing token data")
                )
        except ValueError as exc:
            failures.append(_rejected(f"example.{example.example_id}", str(exc)))
    if failures:
        return failures
    return [_accepted("examples", f"validated {len(examples.examples)} example(s)")]


def _validate_token_example(
    example: QuotationExample,
    codebook: Any,
) -> None:
    numeral = natural_to_numeral(_required_example_int(example.token, "token"))
    depth = numeral_to_natural(numeral)
    if example.expected_depth is None:
        raise ValueError("token example missing expected depth")
    if depth != example.expected_depth:
        raise ValueError(
            f"expected depth mismatch: expected {example.expected_depth} got {depth}"
        )
    encoded = encode_node(numeral, codebook)
    if encoded != example.expected_code:
        raise ValueError(
            "expected code mismatch: expected "
            + _format_code(example.expected_code)
            + " got "
            + _format_code(encoded)
        )
    decoded = decode_code(example.expected_code, codebook)
    if decoded != numeral:
        raise ValueError("expected code did not decode to expected numeral")


def _validate_sequence_example(example: QuotationExample) -> None:
    if example.status != VALID_SEQUENCE_STATUS:
        raise ValueError(f"unknown sequence status: {example.status}")
    numerals = quote_code_tokens(example.tokens)
    if example.expected_token_count is None:
        raise ValueError("sequence example missing expected token count")
    if len(numerals) != example.expected_token_count:
        raise ValueError(
            "expected token count mismatch: expected "
            + str(example.expected_token_count)
            + " got "
            + str(len(numerals))
        )
    if example.expected_first_token_depth is None:
        raise ValueError("sequence example missing expected first token depth")
    first_depth = numeral_to_natural(numerals[0])
    if first_depth != example.expected_first_token_depth:
        raise ValueError(
            "expected first token depth mismatch: expected "
            + str(example.expected_first_token_depth)
            + " got "
            + str(first_depth)
        )
    if example.expected_last_token_depth is None:
        raise ValueError("sequence example missing expected last token depth")
    last_depth = numeral_to_natural(numerals[-1])
    if last_depth != example.expected_last_token_depth:
        raise ValueError(
            "expected last token depth mismatch: expected "
            + str(example.expected_last_token_depth)
            + " got "
            + str(last_depth)
        )


def _parse_example(item: dict[str, Any]) -> QuotationExample:
    token = _optional_int(item, "token")
    tokens = tuple(_optional_int_list(item, "tokens"))
    return QuotationExample(
        example_id=_required_text(item, "example_id"),
        token=token,
        tokens=tokens,
        expected_depth=_optional_int(item, "expected_depth"),
        expected_code=tuple(_optional_int_list(item, "expected_code")),
        expected_token_count=_optional_int(item, "expected_token_count"),
        expected_first_token_depth=_optional_int(item, "expected_first_token_depth"),
        expected_last_token_depth=_optional_int(item, "expected_last_token_depth"),
        status=_optional_text(item, "status"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "formal-quotation-willard-anchor"
    if subject in {"codebook_path", "fixed_point_targets_path"}:
        return "formal-quotation-reference"
    if subject in {"codebook", "quotation_kind"}:
        return "formal-quotation-manifest"
    if subject.startswith("example") or subject == "examples":
        return "formal-quotation-example"
    return "formal-quotation"


def _required_example_int(value: int | None, key: str) -> int:
    if value is None:
        raise ValueError(f"example missing {key}")
    return value


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"required text field missing: {key}")
    return value


def _optional_text(item: dict[str, Any], key: str) -> str | None:
    value = item.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _optional_int(item: dict[str, Any], key: str) -> int | None:
    value = item.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
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


def _optional_int_list(item: dict[str, Any], key: str) -> list[int]:
    value = item.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    result: list[int] = []
    for list_item in value:
        if not isinstance(list_item, int) or isinstance(list_item, bool):
            raise ValueError(f"{key} contains non-integer item")
        result.append(list_item)
    return result


def _required_node(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required node field missing: {key}")
    return value


def _format_code(code: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(item) for item in code) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> QuotationValidation:
    return QuotationValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> QuotationValidation:
    return QuotationValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_quotation_cli())
