#!/usr/bin/env python3
"""Prove the PromptIR conformance checker rejects what it claims to reject.

Each fixture in tests/non-conformant/ carries exactly one injected defect.
tests/non-conformant/expected.json records the invariant code that defect must
trigger. This test asserts the checker reports it — and that the conformant
examples in examples/ still pass cleanly.

Usage:
    python3 scripts/test_validator.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_prompt_ir import check_file  # noqa: E402

FIXTURES = ROOT / "tests" / "non-conformant"
EXAMPLES = ROOT / "examples"


def codes(messages: list[str]) -> set[str]:
    found = set()
    for message in messages:
        match = re.match(r"\[([A-Z0-9-]+)\]", message)
        if match:
            found.add(match.group(1))
    return found


def main() -> int:
    failures: list[str] = []
    checked = 0

    expected = json.loads((FIXTURES / "expected.json").read_text())
    for name, spec in sorted(expected.items()):
        path = FIXTURES / name
        if not path.is_file():
            failures.append(f"{name}: fixture missing")
            continue
        report = check_file(path)
        checked += 1
        if report is None:
            failures.append(f"{name}: not recognised as a PromptIR or PromptBuild document")
            continue
        reported = codes(report.errors)
        missing = set(spec["expect"]) - reported
        if missing:
            failures.append(
                f"{name}: expected {sorted(missing)} but the checker reported "
                f"{sorted(reported) or 'nothing'} — {spec['note']}"
            )
        elif not report.errors:
            failures.append(f"{name}: fixture accepted; it must be rejected")

    for path in sorted(EXAMPLES.rglob("*.json")):
        report = check_file(path)
        checked += 1
        if report is None:
            failures.append(f"{path.name}: not recognised as a PromptIR or PromptBuild document")
        elif report.errors or report.warnings:
            findings = report.errors + report.warnings
            failures.append(f"{path.name}: conformant example produced findings: {findings}")

    for failure in failures:
        print(f"FAIL  {failure}")
    if failures:
        print(f"\n{len(failures)} failure(s) across {checked} document(s).")
        return 1
    print(f"OK    {checked} document(s): every fixture rejected for its recorded invariant, "
          "every example clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
