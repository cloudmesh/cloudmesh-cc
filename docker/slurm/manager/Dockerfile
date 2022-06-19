FROM cloudmesh/python:latest

RUN apt update -y && \
    apt install munge -y && \
    apt-get install mariadb-server -y

ARG DEBIAN_FRONTEND=noninteractive
RUN apt install slurmd slurm-client slurmctld -y
RUN apt install sudo -y && \
    useradd -m admin -s /usr/bin/bash -d /home/admin && \
    echo "admin:admin" | chpasswd && \
    adduser admin sudo && \
    echo "admin     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN apt update -y && \
    apt install libopenmpi-dev -y && \
    pip install mpi4py

COPY slurm.conf /etc/slurm/
COPY cgroup.conf /etc/slurm/
COPY docker-entrypoint.sh /etc/slurm/

EXPOSE 6817 6818 6819 3306 

WORKDIR /home/admin

ENTRYPOINT ["/etc/slurm/docker-entrypoint.sh"]
