#!/bin/bash -e

./00_init_workspace.sh
./10_init_opsconf.sh
./20_commits.sh
./21_commits_hooks.sh

