#!/bin/bash
set -xe
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
"$SCRIPT_DIR/build.sh"
"$SCRIPT_DIR/test.sh"
"$SCRIPT_DIR/run.sh"