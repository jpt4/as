"""Loader, evaluator, and proof checks for transition-chain claims."""

from __future__ import annotations

import argparse
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


@dataclass(frozen=True)
class ChainClaimProjectValidation:
    """One validation result for the transition-chain claim project surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class ChainClaimProjectReport:
    """Operator-facing validation report for transition-chain claims."""

    language_id: str
    claims_path: Path
    certificates_path: Path
    language_path: Path
    claim_count: int
    certificate_count: int
    results: tuple[ChainClaimProjectValidation, ...]


def load_transition_chain_claims(path: Path | str) -> list[ChainClaim]:
    """Load transition-chain claims from a JSON manifest."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    claims = data.get("claims")
    if not isinstance(claims, list):
        raise ValueError("chain claim manifest must contain a claims list")
    return [_parse_claim(item) for item in claims]


def validate_transition_chain_claim_project(
    claims_path: Path | str = "claims/transition_chain_claims.json",
    certificates_path: Path | str = "claims/transition_chain_proof_certificates.json",
    language_path: Path | str = "language/transition_chain_claim_language.json",
) -> ChainClaimProjectReport:
    """Validate chain claims, certificates, and language as one surface."""

    from autarkic_systems.chain_object_language import (
        load_transition_chain_claim_language,
        validate_chain_claim_surface,
        validate_chain_language_manifest,
    )

    claim_manifest = Path(claims_path)
    certificate_manifest = Path(certificates_path)
    language_manifest = Path(language_path)
    language = load_transition_chain_claim_language(language_manifest)
    claims = load_transition_chain_claims(claim_manifest)
    certificates = _load_chain_certificates(certificate_manifest)

    language_results = validate_chain_language_manifest(language)
    evaluations = evaluate_chain_claim_examples(claims)
    certificate_results = verify_chain_claim_certificates(claims, certificates)
    surface_results = validate_chain_claim_surface(language, claims, certificates)

    results = (
        _summarize_language_results(language_results),
        _summarize_example_results(evaluations),
        _summarize_certificate_results(certificate_results),
        _summarize_surface_results(surface_results, len(claims)),
    )
    return ChainClaimProjectReport(
        language_id=language.language_id,
        claims_path=claim_manifest,
        certificates_path=certificate_manifest,
        language_path=language_manifest,
        claim_count=len(claims),
        certificate_count=len(certificates),
        results=results,
    )


def format_chain_claim_validation_report(report: ChainClaimProjectReport) -> str:
    """Format a concise operator report for chain-claim validation."""

    lines = [f"Transition chain claims: {report.language_id}"]
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def chain_claim_validation_report_payload(
    report: ChainClaimProjectReport,
) -> dict[str, Any]:
    """Return a structured chain-claim validation report payload."""

    return {
        "language_id": report.language_id,
        "accepted": all(result.accepted for result in report.results),
        "claim_count": report.claim_count,
        "certificate_count": report.certificate_count,
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


def run_chain_claim_cli(argv: list[str] | None = None) -> int:
    """Run the transition-chain claim validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.chain_claims",
        description="Validate the AS transition-chain claim surface.",
    )
    parser.add_argument(
        "--claims",
        default="claims/transition_chain_claims.json",
        help="Path to the transition-chain claim manifest.",
    )
    parser.add_argument(
        "--certificates",
        default="claims/transition_chain_proof_certificates.json",
        help="Path to the transition-chain proof certificate manifest.",
    )
    parser.add_argument(
        "--language",
        default="language/transition_chain_claim_language.json",
        help="Path to the transition-chain claim language manifest.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    report = validate_transition_chain_claim_project(
        claims_path=args.claims,
        certificates_path=args.certificates,
        language_path=args.language,
    )
    if args.format == "json":
        print(json.dumps(chain_claim_validation_report_payload(report), sort_keys=True))
    else:
        print(format_chain_claim_validation_report(report))
    return 0 if all(result.accepted for result in report.results) else 1


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


def _load_chain_certificates(path: Path | str) -> list[ClaimCertificate]:
    from autarkic_systems.proof_certificates import load_proof_certificates

    return load_proof_certificates(path)


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


def _project_accepted(
    subject: str,
    detail: str,
) -> ChainClaimProjectValidation:
    return ChainClaimProjectValidation(subject=subject, accepted=True, detail=detail)


def _project_rejected(
    subject: str,
    detail: str,
) -> ChainClaimProjectValidation:
    return ChainClaimProjectValidation(subject=subject, accepted=False, detail=detail)


def _summarize_language_results(results: list[Any]) -> ChainClaimProjectValidation:
    failures = [result.detail for result in results if not result.accepted]
    if failures:
        return _project_rejected(
            "chain-language-manifest",
            "; ".join(failures),
        )
    return _project_accepted(
        "chain-language-manifest",
        f"validated {len(results)} language clauses",
    )


def _summarize_example_results(
    evaluations: list[ChainExampleEvaluation],
) -> ChainClaimProjectValidation:
    failures = [
        f"{evaluation.claim_id}/{evaluation.example_name}: {evaluation.detail}"
        for evaluation in evaluations
        if not evaluation.matched
    ]
    if failures:
        return _project_rejected("chain-examples", " | ".join(failures))
    return _project_accepted(
        "chain-examples",
        f"evaluated {len(evaluations)} examples",
    )


def _summarize_certificate_results(
    results: list[CertificateVerification],
) -> ChainClaimProjectValidation:
    failures = [
        f"{result.claim_id}: {result.detail}" for result in results if not result.accepted
    ]
    if failures:
        return _project_rejected("chain-certificates", " | ".join(failures))
    return _project_accepted(
        "chain-certificates",
        f"verified {len(results)} certificates",
    )


def _summarize_surface_results(
    results: list[Any],
    claim_count: int,
) -> ChainClaimProjectValidation:
    failures = [f"{result.subject}: {result.detail}" for result in results if not result.accepted]
    if failures:
        return _project_rejected("chain-surface", " | ".join(failures))
    return _project_accepted(
        "chain-surface",
        f"validated {claim_count} chain claims",
    )


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


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_chain_claim_cli())
