#!/bin/bash

sudo sed -i "s/REPLACE_IT/CPUs=$(nproc)/g" /etc/slurm/slurm.conf

sudo service munge start
sudo slurmd -N $(hostname)
sudo cp /home/admin/munge.key /etc/munge/munge.key
sudo rm /home/admin/munge.key

tail -f /dev/null
