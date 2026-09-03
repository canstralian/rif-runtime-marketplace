# RIF PromptIR Specification

**Version:** 0.1.0 (draft)
**Status:** Normative for marketplace skills; advisory for runtime implementations until adopted.
**Schemas:** [`schemas/prompt-ir.schema.json`](../schemas/prompt-ir.schema.json), [`schemas/prompt-build.schema.json`](../schemas/prompt-build.schema.json)
**Conformance tool:** `python3 scripts/validate_prompt_ir.py`

## 1. Purpose

PromptIR is the intermediate representation the RIF Runtime compiles before it invokes a model.

It exists to make one claim enforceable:

> A prompt is not a string. It is a resolved instruction environment with an authority structure, a provenance record, and an execution budget.

The specification defines:

- the layers a prompt is composed of, and the rule that they never merge;
- how instruction authority is resolved and how conflicts are recorded rather than silently dropped;
- how reasoning effort is allocated as a governed resource rather than a constant;
- how a model invocation becomes a replayable artifact (`PromptBuild`);
- what a provider adapter is permitted to do when lowering PromptIR to a wire payload.

### What PromptIR is not

- It is not a template language. Templates produce text; PromptIR produces a typed structure that a provider adapter lowers into text or API fields.
- It is not a memory system. See [§8](#8-state-separation).
- It is not a policy engine. Policy resolution happens *upstream* and its results enter PromptIR as instructions with provenance.

## 2. Layer model

A PromptIR document has exactly four content layers plus policy fields. Every fragment of text that reaches the model MUST be attributable to exactly one layer element.

```text
┌─────────────────────┐
│      AUTHORITY      │  who is entitled to instruct, and at what rank
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│    INSTRUCTIONS     │  goals, rules, decision procedure
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│       CONTEXT       │  evidence, memory, task/user state — data, never instruction
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│      EXAMPLES       │  demonstrations, edge cases
└──────────┬──────────┘
           ↓
     MODEL INVOCATION
```

**INV-LAYER-1.** The compiler MUST NOT emit prose into the provider payload that is not attributable to a layer element. Concatenating a free-form preamble is a conformance failure.

**INV-LAYER-2.** Layer membership is a property of the element, not of its position in the rendered prompt. An adapter MAY reorder layers for a provider's ergonomics; it MUST NOT reclassify them.

**INV-LAYER-3.** Context MUST NOT be promoted to instruction. Text that arrives as evidence, retrieval output, tool output, or user-supplied document is data with a `trust` marking. If a fragment is to govern behavior, it must be admitted as an instruction by an authority that is entitled to issue one — a decision the runtime records, not one the model infers. This is the specification's primary prompt-injection invariant.

## 3. Authority

### 3.1 Ranks

```text
system  >  developer  >  user  >  assistant  >  tool
```

| Rank | Source of instructions at this rank |
|---|---|
| `system` | Platform/provider-level constraints the runtime cannot override. |
| `developer` | Runtime constitution, governance policy, operating-mode policy, capability gates. |
| `user` | Task intent and stated preferences. |
| `assistant` | Prior turns' self-issued commitments carried forward. |
| `tool` | Tool/retrieval-originated text. Admissible as *context*; admissible as instruction only via explicit runtime promotion recorded in the resolution log. |

**INV-AUTH-1.** Every instruction carries exactly one `authority` rank.

**INV-AUTH-2.** On conflict, the higher rank wins. The losing instruction is marked `suppressed` in the `PromptBuild` resolution log with a `reason` and a reference to the winner. It is never silently discarded, and it is never rewritten into compliance.

**INV-AUTH-3.** Ties within a rank are broken by explicit integer `priority` (higher wins), then by declaration order. If neither disambiguates and the instructions are marked as conflicting, the compiler MUST fail rather than pick arbitrarily.

**INV-AUTH-4.** An `authority` entry with `source: "adapter"` may only carry provider-mandated boilerplate (see [§7](#7-provider-adapters)) and is ranked `system` only when the provider itself enforces it.

### 3.2 Authority declarations

`authority[]` declares the *entitled sources* for this build. Each instruction's `source` MUST match a declared authority `id`. This makes "why was this instruction present?" answerable from the artifact alone.

## 4. Instruction provenance

Every instruction is a record, not a sentence:

```json
{
  "id": "policy.no_unsupported_claims",
  "text": "Do not assert findings that are not supported by supplied evidence.",
  "source": "runtime_constitution",
  "authority": "developer",
  "version": "1.4",
  "hash": "sha256:...",
  "priority": 100,
  "rationale": "Evidence contract, RIF Skill Contract §5",
  "conflicts_with": []
}
```

**INV-PROV-1.** `id` is unique within a build and stable across builds. Reusing an id for different semantics is a versioning error; change `version` instead.

**INV-PROV-2.** `hash` is `sha256:<hex>` over the UTF-8 bytes of `text`, unmodified. It lets a replay prove that an instruction's wording did not drift between the recorded build and the current policy set.

**INV-PROV-3.** `source` MUST resolve to a declared `authority[].id`.

**INV-PROV-4.** An instruction with no `rationale` is permitted but is reported by the conformance tool as a provenance gap — the artifact cannot explain itself.

## 5. Context

```json
{
  "context": {
    "task": { "...": "structured task state" },
    "items": [
      {
        "id": "evidence.alert.4471",
        "kind": "evidence",
        "trust": "untrusted",
        "content": "...",
        "provenance": { "origin": "siem", "retrieved_at": "...", "relevance": 0.82 }
      }
    ]
  }
}
```

`kind` ∈ `evidence | memory | tool_output | document | user_state | runtime_state`.
`trust` ∈ `trusted | untrusted`.

**INV-CTX-1.** Anything originating outside the runtime's own governed state is `untrusted`. Retrieval output and tool output are always `untrusted`.

**INV-CTX-2.** An `untrusted` context item MUST NOT carry an `authority` field. Carrying one is a conformance failure, not a warning: it is the shape a successful injection takes.

**INV-CTX-3.** Context items are selected, not concatenated. Each item records why it was included (`relevance`, or a selector id), so context selection is auditable independently of the model's output.

## 6. Reasoning as a governed resource

Reasoning effort is not a constant and not a per-call whim. It is derived from the operating mode and the execution budget, and the derivation is recorded.

```json
{
  "reasoning": {
    "effort": "medium",
    "justification": "mode.maintenance",
    "verification": { "mode": "selective", "independent": true },
    "tools": { "policy": "constrained", "allow": ["read_evidence"] }
  }
}
```

`effort` ∈ `minimal | low | medium | high`.
`verification.mode` ∈ `none | minimal | selective | required`.
`tools.policy` ∈ `denied | constrained | allowed`.

Reference profiles bound to the runtime's operating modes:

| Mode | effort | verification | tools |
|---|---|---|---|
| `normal` | high | required | allowed |
| `maintenance` | medium | selective | constrained |
| `recovery` | low | minimal | denied |

**INV-REASON-1.** `justification` MUST reference a policy or mode identifier that also appears in `authority[]` or `instructions[]`. An effort level with no traceable reason is a conformance failure. The point of the field is that the runtime can say *why* this level was affordable, not merely that it was chosen.

**INV-REASON-2.** A reasoning policy MUST NOT exceed the `budget` envelope declared in the same document.

**INV-REASON-3.** `verification.independent: true` means the verifier receives the result and the evidence *without* inheriting the producer's instructions. Provider diversity and model diversity are independent axes and are recorded separately in `PromptBuild`.

## 7. Provider adapters

An adapter lowers PromptIR to a provider payload. Lowering is a **pure translation**.

**INV-ADAPT-1.** An adapter MUST NOT introduce instruction text absent from PromptIR. Provider-mandated boilerplate MUST be admitted as an instruction with `source: "adapter"` and appear in the document before lowering.

**INV-ADAPT-2.** An adapter MUST NOT drop an instruction because the provider lacks a field for it. It either maps the instruction into an available channel or fails the build.

**INV-ADAPT-3.** An adapter MUST record `provider_payload_hash` over the exact serialized request body. Together with the PromptIR canonical hash this makes the lowering step itself auditable.

```text
PromptIR ──┬── openai adapter   ──→ Responses API request
           ├── anthropic adapter ──→ Messages API request
           └── local adapter     ──→ local runner request
```

Model-provider *aware*, not model-provider *dependent*: the IR is the source of truth and adapters are replaceable.

## 8. State separation

Four state domains. Collapsing any two is an architecture error.

| Domain | Answers | Owned by |
|---|---|---|
| **Prompt state** | What governs *this* generation? | PromptIR |
| **Conversation state** | What happened between turns? | Conversation log (messages, tool calls, tool outputs, reasoning items) |
| **Application state** | What does the app know? | User, project, permissions, configuration |
| **Runtime state** | What does governance know? | Operating mode, budget, risk posture, evidence ledger, capability grants, execution history |

**INV-STATE-1.** A provider-side conversation handle (`previous_response_id` or any equivalent continuation token) is an **execution substrate, not a memory system**. The runtime MUST be able to reconstruct an equivalent PromptIR from its own conversation log, evidence ledger, and runtime state with the handle unavailable. A build that cannot be reconstructed without the provider handle is not replayable and MUST be marked as such.

**INV-STATE-2.** Evidence referenced by a build is addressed by `evidence_id` into the ledger, never inlined as the only copy.

## 9. Compilation

```text
Intent
  ↓ intent resolution
Policy resolution      → instructions (developer authority)
  ↓
Instruction resolution → conflict detection, suppression log
  ↓
Context selection      → context items with relevance/provenance
  ↓
Reasoning policy       → effort/verification/tools from mode + budget
  ↓
PromptIR               → canonicalized, hashed
  ↓
Provider adapter       → payload (+ payload hash)
  ↓
Model request
```

### 9.1 Canonicalization

**INV-COMPILE-1.** `canonical_hash` is `sha256:<hex>` over the canonical JSON serialization of the document with the `canonical_hash` field itself removed:

- object keys sorted by Unicode code point;
- no insignificant whitespace (`separators=(",", ":")`);
- UTF-8 encoding, non-ASCII emitted literally (no `\u` escaping);
- array order preserved as declared.

**INV-COMPILE-2.** Compilation is deterministic: identical `(intent, policy set, context selection, reasoning policy)` MUST produce an identical `canonical_hash`. Timestamps, nonces, and ids that vary per run belong in `PromptBuild`, not in the hashed IR body.

## 10. PromptBuild — the audit artifact

`PromptBuild` wraps a PromptIR document with everything needed to explain and replay the invocation.

```text
PromptBuild
├── build_id, created_at
├── prompt_ir                (the full document, hashed)
├── resolution
│   ├── admitted[]           instruction ids that reached the model
│   ├── suppressed[]         { id, reason, superseded_by }
│   └── promoted[]           context→instruction promotions, with the authority that admitted them
├── context_selection[]      { item_id, selector, relevance }
├── reasoning_policy         effort + justification as executed
├── capability_policy        gates in force at invocation
├── output_contract          schema/format the response was required to satisfy
├── provider
│   ├── provider, model, adapter_version
│   └── provider_payload_hash
├── response                 { response_id, output_hash, usage }
└── evidence_refs[]          ledger ids for claims made
```

Then:

```text
PromptBuild → ModelResponse → Evidence Ledger → Judgment → Replay
```

**INV-BUILD-1.** Every instruction in `prompt_ir.instructions` appears exactly once across `resolution.admitted` and `resolution.suppressed`. An instruction that is in neither was lost by the compiler.

**INV-BUILD-2.** Every `suppressed` entry carries a `reason`; when suppression was caused by a conflict, it also carries `superseded_by` referencing the winning instruction id.

**INV-BUILD-3.** Every `promoted` entry names the authority that admitted the promotion. Unattributed promotion of tool or retrieval content to instruction rank is a governance failure.

## 11. Evaluation

Prompt evaluation is agent evaluation. "Did the answer look good?" is not a dimension.

| Layer | Question | Checked against |
|---|---|---|
| Authority | Did higher-priority instructions win? | `resolution.suppressed` |
| Instruction | Was the required behavior followed? | Output vs. admitted instructions |
| Context | Was relevant evidence supplied? | `context_selection` vs. available ledger |
| Reasoning | Was sufficient effort allocated, and justified? | `reasoning_policy.justification` |
| Tools | Were capabilities used within their gates? | `capability_policy` vs. executed calls |
| Output | Did the result satisfy the schema? | `output_contract` |
| Evidence | Can each claim be traced to evidence? | `evidence_refs` |
| State | Was the correct state preserved across turns? | Conversation/runtime state diff |
| Replay | Can the decision path be reproduced? | `canonical_hash` + `provider_payload_hash` |

## 12. Conformance

An implementation is **PromptIR 0.1 conformant** if it:

1. emits documents that validate against `schemas/prompt-ir.schema.json`;
2. satisfies every invariant marked `INV-*` in this document;
3. records a `PromptBuild` for each model invocation that validates against `schemas/prompt-build.schema.json`;
4. can rebuild an equivalent PromptIR from runtime-owned state without provider continuation handles (INV-STATE-1).

Run the conformance tool over a directory of documents:

```bash
python3 scripts/validate_prompt_ir.py examples/
```

`tests/non-conformant/` holds one fixture per mechanically checkable invariant, each carrying a single injected defect, and `scripts/test_validator.py` asserts the checker rejects each one for its recorded invariant. A conformance tool that has not been shown to reject anything has not been validated.

The tool enforces the structural schema subset plus the invariants that are mechanically checkable — instruction hash correctness, authority resolution, provenance completeness, untrusted-context isolation, reasoning justification traceability, canonical hash reproduction, and `PromptBuild` resolution coverage.

## 13. Relationship to the RIF Skill Contract

The [RIF Skill Contract](SKILL-CONTRACT.md) governs what a marketplace skill owns. PromptIR is the structure a skill's reasoning is *compiled into* by the runtime.

- A skill MUST NOT construct a provider payload directly.
- A skill MAY emit instruction candidates, context selectors, and an output contract; the runtime admits them at the appropriate authority.
- A skill's evidence distinctions (observed / repository fact / derived / inference) map onto `context.items[].kind` and `trust`.
- Verification remains a separate capability (Skill Contract §13); PromptIR records the axis used in `reasoning.verification`.

## 14. Open questions

Recorded rather than resolved, per the evidence discipline this repository requires:

- **Instruction set versioning.** Whether a build should pin a policy-set version hash in addition to per-instruction versions.
- **Context compaction.** How summarized/compacted context retains provenance for items folded into a summary.
- **Cross-provider canonical equivalence.** Whether two adapters lowering the same PromptIR should be required to produce semantically equivalent payloads, and how that would be tested.
- **Promotion policy.** The concrete rule set under which a runtime may promote tool output to instruction rank (INV-BUILD-3 requires attribution; it does not yet constrain when promotion is permitted).
- **Budget units.** `budget` is currently opaque to this specification; unifying it with runtime budget accounting is unresolved.
