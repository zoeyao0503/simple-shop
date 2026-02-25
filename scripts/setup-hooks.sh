#!/usr/bin/env bash
#
# Activate SnooCommerce pre-commit hooks.
# This overrides the global core.hooksPath for THIS REPO ONLY so that our
# project hooks run (while still chaining the corporate /opt/reddit hook).
#
# Usage:  bash scripts/setup-hooks.sh
#
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.githooks"

if [ ! -x "$HOOKS_DIR/pre-commit" ]; then
  echo "ERROR: $HOOKS_DIR/pre-commit not found or not executable."
  exit 1
fi

git config --local core.hooksPath .githooks
echo "Done — git hooks now point to .githooks/"
echo "The corporate /opt/reddit hook is still chained automatically."
echo ""
echo "To undo:  git config --local --unset core.hooksPath"
