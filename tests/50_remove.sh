#!/bin/bash -e

. env.sh

CURRENT_TEST=50_remove

pushd "$REPO_LOCAL" > /dev/null
git checkout work 2> /dev/null
mkdir ${CURRENT_TEST}

FILE=${CURRENT_TEST}/file.txt
touch "$FILE"
opsconf commit -m "Create $FILE" "$FILE" &> /dev/null

for k in {2..10} ; do
    lorem_ipsum > $FILE
    opsconf commit -m "Set $FILE content to $k" "$FILE" &> /dev/null
done

opsconf checkout master
opsconf validate "$FILE" v5
if [ "$(opsconf log $FILE | wc -l)" -ne 5 ] ; then
    log_error "Initialization error. File validation failed".
    exit 1
fi

log_test "Removing file from branch master is possible"
yes | opsconf remove -m "Removed" "$FILE"
if [ "$(opsconf log $FILE 2> /dev/null | wc -l)" -eq 0 ] ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "It is possible to validate again a file that was removed"
opsconf validate "$FILE" v3
if [ "$(opsconf log $FILE | wc -l)" -eq 3 ] ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Removing file from branch work is possible"
opsconf checkout work
yes | opsconf remove -m "Removed" "$FILE"
if [ "$(opsconf log $FILE 2> /dev/null | wc -l)" -eq 0 ] ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "It is not possible to rollback a file that was removed"
if ! opsconf rollback -m "Rollback" "$FILE" v1 2> /dev/null ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "It is not possible to validate a file removed from branch work (but not from master)"
opsconf checkout master
if ! opsconf validate "$FILE" v5 ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "It is not possible to validate a file removed from branch work (and from master)"
yes | opsconf remove -m "Removed" "$FILE"
if ! opsconf validate "$FILE" v5 ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "It is possible to create again a file that was removed"
opsconf checkout work
mkdir ${CURRENT_TEST}
touch "$FILE"
opsconf commit -m "Create $FILE" "$FILE" &> /dev/null

for k in {2..5} ; do
    lorem_ipsum > $FILE
    opsconf commit -m "Set $FILE content to $k" "$FILE" &> /dev/null
done

if [ "$(opsconf log $FILE | wc -l)" -eq 5 ] ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "It is possible to rollback a file that was removed then recreated"
if opsconf rollback -m "Rollbacked" $FILE v1 ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "It is possible to validate a file that was removed then recreated"
opsconf checkout master
opsconf validate "$FILE" v3
if [ "$(opsconf log $FILE | wc -l)" -eq 3 ] ; then
    log_result "OK"
else
    log_result "KO"
fi

popd > /dev/null
