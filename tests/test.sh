#!/bin/bash -x
username="$1"

rm -f run.log
rm -f run.error


ssh "$username"@rivanna.hpc.virginia.edu rm -f run.sh run.log run.error

scp run.sh "$username"@rivanna.hpc.virginia.edu:.
ssh "$username"@rivanna.hpc.virginia.edu cat run.sh

# cat run.sh

ssh "$username"@rivanna.hpc.virginia.edu 'nohup ~/run.sh > ~/run.log 2>&1 &'
sleep 2
scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
# scp "$username"@rivanna.hpc.virginia.edu:run.error run.error

cat run.log
