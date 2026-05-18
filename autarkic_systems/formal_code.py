"""First AS formal proof-code encoding surface.

The encoder in this module is deliberately small and inspectable. It encodes
the ADR-0226 formal arithmetic node vocabulary as tagged natural-number
sequences and decodes those sequences back to canonical node dictionaries.
This is proof-code infrastructure only; it is not a proof checker, deduction
apparatus, substitution engine, arithmetic sequence theory, or
self-reference theorem.
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
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_CODEBOOK = Path("language/formal_codebook.json")
DEFAULT_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CODEBOOK_SECTIONS = (
    "variable_codes",
    "term_tags",
    "formula_tags",
    "sentence_tags",
    "proof_line_tags",
    "proof_rule_codes",
    "examples",
)

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.4-TYPE-NS-A-S-M",
)

VALID_ENCODING_KIND = "tagged-prefix-natural-sequence"


@dataclass(frozen=True)
class FormalCodeExample:
    """One checked codebook example with its expected code sequence."""

    example_id: str
    node: dict[str, Any]
    expected_code: tuple[int, ...]


@dataclass(frozen=True)
class FormalCodebook:
    """Loaded manifest for the first formal proof-code codebook."""

    path: Path
    schema_version: int
    codebook_id: str
    reviewed_at: str
    purpose: str
    language_id: str
    encoding_kind: str
    willard_anchor_ids: tuple[str, ...]
    variable_codes: dict[str, int]
    term_tags: dict[str, int]
    formula_tags: dict[str, int]
    sentence_tags: dict[str, int]
    proof_line_tags: dict[str, int]
    proof_rule_codes: dict[str, int]
    examples: tuple[FormalCodeExample, ...]


@dataclass(frozen=True)
class FormalCodeValidation:
    """One validation result for the formal codebook surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FormalCodeReport:
    """Validation report for the formal proof-code codebook."""

    codebook: FormalCodebook
    language_path: Path
    willard_map_path: Path
    results: tuple[FormalCodeValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every codebook validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def example_count(self) -> int:
        """Return the number of checked examples in the codebook."""

        return len(self.codebook.examples)

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


def load_formal_codebook(path: Path | str = DEFAULT_CODEBOOK) -> FormalCodebook:
    """Load the formal proof-code codebook manifest from JSON."""

    codebook_path = Path(path)
    data = json.loads(codebook_path.read_text(encoding="utf-8"))
    return FormalCodebook(
        path=codebook_path,
        schema_version=_required_int(data, "schema_version"),
        codebook_id=_required_text(data, "codebook_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        language_id=_required_text(data, "language_id"),
        encoding_kind=_required_text(data, "encoding_kind"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        variable_codes=_required_code_mapping(data, "variable_codes"),
        term_tags=_required_code_mapping(data, "term_tags"),
        formula_tags=_required_code_mapping(data, "formula_tags"),
        sentence_tags=_required_code_mapping(data, "sentence_tags"),
        proof_line_tags=_required_code_mapping(data, "proof_line_tags"),
        proof_rule_codes=_required_code_mapping(data, "proof_rule_codes"),
        examples=tuple(_parse_example(item) for item in _required_list(data, "examples")),
    )


def validate_formal_codebook(
    codebook: FormalCodebook,
    language_path: Path | str = DEFAULT_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FormalCodeReport:
    """Validate a formal codebook against language and Willard anchors."""

    checked_language_path = Path(language_path)
    checked_willard_map_path = Path(willard_map_path)
    language = load_formal_arithmetic_language(checked_language_path)
    language_report = validate_formal_arithmetic_language(
        language,
        checked_willard_map_path,
    )
    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}

    results: list[FormalCodeValidation] = [
        _accepted("codebook", f"loaded {codebook.codebook_id}")
    ]
    results.extend(_validate_language_reference(codebook, language, language_report))
    results.extend(_validate_encoding_kind(codebook))
    results.extend(_validate_willard_anchors(codebook, known_anchor_ids))
    results.extend(_validate_tags(codebook))
    results.extend(_validate_examples(codebook))

    return FormalCodeReport(
        codebook=codebook,
        language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
    )


def encode_node(node: dict[str, Any], codebook: FormalCodebook) -> tuple[int, ...]:
    """Encode a canonical formal node into a tagged natural-number sequence."""

    kind = _node_kind(node)
    if kind == "variable":
        return (codebook.term_tags["variable"], _variable_code(node, codebook))
    if kind == "zero":
        return (codebook.term_tags["zero"],)
    if kind == "sequence_nil":
        return (codebook.term_tags["sequence_nil"],)
    if kind == "successor":
        return (
            codebook.term_tags["successor"],
            *encode_node(_required_node(node, "term"), codebook),
        )
    if kind == "sequence_cons":
        return (
            codebook.term_tags["sequence_cons"],
            *encode_node(_required_node(node, "head"), codebook),
            *encode_node(_required_node(node, "tail"), codebook),
        )
    if kind in {"addition", "multiplication"}:
        return (
            codebook.term_tags[kind],
            *encode_node(_required_node(node, "left"), codebook),
            *encode_node(_required_node(node, "right"), codebook),
        )
    if kind in {"equals", "less_than", "and", "or", "implies"}:
        return (
            codebook.formula_tags[kind],
            *encode_node(_required_node(node, "left"), codebook),
            *encode_node(_required_node(node, "right"), codebook),
        )
    if kind == "not":
        return (
            codebook.formula_tags["not"],
            *encode_node(_required_node(node, "body"), codebook),
        )
    if kind in {"forall", "exists"}:
        return (
            codebook.formula_tags[kind],
            _variable_code(node, codebook),
            *encode_node(_required_node(node, "body"), codebook),
        )
    if kind in {"bounded_forall", "bounded_exists"}:
        return (
            codebook.formula_tags[kind],
            _variable_code(node, codebook),
            *encode_node(_required_node(node, "bound"), codebook),
            *encode_node(_required_node(node, "body"), codebook),
        )
    if kind in {"pi1", "sigma1"}:
        return (
            codebook.sentence_tags[kind],
            _variable_code(node, codebook),
            *encode_node(_required_node(node, "body"), codebook),
        )
    if kind == "proof_line":
        premises = _required_int_list(node, "premises")
        return (
            codebook.proof_line_tags["proof_line"],
            _required_positive_int(node, "line"),
            _proof_rule_code(node, codebook),
            *encode_node(_required_node(node, "formula"), codebook),
            len(premises),
            *premises,
        )
    raise ValueError(f"unknown node kind: {kind}")


def decode_code(
    code: tuple[int, ...] | list[int],
    codebook: FormalCodebook,
) -> dict[str, Any]:
    """Decode a complete tagged natural-number sequence into a formal node."""

    tokens = tuple(code)
    if not tokens or not all(isinstance(token, int) and token >= 0 for token in tokens):
        raise ValueError("code must be a non-empty sequence of natural numbers")
    node, index = _decode_at(tokens, 0, codebook)
    if index != len(tokens):
        raise ValueError("trailing code tokens")
    return node


def formal_code_report_payload(report: FormalCodeReport) -> dict[str, Any]:
    """Return a JSON-ready formal codebook validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.codebook.schema_version,
        "codebook_path": str(report.codebook.path),
        "codebook_id": report.codebook.codebook_id,
        "reviewed_at": report.codebook.reviewed_at,
        "purpose": report.codebook.purpose,
        "language_path": str(report.language_path),
        "language_id": report.codebook.language_id,
        "encoding_kind": report.codebook.encoding_kind,
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.codebook.willard_anchor_ids),
        "term_tags": dict(report.codebook.term_tags),
        "formula_tags": dict(report.codebook.formula_tags),
        "sentence_tags": dict(report.codebook.sentence_tags),
        "proof_line_tags": dict(report.codebook.proof_line_tags),
        "proof_rule_codes": dict(report.codebook.proof_rule_codes),
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


def format_formal_code_report(report: FormalCodeReport) -> str:
    """Format a concise human-readable formal codebook report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Formal codebook: {status}",
        f"Codebook: {report.codebook.codebook_id}",
        f"Language: {report.codebook.language_id}",
        f"Encoding: {report.codebook.encoding_kind}",
        f"Examples: {report.example_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
        "Validation:",
    ]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_formal_code_cli(argv: list[str] | None = None) -> int:
    """Run the formal proof-code codebook validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_code",
        description="Validate the AS formal proof-code codebook.",
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

    codebook = load_formal_codebook(args.codebook)
    report = validate_formal_codebook(codebook, args.language, args.willard_map)
    if args.format == "json":
        print(json.dumps(formal_code_report_payload(report), sort_keys=True))
    else:
        print(format_formal_code_report(report))
    return 0 if report.accepted else 1


def _validate_language_reference(
    codebook: FormalCodebook,
    language: Any,
    language_report: Any,
) -> list[FormalCodeValidation]:
    if codebook.language_id != language.language_id:
        return [
            _rejected(
                "language",
                f"codebook language {codebook.language_id} does not match "
                f"{language.language_id}",
            )
        ]
    if not language_report.accepted:
        return [
            _rejected(
                "language",
                "formal arithmetic language rejected: "
                + _joined_or_none(language_report.failed_subjects),
            )
        ]
    return [_accepted("language", "formal arithmetic language accepted")]


def _validate_encoding_kind(codebook: FormalCodebook) -> list[FormalCodeValidation]:
    if codebook.encoding_kind == VALID_ENCODING_KIND:
        return [_accepted("encoding_kind", VALID_ENCODING_KIND)]
    return [
        _rejected(
            "encoding_kind",
            f"unknown encoding kind: {codebook.encoding_kind}",
        )
    ]


def _validate_willard_anchors(
    codebook: FormalCodebook,
    known_anchor_ids: set[str],
) -> list[FormalCodeValidation]:
    unknown_anchor_ids = sorted(set(codebook.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(codebook.willard_anchor_ids)
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


def _validate_tags(codebook: FormalCodebook) -> list[FormalCodeValidation]:
    results: list[FormalCodeValidation] = []
    required_tags = {
        "term_tags": (
            "variable",
            "zero",
            "successor",
            "addition",
            "multiplication",
            "sequence_nil",
            "sequence_cons",
        ),
        "formula_tags": (
            "equals",
            "less_than",
            "not",
            "and",
            "or",
            "implies",
            "forall",
            "exists",
            "bounded_forall",
            "bounded_exists",
        ),
        "sentence_tags": ("pi1", "sigma1"),
        "proof_line_tags": ("proof_line",),
    }
    tag_maps = {
        "term_tags": codebook.term_tags,
        "formula_tags": codebook.formula_tags,
        "sentence_tags": codebook.sentence_tags,
        "proof_line_tags": codebook.proof_line_tags,
    }

    for subject, required_names in required_tags.items():
        missing_names = [name for name in required_names if name not in tag_maps[subject]]
        if missing_names:
            results.append(
                _rejected(subject, "missing tags: " + ", ".join(missing_names))
            )
        else:
            results.append(_accepted(subject, "required tags present"))

    tag_values: list[int] = []
    for tag_map in tag_maps.values():
        tag_values.extend(tag_map.values())
    duplicate_values = _duplicates(tag_values)
    if duplicate_values:
        results.append(
            _rejected(
                "tag_values",
                "duplicate code values: "
                + ", ".join(str(value) for value in duplicate_values),
            )
        )
    else:
        results.append(_accepted("tag_values", "tag code values are unique"))

    return results


def _validate_examples(codebook: FormalCodebook) -> list[FormalCodeValidation]:
    if not codebook.examples:
        return [_rejected("examples", "codebook must include examples")]

    failures: list[FormalCodeValidation] = []
    for example in codebook.examples:
        try:
            encoded = encode_node(example.node, codebook)
            if encoded != example.expected_code:
                failures.append(
                    _rejected(
                        f"example.{example.example_id}",
                        "expected code mismatch: expected "
                        + _format_code(example.expected_code)
                        + " got "
                        + _format_code(encoded),
                    )
                )
                continue
            decoded = decode_code(encoded, codebook)
            if decoded != example.node:
                failures.append(
                    _rejected(
                        f"example.{example.example_id}",
                        "round trip mismatch",
                    )
                )
        except ValueError as exc:
            failures.append(_rejected(f"example.{example.example_id}", str(exc)))
    if failures:
        return failures
    return [_accepted("examples", f"round-tripped {len(codebook.examples)} example(s)")]


def _decode_at(
    tokens: tuple[int, ...],
    index: int,
    codebook: FormalCodebook,
) -> tuple[dict[str, Any], int]:
    if index >= len(tokens):
        raise ValueError("unexpected end of code")
    tag = tokens[index]
    index += 1

    reverse_term_tags = _reverse_mapping(codebook.term_tags)
    reverse_formula_tags = _reverse_mapping(codebook.formula_tags)
    reverse_sentence_tags = _reverse_mapping(codebook.sentence_tags)
    reverse_proof_line_tags = _reverse_mapping(codebook.proof_line_tags)
    reverse_variables = _reverse_mapping(codebook.variable_codes)
    reverse_rules = _reverse_mapping(codebook.proof_rule_codes)

    if tag in reverse_term_tags:
        return _decode_term(tag, tokens, index, codebook, reverse_term_tags, reverse_variables)
    if tag in reverse_formula_tags:
        return _decode_formula(tag, tokens, index, codebook, reverse_formula_tags, reverse_variables)
    if tag in reverse_sentence_tags:
        return _decode_sentence(tag, tokens, index, codebook, reverse_sentence_tags, reverse_variables)
    if tag in reverse_proof_line_tags:
        return _decode_proof_line(tokens, index, codebook, reverse_rules)
    raise ValueError(f"unknown code tag: {tag}")


def _decode_term(
    tag: int,
    tokens: tuple[int, ...],
    index: int,
    codebook: FormalCodebook,
    reverse_term_tags: dict[int, str],
    reverse_variables: dict[int, str],
) -> tuple[dict[str, Any], int]:
    kind = reverse_term_tags[tag]
    if kind == "variable":
        variable_code, index = _take_token(tokens, index, "variable code")
        if variable_code not in reverse_variables:
            raise ValueError(f"unknown variable code: {variable_code}")
        return {"kind": "variable", "name": reverse_variables[variable_code]}, index
    if kind == "zero":
        return {"kind": "zero"}, index
    if kind == "sequence_nil":
        return {"kind": "sequence_nil"}, index
    if kind == "successor":
        term, index = _decode_at(tokens, index, codebook)
        return {"kind": "successor", "term": term}, index
    if kind == "sequence_cons":
        head, index = _decode_at(tokens, index, codebook)
        tail, index = _decode_at(tokens, index, codebook)
        return {"kind": "sequence_cons", "head": head, "tail": tail}, index
    if kind in {"addition", "multiplication"}:
        left, index = _decode_at(tokens, index, codebook)
        right, index = _decode_at(tokens, index, codebook)
        return {"kind": kind, "left": left, "right": right}, index
    raise ValueError(f"unknown term tag: {tag}")


def _decode_formula(
    tag: int,
    tokens: tuple[int, ...],
    index: int,
    codebook: FormalCodebook,
    reverse_formula_tags: dict[int, str],
    reverse_variables: dict[int, str],
) -> tuple[dict[str, Any], int]:
    kind = reverse_formula_tags[tag]
    if kind in {"equals", "less_than", "and", "or", "implies"}:
        left, index = _decode_at(tokens, index, codebook)
        right, index = _decode_at(tokens, index, codebook)
        return {"kind": kind, "left": left, "right": right}, index
    if kind == "not":
        body, index = _decode_at(tokens, index, codebook)
        return {"kind": "not", "body": body}, index
    if kind in {"forall", "exists"}:
        variable, index = _decode_variable_code(tokens, index, reverse_variables)
        body, index = _decode_at(tokens, index, codebook)
        return {"kind": kind, "variable": variable, "body": body}, index
    if kind in {"bounded_forall", "bounded_exists"}:
        variable, index = _decode_variable_code(tokens, index, reverse_variables)
        bound, index = _decode_at(tokens, index, codebook)
        body, index = _decode_at(tokens, index, codebook)
        return {
            "kind": kind,
            "variable": variable,
            "bound": bound,
            "body": body,
        }, index
    raise ValueError(f"unknown formula tag: {tag}")


def _decode_sentence(
    tag: int,
    tokens: tuple[int, ...],
    index: int,
    codebook: FormalCodebook,
    reverse_sentence_tags: dict[int, str],
    reverse_variables: dict[int, str],
) -> tuple[dict[str, Any], int]:
    kind = reverse_sentence_tags[tag]
    variable, index = _decode_variable_code(tokens, index, reverse_variables)
    body, index = _decode_at(tokens, index, codebook)
    return {"kind": kind, "variable": variable, "body": body}, index


def _decode_proof_line(
    tokens: tuple[int, ...],
    index: int,
    codebook: FormalCodebook,
    reverse_rules: dict[int, str],
) -> tuple[dict[str, Any], int]:
    line, index = _take_token(tokens, index, "line")
    if line <= 0:
        raise ValueError("line must be positive")
    rule_code, index = _take_token(tokens, index, "proof rule")
    if rule_code not in reverse_rules:
        raise ValueError(f"unknown proof rule code: {rule_code}")
    formula, index = _decode_at(tokens, index, codebook)
    premise_count, index = _take_token(tokens, index, "premise count")
    if premise_count < 0:
        raise ValueError("premise count must be non-negative")
    premises: list[int] = []
    for _ in range(premise_count):
        premise, index = _take_token(tokens, index, "premise")
        if premise <= 0:
            raise ValueError("premises must be positive")
        premises.append(premise)
    return {
        "kind": "proof_line",
        "line": line,
        "rule": reverse_rules[rule_code],
        "formula": formula,
        "premises": premises,
    }, index


def _parse_example(item: dict[str, Any]) -> FormalCodeExample:
    node = item.get("node")
    if not isinstance(node, dict):
        raise ValueError("codebook example must contain node")
    return FormalCodeExample(
        example_id=_required_text(item, "example_id"),
        node=node,
        expected_code=tuple(_required_int_list(item, "expected_code")),
    )


def _node_kind(node: dict[str, Any]) -> str:
    return _required_text(node, "kind")


def _variable_code(node: dict[str, Any], codebook: FormalCodebook) -> int:
    variable = _required_text(node, "variable" if "variable" in node else "name")
    if variable not in codebook.variable_codes:
        raise ValueError(f"unknown variable: {variable}")
    return codebook.variable_codes[variable]


def _proof_rule_code(node: dict[str, Any], codebook: FormalCodebook) -> int:
    rule = _required_text(node, "rule")
    if rule not in codebook.proof_rule_codes:
        raise ValueError(f"unknown proof rule: {rule}")
    return codebook.proof_rule_codes[rule]


def _required_node(node: dict[str, Any], key: str) -> dict[str, Any]:
    value = node.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required node field missing: {key}")
    return value


def _required_positive_int(node: dict[str, Any], key: str) -> int:
    value = node.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"required positive integer field missing: {key}")
    return value


def _required_int_list(node: dict[str, Any], key: str) -> list[int]:
    value = node.get(key)
    if not isinstance(value, list):
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool):
            raise ValueError(f"{key} contains non-integer item")
        result.append(item)
    return result


def _decode_variable_code(
    tokens: tuple[int, ...],
    index: int,
    reverse_variables: dict[int, str],
) -> tuple[str, int]:
    variable_code, index = _take_token(tokens, index, "variable code")
    if variable_code not in reverse_variables:
        raise ValueError(f"unknown variable code: {variable_code}")
    return reverse_variables[variable_code], index


def _take_token(
    tokens: tuple[int, ...],
    index: int,
    subject: str,
) -> tuple[int, int]:
    if index >= len(tokens):
        raise ValueError(f"missing {subject}")
    return tokens[index], index + 1


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"language", "codebook", "encoding_kind"}:
        return "formal-codebook-manifest"
    if subject == "willard_anchors":
        return "formal-codebook-willard-anchor"
    if subject.endswith("_tags") or subject == "tag_values":
        return "formal-codebook-tag"
    if subject.startswith("example") or subject == "examples":
        return "formal-codebook-example"
    return "formal-codebook"


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


def _required_code_mapping(item: dict[str, Any], key: str) -> dict[str, int]:
    value = item.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"required code mapping missing: {key}")
    result: dict[str, int] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"{key} contains non-text key")
        if not isinstance(map_value, int) or isinstance(map_value, bool) or map_value <= 0:
            raise ValueError(f"{key} contains non-positive integer code")
        result[map_key] = map_value
    return result


def _duplicates(values: list[int]) -> list[int]:
    seen: set[int] = set()
    repeated: set[int] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _reverse_mapping(mapping: dict[str, int]) -> dict[int, str]:
    return {value: key for key, value in mapping.items()}


def _format_code(code: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(value) for value in code) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> FormalCodeValidation:
    return FormalCodeValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> FormalCodeValidation:
    return FormalCodeValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_formal_code_cli())
