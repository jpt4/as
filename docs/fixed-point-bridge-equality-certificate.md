# Fixed-Point Bridge Equality Certificate

ADR-0300 adds finite certificate support for the fixed-point
`bridge-equality-proof` construction case.

The checked manifest is
`claims/fixed_point_bridge_equality_certificate.json`; the validator is
`autarkic_systems.fixed_point_bridge_equality_certificate`.

The surface derives one accepted certificate support object from the existing
fixed-point equation bridge, bridge-equality alignment, bridge-equality
evaluation, and codebook surfaces. Its checked steps are:

- `decode-left-formula`;
- `decode-self-argument`;
- `evaluate-substitution-code`;
- `match-witness-output`;
- `match-right-quote`; and
- `bridge-equation-formed`.

The certificate records the 4815-token bridge equation and the 296-token
evaluated output already checked by the evaluation surface. It is intentionally
non-promotional: it does not prove bridge equality, a fixed-point equation, an
arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.fixed_point_bridge_equality_certificate
python -m autarkic_systems.fixed_point_bridge_equality_certificate --format json
```
