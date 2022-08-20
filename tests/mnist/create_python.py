#!/usr/bin/env python
from cloudmesh.common.Shell import Shell
import sys
import os

try:
    env = sys.argv[1]
    version = sys.argv[2]
except:
    env = "ENV3"
    version = "3.10.5"

"""
conda env list
# conda environments:
#
ENV3                     /ccs/home/gregor/.conda/envs/ENV3
ENV4                     /ccs/home/gregor/.conda/envs/ENV4
bench                    /ccs/home/gregor/.conda/envs/bench
cylon_dev2               /ccs/home/gregor/.conda/envs/cylon_dev2
base                  *  /sw/summit/python/3.8/anaconda3/2020.07-rhel8

$ conda env list
-bash: conda: command not found
"""


if env in Shell.run("conda env list"):
    print ("environment {env} already installed in conda")
else:
    os.system(f"conda create -f -y -n {env} -c conda-forge python={version}")

#nvidia-smi --list-gpus
