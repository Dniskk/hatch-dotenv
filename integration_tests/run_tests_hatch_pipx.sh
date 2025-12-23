#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR/happy-test"
pipx runpip hatch uninstall hatch-dotenv -y
hatch run pip cache purge
hatch run python -m happy_test

cd "$SCRIPT_DIR/missing-test"
pipx runpip hatch uninstall hatch-dotenv -y
hatch run pip cache purge
hatch run python -m missing_test