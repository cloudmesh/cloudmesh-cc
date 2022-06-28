#!/bin/bash -x
date
echo "running the program"
cd ~
cd cm/cloudmesh-cc/cloudmesh/cc/job/localhost
echo "finished running the program"
echo "# cloudmesh status=running progress=0"
ls
echo "# cloudmesh status=running progress=10"
pwd
echo "# cloudmesh status=running progress=20"
hostname
echo "# cloudmesh status=done progress=100"