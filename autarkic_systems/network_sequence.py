"""Post-handoff network sequence witnesses over existing UC transitions.

This module records one narrow durability check for the two-cell witness: after
an init-family neighbor delivery reconfigures the recipient, the recipient can
process a later binary signal through the already implemented fixed-cell
transition. It does not add scheduler, timing, topology, or output-clearing
semantics.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, replace
from typing import Any, Literal

from autarkic_systems.network_witness import (
    TwoCellNetworkWitness,
    execute_two_cell_neighbor_delivery_witness,
    two_cell_network_witness_payload,
)
from autarkic_systems.universal_cell import (
    Cell,
    Signal,
    StepResult,
    step_fixed_cell,
    step_stem_cell,
)


SequenceStatus = Literal[
    "post-handoff-signal-routed",
    "handoff-not-init-consumed",
    "followup-not-routed",
]

DEFAULT_FOLLOWUP_INPUT: tuple[Signal, Signal, Signal] = (1, 0, 0)


@dataclass(frozen=True)
class PostHandoffSignalWitness:
    """A follow-up signal witness after an accepted init delivery."""

    status: SequenceStatus
    accepted: bool
    delivery_witness: TwoCellNetworkWitness
    followup_input: tuple[Signal, Signal, Signal]
    recipient_before_followup: Cell | None
    followup_result: StepResult | None
    detail: str

    @property
    def recipient_after_followup(self) -> Cell | None:
        """Recipient state after the follow-up step, if one ran."""

        if self.followup_result is None:
            return None
        return self.followup_result.cell


def execute_post_handoff_signal_witness(
    sender: Cell,
    recipient: Cell,
    *,
    followup_input: tuple[Signal, Signal, Signal] = DEFAULT_FOLLOWUP_INPUT,
) -> PostHandoffSignalWitness:
    """Execute a delivery witness followed by one recipient signal step."""

    delivery = execute_two_cell_neighbor_delivery_witness(sender, recipient)
    if not _is_init_delivery(delivery):
        return PostHandoffSignalWitness(
            status="handoff-not-init-consumed",
            accepted=False,
            delivery_witness=delivery,
            followup_input=followup_input,
            recipient_before_followup=None,
            followup_result=None,
            detail=(
                "delivery must be an accepted init-family recipient command "
                f"handoff, got {delivery.status}"
            ),
        )

    recipient_before_followup = replace(
        delivery.recipient_after,
        input=followup_input,
    )
    followup_result = _step_recipient(recipient_before_followup)
    if followup_result.status != "routed":
        return PostHandoffSignalWitness(
            status="followup-not-routed",
            accepted=False,
            delivery_witness=delivery,
            followup_input=followup_input,
            recipient_before_followup=recipient_before_followup,
            followup_result=followup_result,
            detail=(
                "follow-up input must route through the recipient, got "
                f"{followup_result.status}"
            ),
        )

    return PostHandoffSignalWitness(
        status="post-handoff-signal-routed",
        accepted=True,
        delivery_witness=delivery,
        followup_input=followup_input,
        recipient_before_followup=recipient_before_followup,
        followup_result=followup_result,
        detail="accepted init handoff changed recipient behavior for follow-up input",
    )


def post_handoff_signal_witness_payload(
    witness: PostHandoffSignalWitness,
) -> dict[str, Any]:
    """Return a JSON-serializable post-handoff witness payload."""

    return {
        "schema_version": 1,
        "sequence_id": "post-handoff-signal-witness",
        "status": witness.status,
        "accepted": witness.accepted,
        "detail": witness.detail,
        "delivery": two_cell_network_witness_payload(witness.delivery_witness),
        "followup_input": list(witness.followup_input),
        "followup_status": (
            witness.followup_result.status
            if witness.followup_result is not None
            else None
        ),
        "recipient": {
            "before_followup": _optional_cell_payload(
                witness.recipient_before_followup
            ),
            "after_followup": _optional_cell_payload(
                witness.recipient_after_followup
            ),
        },
    }


def format_post_handoff_signal_witness(
    witness: PostHandoffSignalWitness,
) -> str:
    """Format a compact text report for the post-handoff witness."""

    followup_status = (
        witness.followup_result.status if witness.followup_result is not None else "none"
    )
    lines = [
        f"Post-handoff signal witness: {witness.status}",
        f"Accepted: {'yes' if witness.accepted else 'no'}",
        f"Delivery: {witness.delivery_witness.status}",
        f"Follow-up input: {_format_signal_tuple(witness.followup_input)}",
        f"Follow-up status: {followup_status}",
        f"Detail: {witness.detail}",
    ]
    if witness.recipient_before_followup is not None:
        lines.append(
            "Recipient before follow-up: "
            + _format_cell_summary(witness.recipient_before_followup)
        )
    if witness.recipient_after_followup is not None:
        lines.append(
            "Recipient after follow-up: "
            + _format_cell_summary(witness.recipient_after_followup)
        )
    return "\n".join(lines)


def run_network_sequence_cli(argv: list[str] | None = None) -> int:
    """Run the post-handoff signal witness command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.network_sequence",
        description="Render a post-handoff recipient signal witness.",
    )
    parser.add_argument(
        "--case",
        choices=tuple(_FIXTURE_CASES),
        default="init-followup-routed",
        help="Named fixture case to execute.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    args = parser.parse_args(argv)

    sender, recipient, followup_input = _fixture_inputs(args.case)
    witness = execute_post_handoff_signal_witness(
        sender,
        recipient,
        followup_input=followup_input,
    )
    if args.format == "json":
        print(json.dumps(post_handoff_signal_witness_payload(witness), sort_keys=True))
    else:
        print(format_post_handoff_signal_witness(witness))
    return 0 if witness.accepted else 1


def _is_init_delivery(witness: TwoCellNetworkWitness) -> bool:
    return (
        witness.accepted
        and witness.recipient_result is not None
        and witness.recipient_result.status == "recipient-init-command-message-processed"
    )


def _step_recipient(cell: Cell) -> StepResult:
    if cell.role == "stem":
        return step_stem_cell(cell)
    return step_fixed_cell(cell)


def _cell_payload(cell: Cell) -> dict[str, Any]:
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


def _optional_cell_payload(cell: Cell | None) -> dict[str, Any] | None:
    if cell is None:
        return None
    return _cell_payload(cell)


def _format_signal_tuple(signal: tuple[Signal, ...]) -> str:
    return ", ".join(str(channel) for channel in signal)


def _format_cell_summary(cell: Cell) -> str:
    return (
        f"role={cell.role} memory={cell.memory} "
        f"upstream={_format_signal_tuple(cell.upstream)} "
        f"input={_format_signal_tuple(cell.input)} "
        f"output={_format_signal_tuple(cell.output)} "
        f"buffer={_format_signal_tuple(cell.buffer)}"
    )


def _init_followup_routed_fixture() -> tuple[Cell, Cell, tuple[Signal, Signal, Signal]]:
    return (
        Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        ),
        Cell(role="wire", memory="right"),
        DEFAULT_FOLLOWUP_INPUT,
    )


def _write_buffer_handoff_not_init_fixture() -> tuple[
    Cell,
    Cell,
    tuple[Signal, Signal, Signal],
]:
    return (
        Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 1, 1),
        ),
        Cell(role="wire", memory="right"),
        DEFAULT_FOLLOWUP_INPUT,
    )


def _malformed_followup_rejected_fixture() -> tuple[
    Cell,
    Cell,
    tuple[Signal, Signal, Signal],
]:
    return (
        Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        ),
        Cell(role="wire", memory="right"),
        ("standard-signal", "_", "_"),
    )


def _fixture_inputs(case: str) -> tuple[Cell, Cell, tuple[Signal, Signal, Signal]]:
    try:
        return _FIXTURE_CASES[case]()
    except KeyError as exc:
        raise ValueError(f"unknown post-handoff witness fixture case: {case!r}") from exc


_FIXTURE_CASES = {
    "init-followup-routed": _init_followup_routed_fixture,
    "write-buffer-handoff-not-init": _write_buffer_handoff_not_init_fixture,
    "malformed-followup-rejected": _malformed_followup_rejected_fixture,
}


if __name__ == "__main__":
    raise SystemExit(run_network_sequence_cli())
