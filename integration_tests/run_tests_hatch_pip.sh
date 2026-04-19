#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Default to "hatch-dotenv" if no argument provided
HATCH_DOTENV_PACKAGE="${1:-hatch-dotenv}"

# Generate pyproject.toml from template
generate_pyproject() {
    local dir="$1"
    sed "s|{{HATCH_DOTENV_PACKAGE}}|$HATCH_DOTENV_PACKAGE|g" "$dir/pyproject.toml.in" > "$dir/pyproject.toml"
}

generate_pyproject "$SCRIPT_DIR/happy-test"
generate_pyproject "$SCRIPT_DIR/missing-test"
generate_pyproject "$SCRIPT_DIR/cross-env-test"

cd "$SCRIPT_DIR/happy-test"
pip uninstall hatch-dotenv -y || true
pip cache purge
hatch run python -m happy_test

cd "$SCRIPT_DIR/missing-test"
pip uninstall hatch-dotenv -y || true
pip cache purge
hatch run python -m missing_test

# Reproduces issue #2: a `secrets` env with fail-on-missing on a missing file
# must not block running the unrelated `default` env.
cd "$SCRIPT_DIR/cross-env-test"
pip uninstall hatch-dotenv -y || true
pip cache purge
hatch run python -m cross_env_test
