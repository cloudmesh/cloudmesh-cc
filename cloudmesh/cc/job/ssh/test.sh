#!/bin/bash -x
username="$1"
scp run.sh atl9rn@rivanna.hpc.virginia.edu:.
ssh atl9rn@rivanna.hpc.virginia.edu cat run.sh
ssh atl9rn@rivanna.hpc.virginia.edu "nohup ./run.sh > run.log; echo $pid"
ssh atl9rn@rivanna.hpc.virginia.edu "nohup ./run.sh > error.log; echo $pid"
scp atl9rn@rivanna.hpc.virginia.edu:run.log run.log
cat run.log