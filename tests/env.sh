#!/bin/bash


ROOT_DIR="$(git rev-parse --show-toplevel)"
export PATH="$ROOT_DIR/src/bin:$PATH"
export PYTHONPATH="$ROOT_DIR/src/lib:$PYTHONPATH"
export OPSCONF_DIR="$ROOT_DIR/src/share"

export TESTS_RESULTS="$ROOT_DIR/tests/tests_results.txt"

WORKSPACE="$ROOT_DIR/tests_exec_workspace"

export REPO_REMOTE="$WORKSPACE/remote_dir.git"
export REPO_LOCAL="$WORKSPACE/local_dir"

# shellcheck disable=SC2120
lorem_ipsum() {
    if [ "$#" -eq 1 ]; then
        nb_lines=$1
    else
        nb_lines=50
    fi
    base64 /dev/urandom | awk '{print(0==NR%10)?"":$nb_lines}' | sed 's/[^[:alpha:]]/ /g' | sed 's/ \+$//' | head -"$nb_lines"
}

rev_from_branch_version() {
    file=$1
    branch=$2
    version=$3
    git log --format=%h --grep "^v$version" "$branch" -- "$file"
}

file_content_in_rev() {
    file=$1
    rev=$2
    git show "$rev:$file"
}

log_debug() {
    echo "[DEBUG] $*"
}

log_info() {
    echo "[DEBUG] $*"
}

log_error() {
    echo "[ERROR] $*"
}

log_test() {
    echo "[TEST] $*" | tee -a "${TESTS_RESULTS}"
}

log_result() {
    echo "[RESULT] $*" | tee -a "${TESTS_RESULTS}"
}

log_synthesis() {
    nb_tests=$(grep -c '\[TEST\]' "${TESTS_RESULTS}" || true)
    nb_ok=$(grep -c '\[RESULT\] OK' "${TESTS_RESULTS}" || true)
    nb_ko=$(grep -c '\[RESULT\] KO' "${TESTS_RESULTS}" || true)
    if [ "$nb_ko" -ne 0 ] ; then
        status="FAILED"
        errno=1
    else
        status="SUCCESS"
        errno=0
    fi
    echo "[SYNTHESIS] TESTS STATUS: $status" | tee -a "${TESTS_RESULTS}"
    echo "[SYNTHESIS] OK: $nb_ok / $nb_tests ; KO: $nb_ko / $nb_tests" | tee -a "${TESTS_RESULTS}"
    return $errno
}

check_file_equal() {
    file1="$1"
    file2="$2"
    for f in "$file1" "$file2"; do
        if [ ! -f "$f" ] ; then
            log_error "File does not exist: $f"
            return 1
        fi
    done
    if ! cmp -s "$file1" "$file2" ; then
        log_error "Files differ: $file1, $file2"
        return 1
    fi
}
