#!/bin/sh

sudo sed -i "s/REPLACE_IT/CPUs=$(nproc)/g" /etc/slurm/slurm.conf

sudo service munge start
sudo slurmd -N $(hostname)

tail -f /dev/null
