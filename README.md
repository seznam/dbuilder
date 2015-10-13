# dbuilder
Docker images for building packages with clean dependencies in multiple distributions.

## Usage
All images are available on docker hub https://hub.docker.com/r/seznam/dbuilder/.

The only thing you have to do is to choose a tag (generated from config.yaml) e.g. 'jessie_latest' and run:
(Docker will automatically pull that image so you don't neet to build anything)
```bash
docker run -it -v `pwd`:/dbuilder/sources seznam/dbuilder:debian_jessie
```
and *.deb will appear in your source directory

### Control environment variables
  - general
    - DBUILDER_SUBDIR - cd to subdir before building starts
    - NCPUS - concurrency
  
  - apt based:
    - DBUILDER_BUILD_CMD - [default="dpkg-buildpackage -j${NCPUS}"]

## For maintaners
## Prepare
```bash
./generate-dockerfiles.py
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
```
All relative paths in configuration file are taken to dirname(configuration file).
