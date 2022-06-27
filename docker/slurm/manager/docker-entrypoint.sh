#!/bin/bash

sudo sed -i "s/REPLACE_IT/CPUs=$(nproc)/g" /etc/slurm/slurm.conf

sudo service munge start
sudo service slurmctld start
sudo cp /etc/munge/munge.key /home/admin/

tail -f /dev/null
