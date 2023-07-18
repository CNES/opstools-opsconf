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
            opsconf commit -m "Change ${FILEPATTERN/<>/$k} : time=$v" "${FILEPATTERN/<>/$k}"
        fi
    done
done

 for operation in "validate" "qualify" ; do
    cmd="${operation}FromFile"
    log_test "$cmd: Dry-run works from stdin"
    if opsconf status | opsconf toolbox $cmd --dry-run ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "$cmd: Dry-run fails if the input is wrong from stdin"
    if ! opsconf status | sed 's/v1 /v23 /' | opsconf toolbox $cmd --dry-run ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "$cmd: Operation succeeds from the stdin (promote only v1)"
    if opsconf status | sed 's/| v. /| v1 |/' | opsconf toolbox $cmd ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "$cmd: Dry-run works from a file"
    opsconf status > "$INPUTFILE"
    if opsconf toolbox $cmd --dry-run "$INPUTFILE" ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    log_test "$cmd: Operation succeeds from a file"
    if opsconf toolbox "$cmd $INPUTFILE" ; then
        log_result "OK"
    else
        log_result "KO"
    fi

    rm "$INPUTFILE"
done

popd > /dev/null
