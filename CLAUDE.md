# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repository is

A **Claude Code plugin marketplace** for the RIF Runtime project. It is a
distribution catalog — pure JSON manifests and Markdown skill definitions.
There is no application code, no build step, no test suite, and no runtime here.

The RIF Runtime application itself lives in a **separate** repository
(`canstralian/rif-runtime`). This separation is intentional: the marketplace
handles catalog and distribution; the application handles execution. Do not
import runtime implementation into this repo, and do not assume the runtime's
source is available when reasoning about a skill.

The only executable file is `scripts/validate.py` (stdlib-only Python 3).

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

Three-tier model, and the boundary between tiers is load-bearing:

| Tier | Artifact | Responsibility |
|---|---|---|
| Marketplace | `.claude-plugin/marketplace.json` | Catalog and distribution |
| Plugin | `plugins/<name>/.claude-plugin/plugin.json` | Installable capability boundary |
| Skill | `plugins/<name>/skills/<skill>/SKILL.md` | One bounded reasoning capability |

Adding a *new capability area* should mean a new plugin, not more skills bolted
onto `rif-runtime`. The README states this explicitly: keeping the marketplace
from becoming a monolith is a design goal.

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

## Current state: skills are intentionally un-specialized

**Read this before editing any `SKILL.md`.**

All ten skill files are currently byte-identical from the `## Operating
principles` heading onward. They differ only in:

- YAML frontmatter (`name`, `description`),
- the `# Title` heading,
- the "You are operating as the `<name>` capability" line.

This is a known, documented state — not an oversight and not something to
"clean up" by deduplicating. `docs/SKILL-MAPPING.md` records it under
**"Immediate specialization requirements"** and specifies, per skill, the
capability-specific criteria that should replace the shared generic workflow.

So:

- **Do not** factor the shared body into an include or a common file. The
  intended direction is divergence, not deduplication.
- **Do** consult the matching section of `docs/SKILL-MAPPING.md` when asked to
  improve a skill — the required checks are already enumerated there.
- **Do** preserve the common contract (evidence discipline, output discipline,
  scope boundary) while specializing the analysis.

## The Skill Contract

`docs/SKILL-CONTRACT.md` is normative for anything under `skills/`. Its rules
that most often get violated by well-meaning edits:

**Evidence discipline (§5).** Every claim must be classifiable as *observed*,
*repository fact*, *derived*, or *inference*. Never assert that a validation,
test, or execution succeeded unless it actually ran. Insufficient evidence must
be reported as such, not filled in.

**Runtime integration boundary (§11).** The runtime — not a skill — owns
orchestration, mode selection, context construction, governance enforcement,
budget accounting, capability gating, provider/model routing, scheduling,
execution, evidence persistence, telemetry, replay, and durable state. A skill
may *recommend* or *report*; it must never duplicate authoritative runtime state
or bypass runtime governance. New skill text that starts owning any of that
list is a contract violation.

**Scope boundary (§2).** Each skill must say what it does *not* own.

**Graded outcomes (§7).** Prefer `pass` / `fail` / `conditional` /
`insufficient evidence` / `not applicable` over forced binaries.

**Evolution (§14).** Changing a capability materially means updating its
contract and version — not silently widening scope.

§ "Reference template" at the end of `SKILL-CONTRACT.md` is the canonical shape
for a specialized skill. Use it verbatim as the section skeleton when writing one.

## The shared runtime mental model

Every skill body carries this lifecycle as its reference model. Keep the stage
names and ordering consistent if you reproduce it:

```text
Intent → Orchestrator → Mode validation → Memory retrieval →
Context construction → Governance evaluation → Budget accounting →
Capability gates → Execution → Evidence ledger → Telemetry →
Replay → Documentation
```

When a task crosses these boundaries, name the affected stages and invariants
explicitly.

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

Note the apparent conflict with `SKILL-CONTRACT.md` §1, which lists `name`,
`description`, `version`, and `scope` as things a skill must declare. The
contract's own reference template resolves it: frontmatter carries `name` and
`description`, `scope` is declared in the body as `## Scope boundary`, and
`version` is qualified "when versioning is introduced" — which has not happened
yet. All ten current skills carry exactly two frontmatter keys. Follow the
reference template, not a literal reading of §1.

**Directory naming.** Lowercase kebab-case; directory name, frontmatter `name`,
and the invocation `/rif-runtime:<name>` are always the same string.

**Output discipline.** Skills instruct: *Assumptions → Decision →
Recommendation → Trade-offs → Validation*. The fuller contract output shape
(§8) is Status / Assumptions / Findings / Evidence / Decision / Recommendation /
Trade-offs / Validation / Unresolved questions.

**Markdown.** Fenced code blocks carry a language tag (`text` for diagrams and
directory trees). Documents lead with a `#` H1.

**Python.** `scripts/validate.py` is stdlib-only with no dependencies. Keep it
that way — there is no `requirements.txt`, no lockfile, and nothing to install.

## Adding a skill

1. `mkdir plugins/rif-runtime/skills/<skill-name>/`
2. Write `SKILL.md` with frontmatter whose `name` matches the directory, and a
   body following the reference template in `docs/SKILL-CONTRACT.md`.
3. Add a row to the table in `docs/SKILL-MAPPING.md` — primary role, owns, must
   not own, concurrency, verification. A skill without a mapping entry has no
   declared boundary.
4. Add the `/rif-runtime:<skill-name>` line to the README's skill list and the
   directory to the README's tree.
5. Bump the plugin version — a new skill changes distributable behavior. This
   value lives in **two** places that must move together:
   `plugins/rif-runtime/.claude-plugin/plugin.json` → `version`, and
   `.claude-plugin/marketplace.json` → `plugins[0].version`. See
   [Versioning](#versioning).
6. Run validation (below).

Note that `scripts/validate.py` does **not** currently check skills at all — it
validates only the marketplace/plugin manifest wiring. Skill frontmatter,
name/directory agreement, and README consistency are unenforced and must be
checked by hand.

## Validation

```bash
python3 scripts/validate.py     # manifest structure; prints "Marketplace structure: OK"
claude plugin validate .        # full Claude Code marketplace validation
```

Local install test from inside Claude Code:

```text
/plugin marketplace add .
/plugin install rif-runtime@rif-runtime-marketplace
```

There is no test suite, linter, formatter, or CI workflow in this repository —
`.github/` does not exist. The two commands above are the entire verification
surface. Don't claim broader validation than that.

## Versioning

Marketplace and plugin both sit at `1.0.0` today, but they are **two distinct
version identities** spread over three fields. Do not treat them as three
copies of one number.

**Plugin version** — one value, duplicated in two fields that must always match:

- `plugins/rif-runtime/.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

Bump it whenever the plugin's distributable behavior changes (skill added,
removed, or materially rewritten). Updating one field and not the other leaves
the catalog advertising a version the plugin manifest does not claim.

**Marketplace version** — the catalog's own version, independent of the plugin:

- `.claude-plugin/marketplace.json` → top-level `version`

Bump it when the catalog itself changes (a plugin added or removed, marketplace
metadata reworked). Adding a skill to an existing plugin does not by itself
require a marketplace bump. The two identities sharing `1.0.0` right now is a
coincidence of a single-plugin catalog, not a constraint.

Owner/repo metadata is likewise duplicated across both manifests
(`canstralian`, `https://github.com/canstralian/rif-runtime`, MIT). Change it in
both or neither.

## Working style in this repo

- Changes are small, documentation-shaped, and reviewable. Match the existing
  measured, specification-like prose in `docs/` — it is deliberate, not verbose.
- Commit messages follow Conventional Commits (`docs:`, `feat:`), as in
  `docs: define RIF skill contract`.
- Nothing here executes at review time. Any statement about runtime behavior is
  a claim about the *other* repository and should be labeled as inference unless
  that source was actually inspected.
