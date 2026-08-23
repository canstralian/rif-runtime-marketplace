#!/usr/bin/env python3
"""Conformance checker for RIF PromptIR and PromptBuild documents.

Enforces the structural contract of schemas/prompt-ir.schema.json and
schemas/prompt-build.schema.json plus the invariants in docs/PROMPT-IR.md that
can be checked mechanically: instruction hash correctness, authority
resolution, provenance completeness, untrusted-context isolation, reasoning
justification traceability, canonical hash reproduction, and PromptBuild
resolution coverage.

Standard library only. If `jsonschema` happens to be installed it is used as an
additional structural pass; it is never required.

Usage:
    python3 scripts/validate_prompt_ir.py [path ...]      # default: examples/
    python3 scripts/validate_prompt_ir.py --strict [path] # warnings fail too
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"

AUTHORITY_RANKS = ["system", "developer", "user", "assistant", "tool"]
RANK_ORDER = {name: index for index, name in enumerate(AUTHORITY_RANKS)}
EFFORTS = ["minimal", "low", "medium", "high"]
EFFORT_ORDER = {name: index for index, name in enumerate(EFFORTS)}
VERIFICATION_MODES = ["none", "minimal", "selective", "required"]
TOOL_POLICIES = ["denied", "constrained", "allowed"]
CONTEXT_KINDS = [
    "evidence",
    "memory",
    "tool_output",
    "document",
    "user_state",
    "runtime_state",
]
OUTPUT_FORMATS = ["text", "structured", "json_schema"]

# docs/PROMPT-IR.md §6 reference profiles. Advisory: deviations warn.
MODE_PROFILES = {
    "normal": {"effort": "high", "verification": "required", "tools": "allowed"},
    "maintenance": {"effort": "medium", "verification": "selective", "tools": "constrained"},
    "recovery": {"effort": "low", "verification": "minimal", "tools": "denied"},
}


class Report:
    """Collects findings for one document."""

    def __init__(self, path: Path, kind: str) -> None:
        self.path = path
        self.kind = kind
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, invariant: str, message: str) -> None:
        self.errors.append(f"[{invariant}] {message}")

    def warn(self, invariant: str, message: str) -> None:
        self.warnings.append(f"[{invariant}] {message}")


def canonical_bytes(document: Any) -> bytes:
    """Canonical serialization per INV-COMPILE-1."""
    return json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_of(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_hash(document: dict) -> str:
    body = {key: value for key, value in document.items() if key != "canonical_hash"}
    return sha256_of(canonical_bytes(body))


def _require(report: Report, obj: dict, keys: list[str], where: str, invariant: str) -> bool:
    ok = True
    for key in keys:
        if key not in obj:
            report.error(invariant, f"{where}: missing required field '{key}'")
            ok = False
    return ok


def _enum(report: Report, value: Any, allowed: list[str], where: str, invariant: str) -> bool:
    if value not in allowed:
        report.error(invariant, f"{where}: {value!r} is not one of {allowed}")
        return False
    return True


def check_prompt_ir(doc: Any, report: Report, prefix: str = "") -> None:
    """Validate one PromptIR document in place, appending findings to report."""
    where = prefix or "PromptIR"
    if not isinstance(doc, dict):
        report.error("SCHEMA", f"{where}: document is not an object")
        return

    _require(
        report,
        doc,
        ["promptir_version", "authority", "instructions", "reasoning", "output"],
        where,
        "SCHEMA",
    )

    version = doc.get("promptir_version")
    if isinstance(version, str):
        parts = version.split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            report.error("SCHEMA", f"{where}: promptir_version {version!r} is not MAJOR.MINOR.PATCH")

    # --- authority declarations -------------------------------------------
    authorities = doc.get("authority")
    authority_rank: dict[str, str] = {}
    if not isinstance(authorities, list) or not authorities:
        report.error("SCHEMA", f"{where}.authority: must be a non-empty array")
        authorities = []
    for index, entry in enumerate(authorities):
        at = f"{where}.authority[{index}]"
        if not isinstance(entry, dict):
            report.error("SCHEMA", f"{at}: not an object")
            continue
        if not _require(report, entry, ["id", "rank"], at, "SCHEMA"):
            continue
        if _enum(report, entry["rank"], AUTHORITY_RANKS, f"{at}.rank", "INV-AUTH-1"):
            if entry["id"] in authority_rank:
                report.error("INV-AUTH-1", f"{at}: duplicate authority id {entry['id']!r}")
            else:
                authority_rank[entry["id"]] = entry["rank"]

    # --- instructions ------------------------------------------------------
    instructions = doc.get("instructions")
    if instructions is None:
        instructions = []
    if not isinstance(instructions, list):
        report.error("SCHEMA", f"{where}.instructions: must be an array")
        instructions = []

    instruction_ids: set[str] = set()
    by_id: dict[str, dict] = {}
    for index, entry in enumerate(instructions):
        at = f"{where}.instructions[{index}]"
        if not isinstance(entry, dict):
            report.error("SCHEMA", f"{at}: not an object")
            continue
        if not _require(report, entry, ["id", "text", "source", "authority", "hash"], at, "SCHEMA"):
            continue

        ident = entry["id"]
        at = f"{where}.instructions[{ident}]"
        if ident in instruction_ids:
            report.error("INV-PROV-1", f"{at}: duplicate instruction id")
        instruction_ids.add(ident)
        by_id[ident] = entry

        # INV-PROV-2: hash is sha256 over the UTF-8 bytes of text.
        expected = sha256_of(str(entry["text"]).encode("utf-8"))
        if entry["hash"] != expected:
            report.error(
                "INV-PROV-2",
                f"{at}: hash does not match text (declared {entry['hash']}, computed {expected})",
            )

        # INV-PROV-3: source must resolve to a declared authority.
        source = entry["source"]
        if source not in authority_rank:
            report.error(
                "INV-PROV-3",
                f"{at}: source {source!r} is not a declared authority[].id",
            )
        elif _enum(report, entry["authority"], AUTHORITY_RANKS, f"{at}.authority", "INV-AUTH-1"):
            declared = authority_rank[source]
            if entry["authority"] != declared:
                report.error(
                    "INV-AUTH-1",
                    f"{at}: claims rank {entry['authority']!r} but its source "
                    f"{source!r} is declared {declared!r}",
                )

        if not entry.get("rationale"):
            report.warn("INV-PROV-4", f"{at}: no rationale — the artifact cannot explain itself")
        # Policy-rank instructions come from versioned sets; a live user or tool
        # turn legitimately has none.
        if entry.get("authority") in ("system", "developer") and not entry.get("version"):
            report.warn(
                "INV-PROV-1",
                f"{at}: policy-rank instruction has no version — drift cannot be detected on replay",
            )

    # INV-AUTH-3: conflicts must be resolvable.
    for ident, entry in by_id.items():
        at = f"{where}.instructions[{ident}]"
        for other_id in entry.get("conflicts_with", []) or []:
            if other_id not in by_id:
                report.error("INV-AUTH-3", f"{at}: conflicts_with references unknown id {other_id!r}")
                continue
            other = by_id[other_id]
            same_rank = entry.get("authority") == other.get("authority")
            same_priority = entry.get("priority") == other.get("priority")
            if same_rank and same_priority:
                report.error(
                    "INV-AUTH-3",
                    f"{at}: conflicts with {other_id!r} at equal rank and priority — "
                    "resolution is arbitrary, compilation must fail",
                )

    # --- context -----------------------------------------------------------
    context = doc.get("context") or {}
    context_ids: set[str] = set()
    if not isinstance(context, dict):
        report.error("SCHEMA", f"{where}.context: must be an object")
        context = {}
    items = context.get("items") or []
    if not isinstance(items, list):
        report.error("SCHEMA", f"{where}.context.items: must be an array")
        items = []
    for index, item in enumerate(items):
        at = f"{where}.context.items[{index}]"
        if not isinstance(item, dict):
            report.error("SCHEMA", f"{at}: not an object")
            continue
        if not _require(report, item, ["id", "kind", "trust"], at, "SCHEMA"):
            continue
        at = f"{where}.context.items[{item['id']}]"
        if item["id"] in context_ids:
            report.error("SCHEMA", f"{at}: duplicate context item id")
        context_ids.add(item["id"])

        _enum(report, item["kind"], CONTEXT_KINDS, f"{at}.kind", "SCHEMA")
        _enum(report, item["trust"], ["trusted", "untrusted"], f"{at}.trust", "INV-CTX-1")

        # INV-CTX-2: this is the shape a successful injection takes.
        if "authority" in item:
            report.error(
                "INV-CTX-2",
                f"{at}: context item carries an 'authority' field — context is data, not instruction",
            )
        if item["kind"] == "tool_output" and item.get("trust") == "trusted":
            report.error(
                "INV-CTX-1",
                f"{at}: tool output is always untrusted",
            )
        if item["kind"] in ("evidence", "document") and item.get("trust") == "trusted":
            report.warn(
                "INV-CTX-1",
                f"{at}: {item['kind']} marked trusted — confirm it originates in governed runtime state",
            )
        if "content" not in item and "evidence_id" not in item:
            report.error("SCHEMA", f"{at}: has neither 'content' nor 'evidence_id'")
        provenance = item.get("provenance") or {}
        if not provenance.get("selector") and provenance.get("relevance") is None:
            report.warn(
                "INV-CTX-3",
                f"{at}: no selector or relevance — context selection is not auditable",
            )

    # --- examples ----------------------------------------------------------
    for index, example in enumerate(doc.get("examples") or []):
        at = f"{where}.examples[{index}]"
        if not isinstance(example, dict):
            report.error("SCHEMA", f"{at}: not an object")
            continue
        _require(report, example, ["id", "input", "output"], at, "SCHEMA")
        if "authority" in example:
            report.error("INV-LAYER-2", f"{at}: examples carry no authority")
        for ref in example.get("demonstrates", []) or []:
            if ref not in instruction_ids:
                report.error("INV-LAYER-1", f"{at}: demonstrates unknown instruction {ref!r}")

    # --- reasoning policy --------------------------------------------------
    reasoning = doc.get("reasoning")
    if not isinstance(reasoning, dict):
        report.error("SCHEMA", f"{where}.reasoning: must be an object")
        reasoning = {}
    else:
        _require(report, reasoning, ["effort", "justification"], f"{where}.reasoning", "SCHEMA")

    effort = reasoning.get("effort")
    if effort is not None:
        _enum(report, effort, EFFORTS, f"{where}.reasoning.effort", "SCHEMA")

    justification = reasoning.get("justification")
    if justification is not None and justification not in authority_rank and justification not in instruction_ids:
        report.error(
            "INV-REASON-1",
            f"{where}.reasoning.justification: {justification!r} does not reference a declared "
            "authority or instruction — the effort level has no traceable reason",
        )

    verification = reasoning.get("verification") or {}
    if verification:
        if "mode" not in verification:
            report.error("SCHEMA", f"{where}.reasoning.verification: missing 'mode'")
        else:
            _enum(
                report,
                verification["mode"],
                VERIFICATION_MODES,
                f"{where}.reasoning.verification.mode",
                "SCHEMA",
            )

    tools = reasoning.get("tools") or {}
    tool_policy = tools.get("policy")
    if tools:
        if tool_policy is None:
            report.error("SCHEMA", f"{where}.reasoning.tools: missing 'policy'")
        else:
            _enum(report, tool_policy, TOOL_POLICIES, f"{where}.reasoning.tools.policy", "SCHEMA")
        if tool_policy == "denied" and tools.get("allow"):
            report.error(
                "INV-REASON-2",
                f"{where}.reasoning.tools: policy is 'denied' but an allow list is present",
            )

    # INV-REASON-2: policy must fit the budget envelope.
    budget = doc.get("budget") or {}
    max_effort = budget.get("max_effort")
    if max_effort in EFFORT_ORDER and effort in EFFORT_ORDER:
        if EFFORT_ORDER[effort] > EFFORT_ORDER[max_effort]:
            report.error(
                "INV-REASON-2",
                f"{where}.reasoning.effort {effort!r} exceeds budget.max_effort {max_effort!r}",
            )
    if budget.get("max_tool_calls") == 0 and tool_policy in ("allowed", "constrained"):
        report.error(
            "INV-REASON-2",
            f"{where}.reasoning.tools.policy is {tool_policy!r} — which still permits tool "
            "calls — but budget.max_tool_calls is 0",
        )

    # Reference profile deviation (advisory, docs/PROMPT-IR.md §6).
    mode = (doc.get("intent") or {}).get("operating_mode")
    profile = MODE_PROFILES.get(mode) if isinstance(mode, str) else None
    if profile:
        if effort in EFFORT_ORDER and EFFORT_ORDER[effort] > EFFORT_ORDER[profile["effort"]]:
            report.warn(
                "PROFILE",
                f"{where}: effort {effort!r} exceeds the {mode!r} profile ({profile['effort']!r})",
            )
        if tool_policy and TOOL_POLICIES.index(tool_policy) > TOOL_POLICIES.index(profile["tools"]):
            report.warn(
                "PROFILE",
                f"{where}: tool policy {tool_policy!r} exceeds the {mode!r} profile "
                f"({profile['tools']!r})",
            )
        mode_verification = verification.get("mode")
        if (
            mode_verification
            and VERIFICATION_MODES.index(mode_verification) < VERIFICATION_MODES.index(profile["verification"])
        ):
            report.warn(
                "PROFILE",
                f"{where}: verification {mode_verification!r} is weaker than the {mode!r} "
                f"profile ({profile['verification']!r})",
            )

    # --- output contract ---------------------------------------------------
    output = doc.get("output")
    if not isinstance(output, dict):
        report.error("SCHEMA", f"{where}.output: must be an object")
    else:
        if "format" not in output:
            report.error("SCHEMA", f"{where}.output: missing 'format'")
        else:
            _enum(report, output["format"], OUTPUT_FORMATS, f"{where}.output.format", "SCHEMA")
            if output["format"] == "json_schema" and not output.get("schema_ref"):
                report.error(
                    "SCHEMA",
                    f"{where}.output: format 'json_schema' requires 'schema_ref'",
                )
        if not output.get("uncertainty_representation"):
            report.warn(
                "SCHEMA",
                f"{where}.output: no uncertainty_representation — the response has no defined "
                "way to report insufficient evidence",
            )

    # --- canonical hash ----------------------------------------------------
    if "canonical_hash" in doc:
        expected = canonical_hash(doc)
        if doc["canonical_hash"] != expected:
            report.error(
                "INV-COMPILE-1",
                f"{where}.canonical_hash: declared {doc['canonical_hash']}, computed {expected}",
            )
    else:
        report.warn("INV-COMPILE-1", f"{where}: no canonical_hash — the build is not replay-verifiable")


def _rank_index(instruction: dict) -> int:
    """Lower index is higher authority; unknown ranks sort last."""
    return RANK_ORDER.get(instruction.get("authority"), len(AUTHORITY_RANKS))


def _check_resolution_order(report: Report, at: str, loser: dict, winner: dict) -> None:
    """A suppressed instruction must not outrank the one that superseded it."""
    loser_rank = _rank_index(loser)
    winner_rank = _rank_index(winner)
    if winner_rank > loser_rank:
        report.error(
            "INV-AUTH-2",
            f"{at}: {loser['id']!r} ({loser.get('authority')}) was suppressed in favour of "
            f"{winner['id']!r} ({winner.get('authority')}) — the lower-authority instruction won",
        )
        return
    if winner_rank == loser_rank:
        loser_priority = loser.get("priority")
        winner_priority = winner.get("priority")
        if (
            isinstance(loser_priority, int)
            and isinstance(winner_priority, int)
            and winner_priority < loser_priority
        ):
            report.error(
                "INV-AUTH-3",
                f"{at}: {loser['id']!r} (priority {loser_priority}) was suppressed in favour of "
                f"{winner['id']!r} (priority {winner_priority}) at equal rank — the lower "
                "priority won",
            )


def check_prompt_build(doc: dict, report: Report) -> None:
    where = "PromptBuild"
    _require(report, doc, ["build_id", "created_at", "prompt_ir", "resolution", "provider"], where, "SCHEMA")

    prompt_ir = doc.get("prompt_ir")
    if isinstance(prompt_ir, dict):
        check_prompt_ir(prompt_ir, report, prefix="PromptBuild.prompt_ir")
    else:
        report.error("SCHEMA", f"{where}.prompt_ir: must be a PromptIR object")
        prompt_ir = {}

    instructions = prompt_ir.get("instructions") or []
    instruction_ids = {
        entry["id"] for entry in instructions if isinstance(entry, dict) and "id" in entry
    }
    by_id = {entry["id"]: entry for entry in instructions if isinstance(entry, dict) and "id" in entry}
    authority_ids = {
        entry["id"]: entry.get("rank")
        for entry in (prompt_ir.get("authority") or [])
        if isinstance(entry, dict) and "id" in entry
    }
    context_ids = {
        item["id"]
        for item in ((prompt_ir.get("context") or {}).get("items") or [])
        if isinstance(item, dict) and "id" in item
    }

    resolution = doc.get("resolution")
    if not isinstance(resolution, dict):
        report.error("SCHEMA", f"{where}.resolution: must be an object")
        return
    _require(report, resolution, ["admitted", "suppressed"], f"{where}.resolution", "SCHEMA")

    admitted = resolution.get("admitted") or []
    suppressed = resolution.get("suppressed") or []
    suppressed_ids = [
        entry.get("id") for entry in suppressed if isinstance(entry, dict)
    ]

    # INV-BUILD-1: exactly-once coverage.
    seen: set[str] = set()
    for ident in list(admitted) + suppressed_ids:
        if ident in seen:
            report.error("INV-BUILD-1", f"{where}.resolution: instruction {ident!r} appears twice")
        seen.add(ident)
        if ident not in instruction_ids:
            report.error(
                "INV-BUILD-1",
                f"{where}.resolution: {ident!r} is not an instruction in prompt_ir",
            )
    for ident in sorted(instruction_ids - seen):
        report.error(
            "INV-BUILD-1",
            f"{where}.resolution: instruction {ident!r} is neither admitted nor suppressed — "
            "it was lost by the compiler",
        )

    # INV-BUILD-2: suppression is explained.
    for index, entry in enumerate(suppressed):
        at = f"{where}.resolution.suppressed[{index}]"
        if not isinstance(entry, dict):
            report.error("SCHEMA", f"{at}: not an object")
            continue
        if not entry.get("reason"):
            report.error("INV-BUILD-2", f"{at}: suppression without a reason")
        ident = entry.get("id")
        conflicts = (by_id.get(ident) or {}).get("conflicts_with") or []
        if conflicts and not entry.get("superseded_by"):
            report.error(
                "INV-BUILD-2",
                f"{at}: {ident!r} declares conflicts_with but no superseded_by is recorded",
            )
        winner = entry.get("superseded_by")
        if winner is not None and winner not in admitted:
            report.error(
                "INV-BUILD-2",
                f"{at}: superseded_by {winner!r} is not an admitted instruction",
            )

        # INV-AUTH-2/3: a resolution log that records a winner is not evidence that the
        # winner was entitled to win. Check the ranks of the recorded pair only —
        # `superseded_by` is the claim of victory. A conflict peer that merely remains
        # admitted claimed nothing: once the loser is gone that conflict is moot, and
        # its rank says nothing about who beat whom.
        if winner is not None and winner in by_id and ident in by_id:
            _check_resolution_order(report, at, by_id[ident], by_id[winner])

    # INV-AUTH-2: a declared conflict is not resolved by admitting both sides.
    admitted_set = set(admitted)
    reported_pairs: set[tuple[str, str]] = set()
    for ident in admitted:
        entry = by_id.get(ident)
        if not entry:
            continue
        for other in entry.get("conflicts_with") or []:
            # A conflict is normally declared on one side only, so dedupe by the pair
            # itself rather than by which id sorts first.
            pair = (ident, other) if ident < other else (other, ident)
            if other not in admitted_set or other not in by_id or pair in reported_pairs:
                continue
            reported_pairs.add(pair)
            report.error(
                "INV-AUTH-2",
                f"{where}.resolution: {ident!r} and {other!r} declare a conflict but both "
                "were admitted — the conflict was never resolved",
            )

    # INV-BUILD-3: promotion is attributed to an entitled authority.
    for index, entry in enumerate(resolution.get("promoted") or []):
        at = f"{where}.resolution.promoted[{index}]"
        if not isinstance(entry, dict):
            report.error("SCHEMA", f"{at}: not an object")
            continue
        if not _require(report, entry, ["context_item_id", "admitted_by", "reason"], at, "INV-BUILD-3"):
            continue
        if entry["context_item_id"] not in context_ids:
            report.error("INV-BUILD-3", f"{at}: unknown context item {entry['context_item_id']!r}")
        rank = authority_ids.get(entry["admitted_by"])
        if rank is None:
            report.error(
                "INV-BUILD-3",
                f"{at}: admitted_by {entry['admitted_by']!r} is not a declared authority",
            )
        elif rank not in ("system", "developer"):
            report.error(
                "INV-BUILD-3",
                f"{at}: promotion admitted by {rank!r} authority — only system or developer "
                "may promote context to instruction rank",
            )
        if entry.get("instruction_id") and entry["instruction_id"] not in instruction_ids:
            report.error("INV-BUILD-3", f"{at}: instruction_id {entry['instruction_id']!r} not in prompt_ir")

    for index, entry in enumerate(doc.get("context_selection") or []):
        at = f"{where}.context_selection[{index}]"
        if not isinstance(entry, dict) or "item_id" not in entry:
            report.error("SCHEMA", f"{at}: missing 'item_id'")
        elif entry["item_id"] not in context_ids:
            report.error("SCHEMA", f"{at}: unknown context item {entry['item_id']!r}")

    provider = doc.get("provider")
    if isinstance(provider, dict):
        _require(
            report,
            provider,
            ["provider", "model", "provider_payload_hash"],
            f"{where}.provider",
            "INV-ADAPT-3",
        )
        payload_hash = provider.get("provider_payload_hash", "")
        if payload_hash and not (
            payload_hash.startswith("sha256:") and len(payload_hash) == 71
        ):
            report.error(
                "INV-ADAPT-3",
                f"{where}.provider.provider_payload_hash: {payload_hash!r} is not sha256:<64 hex>",
            )
        # INV-STATE-1: the provider handle is substrate, not memory.
        if provider.get("continuation_handle") and "replayable" not in prompt_ir:
            report.warn(
                "INV-STATE-1",
                f"{where}: a provider continuation handle is recorded but prompt_ir.replayable "
                "is not declared — state it explicitly",
            )
    if prompt_ir.get("replayable") is False:
        report.warn(
            "INV-STATE-1",
            f"{where}: prompt_ir.replayable is false — this build cannot be reconstructed from "
            "runtime-owned state",
        )

    required_verification = (
        ((prompt_ir.get("reasoning") or {}).get("verification") or {}).get("mode") == "required"
    )
    if required_verification:
        performed = (doc.get("verification") or {}).get("performed")
        if performed is not True:
            report.error(
                "INV-REASON-3",
                f"{where}: reasoning.verification.mode is 'required' but no verification was performed",
            )


def try_jsonschema(path: Path, doc: Any, report: Report) -> bool:
    """Optional extra pass. Returns True when jsonschema actually ran."""
    try:
        import jsonschema  # type: ignore
        from referencing import Registry, Resource  # type: ignore
    except Exception:
        return False
    try:
        ir_schema = json.loads((SCHEMA_DIR / "prompt-ir.schema.json").read_text())
        build_schema = json.loads((SCHEMA_DIR / "prompt-build.schema.json").read_text())
        registry = Registry().with_resources(
            [
                (ir_schema["$id"], Resource.from_contents(ir_schema)),
                (build_schema["$id"], Resource.from_contents(build_schema)),
            ]
        )
        schema = build_schema if report.kind == "PromptBuild" else ir_schema
        validator = jsonschema.Draft202012Validator(schema, registry=registry)
        for error in validator.iter_errors(doc):
            location = "/".join(str(part) for part in error.absolute_path) or "<root>"
            report.error("SCHEMA", f"jsonschema: {location}: {error.message}")
        return True
    except Exception as exc:  # pragma: no cover - optional path
        report.warn("SCHEMA", f"jsonschema pass skipped: {exc}")
        return False


def classify(doc: Any) -> str | None:
    if not isinstance(doc, dict):
        return None
    if "prompt_ir" in doc or "build_id" in doc:
        return "PromptBuild"
    if "promptir_version" in doc:
        return "PromptIR"
    return None


def check_file(path: Path) -> Report | None:
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        report = Report(path, "unknown")
        report.error("SCHEMA", f"invalid JSON: {exc}")
        return report

    kind = classify(doc)
    if kind is None:
        return None

    report = Report(path, kind)
    if kind == "PromptBuild":
        check_prompt_build(doc, report)
    else:
        check_prompt_ir(doc, report)
    try_jsonschema(path, doc, report)
    return report


def collect(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.json")))
        elif path.is_file():
            files.append(path)
        else:
            print(f"warning: {path} does not exist", file=sys.stderr)
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", default=None, help="files or directories (default: examples/)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args(argv)

    targets = [Path(p) for p in args.paths] if args.paths else [ROOT / "examples"]
    files = collect(targets)

    reports = [report for report in (check_file(path) for path in files) if report is not None]
    if not reports:
        print("No PromptIR or PromptBuild documents found.")
        return 0

    errors = warnings = 0
    for report in reports:
        rel = report.path.relative_to(ROOT) if report.path.is_relative_to(ROOT) else report.path
        status = "FAIL" if report.errors else ("WARN" if report.warnings else "OK")
        print(f"{status:4}  {report.kind:12}  {rel}")
        for message in report.errors:
            print(f"        error   {message}")
        for message in report.warnings:
            print(f"        warning {message}")
        errors += len(report.errors)
        warnings += len(report.warnings)

    print(
        f"\n{len(reports)} document(s) checked: {errors} error(s), {warnings} warning(s)."
    )
    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
