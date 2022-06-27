#!/bin/bash -x
username="$1"
<<<<<<< HEAD
scp run.sh "$username"@rivanna.hpc.virginia.edu:.
ssh "$username"@rivanna.hpc.virginia.edu cat run.sh
ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.log; echo $pid"
ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.error; echo $pid"
scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
=======
scp run.sh atl9rn@rivanna.hpc.virginia.edu:.
ssh atl9rn@rivanna.hpc.virginia.edu cat run.sh
ssh atl9rn@rivanna.hpc.virginia.edu "nohup ./run.sh > run.log; echo $pid"
ssh atl9rn@rivanna.hpc.virginia.edu "nohup ./run.sh > error.log; echo $pid"
scp atl9rn@rivanna.hpc.virginia.edu:run.log run.log
>>>>>>> 3d801c03638f0be462f0458b14bbec50f02eb097
cat run.log