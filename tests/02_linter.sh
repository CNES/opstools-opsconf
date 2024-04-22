#!/bin/bash

. env.sh

log_test "The linter returns zero error"
find "${ROOT_DIR}/tests" -type f -name "*.sh" -print0 | xargs -0 shellcheck
result="$?"

find "${ROOT_DIR}/src" -type f -name "*.py" -print0 | xargs -0 python3 -m pylint --rcfile "${ROOT_DIR}/.pylintrc"
result="$(($?+result))"

if [ "$result" -eq 0 ] ; then
    log_result "OK"
else
    log_result "KO"
fi
