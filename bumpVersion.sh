#!/bin/sh

if [ "$#" -ne 1 ] ; then
    echo "[ERROR] Usage: $0 <VERSION>. For example: $0 2.1.4"
    exit 1
fi

VERSION="$1"

if [[ "$VERSION" =~ ^v. ]] ; then
    echo "[ERROR] Only the version number: 2.1.4 instead of v2.1.4"
    exit 1
fi

sed -i "s/OPSCONFVERSION = \".*\"/OPSCONFVERSION = \"$VERSION\/" src/lib/libopsconf.py
for file in src/share/githooks/* ; do
    sed -i "s/OPSCONFVERSION=.*/OPSCONFVERSION=$VERSION/" $file
done    

git tag -a "v$VERSION"
