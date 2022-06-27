#!/bin/bash -x
username="$1"
<<<<<<< HEAD

=======
>>>>>>> fad287017998f96019190af04754e0a080968b7a
scp run.sh "$username"@rivanna.hpc.virginia.edu:.
ssh "$username"@rivanna.hpc.virginia.edu cat run.sh
ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.log; echo $pid"
ssh "$username"@rivanna.hpc.virginia.edu "nohup ./run.sh > run.error; echo $pid"
scp "$username"@rivanna.hpc.virginia.edu:run.log run.log
<<<<<<< HEAD

=======
>>>>>>> fad287017998f96019190af04754e0a080968b7a
cat run.log