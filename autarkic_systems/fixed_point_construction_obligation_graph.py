"""Checked dependency graph for fixed-point construction proof obligations.

The fixed-point construction frontier currently contains five open proof
cases. This module turns those cases into a small directed obligation graph so
operators can see which open cases feed later cases. It is deliberately a
frontier-routing surface only: it does not prove any case, the fixed-point
equation, an arithmetized proof predicate, or self-consistency.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
    validate_fixed_point_construction_cases,
)
from autarkic_systems.fixed_point_construction_frontier_status import (
    load_fixed_point_construction_frontier_status,
    validate_fixed_point_construction_frontier_status,
)


DEFAULT_GRAPH = Path("claims/fixed_point_construction_obligation_graph.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_GRAPH_EDGES = (
    ("diagonal-instance-closure", "substitution-representability-proof"),
    ("diagonal-instance-closure", "bridge-equality-proof"),
    (
        "substitution-graph-correctness-proof",
        "substitution-representability-proof",
    ),
    ("substitution-representability-proof", "bridge-equality-proof"),
    ("substitution-graph-correctness-proof", "bridge-equality-proof"),
    ("bridge-equality-proof", "fixed-point-equation-lifting"),
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_NODE_ORDER = (
    "diagonal-instance-closure",
    "substitution-graph-correctness-proof",
    "substitution-representability-proof",
    "bridge-equality-proof",
    "fixed-point-equation-lifting",
)
EXPECTED_DEPENDENCY_PATHS = {
    "fixed_point_construction_cases_path": "claims/fixed_point_construction_cases.json",
    "fixed_point_construction_frontier_status_path": (
        "claims/fixed_point_construction_frontier_status.json"
    ),
}


@dataclass(frozen=True)
class FixedPointConstructionObligationGraphManifest:
    """Loaded manifest for the fixed-point construction obligation graph."""

    path: Path
    schema_version: int
    graph_id: str
    reviewed_at: str
    purpose: str
    frontier_status: str
    frontier_blocked_by: str
    fixed_point_construction_cases_path: str
    fixed_point_construction_frontier_status_path: str
    expected_node_count: int
    expected_edge_count: int
    required_edges: tuple[tuple[str, str], ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointConstructionObligationGraphNode:
    """One open proof-obligation node derived from construction cases."""

    case_id: str
    case_kind: str
    target_id: str
    status: str
    required_dependency_subjects: tuple[str, ...]
    required_future_work: tuple[str, ...]


@dataclass(frozen=True)
class FixedPointConstructionObligationGraphEdge:
    """One directed dependency edge between open proof obligations."""

    from_case_kind: str
    to_case_kind: str


@dataclass(frozen=True)
class FixedPointConstructionObligationGraphValidation:
    """One validation result for the fixed-point obligation graph."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointConstructionObligationGraphReport:
    """Validation report for the fixed-point construction obligation graph."""

    manifest: FixedPointConstructionObligationGraphManifest
    fixed_point_construction_cases_path: Path
    fixed_point_construction_frontier_status_path: Path
    willard_map_path: Path
    nodes: tuple[FixedPointConstructionObligationGraphNode, ...]
    edges: tuple[FixedPointConstructionObligationGraphEdge, ...]
    acyclic: bool
    results: tuple[FixedPointConstructionObligationGraphValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every obligation-graph validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def node_count(self) -> int:
        """Return the number of checked proof-obligation nodes."""

        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        """Return the number of checked dependency edges."""

        return len(self.edges)

    @property
    def root_case_kinds(self) -> tuple[str, ...]:
        """Return nodes with no incoming obligation edges."""

        incoming = {edge.to_case_kind for edge in self.edges}
        return tuple(node.case_kind for node in self.nodes if node.case_kind not in incoming)

    @property
    def terminal_case_kinds(self) -> tuple[str, ...]:
        """Return nodes with no outgoing obligation edges."""

        outgoing = {edge.from_case_kind for edge in self.edges}
        return tuple(node.case_kind for node in self.nodes if node.case_kind not in outgoing)

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
    """Small report shim used when a dependency cannot be loaded."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    manifest: Any | None = None
    frontier_status: str = ""
    frontier_blocked_by: str = ""


def load_fixed_point_construction_obligation_graph(
    path: Path | str = DEFAULT_GRAPH,
) -> FixedPointConstructionObligationGraphManifest:
    """Load the fixed-point construction obligation graph manifest."""

    graph_path = Path(path)
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    return FixedPointConstructionObligationGraphManifest(
        path=graph_path,
        schema_version=_required_int(data, "schema_version"),
        graph_id=_required_text(data, "graph_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        frontier_status=_required_text(data, "frontier_status"),
        frontier_blocked_by=_required_text(data, "frontier_blocked_by"),
        fixed_point_construction_cases_path=_required_text(
            data,
            "fixed_point_construction_cases_path",
        ),
        fixed_point_construction_frontier_status_path=_required_text(
            data,
            "fixed_point_construction_frontier_status_path",
        ),
        expected_node_count=_required_int(data, "expected_node_count"),
        expected_edge_count=_required_int(data, "expected_edge_count"),
        required_edges=tuple(_required_edge_list(data, "required_edges")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_construction_obligation_graph(
    manifest: FixedPointConstructionObligationGraphManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointConstructionObligationGraphReport:
    """Validate the obligation graph against current construction surfaces."""

    checked_willard_map_path = Path(willard_map_path)
    cases_path = Path(manifest.fixed_point_construction_cases_path)
    frontier_path = Path(manifest.fixed_point_construction_frontier_status_path)
    results: list[FixedPointConstructionObligationGraphValidation] = [
        _accepted("manifest", f"loaded {manifest.graph_id}")
    ]
    results.extend(_validate_manifest(manifest))

    cases_report = _load_cases(cases_path, checked_willard_map_path)
    frontier_report = _load_frontier(frontier_path, checked_willard_map_path)
    results.extend(_validate_dependencies(cases_report, frontier_report, manifest))

    nodes = _derive_nodes(cases_report)
    edges = tuple(
        FixedPointConstructionObligationGraphEdge(from_kind, to_kind)
        for from_kind, to_kind in manifest.required_edges
    )
    acyclic = _is_acyclic(tuple(node.case_kind for node in nodes), edges)
    results.extend(_validate_graph_shape(manifest, nodes, edges, acyclic))

    return FixedPointConstructionObligationGraphReport(
        manifest=manifest,
        fixed_point_construction_cases_path=cases_path,
        fixed_point_construction_frontier_status_path=frontier_path,
        willard_map_path=checked_willard_map_path,
        nodes=nodes,
        edges=edges,
        acyclic=acyclic,
        results=tuple(results),
    )


def fixed_point_construction_obligation_graph_payload(
    report: FixedPointConstructionObligationGraphReport,
) -> dict[str, Any]:
    """Return a JSON-ready obligation graph payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "graph_manifest": str(report.manifest.path),
        "graph_id": report.manifest.graph_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_status": report.manifest.frontier_status,
        "frontier_blocked_by": report.manifest.frontier_blocked_by,
        "fixed_point_construction_cases_path": str(
            report.fixed_point_construction_cases_path
        ),
        "fixed_point_construction_frontier_status_path": str(
            report.fixed_point_construction_frontier_status_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_node_count": report.manifest.expected_node_count,
        "expected_edge_count": report.manifest.expected_edge_count,
        "node_count": report.node_count,
        "edge_count": report.edge_count,
        "acyclic": report.acyclic,
        "root_case_kinds": list(report.root_case_kinds),
        "terminal_case_kinds": list(report.terminal_case_kinds),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "nodes": [
            {
                "case_id": node.case_id,
                "case_kind": node.case_kind,
                "target_id": node.target_id,
                "status": node.status,
                "required_dependency_subjects": list(
                    node.required_dependency_subjects
                ),
                "required_future_work": list(node.required_future_work),
            }
            for node in report.nodes
        ],
        "edges": [
            {"from": edge.from_case_kind, "to": edge.to_case_kind}
            for edge in report.edges
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


def format_fixed_point_construction_obligation_graph_report(
    report: FixedPointConstructionObligationGraphReport,
) -> str:
    """Format a concise human-readable obligation graph report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point construction obligation graph: {status}",
        (
            f"Frontier: {report.manifest.frontier_status} by "
            f"{report.manifest.frontier_blocked_by}"
        ),
        f"Nodes: {report.node_count}",
        f"Edges: {report.edge_count}",
        f"Acyclic: {report.acyclic}",
        f"Root cases: {_joined_or_none(report.root_case_kinds)}",
        f"Terminal cases: {_joined_or_none(report.terminal_case_kinds)}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
        "Obligation edges:",
    ]
    for edge in report.edges:
        lines.append(f"- {edge.from_case_kind} -> {edge.to_case_kind}")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_construction_obligation_graph_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point construction obligation graph validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_construction_obligation_graph",
        description="Validate the AS fixed-point construction obligation graph.",
    )
    parser.add_argument(
        "--graph",
        default=str(DEFAULT_GRAPH),
        help="Path to the fixed-point construction obligation graph manifest.",
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

    manifest = load_fixed_point_construction_obligation_graph(args.graph)
    report = validate_fixed_point_construction_obligation_graph(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_construction_obligation_graph_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_construction_obligation_graph_report(report))
    return 0 if report.accepted else 1


def _load_cases(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_construction_cases(path)
        return validate_fixed_point_construction_cases(manifest, willard_map_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-construction-cases-load",))


def _load_frontier(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_construction_frontier_status(path)
        return validate_fixed_point_construction_frontier_status(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-construction-frontier-load",))


def _validate_manifest(
    manifest: FixedPointConstructionObligationGraphManifest,
) -> list[FixedPointConstructionObligationGraphValidation]:
    results: list[FixedPointConstructionObligationGraphValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.graph_id == "as-fixed-point-construction-obligation-graph-v1":
        results.append(_accepted("graph_id", "graph id matches"))
    else:
        results.append(_rejected("graph_id", "unexpected graph id"))

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

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.expected_node_count == 5:
        results.append(_accepted("expected_node_count", "five obligation nodes"))
    else:
        results.append(_rejected("expected_node_count", "expected five nodes"))

    if manifest.expected_edge_count == 6:
        results.append(_accepted("expected_edge_count", "six obligation edges"))
    else:
        results.append(_rejected("expected_edge_count", "expected six edges"))

    if manifest.required_edges == REQUIRED_GRAPH_EDGES:
        results.append(_accepted("required_edges", "required edges match"))
    else:
        results.append(_rejected("required_edges", "required edge mismatch"))

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
    cases_report: Any,
    frontier_report: Any,
    manifest: FixedPointConstructionObligationGraphManifest,
) -> list[FixedPointConstructionObligationGraphValidation]:
    results: list[FixedPointConstructionObligationGraphValidation] = []
    if cases_report.accepted:
        results.append(_accepted("fixed_point_construction_cases", "cases accepted"))
    else:
        results.append(
            _rejected(
                "fixed_point_construction_cases",
                "case failures: " + _joined_or_none(cases_report.failed_subjects),
            )
        )

    if frontier_report.accepted:
        results.append(
            _accepted(
                "fixed_point_construction_frontier_status",
                "frontier status accepted",
            )
        )
    else:
        results.append(
            _rejected(
                "fixed_point_construction_frontier_status",
                "frontier failures: " + _joined_or_none(frontier_report.failed_subjects),
            )
        )

    if frontier_report.frontier_status == manifest.frontier_status:
        results.append(_accepted("frontier_status_crosscheck", "frontier status matches"))
    else:
        results.append(
            _rejected(
                "frontier_status_crosscheck",
                (
                    "expected "
                    f"{manifest.frontier_status} but found "
                    f"{frontier_report.frontier_status}"
                ),
            )
        )

    if frontier_report.frontier_blocked_by == manifest.frontier_blocked_by:
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
                    f"{frontier_report.frontier_blocked_by}"
                ),
            )
        )
    return results


def _derive_nodes(cases_report: Any) -> tuple[FixedPointConstructionObligationGraphNode, ...]:
    cases_by_kind = {
        case.case_kind: case
        for case in getattr(getattr(cases_report, "manifest", None), "cases", ())
    }
    nodes: list[FixedPointConstructionObligationGraphNode] = []
    for case_kind in EXPECTED_NODE_ORDER:
        case = cases_by_kind.get(case_kind)
        if case is None:
            continue
        nodes.append(
            FixedPointConstructionObligationGraphNode(
                case_id=case.case_id,
                case_kind=case.case_kind,
                target_id=case.target_id,
                status=case.status,
                required_dependency_subjects=case.required_dependency_subjects,
                required_future_work=case.required_future_work,
            )
        )
    return tuple(nodes)


def _validate_graph_shape(
    manifest: FixedPointConstructionObligationGraphManifest,
    nodes: tuple[FixedPointConstructionObligationGraphNode, ...],
    edges: tuple[FixedPointConstructionObligationGraphEdge, ...],
    acyclic: bool,
) -> list[FixedPointConstructionObligationGraphValidation]:
    results: list[FixedPointConstructionObligationGraphValidation] = []
    case_kinds = tuple(node.case_kind for node in nodes)
    case_kind_set = set(case_kinds)

    if case_kinds == EXPECTED_NODE_ORDER:
        results.append(_accepted("nodes", "node order matches current frontier"))
    else:
        results.append(_rejected("nodes", "node order mismatch"))

    if len(nodes) == manifest.expected_node_count:
        results.append(_accepted("node_count", "node count matches manifest"))
    else:
        results.append(_rejected("node_count", "node count mismatch"))

    if len(edges) == manifest.expected_edge_count:
        results.append(_accepted("edge_count", "edge count matches manifest"))
    else:
        results.append(_rejected("edge_count", "edge count mismatch"))

    unknown_edge_kinds = [
        kind
        for edge in edges
        for kind in (edge.from_case_kind, edge.to_case_kind)
        if kind not in case_kind_set
    ]
    if unknown_edge_kinds:
        results.append(
            _rejected(
                "edge_endpoints",
                "unknown edge endpoints: " + ", ".join(unknown_edge_kinds),
            )
        )
    else:
        results.append(_accepted("edge_endpoints", "all edges reference nodes"))

    open_statuses = [node.case_kind for node in nodes if node.status != "proof-case-open"]
    if open_statuses:
        results.append(
            _rejected(
                "node_statuses",
                "non-open case statuses: " + ", ".join(open_statuses),
            )
        )
    else:
        results.append(_accepted("node_statuses", "all proof cases remain open"))

    if acyclic:
        results.append(_accepted("acyclic", "obligation graph is acyclic"))
    else:
        results.append(_rejected("acyclic", "obligation graph contains a cycle"))
    return results


def _is_acyclic(
    case_kinds: tuple[str, ...],
    edges: tuple[FixedPointConstructionObligationGraphEdge, ...],
) -> bool:
    outgoing: dict[str, list[str]] = {case_kind: [] for case_kind in case_kinds}
    for edge in edges:
        outgoing.setdefault(edge.from_case_kind, []).append(edge.to_case_kind)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(case_kind: str) -> bool:
        if case_kind in visiting:
            return False
        if case_kind in visited:
            return True
        visiting.add(case_kind)
        for child in outgoing.get(case_kind, []):
            if not visit(child):
                return False
        visiting.remove(case_kind)
        visited.add(case_kind)
        return True

    return all(visit(case_kind) for case_kind in case_kinds)


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


def _required_edge_list(data: dict[str, Any], key: str) -> list[tuple[str, str]]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty edge list")
    edges: list[tuple[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"{key} entries must be objects")
        from_kind = item.get("from")
        to_kind = item.get("to")
        if not isinstance(from_kind, str) or not from_kind.strip():
            raise ValueError(f"{key} entries require non-empty from")
        if not isinstance(to_kind, str) or not to_kind.strip():
            raise ValueError(f"{key} entries require non-empty to")
        edges.append((from_kind, to_kind))
    return edges


def _failed_subject_for_result(subject: str) -> str:
    if subject == "required_edges":
        return "fixed-point-construction-obligation-graph-edges"
    if subject == "non_claims":
        return "fixed-point-construction-obligation-graph-non-claim"
    if subject in {"nodes", "node_count", "edge_count", "edge_endpoints", "acyclic"}:
        return "fixed-point-construction-obligation-graph-shape"
    if subject.startswith("fixed_point_construction_cases"):
        return "fixed-point-construction-cases"
    if subject.startswith("fixed_point_construction_frontier"):
        return "fixed-point-construction-frontier-status"
    return subject.replace("_", "-")


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointConstructionObligationGraphValidation:
    return FixedPointConstructionObligationGraphValidation(subject, True, detail)


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointConstructionObligationGraphValidation:
    return FixedPointConstructionObligationGraphValidation(subject, False, detail)


def _joined_or_none(values: tuple[str, ...]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_construction_obligation_graph_cli())
