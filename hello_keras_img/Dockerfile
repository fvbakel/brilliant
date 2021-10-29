FROM python:3.8-slim-buster

#RUN useradd python
RUN adduser -q python

RUN apt-get update && apt-get install -y python3-opencv
USER python
ENV PATH=/home/python/.local/bin:$PATH
WORKDIR /opt/app

#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install keras tensorflow opencv-python matplotlib sklearn torch
RUN pip install keras tensorflow matplotlib SciPy opencv-python

VOLUME /data
VOLUME /opt/app

ENTRYPOINT [ "bash" ]
