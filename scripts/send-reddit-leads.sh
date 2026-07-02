#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SERVER_DIR="${SCRIPT_DIR}/../server"

if [ "$#" -eq 0 ]; then
  set -- --count 100
fi

exec python3 "$SERVER_DIR/manage.py" generate_reddit_leads "$@"
