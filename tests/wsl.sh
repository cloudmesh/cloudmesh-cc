#!/bin/bash -x
USERNAME="$1"
PWD=`pwd`
echo $PWD
H="/mnt$PWD"

rm -f run.log
rm -f run.error

wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && rm -f run.sh"
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && rm -f run.log"
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && rm -f run.err"

wsl sh -c ". ~/.profile && cp run.sh /mnt/c/Users/$USERNAME/run.sh"
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && cat run.sh"

# cat run.sh

wsl nohup sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && ./run.sh &"
sleep 2
wsl sh -c ". ~/.profile && cp /mnt/c/Users/$USERNAME/run.log $H/run.log"
wsl sh -c ". ~/.profile && cp /mnt/c/Users/$USERNAME/run.error $H/run.error"

cat run.log


