############################################################
# Dockerfile to build pytorch
# Based on nvidia/cuda
# bag cmd:docker build -t foton/digitialcamserver:v1 . 
############################################################

FROM ubuntu:20.04
MAINTAINER Pei Xiapqi
#ADD ./wheel /root/wheel
ADD ./api /root/api
WORKDIR /root/api
ENV  TZ="Asia/Shanghai"

RUN apt-get update
# Python3.8.10 /pip 20.0.2 /setuptools 45.2.0 /wheel 0.34.2
RUN apt-get install -y python3-pip
RUN echo y | apt-get install libgl1-mesa-glx
RUN DEBIAN_FRONTEND=noninteractive apt-get -yq install libglib2.0-dev --assume-yes apt-utils
RUN echo y | apt-get install gphoto2
# for cv2
RUN pip3 install -i http://pypi.douban.com/simple --trusted-host pypi.douban.com -r requirements.txt


