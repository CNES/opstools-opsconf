#!/bin/bash -e

. env.sh

CURRENT_TEST=20_commits

pushd "$REPO_LOCAL" > /dev/null
git checkout work 2> /dev/null
mkdir ${CURRENT_TEST}

ONE_FILE=${CURRENT_TEST}/one_file.txt
touch "$ONE_FILE"
OPSCONF_BIN commit -m "Create $ONE_FILE" "$ONE_FILE"
lorem_ipsum >> "$ONE_FILE"
long_msg="Write stuff in toto

It was really needed"
OPSCONF_BIN commit -m "$long_msg" "$ONE_FILE"

for branch in "master" "qualification" ; do
    log_test "Cannot commit from $branch"
    git checkout "$branch" 2> /dev/null
    touch test
    git add test
    if ! OPSCONF_BIN commit test -m "message" &> /dev/null ; then
        log_result "OK"
    else
        log_result "KO"
    fi
    git reset --hard &> /dev/null
    git checkout work 2> /dev/null
done

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
if [ "$(git status -s | wc -l)" -eq 0 ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Local and remote are in sync"
if [ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Committing from a subdir works"
pushd ${CURRENT_TEST} > /dev/null
LOCALFILE="${ONE_FILE/${CURRENT_TEST}\/}"
lorem_ipsum >> "$LOCALFILE"
if OPSCONF_BIN commit -m "subdir commit" "$LOCALFILE" ; then
    log_result "OK"
else
    log_result "KO"
fi
popd > /dev/null

log_test "Tagging works"
if OPSCONF_BIN tag -m "message is here" "VALID" ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Tagging works also without message"
if OPSCONF_BIN tag "VALID2" ; then
    log_result "OK"
else
    log_result "KO"
fi

VERSION_MAX=200
FILE=${CURRENT_TEST}/file_lotofchanges.txt
log_test "Create $VERSION_MAX versions"
for k in $(seq 1 ${VERSION_MAX}) ; do
    echo -ne "$k\\r"
    echo "$k" > "$FILE"
    # No coverage here: it's more of a performence test
    opsconf commit -m "changing content $((k-1)) by $k" $FILE &>/dev/null
done
if [ "$(git log -n1 --format=%s -- $FILE | cut -d: -f1)" = "v${VERSION_MAX}" ]; then
    log_result "OK"
else
    log_result "KO"
fi

popd > /dev/null
