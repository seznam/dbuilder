#!/bin/bash
set -ex

cp -r /dbuilder/sources/. -t /dbuilder/build/
cd /dbuilder/build/${DBUILDER_SUBDIR}

apt-get update

mk-build-deps -i -r -t 'apt-get -f -y --force-yes'
${DBUILDER_BUILD_CMD}

chmod 644 ../*.deb
cp ../*.deb /dbuilder/sources/${DBUILDER_SUBDIR}
