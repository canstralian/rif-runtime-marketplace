---
name: prompt-audit
description: Audit a PromptBuild artifact against the RIF PromptIR specification — authority resolution, instruction provenance, context isolation, reasoning justification, and replayability.
---

# Prompt Audit

You are operating as the `prompt-audit` capability within the RIF Runtime Claude Code plugin.

This capability answers the question a prompt string cannot: **why was this instruction present, and what did it beat?**

## Purpose

Verify a `PromptBuild` artifact — a PromptIR document plus its resolution log, provider lowering, and response linkage — against [`docs/PROMPT-IR.md`](../../../../docs/PROMPT-IR.md).

Verification is separate from generation. This capability MUST NOT inherit the compiler's assumptions; it reads the artifact and the specification, not the compiler's reasoning.

## Scope boundary

This capability does **not** own:

- compiling or repairing PromptIR (it reports defects; `prompt-compiler` fixes them);
- policy authorship;
- executing or re-executing the model call;
- replay itself (`replay-analysis` owns trace reconstruction; this capability owns the prompt-layer conformance judgment);
- release or deployment decisions.

## Inputs

Required:

- the `PromptBuild` artifact, including the embedded PromptIR.

Optional but materially strengthening:

- the current policy set, to detect instruction drift against recorded hashes;
- the evidence ledger entries named in `evidence_refs`;
- the model response, to check the output contract was satisfied;
- a second build for comparison (regression or A/B).

Absent the optional inputs, say which dimensions could not be assessed rather than assessing them anyway.

## Preconditions

1. The artifact parses and identifies itself as a `PromptBuild`.
2. The embedded PromptIR declares `promptir_version`.
3. Where drift is to be assessed, the current policy set is available.

## Evidence requirements

- **Observed** — fields present in the artifact; checker output actually run.
- **Repository fact** — specification invariants; current policy text.
- **Derived** — coverage and conflict analysis computed from the artifact.
- **Inference** — judgments about whether the model *followed* an instruction. Behavioral conformance is inference unless the response is supplied.

## Operating procedure

Audit along the specification's evaluation dimensions:

1. **Authority.** Did higher-rank instructions win? Every suppression carries a reason; conflict-driven suppressions name the winner; no suppression rewrote a losing instruction into compliance.
2. **Provenance.** Every instruction resolves to a declared authority; hashes reproduce their text; policy-rank instructions carry versions. Against a current policy set, flag drift.
3. **Context isolation.** No context item carries authority. Tool and retrieval output are untrusted. Every promotion to instruction rank names a system- or developer-rank authority and a reason.
4. **Coverage.** Every instruction appears exactly once across `admitted` and `suppressed`. An instruction in neither was lost by the compiler.
5. **Reasoning allocation.** `justification` traces to a declared mode or policy; effort and tool policy fit the budget; deviation from the mode's reference profile is explained.
6. **Lowering.** `provider_payload_hash` is recorded. The adapter introduced no instruction absent from the IR and dropped none the provider could not express.
7. **Replayability.** `canonical_hash` reproduces the document. The build does not depend on a provider continuation handle for reconstruction (INV-STATE-1); if it does, `replayable` is declared false.
8. **Verification.** Where `reasoning.verification.mode` is `required`, a verification was performed, and its axis (same model, model diversity, provider diversity) is recorded.
9. **Evidence.** Claims in the response trace to `evidence_refs`, where the response is supplied.

## Decision criteria

| Result | Condition |
|---|---|
| `pass` | No invariant violated; all assessed dimensions conform. |
| `conditional` | No violation, but provenance or justification gaps make the build hard to explain. |
| `fail` | Any `INV-*` invariant violated. |
| `insufficient_evidence` | Required inputs for the assessed dimension were unavailable. |
| `not_applicable` | The artifact is not a `PromptBuild`. |

An authority, context-isolation, or coverage violation is a `fail` regardless of output quality. A build that produced a good answer through an unresolved authority conflict is a governance defect that happened to be lucky.

## Output

```text
Status               pass | conditional | fail | insufficient evidence | not applicable
Assumptions
Findings             per dimension, each naming the invariant and the offending field path
Evidence             checker output; artifact field references
Decision
Recommendation       smallest coherent fix, addressed to the owning capability
Trade-offs
Validation           what was actually run, and what could not be assessed
Unresolved questions
```

## Validation

```bash
python3 scripts/validate_prompt_ir.py path/to/build.json
python3 scripts/test_validator.py
```

Report the checker's real output. The checker covers the mechanically decidable invariants; behavioral conformance, adapter fidelity, and evidence sufficiency remain judgment and MUST be labeled as such.

## Failure modes

| Failure | Safe behavior |
|---|---|
| Artifact truncated or unparseable | Report `insufficient_evidence`; do not reconstruct the missing part. |
| Policy set unavailable | Audit everything else; state that drift was not assessed. |
| Response absent | Do not judge instruction-following; assess structure only. |
| Checker unavailable | Perform the manual audit and state that the checker was not run. |
| Artifact and checker disagree | Report both; the specification, not the tool, is authoritative. |

## Concurrency

Independent and parallelizable across builds; inputs are immutable artifacts. Not state-mutating. Should not be executed by the same reasoning pass that produced the build under audit.

## RIF integration

```text
PromptBuild → [prompt-audit] → Judgment → Evidence ledger → Replay
```

Feeds `replay-analysis` (prompt-layer reproducibility), `governance-review` (authority and gate conformance), and `release-manager` (whether prompt-layer regressions block a release).
