#!/bin/bash -e

. env.sh

log_debug "Init remote repo"
mkdir "$REPO_REMOTE"
cd "$REPO_REMOTE"
git init --bare
cd "$WORKSPACE"
log_debug "Remote OK"

log_debug "Init local repo"
git clone "$REPO_REMOTE" "$REPO_LOCAL"
log_debug "Local OK"

