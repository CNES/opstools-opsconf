#!/bin/bash -e

. env.sh

CURRENT_TEST=22_commits_recursive

pushd "$REPO_LOCAL" > /dev/null
git checkout work 2> /dev/null
mkdir "${CURRENT_TEST}"


for dir in dir1 dir2 ; do
    thedir="${CURRENT_TEST}/$dir"
    mkdir -p "$thedir"
    for filename in file1 file2 file3 ; do
        touch "$thedir/$filename"
        lorem_ipsum >> "$thedir/$filename"
    done
done

log_test "Committing recursively a directory works"
COMMITTED_DIR="${CURRENT_TEST}/dir2"
NOT_COMMITTED_DIR="${CURRENT_TEST}/dir1"
opsconf commit -r -m "Created ${COMMITTED_DIR}" "${COMMITTED_DIR}"

if [ "$(git log --format=%s -n1 -- "${COMMITTED_DIR}" | cut -d: -f1)" = "v1" ]; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "The nearby directory is not committed"
if [ "$(git ls-files -o -- "${NOT_COMMITTED_DIR}" | grep -c "${NOT_COMMITTED_DIR}")" -gt 0 ]; then
    log_result "OK"
else
    log_result "KO"
fi

for filename in "${COMMITTED_DIR}"/* ; do
    lorem_ipsum >> "$filename"
done

log_test "Committing not from the git root directory works"
pushd "${CURRENT_TEST}" > /dev/null
if opsconf commit -r -m "changed dir2" "dir2" ; then
    log_result "OK"
else
    log_result "KO"
fi
popd > /dev/null
log_test "The nearby directory is still not committed"
if [ "$(git ls-files -o -- "${NOT_COMMITTED_DIR}" | grep -c "${NOT_COMMITTED_DIR}")" -gt 0 ]; then
    log_result "OK"
else
    log_result "KO"
fi

popd > /dev/null
