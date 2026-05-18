"""Recorded traces for post-handoff network-sequence witnesses."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from autarkic_systems import network_sequence
from autarkic_systems.universal_cell import Cell


POST_HANDOFF_SIGNAL_SEQUENCE_TRACE_ARTIFACT_ID = (
    "post-handoff-signal-sequence-trace"
)
VALID_NETWORK_SEQUENCE_TRACE_ARTIFACT_IDS = (
    POST_HANDOFF_SIGNAL_SEQUENCE_TRACE_ARTIFACT_ID,
)
REQUIRED_CELL_FIELDS = (
    "role",
    "memory",
    "upstream",
    "input",
    "output",
    "automail",
    "self_mailbox",
    "control",
    "buffer",
)
EMPTY_SIGNAL = ["_", "_", "_"]


@dataclass(frozen=True)
class NetworkSequenceTrace:
    """Loaded trace for one post-handoff network-sequence witness."""

    schema_version: int
    artifact_id: str
    reviewed_at: str
    purpose: str
    sequence_claim_id: str
    sequence_helper: str
    expected_status: str
    expected_delivery_status: str
    expected_delivered_tuple: tuple[Any, ...]
    followup_input: tuple[Any, ...]
    expected_followup_status: str
    sender_initial_cell: dict[str, Any]
    recipient_initial_cell: dict[str, Any]
    expected_recipient_before_followup: dict[str, Any]
    expected_recipient_after_followup: dict[str, Any]
    routed_signal_flow: tuple[str, ...]
    boundaries: tuple[str, ...]

    def with_expected_recipient_after_followup(
        self,
        cell: dict[str, Any],
    ) -> "NetworkSequenceTrace":
        """Return a copy with a replacement expected after-followup cell."""

        return replace(self, expected_recipient_after_followup=cell)


@dataclass(frozen=True)
class NetworkSequenceTraceExecution:
    """Computed result of replaying a network-sequence trace."""

    status: str
    accepted: bool
    delivery_status: str
    delivered_tuple: tuple[Any, ...]
    followup_status: str | None
    recipient_before_followup: dict[str, Any] | None
    recipient_after_followup: dict[str, Any] | None
    detail: str


@dataclass(frozen=True)
class NetworkSequenceTraceValidation:
    """One validation result for a network-sequence trace artifact."""

    subject: str
    accepted: bool
    detail: str


def load_network_sequence_trace(path: Path | str) -> NetworkSequenceTrace:
    """Load a network-sequence trace artifact from JSON."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return NetworkSequenceTrace(
        schema_version=_required_int(data, "schema_version"),
        artifact_id=_required_text(data, "artifact_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        sequence_claim_id=_required_text(data, "sequence_claim_id"),
        sequence_helper=_required_text(data, "sequence_helper"),
        expected_status=_required_text(data, "expected_status"),
        expected_delivery_status=_required_text(data, "expected_delivery_status"),
        expected_delivered_tuple=tuple(_required_list(data, "expected_delivered_tuple")),
        followup_input=tuple(_required_list(data, "followup_input")),
        expected_followup_status=_required_text(data, "expected_followup_status"),
        sender_initial_cell=_parse_cell_mapping(
            _required_dict(data, "sender_initial_cell")
        ),
        recipient_initial_cell=_parse_cell_mapping(
            _required_dict(data, "recipient_initial_cell")
        ),
        expected_recipient_before_followup=_parse_cell_mapping(
            _required_dict(data, "expected_recipient_before_followup")
        ),
        expected_recipient_after_followup=_parse_cell_mapping(
            _required_dict(data, "expected_recipient_after_followup")
        ),
        routed_signal_flow=tuple(_required_text_list(data, "routed_signal_flow")),
        boundaries=tuple(_required_text_list(data, "boundaries")),
    )


def execute_network_sequence_trace(
    trace: NetworkSequenceTrace,
) -> NetworkSequenceTraceExecution:
    """Replay the trace through the recorded network-sequence helper."""

    helper = getattr(network_sequence, trace.sequence_helper, None)
    if helper is None:
        raise ValueError(f"unknown sequence helper: {trace.sequence_helper}")

    witness = helper(
        _cell_from_mapping(trace.sender_initial_cell),
        _cell_from_mapping(trace.recipient_initial_cell),
        followup_input=trace.followup_input,
    )
    return NetworkSequenceTraceExecution(
        status=witness.status,
        accepted=witness.accepted,
        delivery_status=witness.delivery_witness.status,
        delivered_tuple=witness.delivery_witness.delivered_tuple,
        followup_status=(
            None if witness.followup_result is None else witness.followup_result.status
        ),
        recipient_before_followup=(
            None
            if witness.recipient_before_followup is None
            else _cell_to_mapping(witness.recipient_before_followup)
        ),
        recipient_after_followup=(
            None
            if witness.recipient_after_followup is None
            else _cell_to_mapping(witness.recipient_after_followup)
        ),
        detail=witness.detail,
    )


def validate_network_sequence_trace(
    trace: NetworkSequenceTrace,
) -> list[NetworkSequenceTraceValidation]:
    """Validate the trace schema, cells, delivery, follow-up, and replay."""

    return [
        _validate_schema(trace),
        _validate_participants(trace),
        _validate_delivery(trace),
        _validate_followup_step(trace),
        _validate_sequence_execution(trace),
        _validate_boundary(trace),
    ]


def _validate_schema(trace: NetworkSequenceTrace) -> NetworkSequenceTraceValidation:
    if trace.schema_version != 1:
        return _rejected("schema", f"unsupported schema version {trace.schema_version}")
    if trace.artifact_id not in VALID_NETWORK_SEQUENCE_TRACE_ARTIFACT_IDS:
        return _rejected("schema", f"unknown artifact id: {trace.artifact_id}")
    if not trace.boundaries:
        return _rejected("schema", "trace must record semantic boundaries")
    if getattr(network_sequence, trace.sequence_helper, None) is None:
        return _rejected("schema", f"unknown sequence helper: {trace.sequence_helper}")
    return _accepted("schema", "schema version and artifact identity accepted")


def _validate_participants(trace: NetworkSequenceTrace) -> NetworkSequenceTraceValidation:
    missing = []
    for label, cell in (
        ("sender", trace.sender_initial_cell),
        ("recipient", trace.recipient_initial_cell),
        ("recipient-before-followup", trace.expected_recipient_before_followup),
        ("recipient-after-followup", trace.expected_recipient_after_followup),
    ):
        absent = [field for field in REQUIRED_CELL_FIELDS if field not in cell]
        missing.extend(f"{label}.{field}" for field in absent)
    if missing:
        return _rejected("participants", f"missing fields: {', '.join(missing)}")
    if trace.recipient_initial_cell["upstream"] != EMPTY_SIGNAL:
        return _rejected("participants", "recipient initial upstream is not empty")
    if trace.recipient_initial_cell["input"] != EMPTY_SIGNAL:
        return _rejected("participants", "recipient initial input is not empty")
    return _accepted(
        "participants",
        "sender, recipient, and follow-up cells recorded",
    )


def _validate_delivery(trace: NetworkSequenceTrace) -> NetworkSequenceTraceValidation:
    try:
        execution = execute_network_sequence_trace(trace)
    except ValueError as exc:
        return _rejected("delivery", str(exc))

    failures: list[str] = []
    if execution.delivery_status != trace.expected_delivery_status:
        failures.append(f"delivery status mismatch: {execution.delivery_status}")
    if execution.delivered_tuple != trace.expected_delivered_tuple:
        failures.append("delivered tuple mismatch")
    if failures:
        return _rejected("delivery", "; ".join(failures))
    return _accepted("delivery", "recorded delivery matches sequence helper")


def _validate_followup_step(
    trace: NetworkSequenceTrace,
) -> NetworkSequenceTraceValidation:
    try:
        execution = execute_network_sequence_trace(trace)
    except ValueError as exc:
        return _rejected("followup-step", str(exc))

    failures: list[str] = []
    if execution.followup_status != trace.expected_followup_status:
        failures.append(f"followup status mismatch: {execution.followup_status}")
    if execution.recipient_before_followup != trace.expected_recipient_before_followup:
        failures.append("before-followup cell mismatch")
    if execution.recipient_after_followup != trace.expected_recipient_after_followup:
        failures.append("after-followup cell mismatch")
    if not trace.routed_signal_flow:
        failures.append("routed signal flow is empty")
    if failures:
        return _rejected("followup-step", "; ".join(failures))
    return _accepted("followup-step", "recorded follow-up matches execution")


def _validate_sequence_execution(
    trace: NetworkSequenceTrace,
) -> NetworkSequenceTraceValidation:
    try:
        execution = execute_network_sequence_trace(trace)
    except ValueError as exc:
        return _rejected("sequence-execution", str(exc))

    if execution.status != trace.expected_status:
        return _rejected(
            "sequence-execution",
            f"status mismatch: {execution.status}",
        )
    if not execution.accepted:
        return _rejected(
            "sequence-execution",
            f"sequence execution rejected: {execution.detail}",
        )
    return _accepted("sequence-execution", "recorded sequence matches helper execution")


def _validate_boundary(trace: NetworkSequenceTrace) -> NetworkSequenceTraceValidation:
    joined = " ".join(trace.boundaries).lower()
    required_terms = (
        "scheduler",
        "topology",
        "timing",
        "output-clearing",
        "new command semantics",
    )
    missing = [term for term in required_terms if term not in joined]
    if missing:
        return _rejected("boundary", f"missing boundary terms: {', '.join(missing)}")
    return _accepted("boundary", "trace boundaries keep sequence limits explicit")


def _parse_cell_mapping(item: dict[str, Any]) -> dict[str, Any]:
    parsed = dict(item)
    for field in REQUIRED_CELL_FIELDS:
        if field not in parsed:
            raise ValueError(f"cell mapping missing field: {field}")
    for field in ("upstream", "input", "output", "control", "buffer"):
        parsed[field] = list(_required_list(parsed, field))
    return parsed


def _cell_from_mapping(mapping: dict[str, Any]) -> Cell:
    return Cell(
        role=mapping["role"],
        memory=mapping["memory"],
        upstream=tuple(mapping["upstream"]),
        input=tuple(mapping["input"]),
        output=tuple(mapping["output"]),
        automail=mapping["automail"],
        self_mailbox=mapping["self_mailbox"],
        control=tuple(mapping["control"]),
        buffer=tuple(mapping["buffer"]),
    )


def _cell_to_mapping(cell: Cell) -> dict[str, Any]:
    return {
        "role": cell.role,
        "memory": cell.memory,
        "upstream": list(cell.upstream),
        "input": list(cell.input),
        "output": list(cell.output),
        "automail": cell.automail,
        "self_mailbox": cell.self_mailbox,
        "control": list(cell.control),
        "buffer": list(cell.buffer),
    }


def _required_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return value


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be non-empty text")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = _required_list(data, key)
    if not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{key} must be a non-empty list of text")
    return value


def _accepted(subject: str, detail: str) -> NetworkSequenceTraceValidation:
    return NetworkSequenceTraceValidation(subject, True, detail)


def _rejected(subject: str, detail: str) -> NetworkSequenceTraceValidation:
    return NetworkSequenceTraceValidation(subject, False, detail)
