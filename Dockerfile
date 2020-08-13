FROM pytorch/pytorch:latest
LABEL maintainer="synsypa"

COPY requirements.txt /home/
WORKDIR /home

RUN pip install -r requirements.txt

