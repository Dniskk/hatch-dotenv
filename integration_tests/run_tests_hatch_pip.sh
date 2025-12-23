#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd "$SCRIPT_DIR/happy-test"
pip uninstall hatch-dotenv -y
pip cache purge
hatch run python -m happy_test

cd "$SCRIPT_DIR/missing-test"
pip uninstall hatch-dotenv -y
pip cache purge
hatch run python -m missing_test