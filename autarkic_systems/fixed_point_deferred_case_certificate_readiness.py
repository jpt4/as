"""Readiness surface for deferred fixed-point construction proof cases.

ADR-0306 uses the checked obligation graph, the frontier selector, and the
selected-root certificate coverage report to summarize deferred downstream
cases. The report is deliberately non-promotional: finite certificate coverage
on predecessor roots is useful planning evidence, but every downstream proof
case remains deferred until its predecessor proof cases actually close.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_construction_obligation_graph import (
    load_fixed_point_construction_obligation_graph,
    validate_fixed_point_construction_obligation_graph,
)
from autarkic_systems.fixed_point_frontier_selector import (
    load_fixed_point_frontier_selector,
    validate_fixed_point_frontier_selector,
)
from autarkic_systems.fixed_point_selected_root_certificate_coverage import (
    load_fixed_point_selected_root_certificate_coverage,
    validate_fixed_point_selected_root_certificate_coverage,
)


DEFAULT_READINESS = Path("claims/fixed_point_deferred_case_certificate_readiness.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_DEFERRED_CASE_KINDS = (
    "substitution-representability-proof",
    "bridge-equality-proof",
    "fixed-point-equation-lifting",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "obligation_graph_path": "claims/fixed_point_construction_obligation_graph.json",
    "frontier_selector_path": "claims/fixed_point_frontier_selector.json",
    "selected_root_certificate_coverage_path": (
        "claims/fixed_point_selected_root_certificate_coverage.json"
    ),
}
REQUIRED_CASE_STATUS = "proof-case-open"
READINESS_STATUS = "deferred-certificate-readiness-not-proof"


@dataclass(frozen=True)
class FixedPointDeferredCaseCertificateReadinessManifest:
    """Loaded manifest for deferred-case certificate readiness."""

    path: Path
    schema_version: int
    readiness_set_id: str
    reviewed_at: str
    purpose: str
    obligation_graph_path: str
    frontier_selector_path: str
    selected_root_certificate_coverage_path: str
    expected_deferred_case_count: int
    expected_deferred_case_kinds: tuple[str, ...]
    expected_predecessor_counts: dict[str, int]
    expected_certificate_covered_predecessor_counts: dict[str, int]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointDeferredCaseCertificateReadinessEntry:
    """One deferred case and the certificate coverage known for predecessors."""

    readiness_id: str
    deferred_case_kind: str
    construction_case_id: str
    target_id: str
    readiness_status: str
    predecessor_case_kinds: tuple[str, ...]
    certificate_covered_predecessor_case_kinds: tuple[str, ...]
    blocking_open_predecessor_case_kinds: tuple[str, ...]
    selector_defers_case: bool
    construction_case_open: bool
    graph_predecessors_match_selector_blockers: bool
    selected_root_coverage_accepted: bool
    proof_boundary_preserved: bool

    @property
    def predecessor_count(self) -> int:
        """Return the number of graph predecessors for this deferred case."""

        return len(self.predecessor_case_kinds)

    @property
    def certificate_covered_predecessor_count(self) -> int:
        """Return how many predecessors have selected-root certificate coverage."""

        return len(self.certificate_covered_predecessor_case_kinds)

    @property
    def accepted(self) -> bool:
        """Return whether this readiness entry preserves deferred status."""

        return (
            self.readiness_status == READINESS_STATUS
            and self.selector_defers_case
            and self.construction_case_open
            and self.graph_predecessors_match_selector_blockers
            and self.selected_root_coverage_accepted
            and self.proof_boundary_preserved
        )


@dataclass(frozen=True)
class FixedPointDeferredCaseCertificateReadinessValidation:
    """One validation result for deferred-case readiness."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointDeferredCaseCertificateReadinessReport:
    """Validation report for deferred-case certificate readiness."""

    manifest: FixedPointDeferredCaseCertificateReadinessManifest
    obligation_graph_path: Path
    frontier_selector_path: Path
    selected_root_certificate_coverage_path: Path
    willard_map_path: Path
    deferred_case_kinds: tuple[str, ...]
    selected_root_coverage_accepted: bool
    proof_boundary_preserved: bool
    readiness_entries: tuple[FixedPointDeferredCaseCertificateReadinessEntry, ...]
    results: tuple[FixedPointDeferredCaseCertificateReadinessValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every deferred-case readiness validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def readiness_count(self) -> int:
        """Return the number of deferred readiness entries."""

        return len(self.readiness_entries)

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
    """Small report shim used when a dependency cannot load."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    nodes: tuple[Any, ...] = ()
    edges: tuple[Any, ...] = ()
    selected: tuple[Any, ...] = ()
    deferred: tuple[Any, ...] = ()
    coverage_entries: tuple[Any, ...] = ()
    frontier_status: str = ""
    frontier_blocked_by: str = ""


def load_fixed_point_deferred_case_certificate_readiness(
    path: Path | str = DEFAULT_READINESS,
) -> FixedPointDeferredCaseCertificateReadinessManifest:
    """Load the deferred-case certificate readiness manifest."""

    readiness_path = Path(path)
    data = json.loads(readiness_path.read_text(encoding="utf-8"))
    return FixedPointDeferredCaseCertificateReadinessManifest(
        path=readiness_path,
        schema_version=_required_int(data, "schema_version"),
        readiness_set_id=_required_text(data, "readiness_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        obligation_graph_path=_required_text(data, "obligation_graph_path"),
        frontier_selector_path=_required_text(data, "frontier_selector_path"),
        selected_root_certificate_coverage_path=_required_text(
            data,
            "selected_root_certificate_coverage_path",
        ),
        expected_deferred_case_count=_required_int(
            data,
            "expected_deferred_case_count",
        ),
        expected_deferred_case_kinds=tuple(
            _required_text_list(data, "expected_deferred_case_kinds")
        ),
        expected_predecessor_counts=_required_int_map(
            data,
            "expected_predecessor_counts",
        ),
        expected_certificate_covered_predecessor_counts=_required_int_map(
            data,
            "expected_certificate_covered_predecessor_counts",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_deferred_case_certificate_readiness(
    manifest: FixedPointDeferredCaseCertificateReadinessManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointDeferredCaseCertificateReadinessReport:
    """Validate deferred-case readiness against current fixed-point surfaces."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointDeferredCaseCertificateReadinessValidation] = [
        _accepted("manifest", f"loaded {manifest.readiness_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    graph_report = _load_graph(paths["obligation_graph_path"], checked_willard_map_path)
    selector_report = _load_selector(
        paths["frontier_selector_path"],
        checked_willard_map_path,
    )
    coverage_report = _load_coverage(
        paths["selected_root_certificate_coverage_path"],
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(graph_report, selector_report, coverage_report)
    )

    deferred_case_kinds = tuple(case.case_kind for case in selector_report.deferred)
    proof_boundary_preserved = _proof_boundary_preserved(
        manifest,
        graph_report,
        selector_report,
        coverage_report,
    )
    readiness_entries = _derive_readiness_entries(
        graph_report,
        selector_report,
        coverage_report,
        proof_boundary_preserved,
    )
    results.extend(
        _validate_readiness(
            manifest,
            deferred_case_kinds,
            coverage_report.accepted,
            proof_boundary_preserved,
            readiness_entries,
        )
    )

    return FixedPointDeferredCaseCertificateReadinessReport(
        manifest=manifest,
        obligation_graph_path=paths["obligation_graph_path"],
        frontier_selector_path=paths["frontier_selector_path"],
        selected_root_certificate_coverage_path=paths[
            "selected_root_certificate_coverage_path"
        ],
        willard_map_path=checked_willard_map_path,
        deferred_case_kinds=deferred_case_kinds,
        selected_root_coverage_accepted=coverage_report.accepted,
        proof_boundary_preserved=proof_boundary_preserved,
        readiness_entries=tuple(readiness_entries),
        results=tuple(results),
    )


def fixed_point_deferred_case_certificate_readiness_payload(
    report: FixedPointDeferredCaseCertificateReadinessReport,
) -> dict[str, Any]:
    """Return a JSON-ready deferred-case readiness payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "readiness_manifest": str(report.manifest.path),
        "readiness_set_id": report.manifest.readiness_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "obligation_graph_path": str(report.obligation_graph_path),
        "frontier_selector_path": str(report.frontier_selector_path),
        "selected_root_certificate_coverage_path": str(
            report.selected_root_certificate_coverage_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_deferred_case_count": (
            report.manifest.expected_deferred_case_count
        ),
        "expected_deferred_case_kinds": list(
            report.manifest.expected_deferred_case_kinds
        ),
        "expected_predecessor_counts": dict(
            report.manifest.expected_predecessor_counts
        ),
        "expected_certificate_covered_predecessor_counts": dict(
            report.manifest.expected_certificate_covered_predecessor_counts
        ),
        "deferred_case_kinds": list(report.deferred_case_kinds),
        "readiness_count": report.readiness_count,
        "observed_selected_root_coverage_accepted": (
            report.selected_root_coverage_accepted
        ),
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "readiness_entries": [
            _readiness_entry_payload(entry) for entry in report.readiness_entries
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


def format_fixed_point_deferred_case_certificate_readiness_report(
    report: FixedPointDeferredCaseCertificateReadinessReport,
) -> str:
    """Format a concise deferred-case readiness report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point deferred case certificate readiness: {status}",
        f"Readiness set: {report.manifest.readiness_set_id}",
        f"Deferred cases: {_joined_or_none(report.deferred_case_kinds)}",
        f"Deferred readiness entries: {report.readiness_count}",
        "Selected-root coverage accepted: "
        + str(report.selected_root_coverage_accepted).lower(),
        "Proof boundary preserved: " + str(report.proof_boundary_preserved).lower(),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for entry in report.readiness_entries:
        prefix = "deferred" if entry.accepted else "rejected"
        lines.append(
            f"{entry.deferred_case_kind}: {prefix} "
            f"(covered predecessors: "
            f"{entry.certificate_covered_predecessor_count}/"
            f"{entry.predecessor_count}; open blockers: "
            f"{_joined_or_none(entry.blocking_open_predecessor_case_kinds)})"
        )
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_deferred_case_certificate_readiness_cli(
    argv: list[str] | None = None,
) -> int:
    """Run deferred-case readiness validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_deferred_case_certificate_readiness"
        ),
        description=(
            "Validate certificate-readiness handoff for deferred AS "
            "fixed-point construction cases."
        ),
    )
    parser.add_argument(
        "--readiness",
        default=str(DEFAULT_READINESS),
        help="Path to the deferred-case readiness manifest.",
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

    manifest = load_fixed_point_deferred_case_certificate_readiness(args.readiness)
    report = validate_fixed_point_deferred_case_certificate_readiness(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_deferred_case_certificate_readiness_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_deferred_case_certificate_readiness_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointDeferredCaseCertificateReadinessManifest,
) -> dict[str, Path]:
    return {
        "obligation_graph_path": Path(manifest.obligation_graph_path),
        "frontier_selector_path": Path(manifest.frontier_selector_path),
        "selected_root_certificate_coverage_path": Path(
            manifest.selected_root_certificate_coverage_path
        ),
    }


def _load_graph(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_construction_obligation_graph(path)
        return validate_fixed_point_construction_obligation_graph(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-obligation-graph-load",))


def _load_selector(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_frontier_selector(path)
        return validate_fixed_point_frontier_selector(manifest, willard_map_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-frontier-selector-load",))


def _load_coverage(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_selected_root_certificate_coverage(path)
        return validate_fixed_point_selected_root_certificate_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-selected-root-certificate-coverage-load",),
        )


def _validate_manifest(
    manifest: FixedPointDeferredCaseCertificateReadinessManifest,
) -> list[FixedPointDeferredCaseCertificateReadinessValidation]:
    results: list[FixedPointDeferredCaseCertificateReadinessValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.readiness_set_id == "as-fixed-point-deferred-case-certificate-readiness-v1":
        results.append(_accepted("readiness_set_id", "readiness set id matches"))
    else:
        results.append(_rejected("readiness_set_id", "unexpected readiness set id"))

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.expected_deferred_case_count == 3:
        results.append(_accepted("expected_deferred_case_count", "three cases"))
    else:
        results.append(
            _rejected("expected_deferred_case_count", "expected three deferred cases")
        )

    if manifest.expected_deferred_case_kinds == REQUIRED_DEFERRED_CASE_KINDS:
        results.append(_accepted("expected_deferred_case_kinds", "deferred cases match"))
    else:
        results.append(
            _rejected("expected_deferred_case_kinds", "deferred case mismatch")
        )

    missing_predecessor_keys = [
        case_kind
        for case_kind in REQUIRED_DEFERRED_CASE_KINDS
        if case_kind not in manifest.expected_predecessor_counts
    ]
    missing_covered_keys = [
        case_kind
        for case_kind in REQUIRED_DEFERRED_CASE_KINDS
        if case_kind not in manifest.expected_certificate_covered_predecessor_counts
    ]
    if missing_predecessor_keys:
        results.append(
            _rejected(
                "expected_predecessor_counts",
                "missing predecessor counts: "
                + ", ".join(missing_predecessor_keys),
            )
        )
    else:
        results.append(_accepted("expected_predecessor_counts", "all cases counted"))

    if missing_covered_keys:
        results.append(
            _rejected(
                "expected_certificate_covered_predecessor_counts",
                "missing covered predecessor counts: "
                + ", ".join(missing_covered_keys),
            )
        )
    else:
        results.append(
            _accepted(
                "expected_certificate_covered_predecessor_counts",
                "all cases counted",
            )
        )

    missing_non_claims = [
        non_claim
        for non_claim in REQUIRED_NON_CLAIMS
        if non_claim not in manifest.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("non_claims", "all non-claims preserved"))
    return results


def _validate_dependencies(
    graph_report: Any,
    selector_report: Any,
    coverage_report: Any,
) -> list[FixedPointDeferredCaseCertificateReadinessValidation]:
    checks = (
        ("obligation_graph", graph_report, "obligation graph"),
        ("frontier_selector", selector_report, "frontier selector"),
        (
            "selected_root_certificate_coverage",
            coverage_report,
            "selected-root certificate coverage",
        ),
    )
    results: list[FixedPointDeferredCaseCertificateReadinessValidation] = []
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


def _derive_readiness_entries(
    graph_report: Any,
    selector_report: Any,
    coverage_report: Any,
    proof_boundary_preserved: bool,
) -> list[FixedPointDeferredCaseCertificateReadinessEntry]:
    if not (graph_report.accepted and selector_report.accepted):
        return []

    graph_predecessors = _graph_predecessors_by_case_kind(graph_report)
    graph_nodes = {node.case_kind: node for node in graph_report.nodes}
    deferred_by_kind = {case.case_kind: case for case in selector_report.deferred}
    covered_roots = {
        entry.selected_case_kind
        for entry in coverage_report.coverage_entries
        if entry.accepted
    }
    entries: list[FixedPointDeferredCaseCertificateReadinessEntry] = []
    for case_kind in REQUIRED_DEFERRED_CASE_KINDS:
        deferred_case = deferred_by_kind.get(case_kind)
        graph_node = graph_nodes.get(case_kind)
        if deferred_case is None or graph_node is None:
            continue
        predecessors = graph_predecessors.get(case_kind, ())
        covered_predecessors = tuple(
            predecessor for predecessor in predecessors if predecessor in covered_roots
        )
        open_predecessors = _open_predecessors(predecessors, graph_nodes)
        entries.append(
            FixedPointDeferredCaseCertificateReadinessEntry(
                readiness_id=(
                    "AS-FIXED-POINT-DEFERRED-CASE-CERTIFICATE-READINESS-"
                    + case_kind.upper().replace("-", "_")
                ),
                deferred_case_kind=case_kind,
                construction_case_id=deferred_case.case_id,
                target_id=deferred_case.target_id,
                readiness_status=READINESS_STATUS,
                predecessor_case_kinds=predecessors,
                certificate_covered_predecessor_case_kinds=covered_predecessors,
                blocking_open_predecessor_case_kinds=open_predecessors,
                selector_defers_case=case_kind in deferred_by_kind,
                construction_case_open=deferred_case.status == REQUIRED_CASE_STATUS,
                graph_predecessors_match_selector_blockers=(
                    predecessors == deferred_case.blocking_predecessors
                ),
                selected_root_coverage_accepted=coverage_report.accepted,
                proof_boundary_preserved=proof_boundary_preserved,
            )
        )
    return entries


def _validate_readiness(
    manifest: FixedPointDeferredCaseCertificateReadinessManifest,
    deferred_case_kinds: tuple[str, ...],
    selected_root_coverage_accepted: bool,
    proof_boundary_preserved: bool,
    readiness_entries: list[FixedPointDeferredCaseCertificateReadinessEntry],
) -> list[FixedPointDeferredCaseCertificateReadinessValidation]:
    results: list[FixedPointDeferredCaseCertificateReadinessValidation] = []
    if deferred_case_kinds == manifest.expected_deferred_case_kinds:
        results.append(_accepted("deferred_case_kinds", "deferred cases match"))
    else:
        results.append(_rejected("deferred_case_kinds", "deferred case mismatch"))

    if len(readiness_entries) == manifest.expected_deferred_case_count:
        results.append(
            _accepted(
                "readiness_count",
                f"readiness count {len(readiness_entries)} matches",
            )
        )
    else:
        results.append(
            _rejected(
                "readiness_count",
                "readiness count mismatch: expected "
                f"{manifest.expected_deferred_case_count} but found "
                f"{len(readiness_entries)}",
            )
        )

    if selected_root_coverage_accepted:
        results.append(
            _accepted(
                "selected_root_certificate_coverage",
                "selected-root coverage accepted",
            )
        )
    else:
        results.append(
            _rejected(
                "selected_root_certificate_coverage",
                "selected-root coverage rejected",
            )
        )

    if proof_boundary_preserved:
        results.append(_accepted("proof_boundary", "proof boundary preserved"))
    else:
        results.append(_rejected("proof_boundary", "proof boundary not preserved"))

    results.extend(_validate_entry_counts(manifest, readiness_entries))

    rejected_entries = [
        entry.deferred_case_kind for entry in readiness_entries if not entry.accepted
    ]
    if rejected_entries:
        results.append(
            _rejected("readiness_entries", "rejected entries: " + ", ".join(rejected_entries))
        )
    else:
        results.append(_accepted("readiness_entries", "all readiness entries deferred"))
    return results


def _validate_entry_counts(
    manifest: FixedPointDeferredCaseCertificateReadinessManifest,
    readiness_entries: list[FixedPointDeferredCaseCertificateReadinessEntry],
) -> list[FixedPointDeferredCaseCertificateReadinessValidation]:
    results: list[FixedPointDeferredCaseCertificateReadinessValidation] = []
    predecessor_mismatches: list[str] = []
    covered_mismatches: list[str] = []
    for entry in readiness_entries:
        expected_predecessors = manifest.expected_predecessor_counts.get(
            entry.deferred_case_kind
        )
        expected_covered = (
            manifest.expected_certificate_covered_predecessor_counts.get(
                entry.deferred_case_kind
            )
        )
        if expected_predecessors != entry.predecessor_count:
            predecessor_mismatches.append(
                f"{entry.deferred_case_kind} expected {expected_predecessors} "
                f"found {entry.predecessor_count}"
            )
        if expected_covered != entry.certificate_covered_predecessor_count:
            covered_mismatches.append(
                f"{entry.deferred_case_kind} expected {expected_covered} "
                f"found {entry.certificate_covered_predecessor_count}"
            )

    if predecessor_mismatches:
        results.append(
            _rejected(
                "predecessor_counts",
                "predecessor count mismatch: " + "; ".join(predecessor_mismatches),
            )
        )
    else:
        results.append(_accepted("predecessor_counts", "predecessor counts match"))

    if covered_mismatches:
        results.append(
            _rejected(
                "certificate_covered_predecessor_counts",
                "covered predecessor count mismatch: "
                + "; ".join(covered_mismatches),
            )
        )
    else:
        results.append(
            _accepted(
                "certificate_covered_predecessor_counts",
                "covered predecessor counts match",
            )
        )
    return results


def _proof_boundary_preserved(
    manifest: FixedPointDeferredCaseCertificateReadinessManifest,
    graph_report: Any,
    selector_report: Any,
    coverage_report: Any,
) -> bool:
    deferred_open = all(
        case.status == REQUIRED_CASE_STATUS and bool(case.blocking_predecessors)
        for case in selector_report.deferred
    )
    graph_open = all(node.status == REQUIRED_CASE_STATUS for node in graph_report.nodes)
    coverage_non_claims = set(getattr(coverage_report.manifest, "non_claims", ()))
    return (
        graph_report.accepted
        and selector_report.accepted
        and coverage_report.accepted
        and graph_open
        and deferred_open
        and selector_report.frontier_status == "blocked"
        and selector_report.frontier_blocked_by == "fixed-point-construction"
        and set(REQUIRED_NON_CLAIMS).issubset(set(manifest.non_claims))
        and "no fixed-point equation proof" in coverage_non_claims
        and "no self-consistency theorem" in coverage_non_claims
    )


def _readiness_entry_payload(
    entry: FixedPointDeferredCaseCertificateReadinessEntry,
) -> dict[str, Any]:
    return {
        "readiness_id": entry.readiness_id,
        "deferred_case_kind": entry.deferred_case_kind,
        "construction_case_id": entry.construction_case_id,
        "target_id": entry.target_id,
        "readiness_status": entry.readiness_status,
        "predecessor_case_kinds": list(entry.predecessor_case_kinds),
        "predecessor_count": entry.predecessor_count,
        "certificate_covered_predecessor_case_kinds": list(
            entry.certificate_covered_predecessor_case_kinds
        ),
        "certificate_covered_predecessor_count": (
            entry.certificate_covered_predecessor_count
        ),
        "blocking_open_predecessor_case_kinds": list(
            entry.blocking_open_predecessor_case_kinds
        ),
        "observed_selector_defers_case": entry.selector_defers_case,
        "observed_construction_case_open": entry.construction_case_open,
        "observed_graph_predecessors_match_selector_blockers": (
            entry.graph_predecessors_match_selector_blockers
        ),
        "observed_selected_root_coverage_accepted": (
            entry.selected_root_coverage_accepted
        ),
        "observed_proof_boundary_preserved": entry.proof_boundary_preserved,
        "accepted": entry.accepted,
    }


def _graph_predecessors_by_case_kind(graph_report: Any) -> dict[str, tuple[str, ...]]:
    predecessors: dict[str, list[str]] = {node.case_kind: [] for node in graph_report.nodes}
    for edge in graph_report.edges:
        predecessors.setdefault(edge.to_case_kind, []).append(edge.from_case_kind)
    return {
        case_kind: tuple(items)
        for case_kind, items in predecessors.items()
    }


def _open_predecessors(
    predecessor_case_kinds: tuple[str, ...],
    graph_nodes: dict[str, Any],
) -> tuple[str, ...]:
    return tuple(
        case_kind
        for case_kind in predecessor_case_kinds
        if graph_nodes[case_kind].status == REQUIRED_CASE_STATUS
    )


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointDeferredCaseCertificateReadinessValidation:
    return FixedPointDeferredCaseCertificateReadinessValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointDeferredCaseCertificateReadinessValidation:
    return FixedPointDeferredCaseCertificateReadinessValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"expected_deferred_case_kinds", "deferred_case_kinds"}:
        return "fixed-point-deferred-case-certificate-readiness-deferred-cases"
    if subject in {"expected_deferred_case_count", "readiness_count"}:
        return "fixed-point-deferred-case-certificate-readiness-count"
    if subject in {"expected_predecessor_counts", "predecessor_counts"}:
        return "fixed-point-deferred-case-certificate-readiness-predecessors"
    if subject in {
        "expected_certificate_covered_predecessor_counts",
        "certificate_covered_predecessor_counts",
    }:
        return "fixed-point-deferred-case-certificate-readiness-covered-predecessors"
    if subject == "non_claims":
        return "fixed-point-deferred-case-certificate-readiness-non-claim"
    if subject == "proof_boundary":
        return "fixed-point-deferred-case-certificate-readiness-boundary"
    if subject == "readiness_entries":
        return "fixed-point-deferred-case-certificate-readiness-entry"
    if subject.endswith("_path"):
        return "fixed-point-deferred-case-certificate-readiness-path"
    return subject


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return value


def _required_int_map(data: dict[str, Any], key: str) -> dict[str, int]:
    value = data.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{key} must be a non-empty object")
    result: dict[str, int] = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str) or not item_key.strip():
            raise ValueError(f"{key} must have non-empty text keys")
        if not isinstance(item_value, int):
            raise ValueError(f"{key} values must be integers")
        result[item_key] = item_value
    return result


def _joined_or_none(items: tuple[str, ...]) -> str:
    if not items:
        return "none"
    return ", ".join(items)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_deferred_case_certificate_readiness_cli())
