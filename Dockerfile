FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04
LABEL maintainer "B0529047"

RUN apt-get update
RUN apt-get install sudo

RUN useradd -ms /bin/bash ubuntu
RUN echo "ubuntu:ubuntu" | chpasswd && adduser ubuntu sudo

USER ubuntu
WORKDIR /home/ubuntu

RUN apt-get install -y --no-install-recommends \
    vim python3-dev python3-pip python3-numpy \
    libprotobuf-dev libleveldb-dev libsnappy-dev \
    libopencv-dev libhdf5-serial-dev protobuf-compiler libboost-all-dev \
    libopenblas-dev liblapack-dev libatlas-base-dev \
    libgflags-dev libgoogle-glog-dev liblmdb-dev \
    git cmake-gui build-essential && \
    ln -s /usr/bin/python3 /usr/local/bin/python

RUN mkdir app && cd app && \
    git clone --recursive https://github.com/CMU-Perceptual-Computing-Lab/openpose.git

RUN cd app/openpose/3rdparty/caffe && \
    cp Makefile.config.Ubuntu16_cuda8.example Makefile.config

CMD [ "/bin/bash" ]