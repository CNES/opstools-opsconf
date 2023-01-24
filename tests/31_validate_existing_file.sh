#!/bin/bash -e

. env.sh

CURRENT_TEST=before_opsconf

pushd "$REPO_LOCAL" > /dev/null
git checkout work 2> /dev/null

FILE=${CURRENT_TEST}/file1.txt

branch=master
cmd=validate
log_test "Branch $branch has no version of $FILE"
opsconf checkout "$branch"
if [ "$(opsconf log "$FILE" | wc -l)" -eq 0 ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "1 version of $FILE is available"
if [ "$(opsconf log --all "$FILE" | wc -l)" -eq 1 ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Bring new file (directly in v1) to branch $branch"
opsconf "$cmd" "$FILE" 1
if [ "$(opsconf log "$FILE" | wc -l)" -eq 1 ]; then
    log_result "OK"
else
    log_result "KO"
fi

