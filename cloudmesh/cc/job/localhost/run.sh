#!/bin/bash

date
echo "running the program"
cd ~
cd cm/cloudmesh-cc/cloudmesh/cc/job/localhost
touch job_output.txt
nohup cms cc run --command="echo hello world 1" > job_output.txt
nohup sleep 10
nohup cms cc run --command="echo hello world 2" > job_output.txt
nohup sleep 10
nohup cms cc run --command="echo hello world 3" > job_output.txt
nohup sleep 10
nohup cms cc run --command="echo hello world 4" > job_output.txt
nohup sleep 10
nohup cms cc run --command="echo hello world 5" > job_utput.txt
nohup sleep 10
echo "finished running the program"