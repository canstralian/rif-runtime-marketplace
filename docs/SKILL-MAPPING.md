# RIF Skill Mapping

This document maps the current marketplace skills to the RIF Skill Contract and identifies the architectural boundary each capability should preserve.

| Skill | Primary role | Owns | Must not own | Concurrency | Verification |
|---|---|---|---|---|---|
| `rif-runtime` | Runtime architectural context | Explain runtime lifecycle, boundaries, invariants | Execute authoritative runtime state changes | Independent for read-only analysis | Recommended for consequential claims |
| `run-rif-runtime` | Runtime execution entry point | Translate intent into a runtime execution request | Provider selection, evidence persistence, governance bypass | Runtime-controlled | Mandatory for material execution |
| `architecture-review` | Structural review | Boundaries, coupling, failure modes, evolution risk | Runtime implementation or release approval | Parallel with other read-only reviews | Recommended |
| `constitution-guardian` | Constitutional review | Invariants, authority boundaries, prohibited changes | Operational execution | Parallel when inputs are immutable | Recommended; mandatory for governed changes |
| `governance-review` | Governance review | Policies, authority, controls, evidence requirements | Constitutional source of truth | Parallel with architecture review | Recommended |
| `knowledge-engine` | Knowledge reconciliation | Retrieval, reconciliation, synthesis, provenance distinctions | Durable memory authority | Parallel for independent knowledge scopes | Recommended when evidence conflicts |
| `provider-review` | Provider/model assessment | Capability, reliability, portability, cost/security criteria | Provider routing or credential management | Parallel across providers/models | Strongly recommended; cross-provider/model comparison preferred |
| `replay-analysis` | Execution audit | Reproducibility, explainability, trace/evidence reconciliation | Runtime execution | Parallel across independent traces | Mandatory for replay claims |
| `documentation-engine` | Documentation synthesis | Transform validated implementation/decisions into documentation | Source-of-truth runtime state | Parallel by document scope | Validate against repository state |
| `release-manager` | Release readiness | Versioning, regression risk, release evidence, readiness assessment | Performing the release itself | Mostly order-sensitive | Mandatory before release recommendation |

## Immediate specialization requirements

The current skills share a common generic workflow. The next implementation pass should replace that duplication with capability-specific criteria while retaining the common contract.

### `architecture-review`

Add explicit analysis for:

- boundary violations;
- hidden coupling;
- authority duplication;
- state ownership;
- failure propagation;
- migration/reversibility risk;
- concurrency hazards.

### `constitution-guardian`

Add explicit checks for:

- constitutional invariant preservation;
- authority hierarchy;
- governance bypass;
- evidence requirements;
- prohibited side effects;
- exception handling.

### `governance-review`

Add explicit checks for:

- policy applicability;
- decision authority;
- capability gates;
- budget constraints;
- evidence sufficiency;
- escalation conditions.

### `knowledge-engine`

Add explicit handling for:

- provenance;
- source ranking;
- conflicting evidence;
- stale information;
- inferred versus observed facts;
- retrieval completeness.

### `provider-review`

Add explicit evaluation of:

- provider capability;
- model capability;
- context/tool/structured-output support;
- latency and reliability;
- cost;
- rate/concurrency constraints;
- portability;
- primary/verifier suitability;
- same-provider versus cross-provider verification.

### `replay-analysis`

Add explicit checks for:

- trace completeness;
- input/state capture;
- evidence availability;
- nondeterministic dependencies;
- provider/model identity;
- replay divergence;
- explainability.

### `documentation-engine`

Add explicit provenance requirements:

- source artifact;
- implementation version;
- decision evidence;
- unresolved uncertainty;
- generated-versus-observed distinction.

### `release-manager`

Add explicit gates for:

- version consistency;
- validation status;
- regression evidence;
- contract compatibility;
- changelog completeness;
- rollback readiness.

### `rif-runtime` and `run-rif-runtime`

Keep these distinct:

- `rif-runtime` is the **understanding/context capability**.
- `run-rif-runtime` is the **execution entry capability**.

Neither should become a substitute for the authoritative runtime implementation.

## Target capability flow

```text
Intent
  ↓
run-rif-runtime
  ↓
Runtime orchestration
  ├── architecture-review ─────┐
  ├── constitution-guardian ───┤
  ├── governance-review ───────┤
  ├── knowledge-engine ────────┤
  └── provider-review ─────────┘
               ↓
        async independent work
               ↓
          execution/gates
               ↓
          evidence ledger
               ↓
       replay-analysis / verifier
               ↓
       documentation-engine
               ↓
        release-manager
```

The arrows are architectural intent, not evidence that the current runtime already implements these orchestration semantics.
