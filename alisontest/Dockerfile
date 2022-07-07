#Alison
FROM ubuntu:22.04
MAINTAINER Gregor von Laszewski <laszewski@gmail.com>

# RUN add-apt-repository universe

RUN apt update -yq && apt upgrade -yq

#
# DEADSNAKE PYTHON
#
# RUN apt install software-properties-common -y
# RUN add-apt-repository ppa:deadsnakes/ppa -y
# # RUN add-apt-repository ppa:deadsnakes/nightly -y
# RUN apt update
# RUN apt install python3.10 python3.10-dev python3.10-venv -y

#
# PYTHON FROM SOURCE
#

RUN apt install -y build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    libffi-dev \
    curl \
    wget \
    libbz2-dev \
    pkg-config \
    make \
    git \
    sudo \
    nano

RUN mkdir -p /opt

WORKDIR /root

RUN wget https://www.python.org/ftp/python/3.10.5/Python-3.10.5.tar.xz
RUN tar -xf Python-3.10.5.tar.xz
RUN mv Python-3.10.5 /opt/
RUN rm -f Python-3.10.5.tar.xz
RUN mkdir -p ~/.ssh/
RUN touch ~/.ssh/config
RUN echo "Host *" >> ~/.ssh/config
RUN echo "	SetEnv LC_CTYPE=" >> ~/.ssh/config

WORKDIR /opt/Python-3.10.5

RUN ./configure --enable-optimizations --enable-shared
RUN make -j `nproc`
RUN make install
RUN ldconfig /opt/Python-3.10.5
RUN ln -s /usr/local/bin/python3.10 /usr/local/bin/python
RUN ln -s /usr/local/bin/pip3.10 /usr/local/bin/pip
RUN pip install pip -U

#
# install mpi4py
#
RUN apt install libopenmpi-dev -y && \
    pip install mpi4py

#
# install cloudmesh from source
#

#WORKDIR /root/cm
WORKDIR /home/alibo/cm

RUN pip install cloudmesh-installer
RUN /usr/local/bin/cloudmesh-installer get cc

#RUN /usr/local/bin/cloudmesh-installer get cms
#RUN cd /root/cm && \
#    git clone https://github.com/cloudmesh/cloudmesh-cc.git && \
#    cd cloudmesh-cc && \
#    pip install -r requirements.txt
#    pip install -e .

RUN pip install pip -U

WORKDIR /home/alibo/cm/cloudmesh-cc

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
