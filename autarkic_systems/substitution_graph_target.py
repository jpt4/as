"""Checked substitution graph target surface for AS.

This module names the next formal obligation after the checked substitution
graph witness: construct a delta0 formula whose graph represents
``substitution_code``. It validates the target boundary and its witness tether,
but it does not construct the formula or prove representability.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_arithmetic import (
    FormalArithmeticLanguage,
    load_formal_arithmetic_language,
    validate_formal_arithmetic_language,
)
from autarkic_systems.formal_code import (
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.substitution_representability import (
    SubstitutionRepresentabilityObservation,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_TARGETS = Path("claims/substitution_graph_targets.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.2-SELF-JUSTIFYING-GENAC",
    "W2020-D3.4-TYPE-NS-A-S-M",
)
REQUIRED_LANGUAGE_FEATURES = (
    "bounded-formula-class:delta0",
    "function-symbol:substitution_code",
    "relation-symbol:equals",
    "relation-symbol:less_than",
    "quantifier-form:bounded-forall",
    "quantifier-form:bounded-exists",
)
REQUIRED_FUTURE_WORK = (
    "delta0-graph-formula",
    "formula-correctness-proof",
    "substitution-representability-proof",
    "diagonal-lemma-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
VALID_TARGET_STATUSES = {
    "graph-formula-target-not-constructed",
}
REQUIRED_GRAPH_VARIABLE_KEYS = (
    "formula_code",
    "argument_code",
    "output_code",
)


@dataclass(frozen=True)
class SubstitutionGraphTarget:
    """One target for a future delta0 substitution graph formula."""

    target_id: str
    witness_id: str
    relation_name: str
    formula_class: str
    status: str
    graph_variables: dict[str, str]
    expected_witness_formula_code: tuple[int, ...]
    expected_witness_argument_code: tuple[int, ...]
    expected_witness_output_code_length: int
    expected_witness_output_code_prefix: tuple[int, ...]
    expected_witness_output_free_variables: tuple[str, ...]
    required_language_features: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphManifest:
    """Loaded manifest for substitution graph formula targets."""

    path: Path
    schema_version: int
    graph_target_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    substitution_representability_targets_path: str
    willard_anchor_ids: tuple[str, ...]
    targets: tuple[SubstitutionGraphTarget, ...]


@dataclass(frozen=True)
class SubstitutionGraphValidation:
    """One validation result for substitution graph targets."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphObservation:
    """Observed witness facts for one graph-formula target."""

    target_id: str
    witness_id: str
    status: str
    witness_formula_code: tuple[int, ...]
    witness_argument_code: tuple[int, ...]
    witness_output_code_length: int
    witness_output_code_prefix: tuple[int, ...]
    witness_output_free_variables: tuple[str, ...]


@dataclass(frozen=True)
class SubstitutionGraphReport:
    """Validation report over substitution graph formula targets."""

    manifest: SubstitutionGraphManifest
    formal_language_path: Path
    codebook_path: Path
    substitution_representability_targets_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphValidation, ...]
    observations: tuple[SubstitutionGraphObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every graph target validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def target_count(self) -> int:
        """Return the number of checked graph targets."""

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


def load_substitution_graph_targets(
    path: Path | str = DEFAULT_TARGETS,
) -> SubstitutionGraphManifest:
    """Load substitution graph formula targets from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return SubstitutionGraphManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        graph_target_set_id=_required_text(data, "graph_target_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        substitution_representability_targets_path=_required_text(
            data,
            "substitution_representability_targets_path",
        ),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        targets=tuple(
            _parse_target(item) for item in _required_list(data, "targets")
        ),
    )


def validate_substitution_graph_targets(
    manifest: SubstitutionGraphManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphReport:
    """Validate substitution graph targets and their dependency surfaces."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_witness_path = Path(manifest.substitution_representability_targets_path)

    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
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
    witness_manifest = load_substitution_representability_targets(checked_witness_path)
    witness_report = validate_substitution_representability_targets(
        witness_manifest,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[SubstitutionGraphValidation] = [
        _accepted("manifest", f"loaded {len(manifest.targets)} target(s)")
    ]
    observations: list[SubstitutionGraphObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            language_report,
            codebook_report,
            witness_report,
        )
    )
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    target_results, observations = _validate_targets(
        manifest.targets,
        language,
        witness_report.observations,
    )
    results.extend(target_results)

    return SubstitutionGraphReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        substitution_representability_targets_path=checked_witness_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def substitution_graph_report_payload(
    report: SubstitutionGraphReport,
) -> dict[str, Any]:
    """Return a JSON-ready substitution graph target payload."""

    observations = {
        observation.target_id: observation
        for observation in report.observations
    }
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "target_manifest": str(report.manifest.path),
        "graph_target_set_id": report.manifest.graph_target_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "substitution_representability_targets_path": str(
            report.substitution_representability_targets_path
        ),
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
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


def format_substitution_graph_report(report: SubstitutionGraphReport) -> str:
    """Format a concise human-readable substitution graph target report."""

    observations = {
        observation.target_id: observation
        for observation in report.observations
    }
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Substitution graph targets: {status}",
        f"Target set: {report.manifest.graph_target_set_id}",
        f"Targets: {report.target_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for target in report.manifest.targets:
        observation = observations.get(target.target_id)
        output_length = "unknown"
        if observation is not None:
            output_length = str(observation.witness_output_code_length)
        lines.extend([
            f"- {target.target_id}",
            f"  Relation: {target.relation_name}",
            f"  Formula class: {target.formula_class}",
            f"  Status: {target.status}",
            f"  Witness: {target.witness_id}",
            f"  Witness output code length: {output_length}",
            "  Future work: " + _joined_or_none(target.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_cli(argv: list[str] | None = None) -> int:
    """Run the substitution graph target validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.substitution_graph_target",
        description="Validate AS substitution graph formula targets.",
    )
    parser.add_argument(
        "--targets",
        default=str(DEFAULT_TARGETS),
        help="Path to the substitution graph target manifest.",
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

    manifest = load_substitution_graph_targets(args.targets)
    report = validate_substitution_graph_targets(manifest, args.willard_map)
    if args.format == "json":
        print(json.dumps(substitution_graph_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_graph_report(report))
    return 0 if report.accepted else 1


def _target_payload(
    target: SubstitutionGraphTarget,
    observation: SubstitutionGraphObservation | None,
) -> dict[str, Any]:
    payload = {
        "target_id": target.target_id,
        "witness_id": target.witness_id,
        "relation_name": target.relation_name,
        "formula_class": target.formula_class,
        "status": target.status,
        "graph_variables": dict(target.graph_variables),
        "expected_witness_formula_code": list(target.expected_witness_formula_code),
        "expected_witness_argument_code": list(target.expected_witness_argument_code),
        "expected_witness_output_code_length": target.expected_witness_output_code_length,
        "expected_witness_output_code_prefix": list(
            target.expected_witness_output_code_prefix
        ),
        "expected_witness_output_free_variables": list(
            target.expected_witness_output_free_variables
        ),
        "required_language_features": list(target.required_language_features),
        "required_future_work": list(target.required_future_work),
        "non_claims": list(target.non_claims),
        "next_as_action": target.next_as_action,
    }
    if observation is None:
        payload.update({
            "observed_witness_formula_code_length": None,
            "observed_witness_formula_code": None,
            "observed_witness_argument_code_length": None,
            "observed_witness_argument_code": None,
            "observed_witness_output_code_length": None,
            "observed_witness_output_code_prefix": None,
            "observed_witness_output_free_variables": None,
        })
    else:
        payload.update({
            "observed_witness_formula_code_length": len(observation.witness_formula_code),
            "observed_witness_formula_code": list(observation.witness_formula_code),
            "observed_witness_argument_code_length": len(observation.witness_argument_code),
            "observed_witness_argument_code": list(observation.witness_argument_code),
            "observed_witness_output_code_length": observation.witness_output_code_length,
            "observed_witness_output_code_prefix": list(
                observation.witness_output_code_prefix
            ),
            "observed_witness_output_free_variables": list(
                observation.witness_output_free_variables
            ),
        })
    return payload


def _validate_references(
    manifest: SubstitutionGraphManifest,
) -> list[SubstitutionGraphValidation]:
    expected = (
        (
            "formal_language_path",
            manifest.formal_language_path,
            "language/formal_arithmetic_language.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "substitution_representability_targets_path",
            manifest.substitution_representability_targets_path,
            "claims/substitution_representability_targets.json",
        ),
    )
    results: list[SubstitutionGraphValidation] = []
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
    witness_report: Any,
) -> list[SubstitutionGraphValidation]:
    checks = (
        ("formal_language", language_report, "formal arithmetic language"),
        ("codebook", codebook_report, "formal codebook"),
        (
            "substitution_representability",
            witness_report,
            "substitution representability witness",
        ),
    )
    results: list[SubstitutionGraphValidation] = []
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
    manifest: SubstitutionGraphManifest,
    known_anchor_ids: set[str],
) -> list[SubstitutionGraphValidation]:
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
    targets: tuple[SubstitutionGraphTarget, ...],
    language: FormalArithmeticLanguage,
    witness_observations: tuple[SubstitutionRepresentabilityObservation, ...],
) -> tuple[list[SubstitutionGraphValidation], list[SubstitutionGraphObservation]]:
    if not targets:
        return [_rejected("targets", "no substitution graph targets")], []

    results: list[SubstitutionGraphValidation] = []
    observations: list[SubstitutionGraphObservation] = []
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
            language,
            witness_observations,
        )
        results.extend(target_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("targets", f"checked {len(targets)} target(s)"))
    return results, observations


def _validate_target(
    target: SubstitutionGraphTarget,
    language: FormalArithmeticLanguage,
    witness_observations: tuple[SubstitutionRepresentabilityObservation, ...],
) -> tuple[list[SubstitutionGraphValidation], SubstitutionGraphObservation | None]:
    subject = target.target_id
    results: list[SubstitutionGraphValidation] = []

    if target.status in {
        "delta0-graph-formula-constructed",
        "substitution-representability-proved",
    }:
        results.append(
            _rejected(
                f"{subject}.status",
                "constructed graph formulas are not supported",
            )
        )
    elif target.status not in VALID_TARGET_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {target.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    if target.relation_name != "subst_code_graph":
        results.append(
            _rejected(
                f"{subject}.relation_name",
                "expected subst_code_graph",
            )
        )
    else:
        results.append(_accepted(f"{subject}.relation_name", "relation target named"))

    if target.formula_class != "delta0":
        results.append(
            _rejected(f"{subject}.formula_class", "expected delta0 formula class")
        )
    else:
        results.append(_accepted(f"{subject}.formula_class", "delta0 target selected"))

    results.extend(_validate_graph_variables(target, language))
    results.extend(_validate_language_features(target, language))

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

    if not target.non_claims:
        results.append(_rejected(f"{subject}.non_claims", "non-claims must be explicit"))
    else:
        results.append(_accepted(f"{subject}.non_claims", "non-claims are explicit"))

    try:
        witness = _find_witness_observation(witness_observations, target.witness_id)
    except ValueError as exc:
        results.append(_rejected(f"{subject}.witness", str(exc)))
        return results, None

    observation = SubstitutionGraphObservation(
        target_id=target.target_id,
        witness_id=target.witness_id,
        status=target.status,
        witness_formula_code=witness.formula_code,
        witness_argument_code=witness.argument_code,
        witness_output_code_length=witness.output_code_length,
        witness_output_code_prefix=witness.output_code_prefix,
        witness_output_free_variables=witness.output_free_variables,
    )
    results.extend(_validate_witness_tether(target, observation))
    return results, observation


def _validate_graph_variables(
    target: SubstitutionGraphTarget,
    language: FormalArithmeticLanguage,
) -> list[SubstitutionGraphValidation]:
    subject = f"{target.target_id}.graph_variables"
    expected_keys = set(REQUIRED_GRAPH_VARIABLE_KEYS)
    actual_keys = set(target.graph_variables)
    if actual_keys != expected_keys:
        return [
            _rejected(
                subject,
                "expected graph variable keys: " + ", ".join(REQUIRED_GRAPH_VARIABLE_KEYS),
            )
        ]

    allowed_variables = set(_language_variables(language))
    unknown_variables = sorted(set(target.graph_variables.values()) - allowed_variables)
    if unknown_variables:
        return [
            _rejected(
                subject,
                "unknown graph variables: " + ", ".join(unknown_variables),
            )
        ]
    if len(set(target.graph_variables.values())) != len(target.graph_variables):
        return [_rejected(subject, "graph variables must be distinct")]
    return [_accepted(subject, "graph variables are language variables")]


def _validate_language_features(
    target: SubstitutionGraphTarget,
    language: FormalArithmeticLanguage,
) -> list[SubstitutionGraphValidation]:
    subject = f"{target.target_id}.language_features"
    missing_required = [
        item for item in REQUIRED_LANGUAGE_FEATURES if item not in target.required_language_features
    ]
    if missing_required:
        return [
            _rejected(
                subject,
                "missing required language features: " + ", ".join(missing_required),
            )
        ]

    unsupported = [
        item
        for item in target.required_language_features
        if not _language_supports_feature(language, item)
    ]
    if unsupported:
        return [
            _rejected(
                subject,
                "language does not support: " + ", ".join(unsupported),
            )
        ]
    return [_accepted(subject, "required language features are present")]


def _validate_witness_tether(
    target: SubstitutionGraphTarget,
    observation: SubstitutionGraphObservation,
) -> list[SubstitutionGraphValidation]:
    subject = f"{target.target_id}.witness"
    if observation.witness_formula_code != target.expected_witness_formula_code:
        return [
            _rejected(
                subject,
                "witness formula code mismatch: expected "
                + _format_code(target.expected_witness_formula_code)
                + " got "
                + _format_code(observation.witness_formula_code),
            )
        ]
    if observation.witness_argument_code != target.expected_witness_argument_code:
        return [
            _rejected(
                subject,
                "witness argument code mismatch: expected "
                + _format_code(target.expected_witness_argument_code)
                + " got "
                + _format_code(observation.witness_argument_code),
            )
        ]
    if observation.witness_output_code_length != target.expected_witness_output_code_length:
        return [
            _rejected(
                subject,
                "witness output code length mismatch: expected "
                + str(target.expected_witness_output_code_length)
                + " got "
                + str(observation.witness_output_code_length),
            )
        ]
    if observation.witness_output_code_prefix != target.expected_witness_output_code_prefix:
        return [
            _rejected(
                subject,
                "witness output code prefix mismatch: expected "
                + _format_code(target.expected_witness_output_code_prefix)
                + " got "
                + _format_code(observation.witness_output_code_prefix),
            )
        ]
    if observation.witness_output_free_variables != target.expected_witness_output_free_variables:
        return [
            _rejected(
                subject,
                "witness output free variables mismatch: expected "
                + _joined_or_none(target.expected_witness_output_free_variables)
                + " got "
                + _joined_or_none(observation.witness_output_free_variables),
            )
        ]
    return [_accepted(subject, "witness graph point is tethered")]


def _language_supports_feature(
    language: FormalArithmeticLanguage,
    feature: str,
) -> bool:
    if feature.startswith("bounded-formula-class:"):
        name = feature.split(":", 1)[1]
        return name in language.bounded_formula_classes
    if feature.startswith("function-symbol:"):
        name = feature.split(":", 1)[1]
        terms = language.syntax_classes.get("terms", {})
        symbols = terms.get("function_symbols", {}) if isinstance(terms, dict) else {}
        return isinstance(symbols, dict) and name in symbols
    if feature.startswith("relation-symbol:"):
        name = feature.split(":", 1)[1]
        formulae = language.syntax_classes.get("formulae", {})
        symbols = formulae.get("relation_symbols", {}) if isinstance(formulae, dict) else {}
        return isinstance(symbols, dict) and name in symbols
    if feature.startswith("quantifier-form:"):
        name = feature.split(":", 1)[1]
        formulae = language.syntax_classes.get("formulae", {})
        quantifiers = formulae.get("quantifier_forms", []) if isinstance(formulae, dict) else []
        return isinstance(quantifiers, list) and name in quantifiers
    return False


def _language_variables(language: FormalArithmeticLanguage) -> tuple[str, ...]:
    terms = language.syntax_classes.get("terms", {})
    variables = terms.get("variables", []) if isinstance(terms, dict) else []
    if not isinstance(variables, list):
        return ()
    return tuple(value for value in variables if isinstance(value, str))


def _find_witness_observation(
    observations: tuple[SubstitutionRepresentabilityObservation, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityObservation:
    for observation in observations:
        if observation.witness_id == witness_id:
            return observation
    raise ValueError(f"unknown substitution witness: {witness_id}")


def _parse_target(item: dict[str, Any]) -> SubstitutionGraphTarget:
    return SubstitutionGraphTarget(
        target_id=_required_text(item, "target_id"),
        witness_id=_required_text(item, "witness_id"),
        relation_name=_required_text(item, "relation_name"),
        formula_class=_required_text(item, "formula_class"),
        status=_required_text(item, "status"),
        graph_variables=_required_text_mapping(item, "graph_variables"),
        expected_witness_formula_code=tuple(
            _required_int_list(item, "expected_witness_formula_code")
        ),
        expected_witness_argument_code=tuple(
            _required_int_list(item, "expected_witness_argument_code")
        ),
        expected_witness_output_code_length=_required_int(
            item,
            "expected_witness_output_code_length",
        ),
        expected_witness_output_code_prefix=tuple(
            _required_int_list(item, "expected_witness_output_code_prefix")
        ),
        expected_witness_output_free_variables=tuple(
            _required_text_list(
                item,
                "expected_witness_output_free_variables",
                allow_empty=True,
            )
        ),
        required_language_features=tuple(
            _required_text_list(item, "required_language_features")
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "substitution-graph-willard-anchor"
    if subject.endswith(".status"):
        return "substitution-graph-status"
    if subject.endswith(".relation_name"):
        return "substitution-graph-relation"
    if subject.endswith(".formula_class"):
        return "substitution-graph-formula-class"
    if subject.endswith(".graph_variables"):
        return "substitution-graph-variable"
    if subject.endswith(".language_features"):
        return "substitution-graph-language-feature"
    if subject.endswith(".witness"):
        return "substitution-graph-witness"
    if subject.endswith(".required_future_work"):
        return "substitution-graph-future-work"
    if subject.endswith(".non_claims"):
        return "substitution-graph-non-claim"
    if subject in {"formal_language", "codebook", "substitution_representability"}:
        return "substitution-graph-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-reference"
    if subject.startswith("targets"):
        return "substitution-graph-target"
    return "substitution-graph"


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


def _required_text_mapping(item: dict[str, Any], key: str) -> dict[str, str]:
    value = item.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"required mapping field missing: {key}")
    result: dict[str, str] = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str) or not item_key.strip():
            raise ValueError(f"{key} contains non-text key")
        if not isinstance(item_value, str) or not item_value.strip():
            raise ValueError(f"{key} contains non-text value")
        result[item_key] = item_value
    return result


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _accepted(subject: str, detail: str) -> SubstitutionGraphValidation:
    return SubstitutionGraphValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> SubstitutionGraphValidation:
    return SubstitutionGraphValidation(subject=subject, accepted=False, detail=detail)


def _format_code(values: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(value) for value in values) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_cli())
