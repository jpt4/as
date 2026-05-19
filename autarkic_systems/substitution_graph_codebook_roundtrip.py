"""Finite codebook roundtrip domain for substitution graph evidence.

This module checks the graph-domain codes currently exercised by the
substitution graph formula candidate and finite evaluation examples. It is
finite executable evidence for the first correctness proof case, not a proof
that every possible substitution graph code round-trips.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.formal_code import (
    FormalCodebook,
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import substitute_node
from autarkic_systems.substitution_graph_evaluation import (
    SubstitutionGraphEvaluationExample,
    load_substitution_graph_evaluation_examples,
    validate_substitution_graph_evaluation_examples,
)
from autarkic_systems.substitution_graph_formula import (
    SubstitutionGraphFormulaCandidate,
    load_substitution_graph_formula_candidates,
    validate_substitution_graph_formula_candidates,
)
from autarkic_systems.substitution_representability import (
    SubstitutionRepresentabilityObservation,
    SubstitutionRepresentabilityWitness,
    build_substitution_witness_output_code,
    load_substitution_representability_targets,
    validate_substitution_representability_targets,
)


DEFAULT_ROUNDTRIP = Path("claims/substitution_graph_codebook_roundtrip.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = (
    "formula-candidate",
    "finite-evaluation",
)
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


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripManifest:
    """Loaded manifest for the current substitution graph roundtrip domain."""

    path: Path
    schema_version: int
    roundtrip_set_id: str
    reviewed_at: str
    purpose: str
    codebook_path: str
    formula_candidates_path: str
    evaluation_examples_path: str
    expected_subject_count: int
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripValidation:
    """One validation result for graph-domain codebook roundtrips."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripSubject:
    """One observed graph-domain code subject and its roundtrip result."""

    subject_id: str
    source_kind: str
    source_id: str
    code_role: str
    code_length: int
    decoded_kind: str
    roundtrip_ok: bool


@dataclass(frozen=True)
class SubstitutionGraphCodebookRoundtripReport:
    """Validation report over the finite graph-domain roundtrip set."""

    manifest: SubstitutionGraphCodebookRoundtripManifest
    codebook_path: Path
    formula_candidates_path: Path
    evaluation_examples_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionGraphCodebookRoundtripValidation, ...]
    subjects: tuple[SubstitutionGraphCodebookRoundtripSubject, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every roundtrip validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def subject_count(self) -> int:
        """Return the number of checked graph-domain code subjects."""

        return len(self.subjects)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed subject counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for subject in self.subjects:
            counts[subject.source_kind] = counts.get(subject.source_kind, 0) + 1
        return counts

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


def load_substitution_graph_codebook_roundtrip(
    path: Path | str = DEFAULT_ROUNDTRIP,
) -> SubstitutionGraphCodebookRoundtripManifest:
    """Load the graph-domain codebook roundtrip manifest from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return SubstitutionGraphCodebookRoundtripManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        roundtrip_set_id=_required_text(data, "roundtrip_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        codebook_path=_required_text(data, "codebook_path"),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        evaluation_examples_path=_required_text(data, "evaluation_examples_path"),
        expected_subject_count=_required_int(data, "expected_subject_count"),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_codebook_roundtrip(
    manifest: SubstitutionGraphCodebookRoundtripManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphCodebookRoundtripReport:
    """Validate graph-domain code roundtrips through the checked codebook."""

    checked_willard_map_path = Path(willard_map_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_formula_path = Path(manifest.formula_candidates_path)
    checked_evaluation_path = Path(manifest.evaluation_examples_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        willard_map_path=checked_willard_map_path,
    )
    formula_manifest = load_substitution_graph_formula_candidates(checked_formula_path)
    formula_report = validate_substitution_graph_formula_candidates(
        formula_manifest,
        checked_willard_map_path,
    )
    evaluation_manifest = load_substitution_graph_evaluation_examples(
        checked_evaluation_path,
    )
    evaluation_report = validate_substitution_graph_evaluation_examples(
        evaluation_manifest,
        checked_willard_map_path,
    )

    results: list[SubstitutionGraphCodebookRoundtripValidation] = [
        _accepted("manifest", f"loaded {manifest.roundtrip_set_id}")
    ]
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            codebook_report,
            formula_report,
            evaluation_report,
        )
    )
    subjects: list[SubstitutionGraphCodebookRoundtripSubject] = []
    try:
        subjects = _derive_roundtrip_subjects(
            formula_manifest.candidates,
            evaluation_manifest.examples,
            codebook,
            formula_manifest.substitution_representability_targets_path,
            checked_willard_map_path,
        )
    except ValueError as exc:
        results.append(_rejected("roundtrip_subjects", str(exc)))

    results.extend(_validate_subject_set(manifest, tuple(subjects)))

    return SubstitutionGraphCodebookRoundtripReport(
        manifest=manifest,
        codebook_path=checked_codebook_path,
        formula_candidates_path=checked_formula_path,
        evaluation_examples_path=checked_evaluation_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        subjects=tuple(subjects),
    )


def substitution_graph_codebook_roundtrip_report_payload(
    report: SubstitutionGraphCodebookRoundtripReport,
) -> dict[str, Any]:
    """Return a JSON-ready graph-domain roundtrip payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "roundtrip_manifest": str(report.manifest.path),
        "roundtrip_set_id": report.manifest.roundtrip_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "codebook_path": str(report.codebook_path),
        "formula_candidates_path": str(report.formula_candidates_path),
        "evaluation_examples_path": str(report.evaluation_examples_path),
        "willard_map": str(report.willard_map_path),
        "expected_subject_count": report.manifest.expected_subject_count,
        "subject_count": report.subject_count,
        "source_kind_counts": report.source_kind_counts,
        "required_source_kinds": list(report.manifest.required_source_kinds),
        "required_future_work": list(report.manifest.required_future_work),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "subjects": [
            {
                "subject_id": subject.subject_id,
                "source_kind": subject.source_kind,
                "source_id": subject.source_id,
                "code_role": subject.code_role,
                "observed_code_length": subject.code_length,
                "observed_decoded_kind": subject.decoded_kind,
                "observed_roundtrip_ok": subject.roundtrip_ok,
            }
            for subject in report.subjects
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


def format_substitution_graph_codebook_roundtrip_report(
    report: SubstitutionGraphCodebookRoundtripReport,
) -> str:
    """Format a concise human-readable graph-domain roundtrip report."""

    status = "accepted" if report.accepted else "rejected"
    failures = [
        subject.subject_id for subject in report.subjects if not subject.roundtrip_ok
    ]
    source_counts = ", ".join(
        f"{source_kind}={count}"
        for source_kind, count in report.source_kind_counts.items()
    )
    lines = [
        f"Substitution graph codebook roundtrip: {status}",
        f"Roundtrip set: {report.manifest.roundtrip_set_id}",
        f"Subjects: {report.subject_count}",
        f"Source kinds: {source_counts}",
        f"Roundtrip failures: {_joined_or_none(tuple(failures))}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_codebook_roundtrip_cli(
    argv: list[str] | None = None,
) -> int:
    """Run finite graph-domain codebook roundtrip validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.substitution_graph_codebook_roundtrip",
        description="Validate substitution graph codebook roundtrip subjects.",
    )
    parser.add_argument(
        "--roundtrip",
        default=str(DEFAULT_ROUNDTRIP),
        help="Path to the graph-domain roundtrip manifest.",
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

    manifest = load_substitution_graph_codebook_roundtrip(args.roundtrip)
    report = validate_substitution_graph_codebook_roundtrip(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_graph_codebook_roundtrip_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_graph_codebook_roundtrip_report(report))
    return 0 if report.accepted else 1


def _validate_references(
    manifest: SubstitutionGraphCodebookRoundtripManifest,
) -> list[SubstitutionGraphCodebookRoundtripValidation]:
    expected = (
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "formula_candidates_path",
            manifest.formula_candidates_path,
            "claims/substitution_graph_formula_candidates.json",
        ),
        (
            "evaluation_examples_path",
            manifest.evaluation_examples_path,
            "claims/substitution_graph_evaluation_examples.json",
        ),
    )
    results: list[SubstitutionGraphCodebookRoundtripValidation] = []
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
    formula_report: Any,
    evaluation_report: Any,
) -> list[SubstitutionGraphCodebookRoundtripValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("formula_candidates", formula_report, "substitution graph formula"),
        ("evaluation_examples", evaluation_report, "substitution graph evaluation"),
    )
    results: list[SubstitutionGraphCodebookRoundtripValidation] = []
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


def _derive_roundtrip_subjects(
    candidates: tuple[SubstitutionGraphFormulaCandidate, ...],
    examples: tuple[SubstitutionGraphEvaluationExample, ...],
    codebook: FormalCodebook,
    representability_targets_path: str,
    willard_map_path: Path,
) -> list[SubstitutionGraphCodebookRoundtripSubject]:
    subjects: list[SubstitutionGraphCodebookRoundtripSubject] = []
    witness_manifest = load_substitution_representability_targets(
        representability_targets_path,
    )
    witness_report = validate_substitution_representability_targets(
        witness_manifest,
        willard_map_path=willard_map_path,
    )
    if not witness_report.accepted:
        raise ValueError(
            "substitution representability rejected: "
            + _joined_or_none(witness_report.failed_subjects)
        )

    for candidate in candidates:
        witness = _find_witness(witness_manifest.witnesses, candidate.witness_id)
        observation = _find_witness_observation(
            witness_report.observations,
            candidate.witness_id,
        )
        subjects.extend(
            _candidate_subjects(
                candidate,
                witness,
                observation,
                codebook,
                representability_targets_path,
            )
        )

    for example in examples:
        subjects.extend(_evaluation_subjects(example, codebook))

    return subjects


def _candidate_subjects(
    candidate: SubstitutionGraphFormulaCandidate,
    witness: SubstitutionRepresentabilityWitness,
    observation: SubstitutionRepresentabilityObservation,
    codebook: FormalCodebook,
    representability_targets_path: str,
) -> list[SubstitutionGraphCodebookRoundtripSubject]:
    output_code = build_substitution_witness_output_code(
        witness_id=candidate.witness_id,
        targets_path=representability_targets_path,
    )
    instance = candidate.formula_node
    substitutions = (
        (candidate.graph_variables["formula_code"], observation.formula_code),
        (candidate.graph_variables["argument_code"], observation.argument_code),
        (candidate.graph_variables["output_code"], output_code),
    )
    for variable, code in substitutions:
        instance = substitute_node(instance, variable, quote_tokens_as_term(code))

    formula_node = decode_code(observation.formula_code, codebook)
    evaluated_output_node = substitute_node(
        formula_node,
        witness.variable,
        quote_tokens_as_term(observation.argument_code),
    )
    return [
        _roundtrip_subject(
            f"{candidate.candidate_id}.formula_code",
            "formula-candidate",
            candidate.candidate_id,
            "formula_code",
            encode_node(candidate.formula_node, codebook),
            codebook,
        ),
        _roundtrip_subject(
            f"{candidate.candidate_id}.witness_instance_code",
            "formula-candidate",
            candidate.candidate_id,
            "witness_instance_code",
            encode_node(instance, codebook),
            codebook,
        ),
        _roundtrip_subject(
            f"{candidate.candidate_id}.evaluated_output_code",
            "formula-candidate",
            candidate.candidate_id,
            "evaluated_output_code",
            encode_node(evaluated_output_node, codebook),
            codebook,
        ),
    ]


def _evaluation_subjects(
    example: SubstitutionGraphEvaluationExample,
    codebook: FormalCodebook,
) -> list[SubstitutionGraphCodebookRoundtripSubject]:
    output_node = substitute_node(
        example.formula_node,
        example.variable,
        quote_tokens_as_term(example.argument_code),
    )
    return [
        _roundtrip_subject(
            f"{example.example_id}.formula_code",
            "finite-evaluation",
            example.example_id,
            "formula_code",
            encode_node(example.formula_node, codebook),
            codebook,
        ),
        _roundtrip_subject(
            f"{example.example_id}.argument_code",
            "finite-evaluation",
            example.example_id,
            "argument_code",
            example.argument_code,
            codebook,
        ),
        _roundtrip_subject(
            f"{example.example_id}.output_code",
            "finite-evaluation",
            example.example_id,
            "output_code",
            encode_node(output_node, codebook),
            codebook,
        ),
    ]


def _roundtrip_subject(
    subject_id: str,
    source_kind: str,
    source_id: str,
    code_role: str,
    code: tuple[int, ...],
    codebook: FormalCodebook,
) -> SubstitutionGraphCodebookRoundtripSubject:
    decoded = decode_code(code, codebook)
    reencoded = encode_node(decoded, codebook)
    return SubstitutionGraphCodebookRoundtripSubject(
        subject_id=subject_id,
        source_kind=source_kind,
        source_id=source_id,
        code_role=code_role,
        code_length=len(code),
        decoded_kind=_node_kind(decoded),
        roundtrip_ok=reencoded == code,
    )


def _validate_subject_set(
    manifest: SubstitutionGraphCodebookRoundtripManifest,
    subjects: tuple[SubstitutionGraphCodebookRoundtripSubject, ...],
) -> list[SubstitutionGraphCodebookRoundtripValidation]:
    results: list[SubstitutionGraphCodebookRoundtripValidation] = []
    subject_ids = [subject.subject_id for subject in subjects]
    duplicate_ids = _duplicates(subject_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "roundtrip_subject_ids",
                "duplicate subject ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("roundtrip_subject_ids", "subject ids are unique"))

    if len(subjects) != manifest.expected_subject_count:
        results.append(
            _rejected(
                "expected_subject_count",
                "subject count mismatch: expected "
                + str(manifest.expected_subject_count)
                + " got "
                + str(len(subjects)),
            )
        )
    else:
        results.append(
            _accepted(
                "expected_subject_count",
                f"checked {len(subjects)} subject(s)",
            )
        )

    source_kinds = {subject.source_kind for subject in subjects}
    missing_source_kinds = [
        source_kind
        for source_kind in REQUIRED_SOURCE_KINDS
        if source_kind not in manifest.required_source_kinds
        or source_kind not in source_kinds
    ]
    if missing_source_kinds:
        results.append(
            _rejected(
                "required_source_kinds",
                "missing source kinds: " + ", ".join(missing_source_kinds),
            )
        )
    else:
        results.append(_accepted("required_source_kinds", "source kinds covered"))

    failures = [subject.subject_id for subject in subjects if not subject.roundtrip_ok]
    if failures:
        results.append(
            _rejected(
                "roundtrip_subjects",
                "roundtrip failures: " + ", ".join(failures),
            )
        )
    else:
        results.append(
            _accepted(
                "roundtrip_subjects",
                f"round-tripped {len(subjects)} graph-domain code subject(s)",
            )
        )

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in manifest.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                "required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(_accepted("required_future_work", "future work is explicit"))

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in manifest.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    return results


def _find_witness(
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityWitness:
    for witness in witnesses:
        if witness.witness_id == witness_id:
            return witness
    raise ValueError(f"unknown substitution witness: {witness_id}")


def _find_witness_observation(
    observations: tuple[SubstitutionRepresentabilityObservation, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityObservation:
    for observation in observations:
        if observation.witness_id == witness_id:
            return observation
    raise ValueError(f"missing substitution witness observation: {witness_id}")


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_subject_count":
        return "substitution-graph-codebook-roundtrip-count"
    if subject in {"roundtrip_subject_ids", "roundtrip_subjects"}:
        return "substitution-graph-codebook-roundtrip-subject"
    if subject == "required_source_kinds":
        return "substitution-graph-codebook-roundtrip-source-kind"
    if subject == "required_future_work":
        return "substitution-graph-codebook-roundtrip-future-work"
    if subject == "non_claims":
        return "substitution-graph-codebook-roundtrip-non-claim"
    if subject in {"codebook", "formula_candidates", "evaluation_examples"}:
        return "substitution-graph-codebook-roundtrip-dependency"
    if subject.endswith("_path"):
        return "substitution-graph-codebook-roundtrip-reference"
    return "substitution-graph-codebook-roundtrip"


def _node_kind(node: dict[str, Any]) -> str:
    kind = node.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ValueError("node kind missing")
    return kind


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
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
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


def _accepted(
    subject: str,
    detail: str,
) -> SubstitutionGraphCodebookRoundtripValidation:
    return SubstitutionGraphCodebookRoundtripValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphCodebookRoundtripValidation:
    return SubstitutionGraphCodebookRoundtripValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_graph_codebook_roundtrip_cli())
