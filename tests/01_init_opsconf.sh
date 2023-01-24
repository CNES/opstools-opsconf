#!/bin/bash -e

. env.sh

cd "$REPO_LOCAL"
log_debug "Initialize repo"

git config --local user.email "testing@test.tld"
git config --local user.name "The Tester"

log_debug "Pretend we worked before opsconf"
(
git checkout -b develop
mkdir before_opsconf
lorem_ipsum > before_opsconf/file1.txt
git add before_opsconf
git commit -m "commit before opsconf 1"

lorem_ipsum >> before_opsconf/file1.txt
git commit -am "commit before opsconf 2"
lorem_ipsum >> before_opsconf/file1.txt
git commit -am "commit before opsconf 3"
git push -u origin develop
) &> /dev/null

log_test "Cannot run opsconf command before init."
if ! opsconf checkout master 2> /dev/null ; then
   log_result "OK"
else
   log_result "KO"
fi

log_test "Cannot run opsconf init command without a root branch."
if ! opsconf init 2> /dev/null ; then
   log_result "OK"
else
   log_result "KO"
fi

log_info "Initialize opsconf"
opsconf init --root-branch develop

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
