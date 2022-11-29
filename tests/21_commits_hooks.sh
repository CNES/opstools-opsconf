#!/bin/bash -e

. env.sh

## TEST HOOK
# change 1 file + git add + git commit = OK + check version was prepended
# change N file + git add + git commit = KO
## END TEST HOOK
