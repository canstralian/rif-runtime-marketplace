# RIF Skill Contract

## Purpose

The RIF Skill Contract defines the boundary between a marketplace-distributed skill and the RIF Runtime. A skill is a bounded reasoning capability; it is not the runtime, provider router, evidence store, or execution engine.

The contract is designed to prevent skill drift, duplicated orchestration logic, and claims that cannot be grounded in runtime evidence.

## 1. Skill identity

Every skill MUST declare:

- `name`: stable identifier matching its directory and frontmatter name.
- `description`: concise statement of the capability and its decision boundary.
- `version`: skill contract version or compatible contract range when versioning is introduced.
- `scope`: the runtime concern the skill owns.

The skill name MUST describe a capability, not a model, provider, implementation detail, or transient workflow.

## 2. Purpose and decision boundary

A skill MUST state:

- what problem it solves;
- what decision, analysis, or transformation it owns;
- what it explicitly does not own.

A skill MUST NOT silently assume responsibility for runtime orchestration, provider routing, persistent state, evidence storage, telemetry, or replay unless that responsibility is explicitly part of the skill's contract.

## 3. Inputs

A skill MUST identify the inputs it expects. Inputs should distinguish:

- user intent;
- repository/runtime state;
- prior evidence;
- configuration/policy;
- outputs from other capabilities.

Missing required inputs MUST be surfaced rather than invented.

## 4. Preconditions

A skill MUST define conditions that must hold before execution.

Examples:

- repository context is available;
- a runtime trace exists;
- a policy or constitution is available;
- provider metadata has been resolved.

Preconditions are checks, not assumptions.

## 5. Evidence contract

A skill MUST distinguish:

- **Observed** — directly inspected or returned by a tool/runtime.
- **Repository fact** — established by source/configuration/documentation.
- **Derived** — calculated or logically derived from observed facts.
- **Inference** — interpretation that remains uncertain.

Claims about validation, execution, provider behavior, or runtime state MUST be supported by evidence available to the skill.

If evidence is insufficient, the skill MUST report the limitation.

## 6. Operating procedure

A skill MUST provide a capability-specific procedure. The procedure should normally follow:

1. establish scope;
2. resolve inputs and preconditions;
3. inspect relevant evidence;
4. apply capability-specific analysis;
5. produce a decision or result;
6. validate where possible;
7. record unresolved risks and evidence gaps.

The generic RIF workflow is a baseline, not a substitute for specialized reasoning.

## 7. Decision criteria

A skill MUST define the criteria used to reach its result.

Criteria should be explicit enough that another model, reviewer, or later replay can understand why the conclusion was reached.

Where a binary result is inappropriate, use graded outcomes such as:

- pass;
- fail;
- conditional;
- insufficient evidence;
- not applicable.

## 8. Output contract

Skill output SHOULD be structured around:

```text
Status
Assumptions
Findings
Evidence
Decision
Recommendation
Trade-offs
Validation
Unresolved questions
```

The exact output may be adapted to the capability, but the skill MUST make its decision and evidence boundaries visible.

## 9. Validation

A skill MUST state how its result can be checked.

Validation may include:

- tests;
- static inspection;
- schema validation;
- replay;
- independent review;
- provider/model comparison;
- runtime evidence reconciliation.

A skill MUST NOT claim validation succeeded when it was not actually performed.

## 10. Failure modes

A skill MUST identify material failure modes and the safe behavior for each.

At minimum consider:

- missing evidence;
- contradictory evidence;
- unavailable tools;
- stale repository state;
- ambiguous intent;
- unsupported capability;
- partial execution;
- verifier disagreement.

Failure SHOULD degrade to an explicit uncertain state rather than fabricate certainty.

## 11. Runtime integration boundary

The RIF Runtime owns:

- orchestration;
- operating-mode selection;
- context construction;
- governance enforcement;
- budget accounting;
- capability gating;
- provider/model routing;
- concurrency and asynchronous scheduling;
- execution;
- evidence persistence;
- telemetry;
- replay;
- durable state.

Marketplace skills provide bounded reasoning capabilities to that system.

A skill MAY recommend an action or report a decision, but it MUST NOT duplicate authoritative runtime state or silently bypass runtime governance.

## 12. Concurrency semantics

Skills SHOULD declare whether they are:

- independent and safely parallelizable;
- dependent on another capability;
- order-sensitive;
- state-mutating;
- unsuitable for concurrent execution.

The runtime, not the marketplace skill, is authoritative for scheduling.

Independent reviews should be eligible for asynchronous execution when their inputs are immutable and their evidence scopes do not conflict.

## 13. Verification semantics

A result that materially affects execution SHOULD support independent verification.

Verification is a separate capability from generation. The verifier SHOULD receive the relevant evidence and result without inheriting unsupported assumptions from the producer.

Provider diversity and model diversity are independent dimensions:

```text
provider diversity: OpenAI ↔ Anthropic ↔ Gemini ↔ local
model diversity:     model A ↔ model B ↔ model C
```

The runtime may select either dimension for independent verification according to policy, budget, and capability.

## 14. Evolution

Changes to a skill SHOULD preserve its decision boundary. If the capability changes materially, update its contract and version rather than silently expanding scope.

Contract changes should be validated against:

- marketplace metadata;
- plugin metadata;
- skill frontmatter;
- runtime compatibility;
- tests or validation tooling.

## Reference template

```markdown
---
name: example-skill
description: Capability-specific description.
---

# Example Skill

## Purpose

What this capability owns.

## Scope boundary

What it does not own.

## Inputs

Required and optional inputs.

## Preconditions

Checks required before execution.

## Evidence requirements

What must be observed or supplied.

## Operating procedure

Capability-specific steps.

## Decision criteria

How the result is determined.

## Output

Structured result contract.

## Validation

How the result is independently checked.

## Failure modes

Known failure cases and safe degradation.

## Concurrency

Independent, dependent, order-sensitive, or state-mutating.

## RIF integration

Which runtime stages consume or produce this capability.
```
