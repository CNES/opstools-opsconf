#!/bin/bash -e

TEST_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

pushd "${TEST_DIR}" > /dev/null

. env.sh

[[ -f "${TESTS_RESULTS}" ]] && rm "${TESTS_RESULTS}"

# shellcheck disable=SC2010
scripts=$(ls ./* | grep -v 'env.sh' | grep -v 'run_tests.sh')

if [ $# -ge 1 ] ; then
    filter=$*
else
    filter=".*"
fi


for s in $scripts; do 
    # Run all 0* files that are needed for initialization
    if [[ "$s" =~ ^./0.*\.sh ]] ; then
        echo "[INFO] Run script $s" | tee -a "${TESTS_RESULTS}"
        "$s"
    else
        # Run if at least a filter matches
        for f in $filter ; do 
            if [[ "$s" =~ .*"$f".* ]] ; then
                echo "[INFO] Run script $s" | tee -a "${TESTS_RESULTS}"
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

