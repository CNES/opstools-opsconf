#!/bin/bash -e

TEST_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

pushd "${TEST_DIR}" > /dev/null

scripts=$(ls * | grep -v 'env.sh' | grep -v 'run_tests.sh')

if [ $# -ge 1 ] ; then
    filter=$*
else
    filter=".*"
fi


for s in $scripts; do 
    # Run all 0* files that are needed for initialization
    if [[ "$s" =~ ^0.* ]] ; then
        ./"$s"
    else
        # Run if at least a filter matches
        for f in $filter ; do 
            if [[ "$s" =~ .*"$f".* ]] ; then
                ./"$s"
                break
            fi
        done
    fi
done

popd > /dev/null
