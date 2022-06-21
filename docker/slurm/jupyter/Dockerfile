FROM cloudmesh/python:latest

RUN apt update -y &&  \
    apt install munge -y &&  \
    apt-get install mariadb-server -y

ARG DEBIAN_FRONTEND=noninteractive
RUN apt install slurm-client -y
RUN apt install curl dirmngr apt-transport-https lsb-release ca-certificates -y
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt install sudo -y && \
    useradd -m admin -s /usr/bin/bash -d /home/admin && \
    echo "admin:admin" | chpasswd && \
    adduser admin sudo && \
    echo "admin     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN apt update -y && \
    apt install nodejs -y && \
    npm install -g configurable-http-proxy && \
    pip install jupyterlab==2.1.2

COPY slurm.conf /etc/slurm/
COPY cgroup.conf /etc/slurm/
COPY docker-entrypoint.sh /etc/slurm/

WORKDIR /home/admin

COPY job.sh /home/admin
COPY test.py /home/admin

EXPOSE 8888

ENV USER admin
ENV SHELL bash

RUN apt install libopenmpi-dev -y && \
    pip install mpi4py && \
    pip install jupyterlab_slurm

ENTRYPOINT ["/etc/slurm/docker-entrypoint.sh"]
