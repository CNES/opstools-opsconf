#!/bin/bash -e

TEST_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

pushd "${TEST_DIR}" > /dev/null

. env.sh

# Do not execute the linter
NOLINTER=0

[[ -d "$WORKSPACE" ]] && rm -rf "$WORKSPACE"
mkdir "$WORKSPACE"

[[ -f "${COVERAGE_FILE}" ]] && rm "${COVERAGE_FILE}"
[[ -f "${TESTS_RESULTS}" ]] && rm "${TESTS_RESULTS}"

# shellcheck disable=SC2010
scripts=$(ls ./* | grep -v 'env.sh' | grep -v 'run_tests.sh')

while [ $# -ge 1 ] ; do
    if [ "$1" = "--no-linter" ] ; then
        NOLINTER=1
        shift;
    elif [ "$1" = "--linter-only" ] ; then
        ./02_linter.sh | tee -a "${TESTS_RESULTS}"
        log_synthesis
        popd > /dev/null
        exit
    else
        filter=$*
        break;
    fi
done
if [ $# -eq 0 ] ; then
    filter=".*"
fi


for s in $scripts; do
    # Run all 0* files that are needed for initialization
    if [[ "$s" =~ ^./0.*\.sh ]] ; then
        # Do not play the linter script if it was asked not to
        if [ "$NOLINTER" -eq 1 ] && [ "$s" = "./02_linter.sh" ]  ; then
            title "Skipping linter"
            continue
        fi
        title "Run script $s" | tee -a "${TESTS_RESULTS}"
        "$s"
    else
        # Run if at least a filter matches
        for f in $filter ; do
            if [[ "$s" =~ .*"$f".* ]] ; then
                title "Run script $s" | tee -a "${TESTS_RESULTS}"
                "$s"
                # One filter has matched, the script has run
                # no need to try the other ones (or we might run it several times)
                break
            fi
        done
    fi
done

log_synthesis

popd > /dev/null

