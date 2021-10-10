FROM debian:buster-20210927-slim

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
     && build-essential g++ gcc cmake
     && apt-get -y install --no-install-recommends python3-opencv libopencv-dev