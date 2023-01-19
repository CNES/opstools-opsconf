#!/bin/bash -e

. env.sh

CURRENT_TEST=30_qualify_validate_log

pushd "$REPO_LOCAL"
mkdir ${CURRENT_TEST}

FILE=${CURRENT_TEST}/file.txt
touch "$FILE"
opsconf commit -m "Create $FILE" "$FILE" &> /dev/null

for _ in {2..10} ; do
    lorem_ipsum > "$FILE"
    opsconf commit -m "Change $FILE content" "$FILE" &> /dev/null
done

log_test "Branch work has 10 versions of $FILE"
if [ "$(opsconf log "$FILE" | wc -l)" -eq 10 ]; then
    log_result "OK"
else
    log_result "KO"
fi

for branch in "qualification" "master" ; do
    if [ "$branch" = "qualification" ] ; then
        cmd="qualify"
    elif [ "$branch" = "master" ]; then
        cmd="validate"
    else
        log_error "Incorrect branch: $branch"
        exit 1
    fi

    log_info "### BRANCH $branch ###"

    log_test "Cannot $cmd file from branch work"
    if ! opsconf "$cmd" "$FILE" 2 > /dev/null ; then
        log_result "OK"
    else
        log_result "KO"
    fi
    
    log_test "Branch $branch has no version of $FILE"
    opsconf checkout "$branch"
    if [ "$(opsconf log "$FILE" | wc -l)" -eq 0 ]; then
        log_result "OK"
    else
        log_result "KO"
    fi
    
    log_test "10 versions of $FILE are available"
    if [ "$(opsconf log --all "$FILE" | wc -l)" -eq 10 ]; then
        log_result "OK"
    else
        log_result "KO"
    fi
    
    log_test "Bring new file (directly in v5) to branch $branch"
    opsconf "$cmd" "$FILE" 5
    if [ "$(opsconf log "$FILE" | wc -l)" -eq 5 ]; then
        log_result "OK"
    else
        log_result "KO"
    fi
    
    log_test "Bring new version (v5->v7) of existing file to branch $branch"
    opsconf "$cmd" "$FILE" 7
    if [ "$(opsconf log "$FILE" | wc -l)" -eq 7 ]; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "Branch $branch: local and remote are in sync"
    if [ "$(git rev-parse HEAD)" = "$(git rev-parse @{u})" ]; then
        log_result "OK"
    else
        log_result "KO"
    fi

done

popd
