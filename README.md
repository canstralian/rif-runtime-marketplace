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
│           ├── provider-review/
│           ├── release-manager/
│           ├── replay-analysis/
│           ├── rif-runtime/
│           └── run-rif-runtime/
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

## Versioning

The marketplace and plugin currently use `1.0.0`.

Bump the plugin version whenever its distributable behavior changes.

## Validation

With Claude Code installed, validate the marketplace from the repository root using:

```bash
claude plugin validate .
```

Then test installation locally:

```text
/plugin marketplace add .
/plugin install rif-runtime@rif-runtime-marketplace
```

## License

MIT
