# RIF Runtime Claude Code Marketplace

A Claude Code plugin marketplace for the **RIF Runtime** project.

The repository follows Anthropic's marketplace structure:

```text
.
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── rif-runtime/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           ├── architecture-review/
│           ├── constitution-guardian/
│           ├── documentation-engine/
│           ├── governance-review/
│           ├── knowledge-engine/
│           ├── prompt-audit/
│           ├── prompt-compiler/
│           ├── provider-review/
│           ├── release-manager/
│           ├── replay-analysis/
│           ├── rif-runtime/
│           └── run-rif-runtime/
├── docs/
│   ├── PROMPT-IR.md
│   ├── SKILL-CONTRACT.md
│   └── SKILL-MAPPING.md
├── schemas/
│   ├── prompt-ir.schema.json
│   └── prompt-build.schema.json
├── examples/
│   ├── prompt-ir/
│   └── prompt-build/
├── tests/
│   └── non-conformant/
├── scripts/
│   ├── validate.py
│   ├── validate_prompt_ir.py
│   └── test_validator.py
├── LICENSE
└── README.md
```

## Install

From Claude Code:

```text
/plugin marketplace add https://github.com/canstralian/rif-runtime-marketplace.git
/plugin install rif-runtime@rif-runtime-marketplace
```

After installation, skills are namespaced by plugin:

```text
/rif-runtime:architecture-review
/rif-runtime:constitution-guardian
/rif-runtime:documentation-engine
/rif-runtime:governance-review
/rif-runtime:knowledge-engine
/rif-runtime:prompt-audit
/rif-runtime:prompt-compiler
/rif-runtime:provider-review
/rif-runtime:release-manager
/rif-runtime:replay-analysis
/rif-runtime:rif-runtime
/rif-runtime:run-rif-runtime
```

## Marketplace design

The marketplace is intentionally separated from the RIF Runtime application repository.

**Marketplace**
→ catalog and distribution

**Plugin**
→ installable Claude Code capability boundary

**Skills**
→ individual runtime capabilities

This makes it possible to add future plugins without turning the marketplace into a monolith.

## Specifications

The repository carries the contracts the plugin's skills are bound to:

| Document | Defines |
|---|---|
| [`docs/SKILL-CONTRACT.md`](docs/SKILL-CONTRACT.md) | The boundary between a marketplace skill and the RIF Runtime. |
| [`docs/SKILL-MAPPING.md`](docs/SKILL-MAPPING.md) | Which capability each skill owns, and what it must not own. |
| [`docs/PROMPT-IR.md`](docs/PROMPT-IR.md) | PromptIR: the layered, provenance-carrying IR the runtime compiles before invoking a model, and the `PromptBuild` audit artifact. |

PromptIR treats a prompt as a compilation target rather than a string: instruction
authority is resolved and logged, context is data that can never be promoted to
instruction without an attributed decision, reasoning effort is a budgeted resource
with a recorded justification, and every invocation leaves a replayable artifact.

Machine-readable schemas live in [`schemas/`](schemas), conformant examples in
[`examples/`](examples), and deliberately non-conformant fixtures in
[`tests/non-conformant/`](tests/non-conformant).

## Versioning

The marketplace uses `1.0.0`; the `rif-runtime` plugin uses `1.1.0`.

Bump the plugin version whenever its distributable behavior changes. `scripts/validate.py`
enforces that `plugin.json` and the marketplace entry agree.

## Validation

With Claude Code installed, validate the marketplace from the repository root using:

```bash
claude plugin validate .
```

Structural and conformance checks run without Claude Code and without third-party
dependencies:

```bash
python3 scripts/validate.py             # marketplace, plugin, and skill structure
python3 scripts/validate_prompt_ir.py   # PromptIR/PromptBuild conformance (examples/)
python3 scripts/test_validator.py       # proves the conformance checker rejects known defects
```

Then test installation locally:

```text
/plugin marketplace add .
/plugin install rif-runtime@rif-runtime-marketplace
```

## License

MIT
