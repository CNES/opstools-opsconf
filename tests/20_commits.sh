#!/bin/bash -e

. env.sh

cd "$REPO_LOCAL"
ONE_FILE=one_file.txt
touch "$ONE_FILE"
opsconf commit -m "Create $ONE_FILE" "$ONE_FILE"
lorem_ipsum >> "$ONE_FILE"
long_msg="Write stuff in toto

It was really needed"
opsconf commit -m "$long_msg" "$ONE_FILE"

log_test "$ONE_FILE has version 2"
if [ "$(git log --format=%s -n1 | cut -d: -f1)" = "v2" ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "$ONE_FILE, version 2 has the expected comment"
if [ "$(git log --format=%B -n1 )" = "v2: $long_msg" ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Status is clean after commit"
if [ $(git status -s | wc -l) -eq 0 ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Local and remote are in sync"
if [ $(git diff --name-only @{u} | wc -l) -eq 0 ]; then
    log_result "OK"
else
    log_result "KO"
fi

#TODO: COMMIT DIR WITH SUBDIR + FILES
# COMMIT SOME FILES (but not all)
# COMMIT FULL DIR
# => Test all files have same message but not same version
#

# TODO: COMMIT 10000 times, see if version is 10000

