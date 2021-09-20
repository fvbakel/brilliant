#!/bin/sh
DATA_DIR=~/Documenten/nonogram
docker build --pull --rm -f Dockerfile -t mypython:latest .
docker run --rm -it -v $PWD:/opt/app -v ${DATA_DIR}:/data  mypython:latest
