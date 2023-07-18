#!/bin/bash -e

if [ -z "$RELEASE" ] ; then
    RELEASE=1
fi

if [ -z "$PYTHON_VERSION" ] ; then
    PYTHON_VERSION=python3.6
fi

$PYTHON_VERSION setup.py bdist_rpm --python $PYTHON_VERSION --release $RELEASE

echo "[INFO] The RPM was stored in $(dirname "$0")/dist"
