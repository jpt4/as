# Source Manifest

The machine-readable manifest is [`sources/manifest.json`](../sources/manifest.json).

It records repositories that define the AS working context:

| ID | Role on culled main |
|----|---------------------|
| `as` | Root integration repository |
| `afs` | Named formal-systems layer (public repo placeholder) |
| `prc` | Substrate archive; UC slice implemented in AS |
| `sjas` | Logic program and literature |
| `proflog` | **Authoritative** SJAS implementation (pinned) |
| `leantap` | Transparency reference only (ADR-0010) |

## Authoritative Proflog

SJAS executable frontier is **autarkenterprises/proflog**, not `jpt4/proflog` main.
Pin: `sources/proflog_pin.json`. Witness: `claims/proflog_sjas_witness.json`.
Details: [proflog-frontier-status.md](proflog-frontier-status.md),
[sjas-proflog-crosswalk.md](sjas-proflog-crosswalk.md).

## Verification

```sh
jq -e . sources/manifest.json
python3 -m autarkic_systems.proflog_integration
```

Optional local clone check (set your paths):

```sh
export AS_PROFLOG_ROOT=/tmp/proflog-ae
git -C "$AS_PROFLOG_ROOT" rev-parse HEAD   # expect pin from proflog_pin.json
python3 -m autarkic_systems.proflog_integration --run-fast
```

## Notes

- Manifest `reviewed_commit` for `as` records a baseline before manifest edits;
  exact HEAD equality is not expected after each commit.
- Use environment variables (`AS_PROFLOG_ROOT`) for local Proflog paths—not
  hard-coded developer home directories.
- Legacy per-topic `sources/*_source_status.json` files from the fork were
  merged or removed on cull; see `sources/command_semantics_gaps.json`.

See also [guide.md](guide.md) and [correlation/subordinate-manifest.json](correlation/subordinate-manifest.json).
