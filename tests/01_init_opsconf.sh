#!/bin/bash -e

. env.sh

cd "$REPO_LOCAL"
log_debug "Initialize repo"

git config --local user.email "testing@test.tld"
git config --local user.name "The Tester"

log_test "Cannot run opsconf command before init."
if ! opsconf checkout master ; then
   log_result "OK"
else
   log_result "KO"
fi

log_info "Initialize opsconf"
opsconf init

log_test "Hooks are correctly deployed."
result=0
for f in "$OPSCONF_DIR"/githooks/* ; do
    lresult=$(check_file_equal "$f" "$REPO_LOCAL/.git/hooks/$(basename "$f")")
    result=$((result+lresult))
done

if [ "$result" -eq 0 ]; then
    log_result "OK"
else
    log_result "KO"
fi
