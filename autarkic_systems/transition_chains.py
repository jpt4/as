"""Small executable chains that compose existing Universal Cell transitions."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from autarkic_systems.universal_cell import Cell, StepResult, step_fixed_cell, step_stem_cell


ChainStatus = Literal[
    "neighbor-delivery-consumed",
    "sender-not-delivered",
    "recipient-not-ready",
    "recipient-not-consumed",
]

EMPTY = ("_", "_", "_")
NEIGHBOR_DELIVERY_STATUS = "stem-command-buffer-neighbor-delivered"
RECIPIENT_CONSUMED_STATUS = "recipient-init-command-message-processed"


@dataclass(frozen=True)
class NeighborDeliveryRecipientChain:
    """Result of composing one neighbor delivery with one recipient step."""

    status: ChainStatus
    accepted: bool
    sender_result: StepResult
    recipient_before: Cell | None
    recipient_result: StepResult | None
    detail: str


def execute_neighbor_delivery_recipient_chain(
    sender: Cell,
    recipient: Cell,
) -> NeighborDeliveryRecipientChain:
    """Deliver one sender output tuple into a recipient's upstream tuple.

    This is intentionally not a general multi-cell simulator. It only composes
    the already implemented stem neighbor-delivery transition with the already
    implemented recipient init-family command-message transition. The recipient
    must have empty direct input and upstream channels so the chain cannot
    overwrite pending state.
    """

    sender_result = step_stem_cell(sender)
    if sender_result.status != NEIGHBOR_DELIVERY_STATUS:
        return NeighborDeliveryRecipientChain(
            status="sender-not-delivered",
            accepted=False,
            sender_result=sender_result,
            recipient_before=None,
            recipient_result=None,
            detail=(
                "sender must produce "
                f"{NEIGHBOR_DELIVERY_STATUS}, got {sender_result.status}"
            ),
        )

    if recipient.input != EMPTY or recipient.upstream != EMPTY:
        return NeighborDeliveryRecipientChain(
            status="recipient-not-ready",
            accepted=False,
            sender_result=sender_result,
            recipient_before=None,
            recipient_result=None,
            detail="recipient input/upstream must be empty before delivery",
        )

    recipient_before = replace(recipient, upstream=sender_result.cell.output)
    recipient_result = _step_recipient(recipient_before)
    if recipient_result.status != RECIPIENT_CONSUMED_STATUS:
        return NeighborDeliveryRecipientChain(
            status="recipient-not-consumed",
            accepted=False,
            sender_result=sender_result,
            recipient_before=recipient_before,
            recipient_result=recipient_result,
            detail=(
                "recipient must produce "
                f"{RECIPIENT_CONSUMED_STATUS}, got {recipient_result.status}"
            ),
        )

    return NeighborDeliveryRecipientChain(
        status="neighbor-delivery-consumed",
        accepted=True,
        sender_result=sender_result,
        recipient_before=recipient_before,
        recipient_result=recipient_result,
        detail="neighbor delivery output was consumed by recipient init logic",
    )


def _step_recipient(cell: Cell) -> StepResult:
    """Run the appropriate existing single-cell transition for a recipient."""

    if cell.role == "stem":
        return step_stem_cell(cell)
    return step_fixed_cell(cell)
