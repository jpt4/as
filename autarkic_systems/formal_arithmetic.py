"""Syntax-only formal arithmetic language validation for AS.

This module names the first arithmetic syntax surface needed by later
Willard-style formal-confidence work. It deliberately stops at manifest
validation: there is no parser, evaluator, proof-code encoder, substitution
engine, or self-consistency theorem here.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SYNTAX_CLASSES = (
    "terms",
    "formulae",
    "sentences",
    "proof_objects",
)

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.6-LEVEL-K-CONSISTENCY",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.4-TYPE-NS-A-S-M",
    "W2020-T4.4-T4.5-LEM-BOUNDARY",
)


@dataclass(frozen=True)
class FormalArithmeticLanguage:
    """Loaded syntax-only arithmetic language manifest."""

    path: Path
    schema_version: int
    language_id: str
    reviewed_at: str
    purpose: str
    arithmetic_profile: str
    willard_anchor_ids: tuple[str, ...]
    syntax_classes: dict[str, Any]

    @property
    def bounded_formula_classes(self) -> tuple[str, ...]:
        """Return the named bounded formula classes in stable manifest order."""

        formulae = self.syntax_classes.get("formulae", {})
        if not isinstance(formulae, dict):
            return ()
        classes = formulae.get("bounded_formula_classes", {})
        if not isinstance(classes, dict):
            return ()
        return tuple(classes)

    @property
    def sentence_classes(self) -> tuple[str, ...]:
        """Return the named sentence classes in stable manifest order."""

        sentences = self.syntax_classes.get("sentences", {})
        if not isinstance(sentences, dict):
            return ()
        classes = sentences.get("classes", {})
        if not isinstance(classes, dict):
            return ()
        return tuple(classes)


@dataclass(frozen=True)
class FormalArithmeticValidation:
    """One validation result for the arithmetic language surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FormalArithmeticReport:
    """Validation report for a formal arithmetic language manifest."""

    language: FormalArithmeticLanguage
    willard_map_path: Path
    results: tuple[FormalArithmeticValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every validation result accepted."""

        return all(result.accepted for result in self.results)

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


def load_formal_arithmetic_language(
    path: Path | str = DEFAULT_LANGUAGE,
) -> FormalArithmeticLanguage:
    """Load the formal arithmetic language manifest from JSON."""

    language_path = Path(path)
    data = json.loads(language_path.read_text(encoding="utf-8"))
    return FormalArithmeticLanguage(
        path=language_path,
        schema_version=_required_int(data, "schema_version"),
        language_id=_required_text(data, "language_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        arithmetic_profile=_required_text(data, "arithmetic_profile"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        syntax_classes=_required_mapping(data, "syntax_classes"),
    )


def validate_formal_arithmetic_language(
    language: FormalArithmeticLanguage,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FormalArithmeticReport:
    """Validate a syntax-only arithmetic language against Willard anchors."""

    map_path = Path(willard_map_path)
    willard_map = load_willard_definition_map(map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    results: list[FormalArithmeticValidation] = [
        _accepted("language", f"loaded {language.language_id}")
    ]

    results.extend(_validate_profile(language))
    results.extend(_validate_willard_anchors(language, known_anchor_ids))
    results.extend(_validate_syntax_classes(language.syntax_classes))

    return FormalArithmeticReport(
        language=language,
        willard_map_path=map_path,
        results=tuple(results),
    )


def formal_arithmetic_report_payload(
    report: FormalArithmeticReport,
) -> dict[str, Any]:
    """Return a JSON-ready formal arithmetic validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.language.schema_version,
        "language_path": str(report.language.path),
        "language_id": report.language.language_id,
        "reviewed_at": report.language.reviewed_at,
        "purpose": report.language.purpose,
        "arithmetic_profile": report.language.arithmetic_profile,
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.language.willard_anchor_ids),
        "bounded_formula_classes": list(report.language.bounded_formula_classes),
        "sentence_classes": list(report.language.sentence_classes),
        "syntax_classes": list(report.language.syntax_classes),
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


def format_formal_arithmetic_report(report: FormalArithmeticReport) -> str:
    """Format a concise human-readable formal arithmetic report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Formal arithmetic language: {status}",
        f"Language: {report.language.language_id}",
        f"Arithmetic profile: {report.language.arithmetic_profile}",
        "Syntax classes: " + _joined_or_none(tuple(report.language.syntax_classes)),
        "Bounded formula classes: "
        + _joined_or_none(report.language.bounded_formula_classes),
        "Sentence classes: " + _joined_or_none(report.language.sentence_classes),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
        "Validation:",
    ]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_formal_arithmetic_cli(argv: list[str] | None = None) -> int:
    """Run the formal arithmetic language validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_arithmetic",
        description="Validate the AS syntax-only formal arithmetic language.",
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

    language = load_formal_arithmetic_language(args.language)
    report = validate_formal_arithmetic_language(language, args.willard_map)
    if args.format == "json":
        print(json.dumps(formal_arithmetic_report_payload(report), sort_keys=True))
    else:
        print(format_formal_arithmetic_report(report))
    return 0 if report.accepted else 1


def _validate_profile(
    language: FormalArithmeticLanguage,
) -> list[FormalArithmeticValidation]:
    if language.arithmetic_profile == "Type-NS":
        return [_accepted("arithmetic_profile", "Type-NS profile selected")]
    return [
        _rejected(
            "arithmetic_profile",
            f"unsupported arithmetic profile: {language.arithmetic_profile}",
        )
    ]


def _validate_willard_anchors(
    language: FormalArithmeticLanguage,
    known_anchor_ids: set[str],
) -> list[FormalArithmeticValidation]:
    unknown_anchor_ids = sorted(set(language.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(language.willard_anchor_ids)
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


def _validate_syntax_classes(
    syntax_classes: dict[str, Any],
) -> list[FormalArithmeticValidation]:
    results: list[FormalArithmeticValidation] = []
    missing = [
        class_name
        for class_name in REQUIRED_SYNTAX_CLASSES
        if class_name not in syntax_classes
    ]
    if missing:
        results.append(
            _rejected(
                "syntax_classes",
                "missing syntax classes: " + ", ".join(missing),
            )
        )
    else:
        results.append(_accepted("syntax_classes", "required syntax classes present"))

    terms = syntax_classes.get("terms")
    if isinstance(terms, dict):
        results.extend(_validate_terms(terms))
    formulae = syntax_classes.get("formulae")
    if isinstance(formulae, dict):
        results.extend(_validate_formulae(formulae))
    sentences = syntax_classes.get("sentences")
    if isinstance(sentences, dict):
        results.extend(_validate_sentences(sentences))
    proof_objects = syntax_classes.get("proof_objects")
    if isinstance(proof_objects, dict):
        results.extend(_validate_proof_objects(proof_objects))
    return results


def _validate_terms(terms: dict[str, Any]) -> list[FormalArithmeticValidation]:
    results: list[FormalArithmeticValidation] = []
    if _non_empty_text_list(terms.get("examples")):
        results.append(_accepted("terms.examples", "term examples present"))
    else:
        results.append(_rejected("terms.examples", "terms must include examples"))

    function_symbols = terms.get("function_symbols")
    if isinstance(function_symbols, dict) and "successor" in function_symbols:
        results.append(
            _accepted("terms.function_symbols", "successor symbol is named")
        )
    else:
        results.append(
            _rejected("terms.function_symbols", "successor symbol is required")
        )
    return results


def _validate_formulae(formulae: dict[str, Any]) -> list[FormalArithmeticValidation]:
    results: list[FormalArithmeticValidation] = []
    bounded_classes = formulae.get("bounded_formula_classes")
    if not isinstance(bounded_classes, dict):
        return [
            _rejected(
                "bounded_formula_classes",
                "bounded formula classes must be a mapping",
            )
        ]

    delta0 = bounded_classes.get("delta0")
    if not isinstance(delta0, dict):
        results.append(
            _rejected("bounded_formula_classes.delta0", "delta0 must be named")
        )
    elif _non_empty_text_list(delta0.get("examples")):
        results.append(
            _accepted("bounded_formula_classes.delta0", "delta0 examples present")
        )
    else:
        results.append(
            _rejected(
                "bounded_formula_classes.delta0",
                "delta0 must include examples",
            )
        )
    return results


def _validate_sentences(
    sentences: dict[str, Any],
) -> list[FormalArithmeticValidation]:
    classes = sentences.get("classes")
    if not isinstance(classes, dict):
        return [_rejected("sentence_classes", "sentence classes must be a mapping")]

    results: list[FormalArithmeticValidation] = []
    for class_name in ("pi1", "sigma1"):
        sentence_class = classes.get(class_name)
        if not isinstance(sentence_class, dict):
            results.append(
                _rejected("sentence_classes", f"missing sentence class: {class_name}")
            )
        elif _non_empty_text_list(sentence_class.get("examples")):
            results.append(
                _accepted(
                    f"sentence_classes.{class_name}",
                    f"{class_name} examples present",
                )
            )
        else:
            results.append(
                _rejected(
                    f"sentence_classes.{class_name}",
                    f"{class_name} must include examples",
                )
            )
    return results


def _validate_proof_objects(
    proof_objects: dict[str, Any],
) -> list[FormalArithmeticValidation]:
    status = proof_objects.get("status")
    blocked_by = proof_objects.get("blocked_by")
    if status == "placeholder-only" and _non_empty_text_list(blocked_by):
        return [
            _accepted(
                "proof_objects",
                "proof objects are explicitly placeholder-only",
            )
        ]
    return [
        _rejected(
            "proof_objects",
            "proof objects must remain placeholder-only and name blockers",
        )
    ]


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "formal-arithmetic-willard-anchor"
    if subject in {"syntax_classes", "terms.examples", "terms.function_symbols"}:
        return "formal-arithmetic-syntax"
    if subject.startswith("bounded_formula_classes"):
        return "formal-arithmetic-bounded-formula"
    if subject.startswith("sentence_classes"):
        return "formal-arithmetic-sentence"
    if subject == "proof_objects":
        return "formal-arithmetic-proof-object"
    if subject == "arithmetic_profile":
        return "formal-arithmetic-profile"
    return "formal-arithmetic-language"


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


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    values = item.get(key)
    if not isinstance(values, list) or not values:
        raise ValueError(f"required list field missing: {key}")
    text_values: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        text_values.append(value)
    return text_values


def _required_mapping(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required mapping field missing: {key}")
    return value


def _non_empty_text_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> FormalArithmeticValidation:
    return FormalArithmeticValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> FormalArithmeticValidation:
    return FormalArithmeticValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_formal_arithmetic_cli())
