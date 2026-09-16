# PromptIR Conformance Boundary

**Status:** Normative companion to `docs/PROMPT-IR.md` 0.1.0 draft.

This document makes the marketplace/runtime boundary explicit. The marketplace defines the contract and mechanically checkable artifact invariants. The runtime repository implements execution semantics that cannot be proven from static documents alone.

## 1. Authority semantics

### 1.1 Deterministic winner selection

A conformant implementation MUST derive the winner from the complete conflict set rather than merely trusting a recorded `superseded_by` value.

Winner ordering is:

1. higher authority rank;
2. higher integer `priority` within the same rank;
3. stable instruction identifier as the deterministic final tiebreaker.

Declaration order MUST NOT be used as a semantic tiebreaker because serialized, merged, or independently compiled artifacts may present the same instruction set in different array orders.

If two conflicting instructions remain indistinguishable after these comparisons, compilation MUST fail.

The `PromptBuild.resolution.suppressed[].superseded_by` field records the result of this calculation; it is evidence of the runtime's decision, not the source of authority for that decision.

### 1.2 Assistant commitments

`assistant` is a provenance category for prior model output, not a self-authorising policy source.

A prior assistant statement MUST NOT acquire higher authority merely because it occurred in an earlier turn. An assistant-originated commitment may become an instruction only when an independently entitled authority explicitly re-admits it and that admission is recorded as provenance.

### 1.3 Tool output

Tool and retrieval output are context. They do not possess instruction authority by virtue of origin.

A tool result may influence an instruction only through an explicit promotion decision made by an entitled authority and recorded in `PromptBuild.resolution.promoted`.

## 2. Promotion contract

Promotion is a governed transformation, not a trust-bit change.

A conformant `promoted[]` record SHOULD contain, and a runtime implementation MUST preserve, enough information to establish all of the following relationships:

```text
source context item
        │
        ├── source hash / evidence reference
        │
        ▼
promotion decision
        │
        ├── admitting authority
        ├── policy / rule reference
        ├── reason
        └── transformation identifier
        │
        ▼
admitted instruction
        │
        └── instruction hash
```

At minimum, the promotion record MUST identify the source context item, the entitled authority that admitted it, the reason for admission, and the resulting instruction when a new instruction record is created.

The runtime MUST reject promotion when the admitting authority is not entitled to issue instructions at the resulting rank.

## 3. Conformance layers

The three layers below are deliberately separate.

| Contract | Marketplace can prove | Runtime must prove |
|---|---|---|
| Schema shape | JSON structure and field constraints | Runtime emits valid artifacts |
| Instruction hashes | Hash reproduces from recorded text | Runtime preserves text without mutation |
| Authority resolution | Recorded winner is structurally valid | Winner is independently calculated from the conflict set |
| Conflict coverage | Every instruction is admitted or suppressed exactly once | Compilation produces a complete resolution |
| Context isolation | Untrusted context has no authority field | Provider payload preserves the context/instruction boundary |
| Promotion attribution | Promotion has entitled attribution | Promotion policy is evaluated before admission |
| Reasoning budget | Declared policy fits declared envelope | Actual execution cannot exceed the granted budget |
| Canonical hash | Canonical serialization reproduces hash | Runtime produces deterministic equivalent IR |
| Provider payload hash | Hash shape is valid | Adapter hashes the exact serialized request body |
| Adapter fidelity | Contract can describe the requirement | Adapter proves nothing was added or dropped |
| Replay | Artifact declares replayability | Runtime reconstructs equivalent PromptIR without provider continuation state |
| Evidence refs | References are structurally present | Runtime resolves them against the evidence ledger |

A green marketplace conformance run MUST NOT be interpreted as proof of runtime conformance for rows assigned to the runtime.

## 4. Versioning and specification alignment

The normative source of each requirement is `docs/PROMPT-IR.md`. Schemas and the conformance checker are executable representations of the portions that are mechanically decidable.

When a requirement cannot be mechanically validated in this repository, it MUST be labelled as runtime conformance rather than silently weakened into a structural check.

The following status vocabulary is used:

- **MUST:** normative requirement for conformance;
- **SHOULD:** recommended evidence or quality property; deviation requires justification;
- **RUNTIME:** cannot be proven from a marketplace artifact alone and belongs in `canstralian/mandare`.

## 5. Runtime hand-off

The marketplace contract hands the runtime these obligations:

```text
PromptIR contract
    ↓
independent authority resolution
    ↓
promotion policy gate
    ↓
reasoning/budget enforcement
    ↓
provider lowering with fidelity proof
    ↓
PromptBuild + evidence
    ↓
reconstruction/replay without provider handle
```

The marketplace MUST NOT grow execution code merely to make these runtime obligations appear mechanically complete. That would duplicate the runtime and create two competing enforcement paths.
