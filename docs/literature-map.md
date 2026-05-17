# Literature Map

Status: first pass, 2026-05-17.

This map organizes sources by the role they play in Autarkic Systems. It is not
a claim that the literature review is complete. It is a working index for
turning source pressure into ADRs, executable probes, and proof obligations.

## Root And Integration Sources

| Source | Local witness | AS role | Current use |
| --- | --- | --- | --- |
| AS prelude and development rules | `AGENTS.md` | Defines the lower-bound objective: theory, literature organization, novel conceptual contributions, executable artifacts, and hardware schematics/simulation for cognitive sovereignty. | Governs all ADRs and documentation layers. |
| AFS placeholder | `/home/sean/Projects/_upstream/afs/README.md` | Names Autarkic Formal Systems but does not operationalize it. | Forces AS to define AFS requirements locally. |
| AS source manifest | `sources/manifest.json` | Pins the reviewed repository baseline. | Prevents source drift from silently changing conclusions. |

## PRC: Substrate And Embodiment

| Source | Local witness | AS role | Current use |
| --- | --- | --- | --- |
| PRC README | `/home/sean/Projects/_upstream/prc/README.md` | States the embodied-computation argument and the Universal Cell requirements: reversible logic, asynchronous operation, explicit signal/power routing, and organic component-wise reconfigurability. | Basis for AFS-R6 and AFS-R7. |
| GELC universality note | `/home/sean/Projects/_upstream/prc/theory/official/gelc-universality.txt` | Argues that geometrically explicit RLEM circuits can be computationally universal while making wires first-class formal objects. | Supports the decision to model routing as substrate logic, not implementation detail. |
| Universal Cell formal model | `/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt` | Gives the state-machine vocabulary for roles, memory, input, output, automail, control, and buffer. | Source for the fixed-role transition probe. |
| Universal Cell Scheme simulator | `/home/sean/Projects/_upstream/prc/practice/asmsim.scm` | Executable research artifact for UC behavior. | Background only; not yet treated as trusted because first review found rough edges. |
| RALA, Morita RLEM, switchable circulator references | PRC README and GELC note reference sections | Prior art for reconfigurable asynchronous logic, reversible logic elements with memory, and possible physical implementation. | Needed for later hardware/schematic review. |

## SJAS: Formal Confidence

| Source | Local witness | AS role | Current use |
| --- | --- | --- | --- |
| SJAS README | `/home/sean/Projects/_upstream/sjas/README.md` | Defines the self-justifying logic program: consistency relative to PA plus self-provability of consistency under expressivity constraints. | Basis for AFS-R2 through AFS-R5. |
| Willard paper witness archive | `/home/sean/Projects/_upstream/sjas/nachlass/papers/README.md` | Maps many Willard primary texts to local/public witnesses and records gaps. | Primary source index for formal-confidence claims. |
| Works citing Willard archive | `/home/sean/Projects/_upstream/sjas/nachlass/works-citing-dew/README.md` | Maps second-order literature around self-verifying theories, provability of consistency, and AI-adjacent Loebian concerns. | Source for broader significance and related-work review. |
| ISLA notes | `/home/sean/Projects/_upstream/sjas/code/isla/notes.txt` | Records implementation notes for IS(A)/IS-lambda(A), grounding functions, tableaux with equality, and syntax/formula distinctions. | Candidate basis for the first syntax and proof-apparatus ADR. |
| ISLA Racket sketch | `/home/sean/Projects/_upstream/sjas/code/isla/isla.rkt` | Exploratory grammar and grounding-function implementation. | Background for future object-language validators. |
| Theta Clojure/core.logic experiments | `/home/sean/Projects/_upstream/sjas/code/theta/` | Experiments with Willard 2017 theta languages and relational arithmetic. | Background; not yet trusted as a green dependency. |

## Adjacent Proof Apparatus Sources

| Source | Local witness | AS role | Current use |
| --- | --- | --- | --- |
| Proflog public repo | `/home/sean/Projects/_upstream/proflog/proflog.scm` | Candidate Fitting-style semantic-tableaux implementation. | Background only; public main failed the local Guile smoke test and does not expose the newer SJAS ADR-006x frontier. |
| Fitting, "Tableaux for Logic Programming" | `/home/sean/Projects/_upstream/proflog/LPTableaus.pdf` | The immediate source for Proflog's intended proof/refutation apparatus. | Candidate proof-apparatus source for AFS-R3. |
| LeanTAP reference from ISLA notes | External reference in ISLA notes | Candidate transparent tableaux prover direction. | Not yet reviewed in AS; possible future source. |

## Claim-To-Source Map

| AS claim | Source support | Evidence status |
| --- | --- | --- |
| AS must join formal self-confidence to embodied substrate visibility. | AS prelude, PRC README, SJAS README. | Strong enough for roadmap and requirements. |
| AFS cannot currently be delegated to `jpt4/afs`. | AFS placeholder README. | Verified at reviewed commit. |
| Universal Cell routing is a valid first executable substrate slice. | PRC formal model, PRC README, GELC note. | Partially implemented in AS fixed-role probe. |
| Fixed-role transition predicates are only a bridge, not a proof of PRC. | PRC formal model has broader stem/automail/buffer behavior. | Explicit coverage limit in ADR-0004 and ADR-0005. |
| SJAS work requires careful expressivity/proof-apparatus tradeoffs. | SJAS README and Willard witness archive. | Strong enough for AFS requirements; detailed theorem claims still need paper-level annotation. |
| Proflog is relevant but not currently a passing dependency. | SJAS `nachlass/LOG.md`, public Proflog repo, failed Guile run. | Gap recorded in `docs/afs-requirements.md` and `sources/manifest.json`. |

## Evidence Gaps

- The X/Twitter reference in `AGENTS.md` remains uncaptured.
- Willard 1993 and Willard 1997 public full-text witnesses were not available
  in the SJAS paper archive.
- PRC's Scheme simulator and TLA+ sketch need deeper verification before AS
  treats either as canonical.
- The active Proflog ADR-006x frontier described by SJAS logs is not present on
  public Proflog `main`.
- AS has not yet annotated the actual Willard papers at theorem/definition
  granularity; current use is repository-level and README-level.
