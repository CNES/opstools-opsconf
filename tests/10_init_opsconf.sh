#!/bin/bash -e

. env.sh

log_debug "Initialize repo"
cd "$REPO_LOCAL"
opsconf init
log_test "Hooks are correctly deployed?"
result=0
for f in $(ls "$OPSCONF_DIR/githooks"); do
    lresult=$(check_file_equal "$OPSCONF_DIR/githooks/$f" "$REPO_LOCAL/.git/hooks/$f")
    result=$((result+lresult))
done

if [ $result -eq 0 ]; then
    log_result "OK"
else
    log_result "KO"
fi
