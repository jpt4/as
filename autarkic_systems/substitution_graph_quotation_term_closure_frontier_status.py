"""Compact frontier status for quotation-term closure correctness support.

The existing quotation-term-closure module checks a finite support surface for
the substitution graph correctness stack. This module is a handoff layer around
that surface: it finds the matching open proof case, runs the existing support
validator, and reports a compact blocked frontier without promoting the case
to a proof.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.substitution_graph_correctness_cases import (
    REQUIRED_DEPENDENCIES_BY_KIND,
    load_substitution_graph_correctness_cases,
)
from autarkic_systems.substitution_graph_quotation_term_closure import (
    DEFAULT_WILLARD_MAP,
    load_substitution_graph_quotation_term_closure,
    validate_substitution_graph_quotation_term_closure,
)


DEFAULT_STATUS = Path(
    "claims/substitution_graph_quotation_term_closure_frontier_status.json"
)

REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "quotation-term-closure"
REQUIRED_CASE_KIND = "quotation-term-closure"
REQUIRED_CASE_ID = "AS-SUBST-GRAPH-CORRECTNESS-QUOTATION-TERM-CLOSURE"
REQUIRED_CORRECTNESS_TARGET_ID = "AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET"
REQUIRED_SUPPORT_SUBJECTS = ("quotation_term_closure",)
REQUIRED_CASE_SUPPORT_SUBJECTS = REQUIRED_DEPENDENCIES_BY_KIND[
    REQUIRED_CASE_KIND
]
REQUIRED_STATUS_SET_ID = (
    "as-substitution-graph-quotation-term-closure-frontier-status-v1"
)
REQUIRED_CLOSURE_SET_ID = "as-substitution-graph-quotation-term-closure-v1"
REQUIRED_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
REQUIRED_CASE_NON_CLAIMS = (
    "no formula correctness proof",
    "no substitution representability proof",
    "no diagonal lemma proof",
    "no fixed-point equation proof",
    "no self-consistency theorem",
)
PROOF_PROMOTION_STATUSES = {
    "formula-correctness-proved",
    "substitution-representability-proved",
    "diagonal-lemma-proved",
    "fixed-point-equation-proved",
    "arithmetized-proof-predicate-proved",
    "quotation-term-closure-proved",
    "self-consistency-proved",
    "self-consistency-theorem-proved",
}
EXPECTED_CASES_PATH = "claims/substitution_graph_correctness_cases.json"
EXPECTED_CLOSURE_PATH = "claims/substitution_graph_quotation_term_closure.json"
EXPECTED_CASE_PATHS = {
    "correctness_targets_path": "claims/substitution_graph_correctness_targets.json",
    "codebook_path": "language/formal_codebook.json",
    "quotation_term_examples_path": "language/formal_quotation_term_examples.json",
    "quotation_term_closure_path": EXPECTED_CLOSURE_PATH,
}


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureFrontierStatusManifest:
    """Loaded manifest for the compact quotation-term-closure frontier."""

    path: Path
    schema_version: int
    status_set_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    substitution_graph_correctness_cases_path: str
    quotation_term_closure_path: str
    expected_support_surface_count: int
    expected_closure_subject_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureFrontierValidation:
    """One validation result for the compact frontier status."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureFrontierCase:
    """Observed correctness proof case for quotation-term closure."""

    case_id: str
    case_kind: str
    correctness_target_id: str
    status: str
    support_subjects: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureFrontierSupportSurface:
    """Observed finite support surface behind the open proof case."""

    subject: str
    path: Path
    accepted: bool
    failed_subjects: tuple[str, ...]
    facts: dict[str, Any]
    detail: str


@dataclass(frozen=True)
class SubstitutionGraphQuotationTermClosureFrontierStatusReport:
    """Compact validation report for quotation-term-closure handoff."""

    manifest: SubstitutionGraphQuotationTermClosureFrontierStatusManifest
    substitution_graph_correctness_cases_path: Path
    quotation_term_closure_path: Path
    case: SubstitutionGraphQuotationTermClosureFrontierCase | None
    support_surfaces: tuple[
        SubstitutionGraphQuotationTermClosureFrontierSupportSurface,
        ...,
    ]
    results: tuple[SubstitutionGraphQuotationTermClosureFrontierValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every compact status validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def frontier_status(self) -> str:
        """Return the preserved frontier status."""

        return self.manifest.frontier_status

    @property
    def frontier_blocked_by(self) -> str:
        """Return the preserved frontier blocker."""

        return self.manifest.frontier_blocked_by

    @property
    def support_surface_count(self) -> int:
        """Return the number of compact support surfaces observed."""

        return len(self.support_surfaces)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return stable failure subjects for status automation."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


def load_substitution_graph_quotation_term_closure_frontier_status(
    path: Path | str = DEFAULT_STATUS,
) -> SubstitutionGraphQuotationTermClosureFrontierStatusManifest:
    """Load the quotation-term-closure frontier status manifest."""

    status_path = Path(path)
    data = json.loads(status_path.read_text(encoding="utf-8"))
    return SubstitutionGraphQuotationTermClosureFrontierStatusManifest(
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
        quotation_term_closure_path=_required_text(
            data,
            "quotation_term_closure_path",
        ),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        expected_closure_subject_count=_required_int(
            data,
            "expected_closure_subject_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_substitution_graph_quotation_term_closure_frontier_status(
    manifest: SubstitutionGraphQuotationTermClosureFrontierStatusManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionGraphQuotationTermClosureFrontierStatusReport:
    """Validate the compact handoff without changing the underlying case map."""

    results: list[SubstitutionGraphQuotationTermClosureFrontierValidation] = [
        _accepted("manifest", f"loaded {manifest.status_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    cases_path = Path(manifest.substitution_graph_correctness_cases_path)
    closure_path = Path(manifest.quotation_term_closure_path)
    cases_manifest = None
    try:
        cases_manifest = load_substitution_graph_correctness_cases(cases_path)
        results.append(_accepted("cases_manifest", "case manifest loaded"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        results.append(
            _rejected(
                "cases_manifest",
                f"case manifest missing or invalid: {exc}",
            )
        )

    case = None
    support_surfaces: list[
        SubstitutionGraphQuotationTermClosureFrontierSupportSurface
    ] = []
    if cases_manifest is None:
        results.append(_rejected("case", "quotation-term-closure case unavailable"))
    else:
        results.extend(_validate_case_manifest_paths(cases_manifest))
        case, case_results = _case_summary(cases_manifest.cases)
        results.extend(case_results)
        support_surfaces.append(
            _closure_support_surface(
                manifest,
                cases_manifest,
                Path(willard_map_path),
            )
        )
        results.extend(_validate_support_surfaces(manifest, support_surfaces))

    return SubstitutionGraphQuotationTermClosureFrontierStatusReport(
        manifest=manifest,
        substitution_graph_correctness_cases_path=cases_path,
        quotation_term_closure_path=closure_path,
        case=case,
        support_surfaces=tuple(support_surfaces),
        results=tuple(results),
    )


def substitution_graph_quotation_term_closure_frontier_status_payload(
    report: SubstitutionGraphQuotationTermClosureFrontierStatusReport,
) -> dict[str, Any]:
    """Return a JSON-ready frontier status payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "status_manifest": str(report.manifest.path),
        "status_set_id": report.manifest.status_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_status": report.frontier_status,
        "frontier_blocked_by": report.frontier_blocked_by,
        "substitution_graph_correctness_cases_path": str(
            report.substitution_graph_correctness_cases_path
        ),
        "quotation_term_closure_path": str(report.quotation_term_closure_path),
        "expected_support_surface_count": (
            report.manifest.expected_support_surface_count
        ),
        "expected_closure_subject_count": (
            report.manifest.expected_closure_subject_count
        ),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "case": _case_payload(report.case),
        "support_surface_count": report.support_surface_count,
        "failed_subjects": list(report.failed_subjects),
        "support_surfaces": [_support_surface_payload(surface) for surface in report.support_surfaces],
        "support_facts": {
            surface.subject: _json_ready_facts(surface.facts)
            for surface in report.support_surfaces
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


def format_substitution_graph_quotation_term_closure_frontier_status_report(
    report: SubstitutionGraphQuotationTermClosureFrontierStatusReport,
) -> str:
    """Format a concise human-readable quotation-term-closure status."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Substitution graph quotation-term-closure frontier status: {status}",
        f"Status set: {report.manifest.status_set_id}",
        f"Frontier status: {report.frontier_status}",
        f"Blocked by: {report.frontier_blocked_by}",
        f"Support surfaces: {report.support_surface_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    if report.case is None:
        lines.append("Case: none")
    else:
        lines.extend([
            f"Case: {report.case.case_id}",
            f"Case kind: {report.case.case_kind}",
            f"Case status: {report.case.status}",
            "Case support: " + _joined_or_none(report.case.support_subjects),
        ])
    lines.append("Support:")
    for surface in report.support_surfaces:
        prefix = "accepted" if surface.accepted else "rejected"
        detail = surface.detail
        if surface.subject == "quotation_term_closure":
            subject_count = surface.facts.get("subject_count", "unknown")
            detail = f"{detail}; closure subjects {subject_count}"
        lines.append(f"- {surface.subject}: {prefix} ({detail})")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_graph_quotation_term_closure_frontier_status_cli(
    argv: list[str] | None = None,
) -> int:
    """Run quotation-term-closure frontier status validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "substitution_graph_quotation_term_closure_frontier_status"
        ),
        description=(
            "Validate the AS substitution graph quotation-term-closure frontier."
        ),
    )
    parser.add_argument(
        "--status",
        default=str(DEFAULT_STATUS),
        help="Path to the quotation-term-closure frontier status manifest.",
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

    manifest = load_substitution_graph_quotation_term_closure_frontier_status(
        args.status
    )
    report = validate_substitution_graph_quotation_term_closure_frontier_status(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(
            substitution_graph_quotation_term_closure_frontier_status_payload(
                report
            ),
            sort_keys=True,
        ))
    else:
        print(
            format_substitution_graph_quotation_term_closure_frontier_status_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _validate_manifest(
    manifest: SubstitutionGraphQuotationTermClosureFrontierStatusManifest,
) -> list[SubstitutionGraphQuotationTermClosureFrontierValidation]:
    results: list[SubstitutionGraphQuotationTermClosureFrontierValidation] = []
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
        results.append(_accepted("frontier_blocked_by", "blocker preserved"))
    else:
        results.append(
            _rejected(
                "frontier_blocked_by",
                f"expected {REQUIRED_FRONTIER_BLOCKER} blocker",
            )
        )

    if manifest.substitution_graph_correctness_cases_path == EXPECTED_CASES_PATH:
        results.append(
            _accepted(
                "substitution_graph_correctness_cases_path",
                f"{EXPECTED_CASES_PATH} referenced",
            )
        )
    else:
        results.append(
            _rejected(
                "substitution_graph_correctness_cases_path",
                (
                    f"expected {EXPECTED_CASES_PATH} but found "
                    f"{manifest.substitution_graph_correctness_cases_path}"
                ),
            )
        )

    if manifest.quotation_term_closure_path == EXPECTED_CLOSURE_PATH:
        results.append(
            _accepted(
                "quotation_term_closure_path",
                f"{EXPECTED_CLOSURE_PATH} referenced",
            )
        )
    else:
        results.append(
            _rejected(
                "quotation_term_closure_path",
                (
                    f"expected {EXPECTED_CLOSURE_PATH} but found "
                    f"{manifest.quotation_term_closure_path}"
                ),
            )
        )

    if manifest.expected_support_surface_count == len(REQUIRED_SUPPORT_SUBJECTS):
        results.append(_accepted("expected_support_surface_count", "one support surface"))
    else:
        results.append(
            _rejected(
                "expected_support_surface_count",
                "expected one support surface",
            )
        )

    if manifest.expected_closure_subject_count == 12:
        results.append(_accepted("expected_closure_subject_count", "twelve subjects"))
    else:
        results.append(
            _rejected(
                "expected_closure_subject_count",
                "expected twelve closure subjects",
            )
        )

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
        results.append(_accepted("non_claims", "status non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_case_manifest_paths(
    manifest: Any,
) -> list[SubstitutionGraphQuotationTermClosureFrontierValidation]:
    results: list[SubstitutionGraphQuotationTermClosureFrontierValidation] = []
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


def _case_summary(
    cases: tuple[Any, ...],
) -> tuple[
    SubstitutionGraphQuotationTermClosureFrontierCase | None,
    list[SubstitutionGraphQuotationTermClosureFrontierValidation],
]:
    results: list[SubstitutionGraphQuotationTermClosureFrontierValidation] = []
    matches = [case for case in cases if case.case_kind == REQUIRED_CASE_KIND]
    if len(matches) != 1:
        results.append(
            _rejected(
                "case",
                f"expected one {REQUIRED_CASE_KIND} case, found {len(matches)}",
            )
        )
        return None, results

    raw_case = matches[0]
    case = SubstitutionGraphQuotationTermClosureFrontierCase(
        case_id=raw_case.case_id,
        case_kind=raw_case.case_kind,
        correctness_target_id=raw_case.correctness_target_id,
        status=raw_case.status,
        support_subjects=tuple(raw_case.required_dependency_subjects),
        non_claims=tuple(raw_case.non_claims),
        next_as_action=raw_case.next_as_action,
    )
    results.append(_accepted("case", "quotation-term-closure case found"))
    results.extend(_validate_case(case))
    return case, results


def _validate_case(
    case: SubstitutionGraphQuotationTermClosureFrontierCase,
) -> list[SubstitutionGraphQuotationTermClosureFrontierValidation]:
    results: list[SubstitutionGraphQuotationTermClosureFrontierValidation] = []
    if case.case_id == REQUIRED_CASE_ID:
        results.append(_accepted("case.case_id", "case id matches"))
    else:
        results.append(_rejected("case.case_id", "unexpected case id"))

    if case.status == "proof-case-open":
        results.append(_accepted("case.status", "case remains open"))
    elif case.status in PROOF_PROMOTION_STATUSES:
        results.append(
            _rejected(
                "case.status",
                "case is not open: proof-promotion status " + case.status,
            )
        )
    else:
        results.append(
            _rejected("case.status", "case is not open: " + case.status)
        )

    if case.correctness_target_id == REQUIRED_CORRECTNESS_TARGET_ID:
        results.append(_accepted("case.target", "correctness target matches"))
    else:
        results.append(_rejected("case.target", "unknown correctness target"))

    if case.support_subjects == REQUIRED_CASE_SUPPORT_SUBJECTS:
        results.append(_accepted("case.support", "support subjects match"))
    else:
        results.append(
            _rejected(
                "case.support",
                "expected "
                + ", ".join(REQUIRED_CASE_SUPPORT_SUBJECTS)
                + " but found "
                + _joined_or_none(case.support_subjects),
            )
        )

    missing_non_claims = [
        item for item in REQUIRED_CASE_NON_CLAIMS if item not in case.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "case.non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("case.non_claims", "case non-claims are explicit"))

    if case.next_as_action.strip():
        results.append(_accepted("case.next_as_action", "case next action present"))
    else:
        results.append(_rejected("case.next_as_action", "missing case next action"))
    return results


def _closure_support_surface(
    manifest: SubstitutionGraphQuotationTermClosureFrontierStatusManifest,
    cases_manifest: Any,
    willard_map_path: Path,
) -> SubstitutionGraphQuotationTermClosureFrontierSupportSurface:
    path = Path(manifest.quotation_term_closure_path)
    try:
        closure_manifest = load_substitution_graph_quotation_term_closure(path)
        closure_report = validate_substitution_graph_quotation_term_closure(
            closure_manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return SubstitutionGraphQuotationTermClosureFrontierSupportSurface(
            subject="quotation_term_closure",
            path=path,
            accepted=False,
            failed_subjects=(
                "substitution-graph-quotation-term-closure-frontier-support-load",
            ),
            facts={},
            detail=f"support artifact missing or invalid: {exc}",
        )

    facts: dict[str, Any] = {
        "closure_set_id": closure_manifest.closure_set_id,
        "subject_count": closure_report.subject_count,
        "expected_subject_count": closure_manifest.expected_subject_count,
        "source_kind_counts": closure_report.source_kind_counts,
        "required_source_kinds": tuple(closure_manifest.required_source_kinds),
        "failed_subjects": closure_report.failed_subjects,
        "non_claim_count": len(closure_manifest.non_claims),
        "codebook_path": closure_manifest.codebook_path,
        "quotation_term_examples_path": closure_manifest.quotation_term_examples_path,
        "formula_candidates_path": closure_manifest.formula_candidates_path,
        "evaluation_examples_path": closure_manifest.evaluation_examples_path,
    }
    failures: list[str] = []
    if closure_manifest.closure_set_id != REQUIRED_CLOSURE_SET_ID:
        failures.append(
            "substitution-graph-quotation-term-closure-frontier-support-id"
        )
    if Path(cases_manifest.quotation_term_closure_path) != path:
        failures.append(
            "substitution-graph-quotation-term-closure-frontier-support-path"
        )
    if closure_manifest.codebook_path != cases_manifest.codebook_path:
        failures.append(
            "substitution-graph-quotation-term-closure-frontier-support-codebook"
        )
    if (
        closure_manifest.quotation_term_examples_path
        != cases_manifest.quotation_term_examples_path
    ):
        failures.append(
            "substitution-graph-quotation-term-closure-frontier-support-quotation"
        )
    if closure_report.subject_count != manifest.expected_closure_subject_count:
        failures.append(
            "substitution-graph-quotation-term-closure-frontier-support-count"
        )
    if closure_report.failed_subjects:
        failures.append(
            "substitution-graph-quotation-term-closure-frontier-support-failed-subjects"
        )
    if not closure_report.accepted:
        failures.append(
            "substitution-graph-quotation-term-closure-frontier-support-rejected"
        )

    missing_non_claims = [
        item for item in REQUIRED_CASE_NON_CLAIMS if item not in closure_manifest.non_claims
    ]
    if missing_non_claims:
        failures.append(
            "substitution-graph-quotation-term-closure-frontier-support-non-claim"
        )

    if failures:
        detail = "support rejected: " + ", ".join(failures)
        if closure_report.failed_subjects:
            detail += "; failed subjects: " + _joined_or_none(
                closure_report.failed_subjects
            )
        return SubstitutionGraphQuotationTermClosureFrontierSupportSurface(
            subject="quotation_term_closure",
            path=path,
            accepted=False,
            failed_subjects=tuple(failures),
            facts=facts,
            detail=detail,
        )

    return SubstitutionGraphQuotationTermClosureFrontierSupportSurface(
        subject="quotation_term_closure",
        path=path,
        accepted=True,
        failed_subjects=(),
        facts=facts,
        detail="support accepted",
    )


def _validate_support_surfaces(
    manifest: SubstitutionGraphQuotationTermClosureFrontierStatusManifest,
    surfaces: list[SubstitutionGraphQuotationTermClosureFrontierSupportSurface],
) -> list[SubstitutionGraphQuotationTermClosureFrontierValidation]:
    results: list[SubstitutionGraphQuotationTermClosureFrontierValidation] = []
    subjects = tuple(surface.subject for surface in surfaces)
    if subjects == REQUIRED_SUPPORT_SUBJECTS:
        results.append(_accepted("support_surfaces", "support surface order matches"))
    else:
        results.append(_rejected("support_surfaces", "support surface order mismatch"))

    if len(surfaces) == manifest.expected_support_surface_count:
        results.append(_accepted("support_surface_count", "support count matches"))
    else:
        results.append(
            _rejected(
                "support_surface_count",
                (
                    "expected "
                    + str(manifest.expected_support_surface_count)
                    + " support surface(s), found "
                    + str(len(surfaces))
                ),
            )
        )

    for surface in surfaces:
        if surface.accepted:
            results.append(_accepted(surface.subject, surface.detail))
        else:
            results.append(_rejected(surface.subject, surface.detail))
    return results


def _case_payload(
    case: SubstitutionGraphQuotationTermClosureFrontierCase | None,
) -> dict[str, Any] | None:
    if case is None:
        return None
    return {
        "case_id": case.case_id,
        "case_kind": case.case_kind,
        "correctness_target_id": case.correctness_target_id,
        "status": case.status,
        "support_subjects": list(case.support_subjects),
        "non_claims": list(case.non_claims),
        "next_as_action": case.next_as_action,
    }


def _support_surface_payload(
    surface: SubstitutionGraphQuotationTermClosureFrontierSupportSurface,
) -> dict[str, Any]:
    return {
        "subject": surface.subject,
        "path": str(surface.path),
        "accepted": surface.accepted,
        "failed_subjects": list(surface.failed_subjects),
        "facts": _json_ready_facts(surface.facts),
        "detail": surface.detail,
    }


def _json_ready_facts(facts: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in facts.items():
        if isinstance(value, tuple):
            result[key] = list(value)
        elif isinstance(value, dict):
            result[key] = dict(value)
        else:
            result[key] = value
    return result


def _failed_subject_for_result(subject: str) -> str:
    if subject == "frontier_status":
        return "substitution-graph-quotation-term-closure-frontier-status"
    if subject == "non_claims":
        return "substitution-graph-quotation-term-closure-frontier-non-claim"
    if subject == "case.status":
        return "substitution-graph-quotation-term-closure-frontier-case-status"
    if subject == "case.non_claims":
        return "substitution-graph-quotation-term-closure-frontier-case-non-claim"
    if subject in {
        "quotation_term_closure",
        "support_surfaces",
        "support_surface_count",
    }:
        return "substitution-graph-quotation-term-closure-frontier-support"
    if subject in {
        "substitution_graph_correctness_cases_path",
        "quotation_term_closure_path",
        "cases_manifest",
        "correctness_targets_path",
        "codebook_path",
        "quotation_term_examples_path",
    }:
        return "substitution-graph-quotation-term-closure-frontier-dependency"
    if subject.startswith("case."):
        return "substitution-graph-quotation-term-closure-frontier-case"
    if subject == "case":
        return "substitution-graph-quotation-term-closure-frontier-case"
    return "substitution-graph-quotation-term-closure-frontier"


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
) -> SubstitutionGraphQuotationTermClosureFrontierValidation:
    return SubstitutionGraphQuotationTermClosureFrontierValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionGraphQuotationTermClosureFrontierValidation:
    return SubstitutionGraphQuotationTermClosureFrontierValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(
        run_substitution_graph_quotation_term_closure_frontier_status_cli()
    )
