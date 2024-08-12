#!/bin/bash -e

. env.sh

if python3 -m coverage &> /dev/null ; then
    python3 -m coverage xml -o "$COVERAGE_XML"
    python3 -m coverage report
else
    log_error "Coverage is not installed"
fi
