# Historical fork documentation

On **`culled-main`**, many markdown files under `docs/` were written during the
Sean fork integration line (ADR-0004 through ADR-0264). They remain as **design
and status context**; they are not all backed by current Python modules or
evidence registries on this branch.

## How to use this list

| Status | Meaning |
|--------|---------|
| **Active** | Still matches culled-main code or JSON sources. |
| **Partial** | Topic survives in slim form (e.g. one chain bundle, merged gaps file). |
| **Archive-only** | Describes code removed on cull; see `archive/sean-fork-full`. |
| **Superseded** | SJAS topic moved to Proflog; see [sjas-proflog-crosswalk.md](sjas-proflog-crosswalk.md). |

## Per-file status

| Document | Status | Notes |
|----------|--------|-------|
| `transition-claim-language.md` | Active | Matches `language/transition_claim_language.json`. |
| `prc-hardware-witness-map.md` | Active | Matches `sources/prc_hardware_witness_map.json`. |
| `willard-definition-map.md` | Active | Matches `sources/willard_definition_map.json`. |
| `stem-command-buffer-map.md` | Active | Matches `sources/stem_command_buffer_map.json`. |
| `proof-apparatus-options.md` | Active | Updated for Proflog pin. |
| `proflog-frontier-status.md` | Active | Matches `sources/proflog_frontier_status.json`. |
| `sjas-proflog-crosswalk.md` | Active | Current SJAS integration. |
| `afs-requirements.md` | Partial | Matrix references archive ADRs; boundary is `claims/formal_confidence_boundary.json`. |
| `source-manifest.md` | Partial | See `sources/manifest.json`; Proflog now authoritative. |
| `subordinate-review.md` | Partial | Snapshot review; use manifest + guide for current pins. |
| `literature-map.md` | Partial | Bibliography index; some tool paths refer to removed modules. |
| `open-problems.md` | Active | Maintained; P6 closed. |
| `roadmap.md` | Active | Near-term priorities. |
| `glossary.md` | Active | General terms. |
| `project-charter.md` | Active | Charter unchanged in intent. |
| `write-buffer-command-semantics-status.md` | Partial | UC write-buffer still in code; per-ADR status JSON merged into `command_semantics_gaps.json`. |
| `standard-signal-command-semantics-status.md` | Partial | Open gap; see command_semantics_gaps. |
| `standard-signal-source-review-status.md` | Archive-only | Source status JSON removed from culled tree. |
| `stem-command-execution-source-status.md` | Archive-only | Merged into command_semantics_gaps. |
| `stem-buffer-accumulation.md` | Partial | Stem buffer logic in UC; dedicated evidence bundles culled. |
| `recipient-init-command-message-consumption.md` | Partial | Exemplar bundle retained. |
| `recipient-non-init-command-source-status.md` | Archive-only | |
| `recipient-command-consumption-source-status.md` | Archive-only | |
| `self-command-buffer-init-dispatch.md` | Archive-only | Many self/neighbor slices culled from evidence registry. |
| `multi-command-recipient-input-policy-status.md` | Archive-only | |
| `guile-asmsim-command-semantics-status.md` | Archive-only | |
| `asmsim-process-buffer-status.md` | Archive-only | |
| `official-tla-universal-cell-status.md` | Archive-only | TLA non-authority unchanged in intent. |
| `post-handoff-signal-witness.md` | Archive-only | Network-sequence demos removed. |
| `two-cell-network-witness.md` | Archive-only | |
| `vertical-demo-digest.md` | Archive-only | `vertical_demo` removed. |

When a doc disagrees with `culled-main` code, trust **code, JSON claims, and
active ADRs 0001–0002** first, then this table, then the historical markdown.
