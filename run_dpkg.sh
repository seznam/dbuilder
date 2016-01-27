#!/bin/bash
set -ex

cp -r /dbuilder/sources/. -t /dbuilder/build/
cd /dbuilder/build/${DBUILDER_SUBDIR}

# if some deb files exist in additional_packages directory, we create a trivial
# local repository
preinstall_debs=`find /dbuilder/additional_packages/ -name \*.deb`
if [ -n "${preinstall_debs}" ]; then
    repo_path=/dbuilder/local_repository
    mkdir ${repo_path}
    cp ${preinstall_debs} ${repo_path}
    pushd ${repo_path}
    dpkg-scanpackages . > Packages
    popd
    echo "deb file:${repo_path} ./" > /etc/apt/sources.list.d/local_repo.list

    # if pin-priority is defined, propagate it
    if [ -n "${LOCAL_REPO_PRIORITY}" ]; then
        echo -e "Package: *\nPin: origin \"\"\nPin-Priority: ${LOCAL_REPO_PRIORITY}" \
            > /etc/apt/preferences.d/local_repo
    fi
    unset repo_path
fi
unset preinstall_debs

apt-get update

# preinstall hooks
if [ -d /dbuilder/preinstall.d ]; then
    for file in `find /dbuilder/preinstall.d -executable -type f | sort -n`; do
        ${file}
    done
    unset file
fi

mk-build-deps -i -r -t 'apt-get -f -y --force-yes'
${DBUILDER_BUILD_CMD}

chmod 644 ../*.deb
cp ../*.deb /dbuilder/sources/${DBUILDER_SUBDIR}
