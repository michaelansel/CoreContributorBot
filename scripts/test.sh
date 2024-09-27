#!/bin/bash
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
pushd $SCRIPT_DIR
pushd ..

source .env
docker run -it --rm -e "GITHUB_TOKEN=$GITHUB_TOKEN" -e "OPENAI_API_KEY=$OPENAI_API_KEY" -e "GH_REPO=$GH_REPO" github-bot python -m unittest

popd
popd