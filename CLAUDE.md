# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repository is

A **Claude Code plugin marketplace** for the RIF Runtime project. Its core is a
distribution catalog — JSON manifests and Markdown skill definitions — and the
RIF Runtime itself does not run here. Two things sit alongside the catalog and
are easy to miss:

- `web/` — "forge-exchange-web", a React 19 + Vite + TypeScript site with a real
  build (`npm run build` → `tsc --noEmit && vite build`) and npm dependencies,
  deployed to GitHub Pages by `.github/workflows/pages.yml`.
- `schemas/` — JSON Schemas for PromptIR and PromptBuild.

So "no build step" is no longer true of the repository, only of the catalog.
What testing exists validates the catalog's structure and the conformance
fixtures, not a product.

The RIF Runtime application lives in a **separate** repository
(`canstralian/rif-runtime`). This separation is intentional: the marketplace
handles catalog and distribution; the application handles execution. Do not
import runtime implementation into this repo, and do not assume the runtime's
source is available when reasoning about a skill.

The Python code is three stdlib-only scripts in `scripts/`, none marked
executable — run them as `python3 scripts/<name>.py`:

| Script | Purpose |
|---|---|
| `validate.py` | Marketplace, plugin, and skill structure |
| `validate_prompt_ir.py` | PromptIR / PromptBuild conformance over `examples/` |
| `test_validator.py` | Self-test for the conformance checker |

## Constraints

These five rules change what you do. The rest of this file is reference.

| Rule | Why |
|---|---|
| Never deduplicate the ten identical `SKILL.md` bodies | Divergence is the planned direction — [Ten of the twelve skills are intentionally un-specialized](#ten-of-the-twelve-skills-are-intentionally-un-specialized) |
| Never give a skill a runtime responsibility | Contract §11 — [The Skill Contract](#the-skill-contract) |
| Never report a check as passing unless it ran | Contract §5 evidence discipline |
| Move both plugin-version fields together | `validate.py` enforces it — [Versioning](#versioning) |
| Run all three `scripts/` checks before pushing | `validate.yml` runs exactly these — [Validation](#validation) |

## Layout

```text
.
├── .claude-plugin/
│   └── marketplace.json          # Catalog: marketplace metadata + plugin list
├── plugins/
│   └── rif-runtime/
│       ├── .claude-plugin/
│       │   ├── plugin.json       # Plugin manifest
│       │   └── icon.png          # Plugin icon
│       └── skills/
│           └── <skill-name>/
│               └── SKILL.md      # One directory per skill
├── docs/
│   ├── SKILL-CONTRACT.md         # Normative contract every skill must satisfy
│   ├── SKILL-MAPPING.md          # Per-skill boundaries + planned specialization
│   └── adr/                      # Architecture decision records
├── scripts/
│   ├── validate.py               # Marketplace, plugin, and skill structure
│   ├── validate_prompt_ir.py     # PromptIR / PromptBuild conformance
│   └── test_validator.py         # Self-test for the conformance checker
├── examples/                     # PromptIR documents the conformance check reads
├── tests/                        # Conformant and non-conformant fixtures
├── schemas/                      # JSON Schemas for PromptIR and PromptBuild
├── web/                          # forge-exchange-web: React + Vite site (has its own build)
├── .github/
│   └── workflows/
│       ├── validate.yml          # CI: the three scripts above
│       └── pages.yml             # CI: builds web/ and deploys to GitHub Pages
├── .claude/                      # Agent config: hooks, permissions, ECC bundle
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
becoming a monolith is a design goal. A new plugin needs a `skills/` directory
from its first commit, even one holding nothing but a tracked `.gitkeep`:
`validate.py` iterates that path without checking it exists, so a plugin
without it fails with a `FileNotFoundError` rather than a diagnostic. A plugin
that ships only agents or hooks still needs the directory.

## The twelve skills

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
| `prompt-audit` | PromptIR / PromptBuild conformance auditing |
| `prompt-compiler` | PromptIR compilation into PromptBuild output |

`rif-runtime` and `run-rif-runtime` are deliberately distinct — understanding
versus execution — and must not collapse into each other.

## Ten of the twelve skills are intentionally un-specialized

**Read this before editing any `SKILL.md`.**

`prompt-audit` and `prompt-compiler` are specialized: each follows the
reference template in `docs/SKILL-CONTRACT.md`, with `## Purpose`,
`## Scope boundary`, `## Inputs`, `## Preconditions`, and the rest. They are the
model for what the other ten should become.

The other ten skill files are byte-identical from the `## Operating principles`
heading onward. They differ only in:

- YAML frontmatter (`name`, `description`),
- the `# Title` heading,
- the "You are operating as the `<name>` capability" line.

This is a documented state, not an oversight. `docs/SKILL-MAPPING.md` records it
under **"Immediate specialization requirements"** and specifies, per skill, the
capability-specific criteria that should replace the shared generic workflow.
The two specialized skills show that this work has started.

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

`name` **must** match the containing directory name exactly, and unquoted —
`validate.py` compares it as raw text. `description` is a single sentence
stating the capability and its decision boundary — it names a capability, never
a model, provider, or implementation detail. Quote the description if it
contains `: `, as `rif-runtime`'s does; unquoted, such a line is invalid YAML
and no check in this repository catches it.

`SKILL-CONTRACT.md` §1 appears to conflict with this: it lists `name`,
`description`, `version`, and `scope` as things a skill must declare. The
contract's own reference template resolves it. Frontmatter carries `name` and
`description` only; the template declares `scope` in the body under a
`## Scope boundary` heading, and qualifies `version` as "when versioning is
introduced", which has not happened. All twelve skills carry exactly two
frontmatter keys, and `validate.py` enforces an unquoted `name` matching the
directory and a `description` with text after the colon. Follow the reference template, not a literal reading of §1.

The ten un-specialized skills do **not** carry a `## Scope boundary` section —
their shared body runs `## Operating principles`, `## Workflow`, `## RIF Runtime
mental model`, `## Output discipline`, and nothing else. That is part of the
un-specialized state described above, not a pattern to copy. `prompt-audit` and
`prompt-compiler` do carry it, and are the pattern to follow.

**Directory naming.** Lowercase kebab-case. The directory name, frontmatter
`name`, and the invocation `/rif-runtime:<name>` are always the same string.

**Output discipline.** Skills instruct: *Assumptions → Decision →
Recommendation → Trade-offs → Validation*. The fuller contract output shape
(§8) is Status / Assumptions / Findings / Evidence / Decision / Recommendation /
Trade-offs / Validation / Unresolved questions.

**Markdown.** Fenced code blocks carry a language tag (`text` for diagrams and
directory trees). Documents lead with a `#` H1.

**Python.** The `scripts/` checks are stdlib-only. Keep them that way — there is
no `requirements.txt` and no Python lockfile. This says nothing about `web/`,
which has its own `package.json` and npm dependencies.

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
6. Run validation (below). `validate.py` covers **part** of this list: step 2's
   `SKILL.md` existence, frontmatter presence, `name`/directory agreement as
   written, and a `description` field with non-empty raw text — not a decoded
   YAML value; and step 5's version pair. It does **not** cover the
   body structure in step 2, the mapping entry in step 3, or the README edits in
   step 4 — hand-check those.

## Validation

`.github/workflows/validate.yml` runs these three scripts from the repository
root on every push and pull request. Run them yourself before pushing:

```bash
python3 -E scripts/validate.py                     # prints "Marketplace structure: OK (12 skills)"
python3 scripts/validate_prompt_ir.py --strict examples/
python3 scripts/test_validator.py
```

CI invokes `validate.py` without `-E`; the flag is here because a local shell
can carry an inherited `PYTHONOPTIMIZE`, which fakes a pass — see below. The
other two scripts contain no `assert` statements, so the flag changes nothing
for them.

`claude plugin validate .` additionally runs the full Claude Code marketplace
validation, which CI does not.

A second workflow, `.github/workflows/pages.yml`, builds `web/` — `npm install`
then `npm run build` (`tsc --noEmit && vite build`) — on any change under
`web/`, and deploys to GitHub Pages on `master`. None of the `scripts/` checks
touch `web/`, and the Pages build does not touch the catalog. If you change
`web/`, build it yourself; `validate.py` passing says nothing about it.

Local install test from inside Claude Code:

```text
/plugin marketplace add .
/plugin install rif-runtime@rif-runtime-marketplace
```

**What `validate.py` checks.** The marketplace name, owner type, and a non-empty
plugin list; that each catalog entry has a non-empty `name`; that each
`plugins[].source` directory exists and contains `.claude-plugin/plugin.json`;
that each plugin manifest's `name` **and `version`** match its catalog entry; and,
for every skill directory, that `SKILL.md` exists, opens with a `---` fenced
frontmatter block, and carries a `name` matching its directory and a
`description` with text after the colon. It prints the skill count it validated.

Those last two are **raw-text** comparisons, not YAML ones: the script matches
`^(\w+):\s*(.+)$` against the frontmatter lines and never parses them. So the
`name` must equal the directory name *as written* — `name: "architecture-review"`
fails against directory `architecture-review`, because the quotes are part of
the matched string. So `name` is always unquoted.

`description` is the opposite case, and the rule is not "unquoted": quote it
whenever its text contains a colon followed by a space, or any other character
YAML reads as structure. `rif-runtime`'s description does (`…engineering
skill: understand…`), and unquoted it is **not valid YAML** — `yaml.safe_load`
raises `ScannerError` on it, because a plain scalar cannot contain `: `. It sat
in the tree that way until master quoted it. `validate.py` never noticed, in
either state, because it does not parse YAML — see below.

**What it still does not check.** Verify these by hand:

- Skill *body* structure. Frontmatter is matched line by line; the body is not
  read at all. Nothing enforces the reference template or the output contract.
- That the frontmatter is valid YAML, or that `description` decodes to anything.
  Confirmed: both `description: ""` and an unterminated `description: "Review…`
  pass, because two quote characters and an unclosed quote are both non-empty
  raw text. This is not hypothetical — `rif-runtime/SKILL.md` carried an
  unquoted description containing `: `, which `yaml.safe_load` rejects, and
  `validate.py` reported `OK` on every run until master quoted it. Read the
  frontmatter yourself, or parse it.
- README consistency with the skill list or directory tree.
- The top-level marketplace `version` — only the plugin version pair is
  compared.

**What failure looks like.** Every failure is an unhandled traceback and a
non-zero exit, never a purpose-built diagnostic. Which exception you get depends
on where the script gives up:

| Broken input | Exception |
|---|---|
| `.claude-plugin/marketplace.json` missing | `FileNotFoundError` — it is read before the first assert |
| A catalog plugin whose source directory has no `skills/` | `FileNotFoundError` — `skills/` is iterated, never existence-checked |
| Malformed JSON in either manifest | `json.decoder.JSONDecodeError` |
| Missing `name`, `owner`, or `plugins` key | `KeyError` |
| Empty plugin list or entry `name`, missing source directory, missing `plugin.json`, name or version mismatch, missing or malformed `SKILL.md` frontmatter | `AssertionError` |

The assertions carrying a message — version mismatch, skill name/directory
disagreement, missing description — print it with the traceback.

**Never run any of them under `python -O`.** That flag strips every assert, and
these scripts are almost entirely asserts. A missing source *directory* or
plugin *manifest* is caught by an assert rather than by a file read, so `-O`
skips those existence checks too. Against a manifest whose `plugin.json` name
disagrees with its catalog entry — which the normal invocation rejects with exit
1 — `python3 -O scripts/validate.py` prints `Marketplace structure: OK` and
exits 0.

**The `PYTHONOPTIMIZE` environment variable does the same thing silently.** It
needs no flag on the command line, so a validator invoked from a script or CI
step inherits it and reports a false pass. Anything that runs these scripts
unattended should invoke `python3 -E`, which ignores `PYTHON*` variables;
`.claude/hooks/session-start.sh` does. Confirmed: with `PYTHONOPTIMIZE=1` a
version desync prints `Marketplace structure: OK (12 skills)` and exits 0, while
`python3 -E` fails it correctly.

## Versioning

The plugin sits at `1.1.0` and the marketplace at `1.0.0`. They are **two
distinct version identities** spread over three fields, not three copies of one
number — and the current values show it.

**Plugin version** — one value, duplicated in two fields that must always match:

- `plugins/rif-runtime/.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

Bump it whenever the plugin's distributable behavior changes: a skill added,
removed, or materially rewritten. Updating one field and not the other leaves
the catalog advertising a version the plugin manifest does not claim.
`validate.py` now enforces the pair and fails with a message naming both values,
so a desync breaks CI rather than shipping silently.

**Marketplace version** — the catalog's own version, independent of the plugin:

- `.claude-plugin/marketplace.json` → top-level `version`

Bump it when the catalog itself changes: a plugin added or removed, marketplace
metadata reworked. Adding a skill to an existing plugin does not by itself
require a marketplace bump — which is why the plugin has moved to `1.1.0` while
the marketplace stays at `1.0.0`. Nothing validates this field.

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
