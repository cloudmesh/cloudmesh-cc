FROM cloudmesh/python:latest

RUN apt update -y && \
    apt-get install mariadb-server -y && \
    apt install ntpdate -y && \
    apt install systemctl -y

ARG DEBIAN_FRONTEND=noninteractive
RUN groupadd -g 3456 munge
RUN useradd  -m -c "MUNGE Uid 'N' Gid Emporium" -d /var/lib/munge -u 3456 -g munge  -s /sbin/nologin munge
RUN groupadd -g 3457 slurm
RUN useradd  -m -c "SLURM workload manager" -d /var/lib/slurm -u 3457 -g slurm  -s /bin/bash slurm
RUN apt install munge libmunge2 libmunge-dev
RUN chown -R munge: /etc/munge/ /var/log/munge/ /var/lib/munge/
RUN chmod 0700 /etc/munge/ /var/log/munge/ /var/lib/munge/
RUN systemctl enable munge
RUN apt install slurm-wlm -y
RUN apt install sudo -y && \
    useradd -m admin -s /usr/bin/bash -d /home/admin && \
    chmod x+u /home/admin \
    echo "admin:admin" | chpasswd && \
    adduser admin sudo && \
    echo "admin     ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN mkdir /var/spool/slurmd && \
    chown admin:admin /var/spool/slurmd && \
    chmod 755 /var/spool/slurmd && \
    touch /var/log/slurm/slurmd.log && \
    chown -R admin:admin /var/log/slurm/slurmd.log

COPY slurm.conf /etc/slurm/
COPY cgroup.conf /etc/slurm/
COPY docker-entrypoint.sh /etc/slurm/

EXPOSE 6817 6818 6819  


ENTRYPOINT ["/etc/slurm/docker-entrypoint.sh"]
