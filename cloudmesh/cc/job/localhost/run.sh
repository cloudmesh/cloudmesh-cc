#!/bin/bash

date
echo "running the program"
cd cm/cloudmesh-cc/cloudmesh/cc/job/localhost
nohup cms cc run > touch output.txt
