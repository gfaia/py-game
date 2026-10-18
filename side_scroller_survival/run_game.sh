#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "$0")" && pwd)"
project_dir="$(cd "$script_dir/.." && pwd)"
python_bin="$project_dir/.venv-py312/bin/python"

if [[ ! -x "$python_bin" ]]; then
    echo "Python 3.12 game environment was not found: $python_bin" >&2
    exit 1
fi

cd "$script_dir"
exec "$python_bin" main.py
