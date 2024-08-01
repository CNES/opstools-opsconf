#!/bin/bash -e

. env.sh

CURRENT_TEST=32_qualify_validate_from_file

pushd "$REPO_LOCAL" > /dev/null
git checkout work 2> /dev/null

FILEPATTERN="${CURRENT_TEST}/file<>.txt"
INPUTFILE="file_input.txt"

mkdir -p "$(dirname ${FILEPATTERN})"

log_info "Initialize the work branch"

for k in {1..5} ; do
    for v in {1..3} ; do
        if [ "$k" -ge "$v" ] ; then
            lorem_ipsum >> "${FILEPATTERN/<>/$k}"
            opsconf commit -m "Change ${FILEPATTERN/<>/$k} : time=$v" "${FILEPATTERN/<>/$k}" 2> /dev/null
        fi
    done
done

for operation in "validate" "qualify" ; do
    cmd="${operation}FromFile"
    log_test "$cmd: Dry-run works from stdin"
    # the grep -v ;0; removes the new files
    if opsconf status --to-csv | grep -v ';0;' | opsconf toolbox $cmd --dry-run 2> /dev/null ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "$cmd: Dry-run fails if the input is wrong from stdin"
    if ! opsconf status --to-csv | grep -v ';0;' | sed 's/;1;/;23;/' | opsconf toolbox $cmd --dry-run 2> /dev/null ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "$cmd: Operation succeeds from the stdin (promote only v1)"
    if opsconf status --to-csv | grep -v ';0;' | sed 's/;[[:digit:]];/;1;/' | opsconf toolbox $cmd 2> /dev/null ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "$cmd: Dry-run works from a file"
    opsconf status --to-csv | grep -v ';0;' > "$INPUTFILE"
    if opsconf toolbox $cmd --dry-run "$INPUTFILE" 2> /dev/null ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "$cmd: Operation succeeds from a file"
    if opsconf toolbox $cmd "$INPUTFILE" 2> /dev/null ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    rm "$INPUTFILE"
done

for k in {1..3} ; do
    lorem_ipsum >> "${FILEPATTERN/<>/$k}"
    opsconf commit -m "Change ${FILEPATTERN/<>/$k} : again" "${FILEPATTERN/<>/$k}" 2> /dev/null
done

for operation in "validate" "qualify" ; do
    cmd="${operation}FromFile"
    if [ "${operation}" = "validate" ] ; then
        branch=master
    else
        branch=qualification
    fi
    MESSAGE="VALIDATION MESSAGE"
    log_test "$cmd: Promotion is correctly stored on newly promoted version"
    opsconf status --to-csv | grep -v ';0;' | opsconf toolbox $cmd -m "$MESSAGE" 2> /dev/null
    opsconf checkout  "$branch" 2> /dev/null
    if [ "$(opsconf status --with-notes | grep -c "$MESSAGE")" -eq 3 ] ; then
        log_result "OK"
    else
        log_result "KO"
    fi
    opsconf checkout work 2> /dev/null
done

popd > /dev/null
