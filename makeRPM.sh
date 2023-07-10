#!/bin/sh

if [ -z "$RELEASE" ] ; then
    RELEASE=1
fi

if [ -z "$PYTHON_VERSION" ] ; then
    PYTHON_VERSION=python3.4
fi

$PYTHON_VERSION setup.py bdist_rpm --python $PYTHON_VERSION --release $RELEASE
