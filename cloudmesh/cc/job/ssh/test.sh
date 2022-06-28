#!/bin/bash -x
username="$1"

scp run.sh "$username"@rivanna.hpc.virginia.edu:.
ssh "$username"@rivanna.hpc.virginia.edu cat run.sh

# cat run.sh

ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.log 2>run.error; echo $pid"
scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
scp "$username"@rivanna.hpc.virginia.edu:run.error run.error

cat run.log