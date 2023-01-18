#!/bin/bash -e

TEST_DIR="$(dirname $(realpath ${BASH_SOURCE[0]}))"

pushd ${TEST_DIR}

./00_init_workspace.sh
./10_init_opsconf.sh
./20_commits.sh
./21_commits_hooks.sh

popd
