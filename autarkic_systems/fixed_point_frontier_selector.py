"""Selector for the currently actionable fixed-point construction frontier.

ADR-0301 records the open proof obligations as a checked graph. This module
uses that graph to select open root obligations and defer downstream open
obligations whose predecessors are still open. It is a scheduling surface only:
it does not prove any fixed-point construction case or promote AS
self-consistency claims.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_construction_obligation_graph import (
    load_fixed_point_construction_obligation_graph,
    validate_fixed_point_construction_obligation_graph,
)


DEFAULT_SELECTOR = Path("claims/fixed_point_frontier_selector.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SELECTED_CASE_KINDS = (
    "diagonal-instance-closure",
    "substitution-graph-correctness-proof",
)
REQUIRED_DEFERRED_CASE_KINDS = (
    "substitution-representability-proof",
    "bridge-equality-proof",
    "fixed-point-equation-lifting",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_GRAPH_PATH = "claims/fixed_point_construction_obligation_graph.json"


@dataclass(frozen=True)
class FixedPointFrontierSelectorManifest:
    """Loaded manifest for the fixed-point frontier selector."""

    path: Path
    schema_version: int
    selector_id: str
    reviewed_at: str
    purpose: str
    selection_policy: str
    frontier_status: str
    frontier_blocked_by: str
    fixed_point_construction_obligation_graph_path: str
    expected_selected_count: int
    expected_deferred_count: int
    expected_selected_case_kinds: tuple[str, ...]
    expected_deferred_case_kinds: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointFrontierSelectorItem:
    """One selected or deferred proof obligation."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    blocking_predecessors: tuple[str, ...]
    required_dependency_subjects: tuple[str, ...]
    required_future_work: tuple[str, ...]


@dataclass(frozen=True)
class FixedPointFrontierSelectorValidation:
    """One validation result for the fixed-point frontier selector."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointFrontierSelectorReport:
    """Validation report for the fixed-point frontier selector."""

    manifest: FixedPointFrontierSelectorManifest
    fixed_point_construction_obligation_graph_path: Path
    willard_map_path: Path
    frontier_status: str
    frontier_blocked_by: str
    selected: tuple[FixedPointFrontierSelectorItem, ...]
    deferred: tuple[FixedPointFrontierSelectorItem, ...]
    results: tuple[FixedPointFrontierSelectorValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every frontier-selector validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def selected_count(self) -> int:
        """Return the number of selected open root obligations."""

        return len(self.selected)

    @property
    def deferred_count(self) -> int:
        """Return the number of deferred open downstream obligations."""

        return len(self.deferred)

    @property
    def selected_case_kinds(self) -> tuple[str, ...]:
        """Return selected case kinds in selector order."""

        return tuple(item.case_kind for item in self.selected)

    @property
    def deferred_case_kinds(self) -> tuple[str, ...]:
        """Return deferred case kinds in selector order."""

        return tuple(item.case_kind for item in self.deferred)

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
    """Small report shim used when the graph dependency cannot load."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    frontier_status: str = ""
    frontier_blocked_by: str = ""
    nodes: tuple[Any, ...] = ()
    edges: tuple[Any, ...] = ()


def load_fixed_point_frontier_selector(
    path: Path | str = DEFAULT_SELECTOR,
) -> FixedPointFrontierSelectorManifest:
    """Load the fixed-point frontier selector manifest."""

    selector_path = Path(path)
    data = json.loads(selector_path.read_text(encoding="utf-8"))
    return FixedPointFrontierSelectorManifest(
        path=selector_path,
        schema_version=_required_int(data, "schema_version"),
        selector_id=_required_text(data, "selector_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        selection_policy=_required_text(data, "selection_policy"),
        frontier_status=_required_text(data, "frontier_status"),
        frontier_blocked_by=_required_text(data, "frontier_blocked_by"),
        fixed_point_construction_obligation_graph_path=_required_text(
            data,
            "fixed_point_construction_obligation_graph_path",
        ),
        expected_selected_count=_required_int(data, "expected_selected_count"),
        expected_deferred_count=_required_int(data, "expected_deferred_count"),
        expected_selected_case_kinds=tuple(
            _required_text_list(data, "expected_selected_case_kinds")
        ),
        expected_deferred_case_kinds=tuple(
            _required_text_list(data, "expected_deferred_case_kinds")
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_frontier_selector(
    manifest: FixedPointFrontierSelectorManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointFrontierSelectorReport:
    """Validate the selector against the checked obligation graph."""

    checked_willard_map_path = Path(willard_map_path)
    graph_path = Path(manifest.fixed_point_construction_obligation_graph_path)
    results: list[FixedPointFrontierSelectorValidation] = [
        _accepted("manifest", f"loaded {manifest.selector_id}")
    ]
    results.extend(_validate_manifest(manifest))

    graph_report = _load_graph(graph_path, checked_willard_map_path)
    results.extend(_validate_graph_dependency(graph_report, manifest))

    selected, deferred = _derive_selection(graph_report)
    results.extend(_validate_selection(manifest, selected, deferred))

    return FixedPointFrontierSelectorReport(
        manifest=manifest,
        fixed_point_construction_obligation_graph_path=graph_path,
        willard_map_path=checked_willard_map_path,
        frontier_status=_graph_frontier_status(graph_report),
        frontier_blocked_by=_graph_frontier_blocked_by(graph_report),
        selected=selected,
        deferred=deferred,
        results=tuple(results),
    )


def fixed_point_frontier_selector_payload(
    report: FixedPointFrontierSelectorReport,
) -> dict[str, Any]:
    """Return a JSON-ready fixed-point frontier selector payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "selector_manifest": str(report.manifest.path),
        "selector_id": report.manifest.selector_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "selection_policy": report.manifest.selection_policy,
        "frontier_status": report.frontier_status,
        "frontier_blocked_by": report.frontier_blocked_by,
        "fixed_point_construction_obligation_graph_path": str(
            report.fixed_point_construction_obligation_graph_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_selected_count": report.manifest.expected_selected_count,
        "expected_deferred_count": report.manifest.expected_deferred_count,
        "selected_count": report.selected_count,
        "deferred_count": report.deferred_count,
        "selected_case_kinds": list(report.selected_case_kinds),
        "deferred_case_kinds": list(report.deferred_case_kinds),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "selected": [_selector_item_payload(item) for item in report.selected],
        "deferred": [_selector_item_payload(item) for item in report.deferred],
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


def format_fixed_point_frontier_selector_report(
    report: FixedPointFrontierSelectorReport,
) -> str:
    """Format a concise human-readable frontier selector report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point frontier selector: {status}",
        f"Frontier: {report.frontier_status} by {report.frontier_blocked_by}",
        f"Policy: {report.manifest.selection_policy}",
        f"Selected open obligations: {report.selected_count}",
    ]
    for item in report.selected:
        lines.append(f"- {item.case_kind}: {item.status}")
    lines.append(f"Deferred open obligations: {report.deferred_count}")
    for item in report.deferred:
        lines.append(
            (
                f"- {item.case_kind}: {item.status} "
                f"(blocked by {_joined_or_none(item.blocking_predecessors)})"
            )
        )
    lines.extend(
        (
            "Non-claims: " + _joined_or_none(report.manifest.non_claims),
            f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
            "Validation:",
        )
    )
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_frontier_selector_cli(argv: list[str] | None = None) -> int:
    """Run fixed-point frontier selector validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_frontier_selector",
        description="Validate the AS fixed-point construction frontier selector.",
    )
    parser.add_argument(
        "--selector",
        default=str(DEFAULT_SELECTOR),
        help="Path to the fixed-point frontier selector manifest.",
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

    manifest = load_fixed_point_frontier_selector(args.selector)
    report = validate_fixed_point_frontier_selector(manifest, args.willard_map)
    if args.format == "json":
        print(json.dumps(fixed_point_frontier_selector_payload(report), sort_keys=True))
    else:
        print(format_fixed_point_frontier_selector_report(report))
    return 0 if report.accepted else 1


def _load_graph(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_construction_obligation_graph(path)
        return validate_fixed_point_construction_obligation_graph(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-obligation-graph-load",))


def _derive_selection(
    graph_report: Any,
) -> tuple[
    tuple[FixedPointFrontierSelectorItem, ...],
    tuple[FixedPointFrontierSelectorItem, ...],
]:
    incoming_by_kind: dict[str, list[str]] = {
        node.case_kind: [] for node in graph_report.nodes
    }
    for edge in graph_report.edges:
        incoming_by_kind.setdefault(edge.to_case_kind, []).append(edge.from_case_kind)

    selected: list[FixedPointFrontierSelectorItem] = []
    deferred: list[FixedPointFrontierSelectorItem] = []
    for node in graph_report.nodes:
        blockers = tuple(incoming_by_kind.get(node.case_kind, ()))
        item = FixedPointFrontierSelectorItem(
            case_id=node.case_id,
            case_kind=node.case_kind,
            target_id=node.target_id,
            status=node.status,
            blocking_predecessors=blockers,
            required_dependency_subjects=node.required_dependency_subjects,
            required_future_work=node.required_future_work,
        )
        if blockers:
            deferred.append(item)
        else:
            selected.append(item)
    return tuple(selected), tuple(deferred)


def _validate_manifest(
    manifest: FixedPointFrontierSelectorManifest,
) -> list[FixedPointFrontierSelectorValidation]:
    results: list[FixedPointFrontierSelectorValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.selector_id == "as-fixed-point-frontier-selector-v1":
        results.append(_accepted("selector_id", "selector id matches"))
    else:
        results.append(_rejected("selector_id", "unexpected selector id"))

    if manifest.selection_policy == "open-root-obligations-before-dependent-cases":
        results.append(_accepted("selection_policy", "selection policy matches"))
    else:
        results.append(_rejected("selection_policy", "unexpected selection policy"))

    if manifest.frontier_status == "blocked":
        results.append(_accepted("frontier_status", "blocked frontier preserved"))
    else:
        results.append(_rejected("frontier_status", "expected blocked frontier"))

    if manifest.frontier_blocked_by == "fixed-point-construction":
        results.append(_accepted("frontier_blocked_by", "aggregate blocker preserved"))
    else:
        results.append(
            _rejected("frontier_blocked_by", "expected fixed-point-construction")
        )

    if manifest.fixed_point_construction_obligation_graph_path == EXPECTED_GRAPH_PATH:
        results.append(_accepted("obligation_graph_path", "graph path matches"))
    else:
        results.append(
            _rejected(
                "obligation_graph_path",
                (
                    f"expected {EXPECTED_GRAPH_PATH} but found "
                    f"{manifest.fixed_point_construction_obligation_graph_path}"
                ),
            )
        )

    if manifest.expected_selected_count == 2:
        results.append(_accepted("expected_selected_count", "two selected roots"))
    else:
        results.append(
            _rejected("expected_selected_count", "expected two selected roots")
        )

    if manifest.expected_deferred_count == 3:
        results.append(_accepted("expected_deferred_count", "three deferred cases"))
    else:
        results.append(
            _rejected("expected_deferred_count", "expected three deferred cases")
        )

    if manifest.expected_selected_case_kinds == REQUIRED_SELECTED_CASE_KINDS:
        results.append(
            _accepted("expected_selected_case_kinds", "selected cases match")
        )
    else:
        results.append(
            _rejected(
                "expected_selected_case_kinds",
                "selected case mismatch",
            )
        )

    if manifest.expected_deferred_case_kinds == REQUIRED_DEFERRED_CASE_KINDS:
        results.append(_accepted("expected_deferred_case_kinds", "deferred cases match"))
    else:
        results.append(
            _rejected("expected_deferred_case_kinds", "deferred case mismatch")
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


def _validate_graph_dependency(
    graph_report: Any,
    manifest: FixedPointFrontierSelectorManifest,
) -> list[FixedPointFrontierSelectorValidation]:
    results: list[FixedPointFrontierSelectorValidation] = []
    if graph_report.accepted:
        results.append(_accepted("obligation_graph", "obligation graph accepted"))
    else:
        results.append(
            _rejected(
                "obligation_graph",
                "graph failures: " + _joined_or_none(graph_report.failed_subjects),
            )
        )

    graph_frontier_status = _graph_frontier_status(graph_report)
    graph_frontier_blocked_by = _graph_frontier_blocked_by(graph_report)

    if graph_frontier_status == manifest.frontier_status:
        results.append(_accepted("frontier_status_crosscheck", "frontier status matches"))
    else:
        results.append(
            _rejected(
                "frontier_status_crosscheck",
                (
                    "expected "
                    f"{manifest.frontier_status} but found "
                    f"{graph_frontier_status}"
                ),
            )
        )

    if graph_frontier_blocked_by == manifest.frontier_blocked_by:
        results.append(
            _accepted("frontier_blocker_crosscheck", "frontier blocker matches")
        )
    else:
        results.append(
            _rejected(
                "frontier_blocker_crosscheck",
                (
                    "expected "
                    f"{manifest.frontier_blocked_by} but found "
                    f"{graph_frontier_blocked_by}"
                ),
            )
        )
    return results


def _graph_frontier_status(graph_report: Any) -> str:
    manifest = getattr(graph_report, "manifest", None)
    return getattr(manifest, "frontier_status", getattr(graph_report, "frontier_status", ""))


def _graph_frontier_blocked_by(graph_report: Any) -> str:
    manifest = getattr(graph_report, "manifest", None)
    return getattr(
        manifest,
        "frontier_blocked_by",
        getattr(graph_report, "frontier_blocked_by", ""),
    )


def _validate_selection(
    manifest: FixedPointFrontierSelectorManifest,
    selected: tuple[FixedPointFrontierSelectorItem, ...],
    deferred: tuple[FixedPointFrontierSelectorItem, ...],
) -> list[FixedPointFrontierSelectorValidation]:
    results: list[FixedPointFrontierSelectorValidation] = []
    selected_case_kinds = tuple(item.case_kind for item in selected)
    deferred_case_kinds = tuple(item.case_kind for item in deferred)

    if selected_case_kinds == manifest.expected_selected_case_kinds:
        results.append(_accepted("selected_case_kinds", "selected cases match graph"))
    else:
        results.append(_rejected("selected_case_kinds", "selected case mismatch"))

    if deferred_case_kinds == manifest.expected_deferred_case_kinds:
        results.append(_accepted("deferred_case_kinds", "deferred cases match graph"))
    else:
        results.append(_rejected("deferred_case_kinds", "deferred case mismatch"))

    if len(selected) == manifest.expected_selected_count:
        results.append(_accepted("selected_count", "selected count matches"))
    else:
        results.append(_rejected("selected_count", "selected count mismatch"))

    if len(deferred) == manifest.expected_deferred_count:
        results.append(_accepted("deferred_count", "deferred count matches"))
    else:
        results.append(_rejected("deferred_count", "deferred count mismatch"))

    if all(item.status == "proof-case-open" for item in selected + deferred):
        results.append(_accepted("case_statuses", "all selected/deferred cases open"))
    else:
        results.append(
            _rejected("case_statuses", "selected/deferred cases must remain open")
        )

    if all(not item.blocking_predecessors for item in selected):
        results.append(_accepted("selected_predecessors", "selected cases have no blockers"))
    else:
        results.append(
            _rejected(
                "selected_predecessors",
                "selected cases must not have open predecessors",
            )
        )

    if all(item.blocking_predecessors for item in deferred):
        results.append(_accepted("deferred_predecessors", "deferred cases have blockers"))
    else:
        results.append(
            _rejected("deferred_predecessors", "deferred cases must have blockers")
        )
    return results


def _selector_item_payload(item: FixedPointFrontierSelectorItem) -> dict[str, Any]:
    return {
        "case_id": item.case_id,
        "case_kind": item.case_kind,
        "target_id": item.target_id,
        "status": item.status,
        "blocking_predecessors": list(item.blocking_predecessors),
        "required_dependency_subjects": list(item.required_dependency_subjects),
        "required_future_work": list(item.required_future_work),
    }


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise ValueError(f"{key} must be a non-empty text list")
    return value


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"expected_selected_case_kinds", "selected_case_kinds"}:
        return "fixed-point-frontier-selector-selected"
    if subject in {"expected_deferred_case_kinds", "deferred_case_kinds"}:
        return "fixed-point-frontier-selector-deferred"
    if subject == "non_claims":
        return "fixed-point-frontier-selector-non-claim"
    if subject == "obligation_graph":
        return "fixed-point-construction-obligation-graph"
    return subject.replace("_", "-")


def _accepted(subject: str, detail: str) -> FixedPointFrontierSelectorValidation:
    return FixedPointFrontierSelectorValidation(subject, True, detail)


def _rejected(subject: str, detail: str) -> FixedPointFrontierSelectorValidation:
    return FixedPointFrontierSelectorValidation(subject, False, detail)


def _joined_or_none(values: tuple[str, ...]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_frontier_selector_cli())
