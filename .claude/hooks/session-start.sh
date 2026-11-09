#!/bin/bash
# SessionStart hook for rif-runtime-marketplace.
#
# This hook installs nothing. The catalog's own checks are three stdlib-only
# Python scripts in scripts/ with no requirements.txt and no Python lockfile, so
# there is nothing to install for them. It confirms python3 is on PATH and runs
# scripts/validate.py, so a web session starts knowing whether the marketplace
# manifests are structurally sound.
#
# It deliberately does NOT cover web/, which is a separate React + Vite app with
# its own package.json and npm dependencies, built by .github/workflows/pages.yml.
# Installing those here would add an npm install to every session start for work
# most sessions never touch. A session working on web/ installs them itself.
#
# It always exits 0. A broken manifest must not block the session that would
# fix it; the failure is reported into the session instead.

set -uo pipefail

# Web sessions only; local checkouts start unchanged.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if ! cd "${CLAUDE_PROJECT_DIR:-.}"; then
  echo "session-start: cannot enter the project directory; skipping manifest validation."
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "session-start: python3 not on PATH; scripts/validate.py cannot run."
  exit 0
fi

if [ ! -f scripts/validate.py ]; then
  echo "session-start: scripts/validate.py not found; skipping manifest validation."
  exit 0
fi

# -E ignores PYTHON* environment variables. Without it, a remote environment
# that exports PYTHONOPTIMIZE strips the script's asserts, and this hook then
# reports OK on a broken manifest — the same trap as running it under -O.
# Verified: with PYTHONOPTIMIZE=1 a version desync passes silently; with -E it
# fails as it should. See the Validation section of CLAUDE.md.
if validate_output=$(python3 -E scripts/validate.py 2>&1); then
  echo "session-start: ${validate_output}"
else
  echo "session-start: scripts/validate.py FAILED — the marketplace manifests are broken."
  echo "${validate_output}"
  echo "session-start: continuing anyway so this session can fix it."
fi
