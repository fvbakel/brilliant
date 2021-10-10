#!/bin/sh
DATA_DIR=~/Documenten/nonogram
BIN_DIR=~/bin
docker build --pull --rm -f Dockerfile -t mypython:latest .
docker run --rm -it -v $PWD:/opt/app -v ${DATA_DIR}:/data -v ${BIN_DIR}:/opt/bin mypython:latest
