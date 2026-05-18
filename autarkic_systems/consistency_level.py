"""Checked consistency-level target selection for AS.

This module chooses the first consistency notion that later formal-confidence
work must target. It validates a manifest selecting Level-1 consistency over
the existing arithmetic language, codebook, and substitution surface. It does
not prove consistency, implement a deduction apparatus, or construct a
self-referential sentence.
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
from autarkic_systems.formal_code import load_formal_codebook, validate_formal_codebook
from autarkic_systems.formal_complement import (
    load_formal_complement_examples,
    validate_formal_complement_examples,
)
from autarkic_systems.formal_substitution import (
    load_substitution_examples,
    validate_substitution_examples,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_TARGETS = Path("claims/consistency_level_targets.json")
DEFAULT_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_CODEBOOK = Path("language/formal_codebook.json")
DEFAULT_SUBSTITUTION = Path("language/formal_substitution_examples.json")
DEFAULT_COMPLEMENT = Path("language/formal_complement_examples.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D5.6-LEVEL-K-CONSISTENCY",
    "W2011-D5.7-SELFCONSK",
)

VALID_TARGET_STATUSES = {
    "target-selected-not-claimed",
}


@dataclass(frozen=True)
class ConsistencyLevelTarget:
    """One selected consistency-level target, not a proved theorem."""

    target_id: str
    level: int
    notion: str
    statement_class: str
    negation_class: str
    proof_code_source: str
    substitution_source: str
    complement_source: str
    status: str
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class ConsistencyLevelManifest:
    """Loaded manifest selecting the first AS consistency notion."""

    path: Path
    schema_version: int
    target_set_id: str
    reviewed_at: str
    purpose: str
    language_path: str
    codebook_path: str
    substitution_examples_path: str
    complement_examples_path: str
    willard_anchor_ids: tuple[str, ...]
    targets: tuple[ConsistencyLevelTarget, ...]


@dataclass(frozen=True)
class ConsistencyLevelValidation:
    """One validation result for consistency-level target selection."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class ConsistencyLevelReport:
    """Validation report over consistency-level targets."""

    manifest: ConsistencyLevelManifest
    language_path: Path
    codebook_path: Path
    substitution_path: Path
    complement_path: Path
    willard_map_path: Path
    results: tuple[ConsistencyLevelValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every consistency-level validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def target_count(self) -> int:
        """Return the number of checked consistency-level targets."""

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


@dataclass(frozen=True)
class _DependencyFailure:
    """Minimal report-shaped object for failed dependency loading."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    detail: str


def load_consistency_level_targets(
    path: Path | str = DEFAULT_TARGETS,
) -> ConsistencyLevelManifest:
    """Load consistency-level targets from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return ConsistencyLevelManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        target_set_id=_required_text(data, "target_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        language_path=_required_text(data, "language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        substitution_examples_path=_required_text(data, "substitution_examples_path"),
        complement_examples_path=_required_text(data, "complement_examples_path"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        targets=tuple(_parse_target(item) for item in _required_list(data, "targets")),
    )


def validate_consistency_level_targets(
    manifest: ConsistencyLevelManifest,
    language_path: Path | str = DEFAULT_LANGUAGE,
    codebook_path: Path | str = DEFAULT_CODEBOOK,
    substitution_path: Path | str = DEFAULT_SUBSTITUTION,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
    complement_path: Path | str = DEFAULT_COMPLEMENT,
) -> ConsistencyLevelReport:
    """Validate consistency-level targets against formal dependencies."""

    checked_language_path = Path(language_path)
    checked_codebook_path = Path(codebook_path)
    checked_substitution_path = Path(substitution_path)
    checked_complement_path = Path(complement_path)
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
    substitution = load_substitution_examples(checked_substitution_path)
    substitution_report = validate_substitution_examples(
        substitution,
        checked_codebook_path,
        checked_language_path,
        checked_willard_map_path,
    )
    try:
        complement = load_formal_complement_examples(checked_complement_path)
        complement_report = validate_formal_complement_examples(
            complement,
            checked_language_path,
            checked_codebook_path,
            checked_willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        complement_report = _DependencyFailure(
            accepted=False,
            failed_subjects=("formal-complement",),
            detail="formal complement rejected: " + str(exc),
        )
    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}

    results: list[ConsistencyLevelValidation] = [
        _accepted("manifest", f"loaded {len(manifest.targets)} target(s)")
    ]
    results.extend(
        _validate_dependency_references(
            manifest,
            checked_language_path,
            checked_codebook_path,
            checked_substitution_path,
            checked_complement_path,
        )
    )
    results.extend(
        _validate_dependency_reports(
            language_report,
            codebook_report,
            substitution_report,
            complement_report,
        )
    )
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    results.extend(_validate_targets(manifest.targets, language, codebook))

    return ConsistencyLevelReport(
        manifest=manifest,
        language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        substitution_path=checked_substitution_path,
        complement_path=checked_complement_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
    )


def consistency_level_report_payload(
    report: ConsistencyLevelReport,
) -> dict[str, Any]:
    """Return a JSON-ready consistency-level validation payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "target_manifest": str(report.manifest.path),
        "target_set_id": report.manifest.target_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "language_path": str(report.language_path),
        "codebook_path": str(report.codebook_path),
        "substitution_path": str(report.substitution_path),
        "complement_examples_path": str(report.complement_path),
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
        "target_count": report.target_count,
        "failed_subjects": list(report.failed_subjects),
        "targets": [
            {
                "target_id": target.target_id,
                "level": target.level,
                "notion": target.notion,
                "statement_class": target.statement_class,
                "negation_class": target.negation_class,
                "proof_code_source": target.proof_code_source,
                "substitution_source": target.substitution_source,
                "complement_source": target.complement_source,
                "status": target.status,
                "non_claims": list(target.non_claims),
                "next_as_action": target.next_as_action,
            }
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


def format_consistency_level_report(report: ConsistencyLevelReport) -> str:
    """Format a concise human-readable consistency-level report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Consistency level targets: {status}",
        f"Target set: {report.manifest.target_set_id}",
        f"Targets: {report.target_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for target in report.manifest.targets:
        lines.extend([
            f"- {target.target_id}: {target.notion}",
            f"  Level: {target.level}",
            f"  Classes: {target.statement_class}/{target.negation_class}",
            f"  Status: {target.status}",
            f"  Next AS action: {target.next_as_action}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_consistency_level_cli(argv: list[str] | None = None) -> int:
    """Run the consistency-level target validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.consistency_level",
        description="Validate AS consistency-level target selection.",
    )
    parser.add_argument(
        "--targets",
        default=str(DEFAULT_TARGETS),
        help="Path to the consistency-level target manifest.",
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
        "--substitution",
        default=str(DEFAULT_SUBSTITUTION),
        help="Path to the formal substitution example manifest.",
    )
    parser.add_argument(
        "--complement",
        default=str(DEFAULT_COMPLEMENT),
        help="Path to the formal complement example manifest.",
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

    manifest = load_consistency_level_targets(args.targets)
    report = validate_consistency_level_targets(
        manifest,
        args.language,
        args.codebook,
        args.substitution,
        args.willard_map,
        args.complement,
    )
    if args.format == "json":
        print(json.dumps(consistency_level_report_payload(report), sort_keys=True))
    else:
        print(format_consistency_level_report(report))
    return 0 if report.accepted else 1


def _validate_dependency_references(
    manifest: ConsistencyLevelManifest,
    language_path: Path,
    codebook_path: Path,
    substitution_path: Path,
    complement_path: Path,
) -> list[ConsistencyLevelValidation]:
    results: list[ConsistencyLevelValidation] = []
    expected = (
        ("language_path", manifest.language_path, str(language_path)),
        ("codebook_path", manifest.codebook_path, str(codebook_path)),
        (
            "substitution_examples_path",
            manifest.substitution_examples_path,
            str(substitution_path),
        ),
        (
            "complement_examples_path",
            manifest.complement_examples_path,
            str(complement_path),
        ),
    )
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
    substitution_report: Any,
    complement_report: Any,
) -> list[ConsistencyLevelValidation]:
    results: list[ConsistencyLevelValidation] = []
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
    if substitution_report.accepted:
        results.append(_accepted("substitution", "formal substitution accepted"))
    else:
        results.append(
            _rejected(
                "substitution",
                "formal substitution rejected: "
                + _joined_or_none(substitution_report.failed_subjects),
            )
        )
    if complement_report.accepted:
        results.append(_accepted("complement", "formal complement accepted"))
    else:
        detail = getattr(
            complement_report,
            "detail",
            "formal complement rejected: "
            + _joined_or_none(complement_report.failed_subjects),
        )
        results.append(_rejected("complement", detail))
    return results


def _validate_willard_anchors(
    manifest: ConsistencyLevelManifest,
    known_anchor_ids: set[str],
) -> list[ConsistencyLevelValidation]:
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


def _validate_targets(
    targets: tuple[ConsistencyLevelTarget, ...],
    language: Any,
    codebook: Any,
) -> list[ConsistencyLevelValidation]:
    if not targets:
        return [_rejected("targets", "no consistency-level targets")]

    results: list[ConsistencyLevelValidation] = []
    sentence_classes = set(language.sentence_classes)
    code_sentence_classes = set(codebook.sentence_tags)
    for target in targets:
        results.extend(_validate_target_shape(target))
        missing_classes = [
            class_name
            for class_name in (target.statement_class, target.negation_class)
            if class_name not in sentence_classes or class_name not in code_sentence_classes
        ]
        if missing_classes:
            results.append(
                _rejected(
                    f"{target.target_id}.sentence_classes",
                    "missing sentence classes: " + ", ".join(sorted(set(missing_classes))),
                )
            )
        else:
            results.append(
                _accepted(
                    f"{target.target_id}.sentence_classes",
                    "statement and negation classes are encoded",
                )
            )
    results.append(_accepted("targets", f"checked {len(targets)} target(s)"))
    return results


def _validate_target_shape(
    target: ConsistencyLevelTarget,
) -> list[ConsistencyLevelValidation]:
    results: list[ConsistencyLevelValidation] = []
    if target.level != 1:
        results.append(
            _rejected(target.target_id, f"unsupported consistency level: {target.level}")
        )
    else:
        results.append(_accepted(target.target_id, "Level-1 target selected"))

    if target.notion != "level-1-consistency":
        results.append(
            _rejected(target.target_id, f"unsupported notion: {target.notion}")
        )
    else:
        results.append(_accepted(target.target_id, "consistency notion named"))

    if target.status == "proved":
        results.append(
            _rejected(
                f"{target.target_id}.status",
                "proved consistency is not supported",
            )
        )
    elif target.status not in VALID_TARGET_STATUSES:
        results.append(
            _rejected(f"{target.target_id}.status", f"unknown status: {target.status}")
        )
    else:
        results.append(_accepted(target.target_id, "status preserves non-claim"))

    if not target.non_claims:
        results.append(_rejected(target.target_id, "non-claims must be explicit"))
    else:
        results.append(_accepted(target.target_id, "non-claims are explicit"))
    return results


def _parse_target(item: dict[str, Any]) -> ConsistencyLevelTarget:
    return ConsistencyLevelTarget(
        target_id=_required_text(item, "target_id"),
        level=_required_int(item, "level"),
        notion=_required_text(item, "notion"),
        statement_class=_required_text(item, "statement_class"),
        negation_class=_required_text(item, "negation_class"),
        proof_code_source=_required_text(item, "proof_code_source"),
        substitution_source=_required_text(item, "substitution_source"),
        complement_source=_required_text(item, "complement_source"),
        status=_required_text(item, "status"),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "consistency-level-willard-anchor"
    if subject.endswith(".sentence_classes"):
        return "consistency-level-sentence-class"
    if subject == "complement":
        return "consistency-level-complement"
    if subject in {"language", "codebook", "substitution"}:
        return "consistency-level-dependency"
    if subject in {
        "language_path",
        "codebook_path",
        "substitution_examples_path",
        "complement_examples_path",
    }:
        return "consistency-level-reference"
    if subject.startswith("AS-CONSISTENCY"):
        if "status" in subject:
            return "consistency-level-status"
        return "consistency-level-target"
    if subject == "targets":
        return "consistency-level-target"
    return "consistency-level-manifest"


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


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> ConsistencyLevelValidation:
    return ConsistencyLevelValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> ConsistencyLevelValidation:
    return ConsistencyLevelValidation(subject=subject, accepted=False, detail=detail)


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_consistency_level_cli())
