"""Loader, evaluator, and proof checks for transition-chain claims."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from autarkic_systems import transition_chain_predicates
from autarkic_systems.proof_certificates import (
    ClaimCertificate,
    CertificateVerification,
    MANIFEST_EXAMPLE_RULE,
)
from autarkic_systems.transition_chains import (
    execute_neighbor_delivery_recipient_chain,
)
from autarkic_systems.universal_cell import Cell


@dataclass(frozen=True)
class ChainClaimExample:
    """One executable example attached to a transition-chain claim."""

    name: str
    expected: bool
    sender: Cell
    recipient: Cell


@dataclass(frozen=True)
class ChainClaim:
    """A manifest claim over a composed transition chain."""

    claim_id: str
    predicate: str
    description: str
    examples: tuple[ChainClaimExample, ...]

    def with_checker(self, checker: str) -> "ChainClaim":
        """Return a copy referencing a different chain predicate checker."""

        return replace(self, predicate=checker)


@dataclass(frozen=True)
class ChainExampleEvaluation:
    """Observed outcome for a transition-chain claim example."""

    claim_id: str
    example_name: str
    expected: bool
    observed: bool
    matched: bool
    detail: str


def load_transition_chain_claims(path: Path | str) -> list[ChainClaim]:
    """Load transition-chain claims from a JSON manifest."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    claims = data.get("claims")
    if not isinstance(claims, list):
        raise ValueError("chain claim manifest must contain a claims list")
    return [_parse_claim(item) for item in claims]


def evaluate_chain_claim_examples(
    claims: Iterable[ChainClaim],
) -> list[ChainExampleEvaluation]:
    """Evaluate every chain example against its predicate checker."""

    evaluations: list[ChainExampleEvaluation] = []
    for claim in claims:
        checker = getattr(transition_chain_predicates, claim.predicate, None)
        if checker is None:
            raise ValueError(f"unknown chain predicate checker: {claim.predicate}")
        for example in claim.examples:
            chain = execute_neighbor_delivery_recipient_chain(
                example.sender,
                example.recipient,
            )
            predicate_result = checker(chain)
            observed = bool(predicate_result.holds)
            evaluations.append(
                ChainExampleEvaluation(
                    claim_id=claim.claim_id,
                    example_name=example.name,
                    expected=example.expected,
                    observed=observed,
                    matched=observed == example.expected,
                    detail=predicate_result.detail,
                )
            )
    return evaluations


def verify_chain_claim_certificates(
    claims: Iterable[ChainClaim],
    certificates: Iterable[ClaimCertificate],
) -> list[CertificateVerification]:
    """Verify manifest-example certificates against transition-chain claims."""

    claim_list = list(claims)
    certificate_list = list(certificates)
    claim_by_id = {claim.claim_id: claim for claim in claim_list}

    results: list[CertificateVerification] = []
    for claim in claim_list:
        matching = [
            certificate
            for certificate in certificate_list
            if certificate.claim_id == claim.claim_id
        ]
        if not matching:
            results.append(_rejected(claim.claim_id, "missing certificate for claim"))
            continue
        if len(matching) > 1:
            results.append(_rejected(claim.claim_id, "duplicate certificates for claim"))
            continue
        results.append(_verify_certificate(claim, matching[0]))

    for certificate in certificate_list:
        if certificate.claim_id not in claim_by_id:
            results.append(
                _rejected(
                    certificate.claim_id,
                    "unknown claim in certificate manifest",
                )
            )

    return results


def _verify_certificate(
    claim: ChainClaim,
    certificate: ClaimCertificate,
) -> CertificateVerification:
    example_by_name = {example.name: example for example in claim.examples}
    step_names = [step.example for step in certificate.steps]
    step_name_set = set(step_names)
    example_name_set = set(example_by_name)

    if not certificate.steps:
        return _rejected(claim.claim_id, "certificate has no steps")
    if len(step_names) != len(step_name_set):
        return _rejected(claim.claim_id, "duplicate example steps in certificate")

    unknown_examples = sorted(step_name_set - example_name_set)
    if unknown_examples:
        return _rejected(
            claim.claim_id,
            f"unknown examples in certificate: {', '.join(unknown_examples)}",
        )

    missing_examples = sorted(example_name_set - step_name_set)
    if missing_examples:
        return _rejected(
            claim.claim_id,
            f"missing examples in certificate: {', '.join(missing_examples)}",
        )

    checker = getattr(transition_chain_predicates, claim.predicate, None)
    if checker is None:
        return _rejected(
            claim.claim_id,
            f"unknown chain predicate checker: {claim.predicate}",
        )

    for step in certificate.steps:
        if step.rule != MANIFEST_EXAMPLE_RULE:
            return _rejected(claim.claim_id, f"unknown certificate rule: {step.rule}")
        example = example_by_name[step.example]
        if step.expected != example.expected:
            return _rejected(
                claim.claim_id,
                "expectation mismatch for "
                f"{step.example}: certificate expected {step.expected}, "
                f"manifest expected {example.expected}",
            )

        chain = execute_neighbor_delivery_recipient_chain(
            example.sender,
            example.recipient,
        )
        predicate_result = checker(chain)
        observed = bool(predicate_result.holds)
        if observed != example.expected:
            return _rejected(
                claim.claim_id,
                "predicate mismatch for "
                f"{step.example}: observed {observed}, "
                f"expected {example.expected}",
            )

    return CertificateVerification(
        claim_id=claim.claim_id,
        accepted=True,
        detail=f"verified {len(certificate.steps)} manifest-example steps",
    )


def _parse_claim(item: dict[str, Any]) -> ChainClaim:
    examples = item.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError(f"chain claim {item.get('id')!r} must define examples")
    return ChainClaim(
        claim_id=_required_text(item, "id"),
        predicate=_required_text(item, "predicate"),
        description=_required_text(item, "description"),
        examples=tuple(_parse_example(example) for example in examples),
    )


def _parse_example(item: dict[str, Any]) -> ChainClaimExample:
    return ChainClaimExample(
        name=_required_text(item, "name"),
        expected=_required_bool(item, "expected"),
        sender=_parse_cell(item["sender"]),
        recipient=_parse_cell(item["recipient"]),
    )


def _parse_cell(item: dict[str, Any]) -> Cell:
    return Cell(
        role=_required_text(item, "role"),
        memory=_required_text(item, "memory"),
        upstream=_parse_signal(item.get("upstream", ["_", "_", "_"])),
        input=_parse_signal(item.get("input", ["_", "_", "_"])),
        output=_parse_signal(item.get("output", ["_", "_", "_"])),
        automail=item.get("automail", "_"),
        self_mailbox=item.get("self_mailbox", "_"),
        control=tuple(item.get("control", [])),
        buffer=tuple(item.get("buffer", [])),
    )


def _parse_signal(value: list[Any]) -> tuple[Any, Any, Any]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("signal must be a three-item list")
    return tuple(value)


def _rejected(claim_id: str, detail: str) -> CertificateVerification:
    return CertificateVerification(claim_id=claim_id, accepted=False, detail=detail)


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_bool(item: dict[str, Any], key: str) -> bool:
    value = item.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"required boolean field missing: {key}")
    return value
