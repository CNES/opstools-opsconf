#!/bin/bash -e

. env.sh

CURRENT_TEST=55_move

pushd "$REPO_LOCAL" > /dev/null
git checkout work 2> /dev/null
mkdir "${CURRENT_TEST}"


mkdir "${CURRENT_TEST}/dir1"
for filename in file1 file2 file3 ; do
   touch "${CURRENT_TEST}/dir1/${filename}"
   lorem_ipsum >> "${CURRENT_TEST}/dir1/${filename}"
   opsconf commit -m "created ${filename}" "${CURRENT_TEST}/dir1/${filename}"
   lorem_ipsum >> "${CURRENT_TEST}/dir1/${filename}"
   opsconf commit -m "updated ${filename}" "${CURRENT_TEST}/dir1/${filename}"
done

log_test "Moving a file works"
if yes | OPSCONF_BIN move -m "Moving file1 to file1bis" "${CURRENT_TEST}/dir1/file1" "${CURRENT_TEST}/file1bis" ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Source file was removed"
if [ ! -f "${CURRENT_TEST}/dir1/file1" ] ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Destination file was created and committed"
if [ "$(opsconf log ${CURRENT_TEST}/file1bis | wc -l)" -eq 1 ] ; then
    log_result "OK"
else
    log_result "KO"
fi

log_test "Moving a file from a subdirectory works"
pushd ${CURRENT_TEST}/dir1 > /dev/null
if yes | OPSCONF_BIN move -m "Moving file2 to file2bis" file2 file2bis ; then
    log_result "OK"
else
    log_result "KO"
fi
popd > /dev/null

log_test "Moving a directory works"
if yes | OPSCONF_BIN move -m "Moving dir1 to dir2" "${CURRENT_TEST}/dir1" "${CURRENT_TEST}/dir2" ; then
    log_result "OK"
else
    log_result "KO"
fi

popd > /dev/null
