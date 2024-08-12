#!/bin/bash -e

. env.sh

CURRENT_TEST=40_rollback

pushd "$REPO_LOCAL" > /dev/null
git checkout work 2> /dev/null
mkdir ${CURRENT_TEST}

FILE=${CURRENT_TEST}/file.txt
touch "$FILE"
OPSCONF_BIN commit -m "Create $FILE" "$FILE" &> /dev/null

for k in {2..10} ; do
    lorem_ipsum > $FILE
    OPSCONF_BIN commit -m "Set $FILE content to $k" "$FILE" &> /dev/null
done

log_test "Rollbacked and new versions have the same content"
rollback_message="Back to v4
Because
You Know

Things happen!"
OPSCONF_BIN rollback -m "$rollback_message" "$FILE" v4
v4rev=$(rev_from_branch_version "$FILE" "work" v4)
if cmp "$FILE" <(file_content_in_rev "$FILE" "$v4rev"); then
    log_result "OK"
else
    log_result "KO"
fi

log_test "New version is the expected one"
latest_version=$(git log --format=%s -n1 -- $FILE | cut -d: -f1)
if [ "$latest_version" = "v11" ] ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Label is correct"
commit_msg=$(git log --format=%B -n1 -- $FILE)
expected_commit_msg="$latest_version: $rollback_message

Rolled-back to v4"

if [ "$commit_msg" = "$expected_commit_msg" ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Rollback does not work on master branch"
OPSCONF_BIN checkout master
if ! OPSCONF_BIN rollback -m "test" $FILE v1 ; then
    log_result "OK"
else
    log_result "KO"
fi

popd > /dev/null
