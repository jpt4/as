# Fork distillation and correlation

Records the review of the long-running fork at
[Sean-Kenneth-Doherty/as](https://github.com/Sean-Kenneth-Doherty/as), blocked from
upstream push per [jpt4/as#1](https://github.com/jpt4/as/issues/1).

| Document | Purpose |
|----------|---------|
| [fork-correlation.md](fork-correlation.md) | Human-readable report: keep, correct, correlate, elide |
| [../correlation/subordinate-manifest.json](../correlation/subordinate-manifest.json) | Machine-readable correlation index |
| [../correlation/sean-fork-sjas-proflog-map.json](../correlation/sean-fork-sjas-proflog-map.json) | Sean fork SJAS → Proflog translation map |
| [../guide.md](../guide.md) | **Current** reader onboarding (post-cull) |

## Outcome

- **Archive:** `archive/sean-fork-full` preserves the full fork (264 ADRs).
- **Integration:** `culled-main` applies the hard cull (ADR-0001) and Proflog
  integration (ADR-0002).
- **Historical branch:** `distill/fork-correlation` may exist from earlier work;
  treat `culled-main` as the integration baseline.

Revisit when the fork advances or when merging `culled-main` to `main`.
