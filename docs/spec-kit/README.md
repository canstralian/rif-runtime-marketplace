# RIF Spec Kit

A set of documents that state what a marketplace skill's specification must
say about authority, scope, untrusted input, and refusal, and how close the
skills are today.

## What "Spec Kit" means here

Spec Kit v2.2 is a governance framework for agent and prompt specifications:
authority tiers T1 to T4, hard-block conditions, injection vectors A to I, a
35-criterion scorecard, and `GREENLIGHT` / `CONDITIONAL` / `SECURITY_FAIL`
gates. This kit applies it to the skill files under `plugins/*/skills/`.

This is **not** the GitHub Spec Kit scaffold (`.specify/`, `specs/`, a
constitution, plan, and tasks). Nothing here generates or consumes that layout.
If the scaffold is what is wanted, it is a different piece of work.

The framework's scoring definitions live in the `spec-kit-evaluator` skill, not
in this repository. The kit summarizes them where it must and does not copy
them.

## Documents

| Document | Normative | Purpose |
|---|---|---|
| [`PROFILE.md`](PROFILE.md) | Yes | What a skill must say. Tiers, hard blocks, vector defenses, output, runtime hand-off |
| [`TEMPLATE.md`](TEMPLATE.md) | No | The contract reference template plus the sections the profile adds, with wording to copy |
| [`ASSESSMENT.md`](ASSESSMENT.md) | No | A strict self-assessment of the twelve skills, the evidence, and the remediation order |

Read in that order for the requirement, then the wording, then the gap.

## Relationship to existing documents

| Document | Relationship |
|---|---|
| [`docs/SKILL-CONTRACT.md`](../SKILL-CONTRACT.md) | The profile adds to it and never relaxes it. The contract governs on any conflict |
| [`docs/SKILL-MAPPING.md`](../SKILL-MAPPING.md) | Owns each skill's boundary. The template's scope text comes from there |
| [`docs/PROMPT-IR-CONFORMANCE.md`](../PROMPT-IR-CONFORMANCE.md) | Source of the MUST / SHOULD / RUNTIME vocabulary |
| [`docs/adr/0001-agent-permission-policy.md`](../adr/0001-agent-permission-policy.md) | Same stance: a guardrail is not a boundary, and the document says what it does not buy |

## Two vocabularies, never mixed

| Words | Grade | Defined in |
|---|---|---|
| `pass`, `fail`, `conditional`, `insufficient evidence`, `not applicable` | What a skill concludes about its subject | Contract §7 |
| `GREENLIGHT`, `CONDITIONAL`, `SECURITY_FAIL` | Whether a skill's specification meets the kit | Spec Kit v2.2 |

`conditional` appears in both. They are different grades on different objects.
A skill file does not use the second set as an output status.

## State of adoption

No skill file has been edited to adopt the profile. At the commit named in
`ASSESSMENT.md`, all twelve skills are non-conformant and score `SECURITY_FAIL`
on the assessment's reading. The kit changes no behavior of the plugin, so it
carries no plugin version bump.

Adopting the profile means editing skills. That is a material change under
contract §14 and needs both plugin-version fields to move together.

## What this kit does not do

- It adds no CI check. The three scripts in `scripts/` do not read skill
  bodies, and the kit does not change that.
- It does not describe the runtime. Statements about runtime behavior are
  labelled inference unless that source was inspected.
- It does not replace independent scoring.
