# ADR-0001: Agent permission policy for `.claude/settings.json`

- **Status:** Accepted
- **Date:** 2026-11-13
- **Supersedes:** none
- **Superseded by:** none

## Context

`.claude/settings.json` entered this repository with the SessionStart hook and
carried a `hooks` block and nothing else. The ECC Tools PR Config Audit flags
that file on every commit of every pull request, with six findings:

| Severity | Finding |
|---|---|
| medium | No PreToolUse security hooks |
| low | Missing deny: `rm -rf` |
| low | Missing deny: `sudo` |
| low | Missing deny: `chmod 777` |
| low | Missing deny: `ssh` |
| low | Missing deny: `> /dev/` |

The findings repeat on each push, so the choice is to act on them or to decide
once, in writing, not to — leaving them unanswered means re-reading the same
report indefinitely and losing the signal if the audit ever reports something
new.

This is a **distribution catalog**: JSON manifests, Markdown skill definitions,
three stdlib-only Python checks, and a React site under `web/`. The RIF Runtime
itself does not execute here. An agent working in this repository edits
documents and runs validators; it has no deployment path, no production
credentials and no infrastructure to reach.

## Decision

Add a `permissions.deny` list to `.claude/settings.json` with **four** rules:

```json
"permissions": {
  "deny": [
    "Bash(rm -rf *)",
    "Bash(sudo *)",
    "Bash(chmod 777 *)",
    "Bash(ssh *)"
  ]
}
```

**Drop the fifth pattern, `> /dev/`.** It would be a self-inflicted wound: this
repository's own `.claude/hooks/session-start.sh` uses `command -v python3
>/dev/null 2>&1`, which is the ordinary idiom for a quiet existence check.
Denying the redirect would train every future contributor — human or agent — to
work around the rule rather than respect it, which is worse than not having it.
A rule that must routinely be bypassed teaches that rules are bypassable.

**Do not add a PreToolUse security hook.** The four deny rules cover the same
commands declaratively, in a file a reviewer can read in full in ten seconds. A
hook would add a second enforcement path, written in shell, that must be kept in
agreement with the first, and whose failure mode is silence. The repository has
no capability a hook would guard that the deny list does not already name.
Revisit if this repository ever gains a deployment or publishing step.

## Consequences

**What this buys.** The four highest-signal footguns are refused without a
prompt, in every permission mode, for every agent session in this repository.
Five of the six ECC findings stop recurring. The repository gains its first
ADR, and with it a place to record this class of decision.

**What it does not buy, stated plainly.** Permission rules are **prefix
matches**, not a sandbox. `Bash(rm -rf *)` refuses `rm -rf build/`, but not
`cd build && rm -rf .`, not `find . -delete`, and not a script that contains the
command. This is a guardrail against an obvious slip, not a security boundary,
and must not be cited as one. Real isolation is the container the session runs
in.

**Cost.** A legitimate `rm -rf` on a build directory now needs a different
spelling or an explicit allow rule. In a catalog repository with no build
artifacts outside `web/node_modules`, that cost is close to zero.

**The medium finding stays open by choice.** ECC will keep reporting "No
PreToolUse security hooks" on every commit. That is now a recorded decision
rather than an unread finding; this ADR is the answer to it.

## Alternatives considered

**A — Adopt all five patterns, including `> /dev/`.** Rejected: it breaks the
repository's own hook idiom, as above.

**B — Four rules, drop `> /dev/`.** Chosen.

**C — Add nothing; document that the audit does not apply.** Rejected. The four
rules cost one block of JSON and are genuinely the commands least likely to be
wanted here. "Not applicable" would have been an overstatement — `rm -rf` is
unwanted in a catalog repository whether or not a scanner asks for it.

## Revisit when

- This repository gains a deployment, publish or release-automation step.
- A deny rule is bypassed in practice rather than respected — the signal that
  the rule is wrong, not that the contributor is.
- Claude Code's permission syntax gains matching that is not prefix-based, at
  which point the "not a security boundary" caveat above may need revising.
