# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repository is

A **Claude Code plugin marketplace** for the RIF Runtime project. It is a
distribution catalog — JSON manifests and Markdown skill definitions. There is
no application code, no build step, no test suite, and no runtime here.

The RIF Runtime application lives in a **separate** repository
(`canstralian/rif-runtime`). This separation is intentional: the marketplace
handles catalog and distribution; the application handles execution. Do not
import runtime implementation into this repo, and do not assume the runtime's
source is available when reasoning about a skill.

The only code is `scripts/validate.py` — stdlib-only Python 3, not marked
executable. Run it as `python3 scripts/validate.py`.

## Constraints

These five rules change what you do. The rest of this file is reference.

| Rule | Why |
|---|---|
| Never deduplicate the ten identical `SKILL.md` bodies | Divergence is the planned direction — [Skills are intentionally un-specialized](#skills-are-intentionally-un-specialized) |
| Never give a skill a runtime responsibility | Contract §11 — [The Skill Contract](#the-skill-contract) |
| Never report a check as passing unless it ran | Contract §5 evidence discipline |
| Move both plugin-version fields together | Nothing verifies they agree — [Versioning](#versioning) |
| Never claim tests or CI ran | Neither exists — [Validation](#validation) |

## Layout

```text
.
├── .claude-plugin/
│   └── marketplace.json          # Catalog: marketplace metadata + plugin list
├── plugins/
│   └── rif-runtime/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest
│       └── skills/
│           └── <skill-name>/
│               └── SKILL.md      # One directory per skill
├── docs/
│   ├── SKILL-CONTRACT.md         # Normative contract every skill must satisfy
│   └── SKILL-MAPPING.md          # Per-skill boundaries + planned specialization
├── scripts/
│   └── validate.py               # Structural validation of the manifests
├── LICENSE                       # MIT
└── README.md
```

Three tiers, and the boundary between them is load-bearing:

| Tier | Artifact | Responsibility |
|---|---|---|
| Marketplace | `.claude-plugin/marketplace.json` | Catalog and distribution |
| Plugin | `plugins/<name>/.claude-plugin/plugin.json` | Installable capability boundary |
| Skill | `plugins/<name>/skills/<skill>/SKILL.md` | One bounded reasoning capability |

A new capability *area* means a new plugin, not more skills bolted onto
`rif-runtime`. The README names this explicitly: keeping the marketplace from
becoming a monolith is a design goal.

## The ten skills

All live under `plugins/rif-runtime/skills/` and are invoked namespaced as
`/rif-runtime:<skill-name>`.

| Skill | Role |
|---|---|
| `rif-runtime` | Runtime architectural **understanding** capability |
| `run-rif-runtime` | Runtime **execution entry** capability |
| `architecture-review` | Boundaries, coupling, failure modes, evolution risk |
| `constitution-guardian` | Invariants, authority boundaries, prohibited changes |
| `governance-review` | Policies, authority, controls, evidence requirements |
| `knowledge-engine` | Retrieval, reconciliation, synthesis, provenance |
| `provider-review` | Provider/model capability, reliability, cost, portability |
| `replay-analysis` | Trace reproducibility, explainability, reconciliation |
| `documentation-engine` | Validated implementation/decisions → documentation |
| `release-manager` | Versioning, regression risk, release readiness |

`rif-runtime` and `run-rif-runtime` are deliberately distinct — understanding
versus execution — and must not collapse into each other.

## Skills are intentionally un-specialized

**Read this before editing any `SKILL.md`.**

All ten skill files are byte-identical from the `## Operating principles`
heading onward. They differ only in:

- YAML frontmatter (`name`, `description`),
- the `# Title` heading,
- the "You are operating as the `<name>` capability" line.

This is a documented state, not an oversight. `docs/SKILL-MAPPING.md` records it
under **"Immediate specialization requirements"** and specifies, per skill, the
capability-specific criteria that should replace the shared generic workflow.

- **Do not** factor the shared body into an include or a common file. The
  intended direction is divergence, not deduplication.
- **Do** consult the matching section of `docs/SKILL-MAPPING.md` when asked to
  improve a skill — the required checks are enumerated there.
- **Do** preserve the common contract (evidence discipline, output discipline,
  scope boundary) while specializing the analysis.

## The Skill Contract

`docs/SKILL-CONTRACT.md` is normative for anything under `skills/`. Well-meaning
edits break these rules most often:

**Evidence discipline (§5).** Every claim must be classifiable as *observed*,
*repository fact*, *derived*, or *inference*. Never assert that a validation,
test, or execution succeeded unless it ran. Report insufficient evidence as
insufficient; do not fill the gap.

**Runtime integration boundary (§11).** The runtime — not a skill — owns
orchestration, mode selection, context construction, governance enforcement,
budget accounting, capability gating, provider/model routing, scheduling,
execution, evidence persistence, telemetry, replay, and durable state. A skill
may *recommend* or *report*. It must never duplicate authoritative runtime state
or bypass runtime governance. Skill text that claims anything on that list
violates the contract.

**Scope boundary (§2).** Each skill must state what it does *not* own.

**Graded outcomes (§7).** Use `pass` / `fail` / `conditional` /
`insufficient evidence` / `not applicable` instead of forcing a binary.

**Evolution (§14).** Changing a capability materially means updating its
contract and version, not silently widening scope.

The "Reference template" section at the end of `SKILL-CONTRACT.md` is the
canonical shape for a specialized skill. Use it verbatim as the section skeleton.

## The shared runtime mental model

Every skill body carries this lifecycle as its reference model. Keep the stage
names and ordering consistent if you reproduce it:

```text
Intent → Orchestrator → Mode validation → Memory retrieval →
Context construction → Governance evaluation → Budget accounting →
Capability gates → Execution → Evidence ledger → Telemetry →
Replay → Documentation
```

When a task crosses these boundaries, name the affected stages and invariants.

## Conventions

**Skill frontmatter.** Minimal YAML, exactly two keys today:

```yaml
---
name: architecture-review
description: Review RIF Runtime architecture for structural integrity, boundaries, coupling, failure modes, and evolution risks.
---
```

`name` **must** match the containing directory name exactly. `description` is a
single sentence stating the capability and its decision boundary — it names a
capability, never a model, provider, or implementation detail.

`SKILL-CONTRACT.md` §1 appears to conflict with this: it lists `name`,
`description`, `version`, and `scope` as things a skill must declare. The
contract's own reference template resolves the conflict. Frontmatter carries
`name` and `description`; `scope` is declared in the body as `## Scope
boundary`; `version` is qualified "when versioning is introduced", which has not
happened. All ten skills carry exactly two frontmatter keys. Follow the
reference template, not a literal reading of §1.

**Directory naming.** Lowercase kebab-case. The directory name, frontmatter
`name`, and the invocation `/rif-runtime:<name>` are always the same string.

**Output discipline.** Skills instruct: *Assumptions → Decision →
Recommendation → Trade-offs → Validation*. The fuller contract output shape
(§8) is Status / Assumptions / Findings / Evidence / Decision / Recommendation /
Trade-offs / Validation / Unresolved questions.

**Markdown.** Fenced code blocks carry a language tag (`text` for diagrams and
directory trees). Documents lead with a `#` H1.

**Python.** `scripts/validate.py` is stdlib-only. Keep it that way — there is no
`requirements.txt`, no lockfile, and nothing to install.

## Adding a skill

1. `mkdir plugins/rif-runtime/skills/<skill-name>/`
2. Write `SKILL.md` with frontmatter whose `name` matches the directory, and a
   body following the reference template in `docs/SKILL-CONTRACT.md`.
3. Add a row to the table in `docs/SKILL-MAPPING.md` — primary role, owns, must
   not own, concurrency, verification. A skill without a mapping entry has no
   declared boundary.
4. Add the `/rif-runtime:<skill-name>` line to the README's skill list and the
   directory to the README's tree.
5. Bump the plugin version — a new skill changes distributable behavior. That
   value lives in **two** fields that must move together:
   `plugins/rif-runtime/.claude-plugin/plugin.json` → `version`, and
   `.claude-plugin/marketplace.json` → `plugins[0].version`. See
   [Versioning](#versioning).
6. Run validation (below), then hand-check steps 2–5 — the validator covers
   none of them.

## Validation

Run both from the repository root:

```bash
python3 scripts/validate.py     # prints "Marketplace structure: OK"
claude plugin validate .        # full Claude Code marketplace validation
```

Local install test from inside Claude Code:

```text
/plugin marketplace add .
/plugin install rif-runtime@rif-runtime-marketplace
```

**What `validate.py` checks.** The marketplace name, owner type, and a non-empty
plugin list; that each `plugins[].source` directory exists; that each source
contains `.claude-plugin/plugin.json`; and that each plugin manifest's `name`
matches its catalog entry.

**What it does not check.** Verify these by hand:

- Anything under `skills/`. Frontmatter, `name`/directory agreement, and body
  structure are unread — the script never opens a `SKILL.md`.
- That the two plugin-version fields agree. Setting `plugins[0].version` to
  `9.9.9` while `plugin.json` stays `1.0.0` still prints
  `Marketplace structure: OK` and exits 0.
- README consistency with the skill list or directory tree.

**What failure looks like.** The script is a chain of bare `assert` statements,
so a failure surfaces as an `AssertionError` traceback and exit 1, not a
diagnostic message.

**Never run it under `python -O`.** That flag strips every assert, reducing the
script to its print statement. Against a manifest whose `plugin.json` name
disagrees with its catalog entry — which the normal invocation rejects with exit
1 — `python3 -O scripts/validate.py` prints `Marketplace structure: OK` and
exits 0.

There is no test suite, linter, formatter, or CI workflow in this repository;
`.github/` does not exist. The commands above are the entire verification
surface. Do not claim broader validation than that.

## Versioning

Marketplace and plugin both sit at `1.0.0` today, but they are **two distinct
version identities** spread over three fields. They are not three copies of one
number.

**Plugin version** — one value, duplicated in two fields that must always match:

- `plugins/rif-runtime/.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

Bump it whenever the plugin's distributable behavior changes: a skill added,
removed, or materially rewritten. Updating one field and not the other leaves
the catalog advertising a version the plugin manifest does not claim, and
`validate.py` does not catch it.

**Marketplace version** — the catalog's own version, independent of the plugin:

- `.claude-plugin/marketplace.json` → top-level `version`

Bump it when the catalog itself changes: a plugin added or removed, marketplace
metadata reworked. Adding a skill to an existing plugin does not by itself
require a marketplace bump. The two identities sharing `1.0.0` is a coincidence
of a single-plugin catalog, not a constraint.

Owner and repo metadata are likewise duplicated across both manifests
(`canstralian`, `https://github.com/canstralian/rif-runtime`, MIT). Change them
in both or neither.

## Working style in this repo

- Keep changes small, documentation-shaped, and reviewable. Match the measured,
  specification-like prose in `docs/` — it is deliberate, not verbose.
- Follow Conventional Commits (`docs:`, `feat:`), as in
  `docs: define RIF skill contract`.
- Nothing here executes at review time. Any statement about runtime behavior is
  a claim about the *other* repository. Label it as inference unless you
  inspected that source.
