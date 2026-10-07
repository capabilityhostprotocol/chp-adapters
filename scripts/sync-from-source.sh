#!/usr/bin/env bash
# Sync the PUBLIC adapter source from the authoritative (private) chp-dev checkout into this public
# monorepo. chp-dev stays the governed source of truth; this repo is its curated public mirror + the
# PyPI publish surface (analogous to chp-core's sync-to-public.sh). Run from the repo root:
#
#   CHP_DEV_ROOT=/path/to/chp-dev bash scripts/sync-from-source.sh
#
# Copies ONLY clean source (pyproject, LICENSE/NOTICE/README, package *.py, trust-anchor *.der/README,
# tests *.py) and FAILS CLOSED if any forbidden artifact (wheels, sqlite, .chp, __pycache__, logs)
# would be published. Review `git status` / `git diff` afterward, then commit + tag to release.
set -euo pipefail

CHP_DEV_ROOT="${CHP_DEV_ROOT:-$HOME/Projects/capabilityhostprotocol/chp-dev}"
SRC="$CHP_DEV_ROOT/packages"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# The curated set of adapters published publicly. Add a package here to open-source it; NEVER add a
# private product adapter (legal, agency, market, …).
PUBLIC_ADAPTERS=(
  chp-adapter-safety
  chp-adapter-audit
  chp-adapter-http
  chp-adapter-filesystem
  chp-adapter-github
  chp-adapter-radicle
  chp-adapter-process
  chp-adapter-composition
  chp-adapter-planning
  chp-adapter-jobs
  chp-adapter-mlx
  chp-adapter-delegation
  chp-adapter-mcp
  chp-adapter-huggingface
  chp-adapter-git
  chp-adapter-host
  chp-adapter-conformance
)

[ -d "$SRC" ] || { echo "chp-dev packages not found at $SRC (set CHP_DEV_ROOT)"; exit 2; }

for a in "${PUBLIC_ADAPTERS[@]}"; do
  s="$SRC/$a"; pkg="${a//-/_}"; d="$ROOT/packages/$a"
  [ -d "$s" ] || { echo "SKIP $a (not in source)"; continue; }
  echo "== sync $a =="
  rm -rf "$d"; mkdir -p "$d/$pkg" "$d/tests"
  cp "$s/pyproject.toml" "$d/"
  for f in LICENSE NOTICE README.md; do [ -f "$s/$f" ] && cp "$s/$f" "$d/"; done
  find "$s/$pkg" -maxdepth 1 -name '*.py' -exec cp {} "$d/$pkg/" \;
  if [ -d "$s/$pkg/trust_anchors" ]; then
    mkdir -p "$d/$pkg/trust_anchors"
    cp "$s/$pkg/trust_anchors/"*.der "$s/$pkg/trust_anchors/"*.md "$d/$pkg/trust_anchors/" 2>/dev/null || true
  fi
  [ -d "$s/tests" ] && find "$s/tests" -maxdepth 1 -name '*.py' -exec cp {} "$d/tests/" \;
done

echo "== hygiene audit (FAIL if any forbidden artifact) =="
bad=$(find "$ROOT/packages" -type f \( -name '*.whl' -o -name '*.sqlite' -o -name '*.sqlite3' \
      -o -name '*.pyc' -o -path '*/.chp/*' -o -name '*.log' -o -name '*.egg-info' \) || true)
if [ -n "$bad" ]; then echo "FORBIDDEN artifacts staged — aborting:"; echo "$bad"; exit 1; fi
echo "clean. Review 'git diff', then: git commit; git tag <package>-v<version>; git push --tags"
