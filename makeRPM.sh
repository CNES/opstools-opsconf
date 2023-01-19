#!/bin/sh

BUILD=build/BUILD
RPMS=build/RPMS
SOURCES=build/SOURCES
SPECS=build/SPECS
SRPMS=build/SRPMS

VERSION="$(git describe 2>/dev/null || echo 0.0 | sed 's/-/_/g')"

if [ -z "$RELEASE" ] ; then
    RELEASE=1
fi

# Create rpmbuild tree
mkdir -p $BUILD $RPMS $SOURCES $SPECS $SRPMS

# Archive sources in SOURCES dir
tar czf "$SOURCES/opsconf-$VERSION.tar.gz" --transform "s,^\./,opsconf-$VERSION/," ./src/

cp opsconf.spec $SPECS/

rpmbuild --define "_topdir $(pwd)/build" \
	 --define "release $RELEASE" \
	 --define "version $VERSION" \
	 -v -bb --clean $SPECS/opsconf.spec
