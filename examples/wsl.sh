#!/bin/sh -x
PWD=`pwd`
echo $PWD
H="/mnt$PWD"

# remove local files
rm -f run-wsl.log run-wsl.error

# cd into wsl and remove wsl files
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && rm -f run-wsl.sh run-wsl.log run-wsl.err"

# copy from local into wsl
wsl sh -c ". ~/.profile && cp run-wsl.sh /mnt/c/Users/$USERNAME/run-wsl.sh"
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && cat run-wsl.sh"

# run
#wsl nohup sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && ./run-wsl.sh > ./run-wsl.log 2>&1 &" >&/dev/null
#wsl --cd /c/Users/$USERNAME nohup sh -c ". ~/.profile && ./run-wsl.sh > ./run-wsl.log 2>&1 &" >&/dev/null
wsl --cd /c/Users/$USERNAME nohup sh -c "./run-wsl.sh > ./run-wsl.log 2>&1 &" >&/dev/null


# wsl nohup sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && ./run-wsl.sh &"
sleep 2

# sync
wsl sh -c ". ~/.profile && cp /mnt/c/Users/$USERNAME/run-wsl.log $H/run-wsl.log"
#wsl sh -c ". ~/.profile && cp /mnt/c/Users/$USERNAME/run-wsl.err $H/run-wsl.err"

cat run-wsl.log

