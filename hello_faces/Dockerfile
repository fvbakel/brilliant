FROM python:3.8-slim-buster

#RUN useradd python
RUN adduser -q python

RUN apt-get update && apt-get install -y python3-opencv
USER python
ENV PATH=/home/python/.local/bin:$PATH
WORKDIR /opt/app

#RUN pip install pillow opencv-python opencv-contrib-python
RUN pip install pillow opencv-contrib-python

VOLUME /data
VOLUME /opt/app

ENTRYPOINT [ "bash" ]
