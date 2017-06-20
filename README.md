# dbuilder
Docker images for building packages with clean dependencies in multiple distributions.

## Usage
All images are available on docker hub https://hub.docker.com/r/seznam/dbuilder/.

The only thing you have to do is to choose a tag (generated from config.yaml) e.g. 'jessie_latest' and run:
(Docker will automatically pull that image so you don't neet to build anything)
```bash
docker run --rm -v `pwd`:/dbuilder/sources seznam/dbuilder:debian_jessie
```
and *.deb will appear in your source directory

### Optional arguments
  - **Additional packages** - It is possible to add additional packages to dbuilder and it will create local repository containing these files. Note the volume `/dbuilder/additional_packages` in the following example. Note, that this feature is implemented in apt-based dbuilder images only now.

```bash
# add some package
cp mypackage_1.0.9.8.2_amd64.deb ./deps/
# add another package, note that the deb package can be located
# in any subdirectory
mkdir ./deps/otherpackage_subdir/
cp otherpackage_0.22.4_all.deb ./deps/otherpackage_subdir/

# build and possibly use additional packages
docker run --rm \
    -v `pwd`/deps:/dbuilder/additional_packages \
    -v `pwd`/src:/dbuilder/sources \
    seznam/dbuilder:debian_jessie
```

  - **Preinstall hooks** - It is possible to add hooks, before dbuilder tries to satisfy build dependencies. Use volume `/dbuilder/preinstall.d` and drop executable files in. All executable files from this folder will be executed in order determined by numeric `sort`.

```bash
cp 00-my-fixer.sh 10-prepare-environment.py ./preinstall.d/
chmod +x ./preinstall.d/*
docker run --rm \
    -v `pwd`/preinstall.d:/dbuilder/preinstall.d \
    -v `pwd`/src:/dbuilder/sources \
    seznam/dbuilder:debian_jessie
```

  - **Postinstall hooks** - It is possible to add hooks, after build package. Use volume `/dbuilder/postinstall.d` and drop executable files in. All executable files from this folder will be executed in order determined by numeric `sort`.

```bash
cp 00-post-builder.sh 10-post-script.py ./preinstall.d/
chmod +x ./postinstall.d/*
docker run --rm \
    -v `pwd`/postinstall.d:/dbuilder/postinstall.d \
    -v `pwd`/src:/dbuilder/sources \
    seznam/dbuilder:debian_jessie
```

### Control environment variables
  - general
    - DBUILDER_SUBDIR - cd to subdir before building starts
    - NCPUS - concurrency

  - apt based:
    - DBUILDER_BUILD_CMD - [default="dpkg-buildpackage -j${NCPUS}"]
    - LOCAL_REPO_PRIORITY - sets [Pin-Priority](https://wiki.debian.org/AptPreferences) to local repository created using /dbuilder/additional_packages volume.
    - BUILD_PACKAGES_FILE_PATH - [default="../"]

## For maintaners
## Prepare
```bash
./generate_dockerfiles.py
```

## Build
```bash
make -C dockerfiles/ build
```

## Push
```bash
make -C dockerfiles/ push
```

## Generating dockerfiles
```bash
$ ./generate_dockerfiles.py -h
Usage: generate_dockerfiles.py [options]

Options:
  -h, --help            show this help message and exit
  -c CONFIGURATION_FILE, --configuration-file=CONFIGURATION_FILE
                        Configuration file path [config.yaml]
  -o OUTPUT_DIR, --output-dir=OUTPUT_DIR
                        Output directory [./dockerfiles/]
  -t TAG_SEPARATOR, --tag-separator=TAG_SEPARATOR
                        Separator of a docker image name and tags which will
                        used to separate output docker image names[_]
```
All relative paths in configuration file are taken to dirname(configuration file).
