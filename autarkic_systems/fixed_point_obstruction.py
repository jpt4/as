"""Checked obstruction for the current naive AS fixed-point candidate.

ADR-0235 records a direct quotation-substitution candidate. This module checks
why that particular construction cannot be the fixed point: quoting a code
sequence as nested ``sequence_cons`` cells with unary numerals makes the
encoded candidate strictly longer than the input code sequence. The result is
an obstruction to this naive construction only; it is not a diagonal lemma or
a fixed-point proof.
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
)
from autarkic_systems.fixed_point_equation import (
    FixedPointEquationCandidate,
    build_candidate_code,
    load_fixed_point_equation_candidates,
    validate_fixed_point_equation_candidates,
)
from autarkic_systems.formal_code import (
    FormalCodebook,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import substitute_node
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_OBSTRUCTIONS = Path("claims/fixed_point_obstructions.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
)
VALID_OBSTRUCTION_KIND = "naive-quotation-length-growth"
VALID_OBSTRUCTION_STATUSES = {
    "obstruction-observed",
}
REQUIRED_FUTURE_WORK = (
    "real-diagonal-construction",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)


@dataclass(frozen=True)
class FixedPointObstruction:
    """One checked reason the current naive candidate cannot be fixed."""

    obstruction_id: str
    candidate_id: str
    status: str
    expected_template_variable_occurrences: int
    expected_context_code_length: int
    expected_observed_input_length: int
    expected_observed_input_token_sum: int
    expected_observed_candidate_length: int
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointObstructionManifest:
    """Loaded fixed-point obstruction manifest."""

    path: Path
    schema_version: int
    obstruction_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_equation_candidates_path: str
    codebook_path: str
    obstruction_kind: str
    willard_anchor_ids: tuple[str, ...]
    obstructions: tuple[FixedPointObstruction, ...]


@dataclass(frozen=True)
class FixedPointObstructionValidation:
    """One validation result for fixed-point obstruction records."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointObstructionObservation:
    """Computed length facts for one obstruction record."""

    obstruction_id: str
    candidate_id: str
    status: str
    template_variable_occurrences: int
    context_code_length: int
    nil_candidate_code_length: int
    observed_input_length: int
    observed_input_token_sum: int
    observed_quote_term_code_length: int
    observed_candidate_length: int
    formula_candidate_length: int
    minimum_growth_delta: int
    impossible_by_length: bool


@dataclass(frozen=True)
class FixedPointObstructionReport:
    """Validation report for the checked fixed-point obstruction surface."""

    manifest: FixedPointObstructionManifest
    fixed_point_equation_candidates_path: Path
    codebook_path: Path
    formal_language_path: Path
    willard_map_path: Path
    results: tuple[FixedPointObstructionValidation, ...]
    observations: tuple[FixedPointObstructionObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every obstruction validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def obstruction_count(self) -> int:
        """Return the number of checked obstruction records."""

        return len(self.manifest.obstructions)

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


def quote_term_code_length_formula(tokens: tuple[int, ...] | list[int]) -> int:
    """Return the encoded length of the nested quotation term for tokens."""

    checked_tokens = _natural_tokens(tokens)
    return 1 + (2 * len(checked_tokens)) + sum(checked_tokens)


def naive_candidate_code_length_formula(
    tokens: tuple[int, ...] | list[int],
    context_code_length: int,
) -> int:
    """Return the naive candidate length implied by the context and tokens."""

    if not isinstance(context_code_length, int) or isinstance(context_code_length, bool):
        raise ValueError("context code length must be an integer")
    if context_code_length < 0:
        raise ValueError("context code length must be non-negative")
    return context_code_length + quote_term_code_length_formula(tokens)


def load_fixed_point_obstructions(
    path: Path | str = DEFAULT_OBSTRUCTIONS,
) -> FixedPointObstructionManifest:
    """Load fixed-point obstruction records from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return FixedPointObstructionManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        obstruction_set_id=_required_text(data, "obstruction_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_equation_candidates_path=_required_text(
            data,
            "fixed_point_equation_candidates_path",
        ),
        codebook_path=_required_text(data, "codebook_path"),
        obstruction_kind=_required_text(data, "obstruction_kind"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        obstructions=tuple(
            _parse_obstruction(item) for item in _required_list(data, "obstructions")
        ),
    )


def validate_fixed_point_obstructions(
    manifest: FixedPointObstructionManifest,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointObstructionReport:
    """Validate fixed-point obstructions and their current dependencies."""

    checked_language_path = Path(formal_language_path)
    checked_willard_map_path = Path(willard_map_path)
    checked_candidates_path = Path(manifest.fixed_point_equation_candidates_path)
    checked_codebook_path = Path(manifest.codebook_path)

    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    candidates = load_fixed_point_equation_candidates(checked_candidates_path)
    candidate_report = validate_fixed_point_equation_candidates(
        candidates,
        checked_language_path,
        checked_willard_map_path,
    )
    targets = load_fixed_point_targets(candidates.fixed_point_targets_path)
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[FixedPointObstructionValidation] = [
        _accepted("manifest", f"loaded {len(manifest.obstructions)} obstruction(s)")
    ]
    observations: list[FixedPointObstructionObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(_validate_dependency_reports(candidate_report, codebook_report))
    results.extend(_validate_obstruction_kind(manifest))
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    obstruction_results, observations = _validate_obstructions(
        manifest.obstructions,
        candidates.candidates,
        targets.targets,
        candidates.fixed_point_targets_path,
        candidates.quotation_term_examples_path,
        candidates.codebook_path,
        codebook,
    )
    results.extend(obstruction_results)

    return FixedPointObstructionReport(
        manifest=manifest,
        fixed_point_equation_candidates_path=checked_candidates_path,
        codebook_path=checked_codebook_path,
        formal_language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def fixed_point_obstruction_report_payload(
    report: FixedPointObstructionReport,
) -> dict[str, Any]:
    """Return a JSON-ready fixed-point obstruction validation payload."""

    observations = {
        observation.obstruction_id: observation
        for observation in report.observations
    }
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "obstruction_manifest": str(report.manifest.path),
        "obstruction_set_id": report.manifest.obstruction_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_equation_candidates_path": (
            str(report.fixed_point_equation_candidates_path)
        ),
        "codebook_path": str(report.codebook_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "obstruction_kind": report.manifest.obstruction_kind,
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
        "obstruction_count": report.obstruction_count,
        "failed_subjects": list(report.failed_subjects),
        "obstructions": [
            _obstruction_payload(
                obstruction,
                observations.get(obstruction.obstruction_id),
            )
            for obstruction in report.manifest.obstructions
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


def format_fixed_point_obstruction_report(
    report: FixedPointObstructionReport,
) -> str:
    """Format a concise human-readable fixed-point obstruction report."""

    observations = {
        observation.obstruction_id: observation
        for observation in report.observations
    }
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point obstructions: {status}",
        f"Obstruction set: {report.manifest.obstruction_set_id}",
        f"Obstructions: {report.obstruction_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for obstruction in report.manifest.obstructions:
        observation = observations.get(obstruction.obstruction_id)
        impossible_text = "unknown"
        growth_text = "unknown"
        if observation is not None:
            impossible_text = "yes" if observation.impossible_by_length else "no"
            growth_text = str(observation.minimum_growth_delta)
        lines.extend([
            f"- {obstruction.obstruction_id}",
            f"  Candidate: {obstruction.candidate_id}",
            f"  Status: {obstruction.status}",
            f"  Impossible by length: {impossible_text}",
            f"  Minimum growth delta: {growth_text}",
            "  Future work: " + _joined_or_none(obstruction.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_obstruction_cli(argv: list[str] | None = None) -> int:
    """Run the fixed-point obstruction validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_obstruction",
        description="Validate AS fixed-point obstruction records.",
    )
    parser.add_argument(
        "--obstructions",
        default=str(DEFAULT_OBSTRUCTIONS),
        help="Path to the fixed-point obstruction manifest.",
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

    manifest = load_fixed_point_obstructions(args.obstructions)
    report = validate_fixed_point_obstructions(
        manifest,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(fixed_point_obstruction_report_payload(report), sort_keys=True))
    else:
        print(format_fixed_point_obstruction_report(report))
    return 0 if report.accepted else 1


def _obstruction_payload(
    obstruction: FixedPointObstruction,
    observation: FixedPointObstructionObservation | None,
) -> dict[str, Any]:
    payload = {
        "obstruction_id": obstruction.obstruction_id,
        "candidate_id": obstruction.candidate_id,
        "status": obstruction.status,
        "expected_template_variable_occurrences": (
            obstruction.expected_template_variable_occurrences
        ),
        "expected_context_code_length": obstruction.expected_context_code_length,
        "expected_observed_input_length": (
            obstruction.expected_observed_input_length
        ),
        "expected_observed_input_token_sum": (
            obstruction.expected_observed_input_token_sum
        ),
        "expected_observed_candidate_length": (
            obstruction.expected_observed_candidate_length
        ),
        "required_future_work": list(obstruction.required_future_work),
        "non_claims": list(obstruction.non_claims),
        "next_as_action": obstruction.next_as_action,
    }
    if observation is None:
        payload.update({
            "template_variable_occurrences": None,
            "context_code_length": None,
            "nil_candidate_code_length": None,
            "observed_input_length": None,
            "observed_input_token_sum": None,
            "observed_quote_term_code_length": None,
            "observed_candidate_length": None,
            "formula_candidate_length": None,
            "minimum_growth_delta": None,
            "impossible_by_length": None,
        })
    else:
        payload.update({
            "template_variable_occurrences": (
                observation.template_variable_occurrences
            ),
            "context_code_length": observation.context_code_length,
            "nil_candidate_code_length": observation.nil_candidate_code_length,
            "observed_input_length": observation.observed_input_length,
            "observed_input_token_sum": observation.observed_input_token_sum,
            "observed_quote_term_code_length": (
                observation.observed_quote_term_code_length
            ),
            "observed_candidate_length": observation.observed_candidate_length,
            "formula_candidate_length": observation.formula_candidate_length,
            "minimum_growth_delta": observation.minimum_growth_delta,
            "impossible_by_length": observation.impossible_by_length,
        })
    return payload


def _validate_references(
    manifest: FixedPointObstructionManifest,
) -> list[FixedPointObstructionValidation]:
    expected = (
        (
            "fixed_point_equation_candidates_path",
            manifest.fixed_point_equation_candidates_path,
            "claims/fixed_point_equation_candidates.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
    )
    results: list[FixedPointObstructionValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    candidate_report: Any,
    codebook_report: Any,
) -> list[FixedPointObstructionValidation]:
    checks = (
        ("fixed_point_equation_candidate", candidate_report, "fixed-point equation candidate"),
        ("codebook", codebook_report, "formal codebook"),
    )
    results: list[FixedPointObstructionValidation] = []
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


def _validate_obstruction_kind(
    manifest: FixedPointObstructionManifest,
) -> list[FixedPointObstructionValidation]:
    if manifest.obstruction_kind == VALID_OBSTRUCTION_KIND:
        return [_accepted("obstruction_kind", VALID_OBSTRUCTION_KIND)]
    return [
        _rejected(
            "obstruction_kind",
            f"unknown obstruction kind: {manifest.obstruction_kind}",
        )
    ]


def _validate_willard_anchors(
    manifest: FixedPointObstructionManifest,
    known_anchor_ids: set[str],
) -> list[FixedPointObstructionValidation]:
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


def _validate_obstructions(
    obstructions: tuple[FixedPointObstruction, ...],
    candidates: tuple[FixedPointEquationCandidate, ...],
    targets: tuple[FixedPointTarget, ...],
    fixed_point_targets_path: str,
    quotation_term_examples_path: str,
    codebook_path: str,
    codebook: FormalCodebook,
) -> tuple[list[FixedPointObstructionValidation], list[FixedPointObstructionObservation]]:
    if not obstructions:
        return [_rejected("obstructions", "no fixed-point obstructions")], []

    results: list[FixedPointObstructionValidation] = []
    observations: list[FixedPointObstructionObservation] = []
    obstruction_ids = [obstruction.obstruction_id for obstruction in obstructions]
    duplicate_ids = _duplicates(obstruction_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "obstructions.obstruction_id",
                "duplicate obstruction ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("obstructions.obstruction_id", "obstruction ids are unique"))

    for obstruction in obstructions:
        obstruction_results, observation = _validate_obstruction(
            obstruction,
            candidates,
            targets,
            fixed_point_targets_path,
            quotation_term_examples_path,
            codebook_path,
            codebook,
        )
        results.extend(obstruction_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("obstructions", f"checked {len(obstructions)} obstruction(s)"))
    return results, observations


def _validate_obstruction(
    obstruction: FixedPointObstruction,
    candidates: tuple[FixedPointEquationCandidate, ...],
    targets: tuple[FixedPointTarget, ...],
    fixed_point_targets_path: str,
    quotation_term_examples_path: str,
    codebook_path: str,
    codebook: FormalCodebook,
) -> tuple[list[FixedPointObstructionValidation], FixedPointObstructionObservation | None]:
    subject = obstruction.obstruction_id
    results: list[FixedPointObstructionValidation] = []

    if obstruction.status not in VALID_OBSTRUCTION_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {obstruction.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "obstruction status preserves non-claim"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in obstruction.required_future_work
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

    if not obstruction.non_claims:
        results.append(_rejected(f"{subject}.non_claims", "non-claims must be explicit"))
    else:
        results.append(_accepted(f"{subject}.non_claims", "non-claims are explicit"))

    try:
        candidate = _find_candidate(candidates, obstruction.candidate_id)
        target = _find_target(targets, candidate.target_id)
    except ValueError as exc:
        results.append(_rejected(f"{subject}.candidate", str(exc)))
        return results, None

    try:
        tokens = candidate.expected_original_code
        nil_node = {"kind": "sequence_nil"}
        nil_code_length = len(encode_node(nil_node, codebook))
        nil_candidate = substitute_node(
            target.template_node,
            target.template_variable,
            nil_node,
        )
        nil_candidate_code_length = len(encode_node(nil_candidate, codebook))
        context_code_length = nil_candidate_code_length - nil_code_length
        observed_candidate_length = len(
            build_candidate_code(
                target_id=candidate.target_id,
                quotation_term_example_id=candidate.quotation_term_example_id,
                fixed_point_targets_path=fixed_point_targets_path,
                quotation_term_examples_path=quotation_term_examples_path,
                codebook_path=codebook_path,
            )
        )
        observed_quote_term_code_length = len(
            encode_node(quote_tokens_as_term(tokens), codebook)
        )
        formula_quote_length = quote_term_code_length_formula(tokens)
        formula_candidate_length = naive_candidate_code_length_formula(
            tokens,
            context_code_length,
        )
        template_variable_occurrences = _count_free_variable_occurrences(
            target.template_node,
            target.template_variable,
        )
    except ValueError as exc:
        results.append(_rejected(f"{subject}.length", str(exc)))
        return results, None

    minimum_growth_delta = context_code_length + 1
    impossible_by_length = (
        template_variable_occurrences == 1
        and context_code_length >= 0
        and minimum_growth_delta > 0
    )

    observation = FixedPointObstructionObservation(
        obstruction_id=obstruction.obstruction_id,
        candidate_id=obstruction.candidate_id,
        status=obstruction.status,
        template_variable_occurrences=template_variable_occurrences,
        context_code_length=context_code_length,
        nil_candidate_code_length=nil_candidate_code_length,
        observed_input_length=len(tokens),
        observed_input_token_sum=sum(tokens),
        observed_quote_term_code_length=observed_quote_term_code_length,
        observed_candidate_length=observed_candidate_length,
        formula_candidate_length=formula_candidate_length,
        minimum_growth_delta=minimum_growth_delta,
        impossible_by_length=impossible_by_length,
    )

    if obstruction.expected_template_variable_occurrences != template_variable_occurrences:
        results.append(
            _rejected(
                f"{subject}.length",
                "template variable occurrence mismatch: expected "
                + str(obstruction.expected_template_variable_occurrences)
                + " got "
                + str(template_variable_occurrences),
            )
        )
    elif obstruction.expected_context_code_length != context_code_length:
        results.append(
            _rejected(
                f"{subject}.length",
                "context code length mismatch: expected "
                + str(obstruction.expected_context_code_length)
                + " got "
                + str(context_code_length),
            )
        )
    elif obstruction.expected_observed_input_length != len(tokens):
        results.append(
            _rejected(
                f"{subject}.length",
                "observed input length mismatch: expected "
                + str(obstruction.expected_observed_input_length)
                + " got "
                + str(len(tokens)),
            )
        )
    elif obstruction.expected_observed_input_token_sum != sum(tokens):
        results.append(
            _rejected(
                f"{subject}.length",
                "observed input token sum mismatch: expected "
                + str(obstruction.expected_observed_input_token_sum)
                + " got "
                + str(sum(tokens)),
            )
        )
    elif formula_quote_length != observed_quote_term_code_length:
        results.append(
            _rejected(
                f"{subject}.length",
                "quotation length formula mismatch",
            )
        )
    elif obstruction.expected_observed_candidate_length != observed_candidate_length:
        results.append(
            _rejected(
                f"{subject}.length",
                "observed candidate length mismatch: expected "
                + str(obstruction.expected_observed_candidate_length)
                + " got "
                + str(observed_candidate_length),
            )
        )
    elif formula_candidate_length != observed_candidate_length:
        results.append(
            _rejected(
                f"{subject}.length",
                "candidate length formula mismatch: expected "
                + str(formula_candidate_length)
                + " got "
                + str(observed_candidate_length),
            )
        )
    elif not impossible_by_length:
        results.append(
            _rejected(
                f"{subject}.obstruction",
                "length growth does not rule out the naive candidate",
            )
        )
    else:
        detail = (
            "naive candidate length strictly grows: candidate length = "
            + str(context_code_length)
            + " + 1 + 2*input_length + token_sum"
        )
        results.append(_accepted(f"{subject}.obstruction", detail))

    return results, observation


def _find_candidate(
    candidates: tuple[FixedPointEquationCandidate, ...],
    candidate_id: str,
) -> FixedPointEquationCandidate:
    for candidate in candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    raise ValueError(f"unknown fixed-point equation candidate: {candidate_id}")


def _find_target(
    targets: tuple[FixedPointTarget, ...],
    target_id: str,
) -> FixedPointTarget:
    for target in targets:
        if target.target_id == target_id:
            return target
    raise ValueError(f"unknown fixed-point target: {target_id}")


def _count_free_variable_occurrences(node: dict[str, Any], name: str) -> int:
    kind = _node_kind(node)
    if kind == "variable":
        return 1 if node.get("name") == name else 0
    if kind in {"zero", "sequence_nil"}:
        return 0
    if kind == "successor":
        return _count_free_variable_occurrences(_required_node(node, "term"), name)
    if kind == "sequence_cons":
        return (
            _count_free_variable_occurrences(_required_node(node, "head"), name)
            + _count_free_variable_occurrences(_required_node(node, "tail"), name)
        )
    if kind in {"addition", "multiplication", "equals", "less_than", "and", "or", "implies"}:
        return (
            _count_free_variable_occurrences(_required_node(node, "left"), name)
            + _count_free_variable_occurrences(_required_node(node, "right"), name)
        )
    if kind == "not":
        return _count_free_variable_occurrences(_required_node(node, "body"), name)
    if kind in {"forall", "exists", "pi1", "sigma1"}:
        if node.get("variable") == name:
            return 0
        return _count_free_variable_occurrences(_required_node(node, "body"), name)
    if kind in {"bounded_forall", "bounded_exists"}:
        bound_count = _count_free_variable_occurrences(_required_node(node, "bound"), name)
        if node.get("variable") == name:
            return bound_count
        return bound_count + _count_free_variable_occurrences(
            _required_node(node, "body"),
            name,
        )
    raise ValueError(f"unknown node kind: {kind}")


def _parse_obstruction(item: dict[str, Any]) -> FixedPointObstruction:
    return FixedPointObstruction(
        obstruction_id=_required_text(item, "obstruction_id"),
        candidate_id=_required_text(item, "candidate_id"),
        status=_required_text(item, "status"),
        expected_template_variable_occurrences=_required_int(
            item,
            "expected_template_variable_occurrences",
        ),
        expected_context_code_length=_required_int(item, "expected_context_code_length"),
        expected_observed_input_length=_required_int(
            item,
            "expected_observed_input_length",
        ),
        expected_observed_input_token_sum=_required_int(
            item,
            "expected_observed_input_token_sum",
        ),
        expected_observed_candidate_length=_required_int(
            item,
            "expected_observed_candidate_length",
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "fixed-point-obstruction-willard-anchor"
    if subject.endswith(".status"):
        return "fixed-point-obstruction-status"
    if subject.endswith(".candidate") or subject.startswith("obstructions"):
        return "fixed-point-obstruction-candidate"
    if subject.endswith(".length") or subject.endswith(".obstruction"):
        return "fixed-point-obstruction-length"
    if subject in {
        "fixed_point_equation_candidate",
        "codebook",
        "obstruction_kind",
    }:
        return "fixed-point-obstruction-manifest"
    if subject in {
        "fixed_point_equation_candidates_path",
        "codebook_path",
    }:
        return "fixed-point-obstruction-reference"
    return "fixed-point-obstruction"


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


def _natural_tokens(tokens: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    checked_tokens = tuple(tokens)
    for token in checked_tokens:
        if not isinstance(token, int) or isinstance(token, bool) or token < 0:
            raise ValueError("code tokens must be natural numbers")
    return checked_tokens


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _node_kind(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ValueError("node missing kind")
    return kind


def _required_node(node: dict[str, Any], key: str) -> dict[str, Any]:
    value = node.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"node missing child: {key}")
    return value


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def _accepted(subject: str, detail: str) -> FixedPointObstructionValidation:
    return FixedPointObstructionValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(subject: str, detail: str) -> FixedPointObstructionValidation:
    return FixedPointObstructionValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess test.
    raise SystemExit(run_fixed_point_obstruction_cli())
