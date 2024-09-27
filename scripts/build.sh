#!/bin/bash
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
pushd $SCRIPT_DIR
pushd ..

source .env
docker build -t github-bot .

popd
popd