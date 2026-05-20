"""Compact frontier status for meta-substitution semantics support.

The existing meta-substitution-semantics module checks a finite support surface
for the substitution graph correctness stack. This handoff layer keeps that
surface in its proper role: accepted finite evidence for an open proof case,
not a promotion to a general substitution-correctness proof.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.substitution_graph_correctness_cases import (
    REQUIRED_DEPENDENCIES_BY_KIND,
    REQUIRED_NON_CLAIMS as CASE_NON_CLAIMS,
    load_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_graph_meta_substitution_semantics import (
    DEFAULT_WILLARD_MAP,
    REQUIRED_NON_CLAIMS as SEMANTICS_NON_CLAIMS,
    load_substitution_graph_meta_substitution_semantics,
    validate_substitution_graph_meta_substitution_semantics,
)


DEFAULT_STATUS = Path(
    "claims/substitution_graph_meta_substitution_semantics_frontier_status.json"
)

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "meta-substitution-semantics"
REQUIRED_CASE_KIND = "meta-substitution-semantics"
REQUIRED_CASE_STATUS = "proof-case-open"
REQUIRED_CASE_ID = "AS-SUBST-GRAPH-CORRECTNESS-META-SUBSTITUTION-SEMANTICS"
REQUIRED_CORRECTNESS_TARGET_ID = "AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET"
REQUIRED_STATUS_SET_ID = (
    "as-substitution-graph-meta-substitution-semantics-frontier-status-v1"
)
REQUIRED_SEMANTICS_SET_ID = "as-substitution-graph-meta-substitution-semantics-v1"
EXPECTED_SEMANTICS_SUBJECT_COUNT = 6
EXPECTED_SUPPORT_SURFACE_COUNT = 1
REQUIRED_SUPPORT_SUBJECTS = ("meta_substitution_semantics",)
REQUIRED_CASE_SUPPORT_SUBJECTS = REQUIRED_DEPENDENCIES_BY_KIND[
    REQUIRED_CASE_KIND
]
REQUIRED_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
PROOF_PROMOTION_STATUSES = {
    "formula-correctness-proved",
    "substitution-representability-proved",
    "substitution-graph-correctness-proved",
    "diagonal-lemma-proved",
    "fixed-point-equation-proved",
    "arithmetized-proof-predicate-proved",
    "meta-substitution-semantics-proved",
    "self-consistency-proved",
    "self-consistency-theorem-proved",
}
PROOF_PROMOTION_NON_CLAIMS = {
    "formula correctness proof",
    "substitution representability proof",
    "diagonal lemma proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "self-consistency theorem",
}
EXPECTED_DEPENDENCY_PATHS = {
    "substitution_graph_correctness_cases_path": (
        "claims/substitution_graph_correctness_cases.json"
    ),
    "meta_substitution_semantics_path": (
        "claims/substitution_graph_meta_substitution_semantics.json"
    ),
    "formal_language_path": "language/formal_arithmetic_language.json",
    "codebook_path": "language/formal_codebook.json",
    "formal_substitution_examples_path": (
        "language/formal_substitution_examples.json"
    ),
    "formula_candidates_path": "claims/substitution_graph_formula_candidates.json",
    "evaluation_examples_path": "claims/substitution_graph_evaluation_examples.json",
}
EXPECTED_CASE_PATHS = {
    "formal_language_path": EXPECTED_DEPENDENCY_PATHS["formal_language_path"],
    "codebook_path": EXPECTED_DEPENDENCY_PATHS["codebook_path"],
    "correctness_targets_path": (
        "claims/substitution_graph_correctness_targets.json"
    ),
    "formal_substitution_examples_path": EXPECTED_DEPENDENCY_PATHS[
        "formal_substitution_examples_path"
    ],
    "formula_candidates_path": EXPECTED_DEPENDENCY_PATHS[
        "formula_candidates_path"
    ],
    "meta_substitution_semantics_path": EXPECTED_DEPENDENCY_PATHS[
        "meta_substitution_semantics_path"
    ],
}
EXPECTED_SEMANTICS_PATHS = {
    "formal_language_path": EXPECTED_DEPENDENCY_PATHS["formal_language_path"],
    "codebook_path": EXPECTED_DEPENDENCY_PATHS["codebook_path"],
    "formal_substitution_examples_path": EXPECTED_DEPENDENCY_PATHS[
        "formal_substitution_examples_path"
    ],
    "formula_candidates_path": EXPECTED_DEPENDENCY_PATHS[
        "formula_candidates_path"
    ],
    "evaluation_examples_path": EXPECTED_DEPENDENCY_PATHS[
        "evaluation_examples_path"
    ],
}


@dataclass(frozen=True)
class SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest:
    """Loaded manifest for the compact meta-substitution frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    substitution_graph_correctness_cases_path: str
    meta_substitution_semantics_path: str
    formal_language_path: str
    codebook_path: str
    formal_substitution_examples_path: str
    formula_candidates_path: str
    evaluation_examples_path: str
    required_case_kind: str
    required_case_status: str
    expected_support_surface_count: int
    expected_semantics_subject_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation:
    """One validation result for the compact frontier status."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphMetaSubstitutionSemanticsFrontierProofCase:
    """Compact view of the matching substitution graph correctness case."""

    case_id: str
    case_kind: str
    correctness_target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphMetaSubstitutionSemanticsFrontierSupportSurface:
    """Observed status of the finite semantics support surface."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusReport:
    """Validation report for the compact meta-substitution frontier."""

    manifest: SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest
    substitution_graph_correctness_cases_path: Path
    meta_substitution_semantics_path: Path
    formal_language_path: Path
    codebook_path: Path
    formal_substitution_examples_path: Path
    formula_candidates_path: Path
    evaluation_examples_path: Path
    proof_case: SubstitutionGraphMetaSubstitutionSemanticsFrontierProofCase
    support_surfaces: tuple[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierSupportSurface,
        ...
    ]
    support_facts: dict[str, dict[str, Any]]
    results: tuple[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation,
        ...
    ]

    @property
    def accepted(self) -> bool:
        """Return whether every compact frontier validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the preserved frontier status."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the proof case that still blocks this frontier."""

        return self.manifest.frontier_blocked_by

    @property
    def support_surface_count(self) -> int:
        """Return the number of compact support surfaces inspected."""

        return len(self.support_surfaces)

    @property
    def semantics_subject_count(self) -> int:
        """Return the observed finite semantics subject count."""

        return int(
            self.support_facts
            .get("meta_substitution_semantics", {})
            .get("subject_count", 0)
        )

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return stable failure subjects for automation and reports."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


@dataclass(frozen=True)
class _SupportLoad:
    """Small result shim for loading support manifests fail-closed."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]


def load_substitution_graph_meta_substitution_semantics_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest:
    """Load the compact meta-substitution frontier manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest(
        path=status_path,
        schema_version=_required_int(data, "schema_version"),
        status_set_id=_required_text(data, "status_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        frontier_status=_required_text(data, "frontier_status"),
        frontier_blocked_by=_required_text(data, "frontier_blocked_by"),
        substitution_graph_correctness_cases_path=_required_text(
            data,
            "substitution_graph_correctness_cases_path",
        ),
        meta_substitution_semantics_path=_required_text(
            data,
            "meta_substitution_semantics_path",
        ),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        formal_substitution_examples_path=_required_text(
            data,
            "formal_substitution_examples_path",
        ),
        formula_candidates_path=_required_text(data, "formula_candidates_path"),
        evaluation_examples_path=_required_text(data, "evaluation_examples_path"),
        required_case_kind=_required_text(data, "required_case_kind"),
        required_case_status=_required_text(data, "required_case_status"),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        expected_semantics_subject_count=_required_int(
            data,
            "expected_semantics_subject_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_meta_substitution_semantics_frontier_status(
    manifest: SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusReport:
    """Validate the compact handoff without promoting the proof case."""

    paths = _manifest_paths(manifest)
    checked_willard_map_path = Path(willard_map_path)
    results: list[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation
    ] = [_accepted("manifest", f"loaded {manifest.status_set_id}")]
    results.extend(_validate_manifest(manifest))

    cases_manifest, cases_load = _load_correctness_cases(
        paths["substitution_graph_correctness_cases_path"]
    )
    semantics_manifest, semantics_load = _load_meta_substitution_semantics(
        paths["meta_substitution_semantics_path"],
        checked_willard_map_path,
    )

    if cases_load.accepted:
        results.append(_accepted("cases_manifest", "case manifest loaded"))
    else:
        results.append(
            _rejected(
                "cases_manifest",
                "case manifest rejected: "
                + _joined_or_none(cases_load.failed_subjects),
            )
        )
    results.extend(_validate_case_manifest_paths(cases_manifest))

    proof_case = _find_meta_substitution_semantics_case(cases_manifest)
    results.extend(_validate_proof_case(proof_case))
    results.extend(
        _validate_support_path_alignment(
            manifest,
            cases_manifest,
            semantics_manifest,
        )
    )

    support_loads = {"meta_substitution_semantics": semantics_load}
    support_surfaces = _support_surfaces(paths, support_loads)
    results.extend(_validate_support_surfaces(manifest, support_surfaces))
    results.extend(_validate_case_support(proof_case, support_surfaces))

    return SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusReport(
        manifest=manifest,
        substitution_graph_correctness_cases_path=paths[
            "substitution_graph_correctness_cases_path"
        ],
        meta_substitution_semantics_path=paths[
            "meta_substitution_semantics_path"
        ],
        formal_language_path=paths["formal_language_path"],
        codebook_path=paths["codebook_path"],
        formal_substitution_examples_path=paths[
            "formal_substitution_examples_path"
        ],
        formula_candidates_path=paths["formula_candidates_path"],
        evaluation_examples_path=paths["evaluation_examples_path"],
        proof_case=proof_case,
        support_surfaces=tuple(support_surfaces),
        support_facts={
            subject: dict(load.facts) for subject, load in support_loads.items()
        },
        results=tuple(results),
    )


def substitution_graph_meta_substitution_semantics_frontier_status_payload(
    report: SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready compact frontier status payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "status_manifest": str(report.manifest.path),
        "status_set_id": report.manifest.status_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_status": report.frontier_status,
        "frontier_blocked_by": report.frontier_blocked_by,
        "support_paths": {
            "substitution_graph_correctness_cases": str(
                report.substitution_graph_correctness_cases_path
            ),
            "meta_substitution_semantics": str(
                report.meta_substitution_semantics_path
            ),
            "formal_language": str(report.formal_language_path),
            "codebook": str(report.codebook_path),
            "formal_substitution_examples": str(
                report.formal_substitution_examples_path
            ),
            "formula_candidates": str(report.formula_candidates_path),
            "evaluation_examples": str(report.evaluation_examples_path),
        },
        "proof_case": {
            "case_id": report.proof_case.case_id,
            "case_kind": report.proof_case.case_kind,
            "correctness_target_id": report.proof_case.correctness_target_id,
            "status": report.proof_case.status,
            "required_dependency_subjects": list(
                report.proof_case.required_dependency_subjects
            ),
            "non_claims": list(report.proof_case.non_claims),
            "next_as_action": report.proof_case.next_as_action,
        },
        "expected_semantics_subject_count": (
            report.manifest.expected_semantics_subject_count
        ),
        "semantics_subject_count": report.semantics_subject_count,
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "support_surface_count": report.support_surface_count,
        "failed_subjects": list(report.failed_subjects),
        "support_surfaces": [
            {
                "subject": surface.subject,
                "path": str(surface.path),
                "accepted": surface.accepted,
                "failed_subjects": list(surface.failed_subjects),
                "facts": _json_ready(surface.facts),
                "detail": surface.detail,
            }
            for surface in report.support_surfaces
        ],
        "support_facts": {
            subject: _json_ready(facts)
            for subject, facts in report.support_facts.items()
        },
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


def format_substitution_graph_meta_substitution_semantics_frontier_status_report(
    report: SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusReport,
) -> str:
    """Format a concise human-readable meta-substitution frontier report."""

    status = "accepted" if report.accepted else "rejected"
    case = report.proof_case
    lines = [
        (
            "Substitution graph meta-substitution-semantics frontier "
            f"status: {status}"
        ),
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Proof case: {case.case_id}",
        f"Case kind: {case.case_kind}",
        f"Case status: {case.status}",
        f"Meta-substitution subjects: {report.semantics_subject_count}",
        f"Support surfaces: {report.support_surface_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        lines.append(
            f"- {surface.subject}: {prefix} ({surface.path}) {surface.detail}"
        )
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_meta_substitution_semantics_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run meta-substitution-semantics frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "substitution_graph_meta_substitution_semantics_frontier_status"
        ),
        description=(
            "Validate the AS substitution graph meta-substitution-semantics "
            "frontier status."
        ),
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the meta-substitution frontier status manifest.",
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

    manifest = load_substitution_graph_meta_substitution_semantics_frontier_status(
        args.status
    )
    report = validate_substitution_graph_meta_substitution_semantics_frontier_status(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                substitution_graph_meta_substitution_semantics_frontier_status_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_substitution_graph_meta_substitution_semantics_frontier_status_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest,
) -> dict[str, Path]:
    return {
        "substitution_graph_correctness_cases_path": Path(
            manifest.substitution_graph_correctness_cases_path
        ),
        "meta_substitution_semantics_path": Path(
            manifest.meta_substitution_semantics_path
        ),
        "formal_language_path": Path(manifest.formal_language_path),
        "codebook_path": Path(manifest.codebook_path),
        "formal_substitution_examples_path": Path(
            manifest.formal_substitution_examples_path
        ),
        "formula_candidates_path": Path(manifest.formula_candidates_path),
        "evaluation_examples_path": Path(manifest.evaluation_examples_path),
    }


def _load_correctness_cases(path: Path) -> tuple[Any | None, _SupportLoad]:
    try:
        loaded = load_substitution_graph_correctness_cases(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _SupportLoad(
            accepted=False,
            failed_subjects=("substitution-graph-correctness-cases-load",),
            facts={},
        )

    failures: list[str] = []
    cases = tuple(getattr(loaded, "cases", ()))
    if getattr(loaded, "case_set_id", None) != (
        "as-substitution-graph-correctness-cases-v1"
    ):
        failures.append("substitution-graph-correctness-cases-id")
    if len(cases) != 5:
        failures.append("substitution-graph-correctness-cases-count")
    if _find_meta_substitution_semantics_case(loaded).case_kind != REQUIRED_CASE_KIND:
        failures.append("substitution-graph-meta-substitution-semantics-case-missing")

    return loaded, _SupportLoad(
        accepted=not failures,
        failed_subjects=tuple(failures),
        facts={
            "case_set_id": getattr(loaded, "case_set_id", ""),
            "case_count": len(cases),
        },
    )


def _load_meta_substitution_semantics(
    path: Path,
    willard_map_path: Path,
) -> tuple[Any | None, _SupportLoad]:
    try:
        loaded = load_substitution_graph_meta_substitution_semantics(path)
        report = validate_substitution_graph_meta_substitution_semantics(
            loaded,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return None, _SupportLoad(
            accepted=False,
            failed_subjects=("substitution-graph-meta-substitution-semantics-load",),
            facts={},
        )

    failures = list(report.failed_subjects)
    if loaded.semantics_set_id != REQUIRED_SEMANTICS_SET_ID:
        failures.append("substitution-graph-meta-substitution-semantics-id")
    if report.subject_count != EXPECTED_SEMANTICS_SUBJECT_COUNT:
        failures.append("substitution-graph-meta-substitution-semantics-count")
    if loaded.expected_subject_count != EXPECTED_SEMANTICS_SUBJECT_COUNT:
        failures.append("substitution-graph-meta-substitution-semantics-expected-count")
    if _missing_items(SEMANTICS_NON_CLAIMS, loaded.non_claims):
        failures.append("substitution-graph-meta-substitution-semantics-non-claim")

    return loaded, _SupportLoad(
        accepted=report.accepted and not failures,
        failed_subjects=tuple(failures),
        facts={
            "semantics_set_id": loaded.semantics_set_id,
            "subject_count": report.subject_count,
            "expected_subject_count": loaded.expected_subject_count,
            "source_kind_counts": report.source_kind_counts,
            "required_source_kinds": tuple(loaded.required_source_kinds),
            "failed_subjects": report.failed_subjects,
            "non_claim_count": len(loaded.non_claims),
            "formal_language_path": loaded.formal_language_path,
            "codebook_path": loaded.codebook_path,
            "formal_substitution_examples_path": (
                loaded.formal_substitution_examples_path
            ),
            "formula_candidates_path": loaded.formula_candidates_path,
            "evaluation_examples_path": loaded.evaluation_examples_path,
        },
    )


def _validate_manifest(
    manifest: SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest,
) -> list[SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation]:
    results: list[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation
    ] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.status_set_id == REQUIRED_STATUS_SET_ID:
        results.append(_accepted("status_set_id", "status set id matches"))
    else:
        results.append(_rejected("status_set_id", "unexpected status set id"))

    if manifest.frontier_status == REQUIRED_FRONTIER_STATUS:
        results.append(_accepted("frontier_status", "frontier remains blocked"))
    elif manifest.frontier_status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                "frontier_status",
                "proof-promotion frontier status: " + manifest.frontier_status,
            )
        )
    else:
        results.append(
            _rejected(
                "frontier_status",
                "unsupported frontier status: " + manifest.frontier_status,
            )
        )

    if manifest.frontier_blocked_by == REQUIRED_FRONTIER_BLOCKER:
        results.append(
            _accepted("frontier_blocked_by", "blocked by meta-substitution-semantics")
        )
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                "expected meta-substitution-semantics blocker",
            )
        )

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.required_case_kind == REQUIRED_CASE_KIND:
        results.append(_accepted("required_case_kind", "meta-substitution case"))
    else:
        results.append(_rejected("required_case_kind", "unexpected proof case kind"))

    if manifest.required_case_status == REQUIRED_CASE_STATUS:
        results.append(_accepted("required_case_status", "proof case remains open"))
    else:
        results.append(_rejected("required_case_status", "unexpected proof case status"))

    if manifest.expected_support_surface_count == EXPECTED_SUPPORT_SURFACE_COUNT:
        results.append(_accepted("expected_support_surface_count", "one surface"))
    else:
        results.append(
            _rejected(
                "expected_support_surface_count",
                "expected one support surface",
            )
        )

    if manifest.expected_semantics_subject_count == EXPECTED_SEMANTICS_SUBJECT_COUNT:
        results.append(_accepted("expected_semantics_subject_count", "six subjects"))
    else:
        results.append(
            _rejected(
                "expected_semantics_subject_count",
                "expected six semantics subjects",
            )
        )

    missing_non_claims = _missing_items(REQUIRED_NON_CLAIMS, manifest.non_claims)
    proof_promotions = [
        item for item in manifest.non_claims if item in PROOF_PROMOTION_NON_CLAIMS
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    elif proof_promotions:
        results.append(
            _rejected(
                "non_claims",
                "proof-promotion non-claims: " + ", ".join(proof_promotions),
            )
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_case_manifest_paths(
    manifest: Any | None,
) -> list[SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation]:
    results: list[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation
    ] = []
    if manifest is None:
        return [_rejected("cases_manifest.paths", "case manifest unavailable")]

    if manifest.case_set_id == "as-substitution-graph-correctness-cases-v1":
        results.append(_accepted("case_set_id", "case set id matches"))
    else:
        results.append(_rejected("case_set_id", "unexpected case set id"))

    for field, expected in EXPECTED_CASE_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))
    return results


def _find_meta_substitution_semantics_case(
    cases_manifest: Any | None,
) -> SubstitutionGraphMetaSubstitutionSemanticsFrontierProofCase:
    if cases_manifest is None:
        return _missing_proof_case()

    for case in tuple(getattr(cases_manifest, "cases", ())):
        if getattr(case, "case_kind", None) != REQUIRED_CASE_KIND:
            continue
        return SubstitutionGraphMetaSubstitutionSemanticsFrontierProofCase(
            case_id=case.case_id,
            case_kind=case.case_kind,
            correctness_target_id=case.correctness_target_id,
            status=case.status,
            required_dependency_subjects=tuple(case.required_dependency_subjects),
            non_claims=tuple(case.non_claims),
            next_as_action=case.next_as_action,
        )
    return _missing_proof_case()


def _missing_proof_case() -> (
    SubstitutionGraphMetaSubstitutionSemanticsFrontierProofCase
):
    return SubstitutionGraphMetaSubstitutionSemanticsFrontierProofCase(
        case_id="missing",
        case_kind="missing",
        correctness_target_id="missing",
        status="missing",
        required_dependency_subjects=(),
        non_claims=(),
        next_as_action="",
    )


def _validate_proof_case(
    proof_case: SubstitutionGraphMetaSubstitutionSemanticsFrontierProofCase,
) -> list[SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation]:
    results: list[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation
    ] = []
    if proof_case.case_id == REQUIRED_CASE_ID:
        results.append(_accepted("proof_case.case_id", "case id matches"))
    else:
        results.append(_rejected("proof_case.case_id", "unexpected case id"))

    if proof_case.case_kind == REQUIRED_CASE_KIND:
        results.append(
            _accepted("proof_case.kind", "meta-substitution-semantics case found")
        )
    else:
        results.append(
            _rejected("proof_case.kind", "meta-substitution-semantics case missing")
        )

    if proof_case.status == REQUIRED_CASE_STATUS:
        results.append(_accepted("proof_case.status", "proof case remains open"))
    elif proof_case.status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                "proof_case.status",
                "proof case is not open: " + proof_case.status,
            )
        )
    else:
        results.append(
            _rejected(
                "proof_case.status",
                "unsupported proof case status: " + proof_case.status,
            )
        )

    if proof_case.correctness_target_id == REQUIRED_CORRECTNESS_TARGET_ID:
        results.append(_accepted("proof_case.target", "correctness target matches"))
    else:
        results.append(_rejected("proof_case.target", "unknown correctness target"))

    if proof_case.required_dependency_subjects == REQUIRED_CASE_SUPPORT_SUBJECTS:
        results.append(
            _accepted(
                "proof_case.required_dependency_subjects",
                "dependency subjects match",
            )
        )
    else:
        results.append(
            _rejected(
                "proof_case.required_dependency_subjects",
                "dependency subjects mismatch: expected "
                + ", ".join(REQUIRED_CASE_SUPPORT_SUBJECTS)
                + " but found "
                + _joined_or_none(proof_case.required_dependency_subjects),
            )
        )

    missing_non_claims = _missing_items(CASE_NON_CLAIMS, proof_case.non_claims)
    if missing_non_claims:
        results.append(
            _rejected(
                "proof_case.non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("proof_case.non_claims", "non-claims are explicit"))

    if proof_case.next_as_action.strip():
        results.append(_accepted("proof_case.next_as_action", "case action present"))
    else:
        results.append(_rejected("proof_case.next_as_action", "missing case action"))
    return results


def _validate_support_path_alignment(
    manifest: SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest,
    cases_manifest: Any | None,
    semantics_manifest: Any | None,
) -> list[SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation]:
    results: list[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation
    ] = []
    if cases_manifest is not None:
        results.extend([
            _path_alignment_result(
                "cases_manifest.formal_substitution_examples_path",
                getattr(cases_manifest, "formal_substitution_examples_path", ""),
                manifest.formal_substitution_examples_path,
            ),
            _path_alignment_result(
                "cases_manifest.meta_substitution_semantics_path",
                getattr(cases_manifest, "meta_substitution_semantics_path", ""),
                manifest.meta_substitution_semantics_path,
            ),
        ])
    else:
        results.append(
            _rejected(
                "cases_manifest.paths",
                "cannot check case manifest path alignment",
            )
        )

    if semantics_manifest is not None:
        for field in EXPECTED_SEMANTICS_PATHS:
            results.append(
                _path_alignment_result(
                    f"semantics_manifest.{field}",
                    getattr(semantics_manifest, field, ""),
                    getattr(manifest, field),
                )
            )
    else:
        results.append(
            _rejected(
                "semantics_manifest.paths",
                "cannot check semantics manifest path alignment",
            )
        )
    return results


def _path_alignment_result(
    subject: str,
    actual: str,
    expected: str,
) -> SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation:
    if actual == expected:
        return _accepted(subject, f"{expected} aligned")
    return _rejected(subject, f"expected {expected} but found {actual}")


def _support_surfaces(
    paths: dict[str, Path],
    support_loads: dict[str, _SupportLoad],
) -> list[SubstitutionGraphMetaSubstitutionSemanticsFrontierSupportSurface]:
    surfaces: list[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierSupportSurface
    ] = []
    for subject in REQUIRED_SUPPORT_SUBJECTS:
        load = support_loads[subject]
        surfaces.append(
            SubstitutionGraphMetaSubstitutionSemanticsFrontierSupportSurface(
                subject=subject,
                path=paths["meta_substitution_semantics_path"],
                accepted=load.accepted,
                failed_subjects=load.failed_subjects,
                facts=load.facts,
                detail=_support_detail(load),
            )
        )
    return surfaces


def _support_detail(load: _SupportLoad) -> str:
    if not load.accepted:
        return (
            "rejected: failed subjects "
            + _joined_or_none(load.failed_subjects)
        )
    return "support accepted; subjects " + str(load.facts.get("subject_count"))


def _validate_support_surfaces(
    manifest: SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusManifest,
    surfaces: list[SubstitutionGraphMetaSubstitutionSemanticsFrontierSupportSurface],
) -> list[SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation]:
    results: list[
        SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation
    ] = []
    observed_subjects = tuple(surface.subject for surface in surfaces)
    if observed_subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "required support surface present"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    if len(surfaces) == manifest.expected_support_surface_count:
        results.append(_accepted("support_surface_count", "support count matches"))
    else:
        results.append(
            _rejected(
                "support_surface_count",
                "expected "
                + str(manifest.expected_support_surface_count)
                + " support surface(s), found "
                + str(len(surfaces)),
            )
        )

    for surface in surfaces:
        if surface.accepted:
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _validate_case_support(
    proof_case: SubstitutionGraphMetaSubstitutionSemanticsFrontierProofCase,
    surfaces: list[SubstitutionGraphMetaSubstitutionSemanticsFrontierSupportSurface],
) -> list[SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation]:
    accepted_surface_subjects = {surface.subject for surface in surfaces if surface.accepted}
    if "meta_substitution_semantics" not in accepted_surface_subjects:
        return [
            _rejected(
                "proof_case.support",
                "meta-substitution semantics support surface rejected",
            )
        ]

    missing_case_support = [
        subject
        for subject in ("formal_substitution", "meta_substitution_semantics")
        if subject not in proof_case.required_dependency_subjects
    ]
    if missing_case_support:
        return [
            _rejected(
                "proof_case.support",
                "case dependencies missing: " + ", ".join(missing_case_support),
            )
        ]

    return [
        _accepted(
            "proof_case.support",
            "formal substitution and meta-substitution support accepted",
        )
    ]


def _json_ready(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "substitution-graph-meta-substitution-semantics-frontier-status"
    if subject == "non_claims":
        return "substitution-graph-meta-substitution-semantics-frontier-non-claim"
    if subject == "proof_case.status":
        return "substitution-graph-meta-substitution-semantics-frontier-case-status"
    if subject == "proof_case.non_claims":
        return (
            "substitution-graph-meta-substitution-semantics-frontier-case-non-claim"
        )
    if subject in {
        "proof_case.required_dependency_subjects",
        "proof_case.support",
    }:
        return "substitution-graph-meta-substitution-semantics-frontier-case-support"
    if (
        subject.endswith("_path")
        or subject.endswith(".paths")
        or ".formal_substitution_examples_path" in subject
        or ".meta_substitution_semantics_path" in subject
        or ".formal_language_path" in subject
        or ".codebook_path" in subject
        or ".formula_candidates_path" in subject
        or ".evaluation_examples_path" in subject
        or subject == "cases_manifest"
        or subject == "case_set_id"
    ):
        return "substitution-graph-meta-substitution-semantics-frontier-dependency"
    if subject in REQUIRED_SUPPORT_SUBJECTS or subject in {
        "support_surfaces",
        "support_surface_count",
    }:
        return "substitution-graph-meta-substitution-semantics-frontier-support"
    if subject.startswith("proof_case."):
        return "substitution-graph-meta-substitution-semantics-frontier-case"
    return "substitution-graph-meta-substitution-semantics-frontier"


def _missing_items(
    required: tuple[str, ...],
    observed: tuple[str, ...],
) -> list[str]:
    return [item for item in required if item not in observed]


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


def _accepted(
    subject: str,
    detail: str,
) -> SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation:
    return SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation:
    return SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(
        run_substitution_graph_meta_substitution_semantics_frontier_status_cli()
    )
