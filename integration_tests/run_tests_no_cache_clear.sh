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

cd "$SCRIPT_DIR/happy-test"
hatch run python -m happy_test

cd "$SCRIPT_DIR/missing-test"
hatch run python -m missing_test
