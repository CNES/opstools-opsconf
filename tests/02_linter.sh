#!/bin/bash

. env.sh

log_test "The linter returns zero error"
find "${ROOT_DIR}/tests" -type f -print0 | xargs -0 shellcheck
result="$?"

find "${ROOT_DIR}/src" -type f -print0 | xargs -0 shellcheck
result="$(($?+result))"

if [ "$result" -eq 0 ] ; then
    log_result "OK"
else
    log_result "KO"
fi
