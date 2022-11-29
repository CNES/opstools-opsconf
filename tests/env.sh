#!/bin/bash

ROOT_DIR="$(git rev-parse --show-toplevel)"
export PATH=$PATH:"$ROOT_DIR/src/bin"
export OPSCONF_DIR="$ROOT_DIR/src/share"

WORKSPACE="$ROOT_DIR/tests_exec_workspace"

REPO_REMOTE="$WORKSPACE/remote_dir.git"
REPO_LOCAL="$WORKSPACE/local_dir"

. ${ROOT_DIR}/src/share/libs/libopsconf

lorem_ipsum() {
    nb_lines=$1
    base64 /dev/urandom | awk '{print(0==NR%10)?"":$1}' | sed 's/[^[:alpha:]]/ /g' | head -$1
}

log_test() {
    echo "[TEST] $@"
}

log_result() {
    echo "[RESULT] $@"
}

check_file_equal() {
    file1="$1"
    file2="$2"
    for f in "$file1" "$file2"; do
        if [ ! -f $f ] ; then
            log_error "File does not exist: $f"
            return 1
        fi
    done
    if ! cmp -s "$file1" "$file2" ; then
        log_error "Files differ: $file1, $file2"
        return 1
    fi
}
