"""Checked diagonal-construction seed surface for AS.

This module validates the first syntactic shape of the diagonal route:
replace the fixed-point target variable with ``substitution_code(n,n)``, then
quote that seed code back into the seed. The result is only a checked seed and
closed syntactic instance. It is not a proof that ``substitution_code``
represents meta-level substitution, not a diagonal lemma, not a fixed-point
equation proof, and not a self-consistency theorem.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_TARGETS = Path("claims/diagonal_construction_targets.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.2-SELF-JUSTIFYING-GENAC",
)
REQUIRED_FUTURE_WORK = (
    "substitution-representability-proof",
    "diagonal-lemma-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
VALID_CONSTRUCTION_STATUSES = {
    "diagonal-seed-not-proved",
}


@dataclass(frozen=True)
class DiagonalConstructionTarget:
    """One checked diagonal seed target, not a proved construction."""

    construction_id: str
    target_id: str
    substitution_term_kind: str
    status: str
    expected_seed_code: tuple[int, ...]
    expected_seed_free_variables: tuple[str, ...]
    expected_instance_code_length: int
    expected_instance_code_prefix: tuple[int, ...]
    expected_instance_free_variables: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class DiagonalConstructionManifest:
    """Loaded manifest for diagonal-construction seed targets."""

    path: Path
    schema_version: int
    construction_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_targets_path: str
    codebook_path: str
    willard_anchor_ids: tuple[str, ...]
    constructions: tuple[DiagonalConstructionTarget, ...]


@dataclass(frozen=True)
class DiagonalConstructionValidation:
    """One validation result for diagonal-construction seed targets."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class DiagonalConstructionObservation:
    """Observed seed and instance facts for one diagonal-construction target."""

    construction_id: str
    target_id: str
    status: str
    seed_code: tuple[int, ...]
    seed_free_variables: tuple[str, ...]
    instance_code_length: int
    instance_code_prefix: tuple[int, ...]
    instance_free_variables: tuple[str, ...]


@dataclass(frozen=True)
class DiagonalConstructionReport:
    """Validation report over diagonal-construction seed targets."""

    manifest: DiagonalConstructionManifest
    fixed_point_targets_path: Path
    codebook_path: Path
    formal_language_path: Path
    willard_map_path: Path
    results: tuple[DiagonalConstructionValidation, ...]
    observations: tuple[DiagonalConstructionObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every diagonal-construction validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def construction_count(self) -> int:
        """Return the number of checked diagonal-construction targets."""

        return len(self.manifest.constructions)

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


def build_diagonal_seed_node(target: FixedPointTarget) -> dict[str, Any]:
    """Build the syntactic diagonal seed for a fixed-point target."""

    variable = target.template_variable
    substitution_term = {
        "kind": "substitution_code",
        "left": {"kind": "variable", "name": variable},
        "right": {"kind": "variable", "name": variable},
    }
    return substitute_node(target.template_node, variable, substitution_term)


def build_diagonal_instance_code(
    *,
    construction_id: str,
    targets_path: Path | str = DEFAULT_TARGETS,
    fixed_point_targets_path: Path | str = "claims/fixed_point_targets.json",
    codebook_path: Path | str = "language/formal_codebook.json",
) -> tuple[int, ...]:
    """Build and encode the quoted diagonal seed instance."""

    manifest = load_diagonal_construction_targets(targets_path)
    construction = _find_construction(manifest.constructions, construction_id)
    fixed_point_targets = load_fixed_point_targets(fixed_point_targets_path)
    fixed_point_target = _find_fixed_point_target(
        fixed_point_targets.targets,
        construction.target_id,
    )
    codebook = load_formal_codebook(codebook_path)
    return _diagonal_instance_code_for(fixed_point_target, codebook)


def load_diagonal_construction_targets(
    path: Path | str = DEFAULT_TARGETS,
) -> DiagonalConstructionManifest:
    """Load diagonal-construction seed targets from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return DiagonalConstructionManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        construction_set_id=_required_text(data, "construction_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        codebook_path=_required_text(data, "codebook_path"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        constructions=tuple(
            _parse_construction(item) for item in _required_list(data, "constructions")
        ),
    )


def validate_diagonal_construction_targets(
    manifest: DiagonalConstructionManifest,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> DiagonalConstructionReport:
    """Validate diagonal-construction seed targets and dependencies."""

    checked_language_path = Path(formal_language_path)
    checked_willard_map_path = Path(willard_map_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_codebook_path = Path(manifest.codebook_path)

    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
    fixed_point_report = validate_fixed_point_targets(
        fixed_point_targets,
        checked_willard_map_path,
        checked_language_path,
    )
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[DiagonalConstructionValidation] = [
        _accepted("manifest", f"loaded {len(manifest.constructions)} construction(s)")
    ]
    observations: list[DiagonalConstructionObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(_validate_dependency_reports(fixed_point_report, codebook_report))
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    construction_results, observations = _validate_constructions(
        manifest.constructions,
        fixed_point_targets.targets,
        codebook,
    )
    results.extend(construction_results)

    return DiagonalConstructionReport(
        manifest=manifest,
        fixed_point_targets_path=checked_fixed_point_path,
        codebook_path=checked_codebook_path,
        formal_language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def diagonal_construction_report_payload(
    report: DiagonalConstructionReport,
) -> dict[str, Any]:
    """Return a JSON-ready diagonal-construction validation payload."""

    observations = {
        observation.construction_id: observation
        for observation in report.observations
    }
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "construction_manifest": str(report.manifest.path),
        "construction_set_id": report.manifest.construction_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "codebook_path": str(report.codebook_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
        "construction_count": report.construction_count,
        "failed_subjects": list(report.failed_subjects),
        "constructions": [
            _construction_payload(
                construction,
                observations.get(construction.construction_id),
            )
            for construction in report.manifest.constructions
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


def format_diagonal_construction_report(
    report: DiagonalConstructionReport,
) -> str:
    """Format a concise human-readable diagonal-construction report."""

    observations = {
        observation.construction_id: observation
        for observation in report.observations
    }
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Diagonal construction targets: {status}",
        f"Construction set: {report.manifest.construction_set_id}",
        f"Constructions: {report.construction_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for construction in report.manifest.constructions:
        observation = observations.get(construction.construction_id)
        instance_length = "unknown"
        if observation is not None:
            instance_length = str(observation.instance_code_length)
        lines.extend([
            f"- {construction.construction_id}",
            f"  Target: {construction.target_id}",
            f"  Status: {construction.status}",
            f"  Substitution term: {construction.substitution_term_kind}",
            f"  Instance code length: {instance_length}",
            "  Future work: " + _joined_or_none(construction.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_diagonal_construction_cli(argv: list[str] | None = None) -> int:
    """Run the diagonal-construction target validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.diagonal_construction",
        description="Validate AS diagonal-construction seed targets.",
    )
    parser.add_argument(
        "--targets",
        default=str(DEFAULT_TARGETS),
        help="Path to the diagonal-construction target manifest.",
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

    manifest = load_diagonal_construction_targets(args.targets)
    report = validate_diagonal_construction_targets(
        manifest,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(diagonal_construction_report_payload(report), sort_keys=True))
    else:
        print(format_diagonal_construction_report(report))
    return 0 if report.accepted else 1


def _construction_payload(
    construction: DiagonalConstructionTarget,
    observation: DiagonalConstructionObservation | None,
) -> dict[str, Any]:
    payload = {
        "construction_id": construction.construction_id,
        "target_id": construction.target_id,
        "substitution_term_kind": construction.substitution_term_kind,
        "status": construction.status,
        "expected_seed_code": list(construction.expected_seed_code),
        "expected_seed_free_variables": list(construction.expected_seed_free_variables),
        "expected_instance_code_length": construction.expected_instance_code_length,
        "expected_instance_code_prefix": list(construction.expected_instance_code_prefix),
        "expected_instance_free_variables": list(
            construction.expected_instance_free_variables
        ),
        "required_future_work": list(construction.required_future_work),
        "non_claims": list(construction.non_claims),
        "next_as_action": construction.next_as_action,
    }
    if observation is None:
        payload.update({
            "observed_seed_code_length": None,
            "observed_seed_code": None,
            "observed_seed_free_variables": None,
            "observed_instance_code_length": None,
            "observed_instance_code_prefix": None,
            "observed_instance_free_variables": None,
        })
    else:
        payload.update({
            "observed_seed_code_length": len(observation.seed_code),
            "observed_seed_code": list(observation.seed_code),
            "observed_seed_free_variables": list(observation.seed_free_variables),
            "observed_instance_code_length": observation.instance_code_length,
            "observed_instance_code_prefix": list(observation.instance_code_prefix),
            "observed_instance_free_variables": list(observation.instance_free_variables),
        })
    return payload


def _validate_references(
    manifest: DiagonalConstructionManifest,
) -> list[DiagonalConstructionValidation]:
    expected = (
        (
            "fixed_point_targets_path",
            manifest.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
    )
    results: list[DiagonalConstructionValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    fixed_point_report: Any,
    codebook_report: Any,
) -> list[DiagonalConstructionValidation]:
    checks = (
        ("fixed_point", fixed_point_report, "fixed-point target"),
        ("codebook", codebook_report, "formal codebook"),
    )
    results: list[DiagonalConstructionValidation] = []
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


def _validate_willard_anchors(
    manifest: DiagonalConstructionManifest,
    known_anchor_ids: set[str],
) -> list[DiagonalConstructionValidation]:
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


def _validate_constructions(
    constructions: tuple[DiagonalConstructionTarget, ...],
    fixed_point_targets: tuple[FixedPointTarget, ...],
    codebook: FormalCodebook,
) -> tuple[list[DiagonalConstructionValidation], list[DiagonalConstructionObservation]]:
    if not constructions:
        return [_rejected("constructions", "no diagonal constructions")], []

    results: list[DiagonalConstructionValidation] = []
    observations: list[DiagonalConstructionObservation] = []
    construction_ids = [construction.construction_id for construction in constructions]
    duplicate_ids = _duplicates(construction_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "constructions.construction_id",
                "duplicate construction ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("constructions.construction_id", "construction ids are unique"))

    for construction in constructions:
        construction_results, observation = _validate_construction(
            construction,
            fixed_point_targets,
            codebook,
        )
        results.extend(construction_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("constructions", f"checked {len(constructions)} construction(s)"))
    return results, observations


def _validate_construction(
    construction: DiagonalConstructionTarget,
    fixed_point_targets: tuple[FixedPointTarget, ...],
    codebook: FormalCodebook,
) -> tuple[list[DiagonalConstructionValidation], DiagonalConstructionObservation | None]:
    subject = construction.construction_id
    results: list[DiagonalConstructionValidation] = []

    if construction.status == "diagonal-lemma-proved":
        results.append(
            _rejected(
                f"{subject}.status",
                "proved diagonal constructions are not supported",
            )
        )
    elif construction.status not in VALID_CONSTRUCTION_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {construction.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    if construction.substitution_term_kind != "substitution_code":
        results.append(
            _rejected(
                f"{subject}.substitution_term_kind",
                "expected substitution_code",
            )
        )
    else:
        results.append(
            _accepted(
                f"{subject}.substitution_term_kind",
                "substitution_code selected",
            )
        )

    missing_future_work = [
        item
        for item in REQUIRED_FUTURE_WORK
        if item not in construction.required_future_work
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

    if not construction.non_claims:
        results.append(_rejected(f"{subject}.non_claims", "non-claims must be explicit"))
    else:
        results.append(_accepted(f"{subject}.non_claims", "non-claims are explicit"))

    try:
        fixed_point_target = _find_fixed_point_target(
            fixed_point_targets,
            construction.target_id,
        )
        seed_node = build_diagonal_seed_node(fixed_point_target)
        seed_code = encode_node(seed_node, codebook)
        seed_free_variables = tuple(sorted(free_variables(seed_node)))
        instance_node = _diagonal_instance_node_for(fixed_point_target, codebook)
        instance_code = encode_node(instance_node, codebook)
        instance_prefix = instance_code[: len(construction.expected_instance_code_prefix)]
        instance_free_variables = tuple(sorted(free_variables(instance_node)))
    except ValueError as exc:
        results.append(_rejected(f"{subject}.target", str(exc)))
        return results, None

    observation = DiagonalConstructionObservation(
        construction_id=construction.construction_id,
        target_id=construction.target_id,
        status=construction.status,
        seed_code=seed_code,
        seed_free_variables=seed_free_variables,
        instance_code_length=len(instance_code),
        instance_code_prefix=instance_prefix,
        instance_free_variables=instance_free_variables,
    )

    if seed_code != construction.expected_seed_code:
        results.append(
            _rejected(
                f"{subject}.seed",
                "seed code mismatch: expected "
                + _format_code(construction.expected_seed_code)
                + " got "
                + _format_code(seed_code),
            )
        )
    elif seed_free_variables != construction.expected_seed_free_variables:
        results.append(
            _rejected(
                f"{subject}.seed",
                "seed free variables mismatch: expected "
                + _joined_or_none(construction.expected_seed_free_variables)
                + " got "
                + _joined_or_none(seed_free_variables),
            )
        )
    else:
        results.append(_accepted(f"{subject}.seed", "diagonal seed accepted"))

    if len(instance_code) != construction.expected_instance_code_length:
        results.append(
            _rejected(
                f"{subject}.instance",
                "instance code length mismatch: expected "
                + str(construction.expected_instance_code_length)
                + " got "
                + str(len(instance_code)),
            )
        )
    elif instance_prefix != construction.expected_instance_code_prefix:
        results.append(
            _rejected(
                f"{subject}.instance",
                "instance code prefix mismatch: expected "
                + _format_code(construction.expected_instance_code_prefix)
                + " got "
                + _format_code(instance_prefix),
            )
        )
    elif instance_free_variables != construction.expected_instance_free_variables:
        results.append(
            _rejected(
                f"{subject}.instance",
                "instance free variables mismatch: expected "
                + _joined_or_none(construction.expected_instance_free_variables)
                + " got "
                + _joined_or_none(instance_free_variables),
            )
        )
    else:
        results.append(_accepted(f"{subject}.instance", "quoted seed instance accepted"))

    return results, observation


def _diagonal_instance_node_for(
    target: FixedPointTarget,
    codebook: FormalCodebook,
) -> dict[str, Any]:
    seed_node = build_diagonal_seed_node(target)
    seed_code = encode_node(seed_node, codebook)
    seed_quote_term = quote_tokens_as_term(seed_code)
    return substitute_node(seed_node, target.template_variable, seed_quote_term)


def _diagonal_instance_code_for(
    target: FixedPointTarget,
    codebook: FormalCodebook,
) -> tuple[int, ...]:
    return encode_node(_diagonal_instance_node_for(target, codebook), codebook)


def _find_construction(
    constructions: tuple[DiagonalConstructionTarget, ...],
    construction_id: str,
) -> DiagonalConstructionTarget:
    for construction in constructions:
        if construction.construction_id == construction_id:
            return construction
    raise ValueError(f"unknown diagonal construction: {construction_id}")


def _find_fixed_point_target(
    targets: tuple[FixedPointTarget, ...],
    target_id: str,
) -> FixedPointTarget:
    for target in targets:
        if target.target_id == target_id:
            return target
    raise ValueError(f"unknown fixed-point target: {target_id}")


def _parse_construction(item: dict[str, Any]) -> DiagonalConstructionTarget:
    return DiagonalConstructionTarget(
        construction_id=_required_text(item, "construction_id"),
        target_id=_required_text(item, "target_id"),
        substitution_term_kind=_required_text(item, "substitution_term_kind"),
        status=_required_text(item, "status"),
        expected_seed_code=tuple(_required_int_list(item, "expected_seed_code")),
        expected_seed_free_variables=tuple(
            _required_text_list(item, "expected_seed_free_variables", allow_empty=True)
        ),
        expected_instance_code_length=_required_int(
            item,
            "expected_instance_code_length",
        ),
        expected_instance_code_prefix=tuple(
            _required_int_list(item, "expected_instance_code_prefix")
        ),
        expected_instance_free_variables=tuple(
            _required_text_list(
                item,
                "expected_instance_free_variables",
                allow_empty=True,
            )
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "diagonal-construction-willard-anchor"
    if subject.endswith(".status"):
        return "diagonal-construction-status"
    if subject.endswith(".seed"):
        return "diagonal-construction-seed"
    if subject.endswith(".instance"):
        return "diagonal-construction-instance"
    if subject.endswith(".target"):
        return "diagonal-construction-target"
    if subject.endswith(".substitution_term_kind"):
        return "diagonal-construction-substitution-term"
    if subject.endswith(".required_future_work"):
        return "diagonal-construction-future-work"
    if subject.endswith(".non_claims"):
        return "diagonal-construction-non-claim"
    if subject in {"fixed_point", "codebook"}:
        return "diagonal-construction-dependency"
    if subject.endswith("_path"):
        return "diagonal-construction-reference"
    return "diagonal-construction"


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


def _accepted(subject: str, detail: str) -> DiagonalConstructionValidation:
    return DiagonalConstructionValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> DiagonalConstructionValidation:
    return DiagonalConstructionValidation(subject=subject, accepted=False, detail=detail)


def _format_code(values: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(value) for value in values) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_diagonal_construction_cli())
