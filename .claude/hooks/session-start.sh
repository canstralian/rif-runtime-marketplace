#!/bin/bash
# SessionStart hook for rif-runtime-marketplace.
#
# This repository has no dependencies to install: no package.json, no
# requirements.txt, no lockfile. The only code is scripts/validate.py, which
# imports json and pathlib from the standard library. So this hook installs
# nothing. It confirms the one assumption the repo makes (python3 on PATH) and
# runs the repo's only verification command, so a web session starts knowing
# whether the marketplace manifests are structurally sound.
#
# It always exits 0. A broken manifest must not block the session that would
# fix it; the failure is reported into the session instead.

set -uo pipefail

# Web sessions only; local checkouts start unchanged.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

if ! command -v python3 >/dev/null 2>&1; then
  echo "session-start: python3 not on PATH; scripts/validate.py cannot run."
  exit 0
fi

if [ ! -f scripts/validate.py ]; then
  echo "session-start: scripts/validate.py not found; skipping manifest validation."
  exit 0
fi

# Deliberately not 'python3 -O': that strips the script's asserts and it then
# reports OK on a broken manifest. See the Validation section of CLAUDE.md.
if validate_output=$(python3 scripts/validate.py 2>&1); then
  echo "session-start: ${validate_output}"
else
  echo "session-start: scripts/validate.py FAILED — the marketplace manifests are broken."
  echo "${validate_output}"
  echo "session-start: continuing anyway so this session can fix it."
fi
