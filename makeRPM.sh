#!/bin/sh

BUILD=build/BUILD
RPMS=build/RPMS
SOURCES=build/SOURCES
SPECS=build/SPECS
SRPMS=build/SRPMS

VERSION="$(git describe 2>/dev/null | sed 's/^v//' | sed 's/-/_/g' || echo 0.0 )"

if [ -z "$RELEASE" ] ; then
    RELEASE=1
fi

# Create rpmbuild tree
mkdir -p $BUILD $RPMS $SOURCES $SPECS $SRPMS

# Archive sources in SOURCES dir
tar czf "$SOURCES/opsconf-$VERSION.tar.gz" --transform "s,^\./,opsconf-$VERSION/," ./src/

cp opsconf.spec $SPECS/

rpmbuild --define "_topdir $(pwd)/build" \
	 --define "_release $RELEASE" \
	 --define "_version $VERSION" \
	 -v -bb --clean $SPECS/opsconf.spec
