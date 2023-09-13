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

if [[ "$(git diff --name-only | wc -l)" -ne 0 ]] ; then
    echo "[ERROR] The repo must be clean to run $0"
    exit 1
fi

sed -i "s/OPSCONFVERSION = \".*\"/OPSCONFVERSION = \"$VERSION\"/" src/lib/opsconf/libopsconf.py
for file in src/share/githooks/* ; do
    sed -i "s/OPSCONFVERSION=.*/OPSCONFVERSION=$VERSION/" $file
done    

git commit -am "Bump version to $VERSION"
git tag -a "v$VERSION"
