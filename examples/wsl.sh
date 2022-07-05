#!/bin/sh -x
# run by standing in cloudmesh-cc/tests and execute ../examples/wsl.sh
PWD=`pwd`
echo $PWD
H="/mnt$PWD"

# remove local files
rm -f run.log run.error

# cd into wsl and remove wsl files
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && rm -f run.sh run.log run.err"

# copy from local into wsl
wsl sh -c ". ~/.profile && cp run.sh /mnt/c/Users/$USERNAME/run.sh"
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && cat run.sh"

# run
#wsl nohup sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && ./run.sh > ./run.log 2>&1 &" >&/dev/null
#wsl --cd /c/Users/$USERNAME nohup sh -c ". ~/.profile && ./run.sh > ./run.log 2>&1 &" >&/dev/null
wsl --cd /c/Users/$USERNAME nohup sh -c "./run.sh > ./run.log 2>&1 &" >&/dev/null


# wsl nohup sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && ./run.sh &"
sleep 2

# sync
wsl sh -c ". ~/.profile && cp /mnt/c/Users/$USERNAME/run.log $H/run.log"
#wsl sh -c ". ~/.profile && cp /mnt/c/Users/$USERNAME/run.err $H/run.err"

cat run.log

