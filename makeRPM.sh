#!/bin/bash -e

if [ -z "$RELEASE" ] ; then
    RELEASE=1
fi

if [ -z "$PYTHON_VERSION" ] ; then
    PYTHON_VERSION=python3.6
fi

if [ -n "$ISIS_BUILD" ] ; then
    cat <<EOF >> setup.cfg

[build]
executable = /usr/bin/env isisPython

[install]
install-lib = /usr/share/isis/lib/py
EOF

    SHEBANG="#!/usr/bin/env isisPython"
    for f in src/share/githooks/* ; do
        sed -i "1s@.*@$SHEBANG@" $f
    done
fi

$PYTHON_VERSION setup.py bdist_rpm --python $PYTHON_VERSION --release $RELEASE

echo "[INFO] The RPM was stored in $(dirname "$0")/dist"

# get back changed files
if [ -n "ISIS_BUILD" ] ; then
    git checkout setup.cfg src/share/githooks
fi
