#!/bin/bash -x
username="$1"

scp run.sh "$username"@rivanna.hpc.virginia.edu:.
ssh "$username"@rivanna.hpc.virginia.edu cat run.sh
ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.log 2>run.error; echo $pid"
#ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.error; echo $pid"
scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
<<<<<<< HEAD
=======
scp "$username"@rivanna.hpc.virginia.edu:run.error run.error
>>>>>>> 86c406372a51099110cdfd46cfb32bdb85356dc9

cat run.log