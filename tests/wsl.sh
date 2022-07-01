#!/bin/bash -x
PWD=`pwd`
echo $PWD
H="/mnt$PWD"

rm -f run-wsl.log
rm -f run-wsl.error

wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && rm -f run-wsl.sh"
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && rm -f run-wsl.log"
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && rm -f run-wsl.err"

wsl sh -c ". ~/.profile && cp run-wsl.sh /mnt/c/Users/$USERNAME/run-wsl.sh"
wsl sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && cat run-wsl.sh"

# cat run-wsl.sh

wsl nohup sh -c ". ~/.profile && cd /mnt/c/Users/$USERNAME && ./run-wsl.sh &"
sleep 2
wsl sh -c ". ~/.profile && cp /mnt/c/Users/$USERNAME/run-wsl.log $H/run-wsl.log"
wsl sh -c ". ~/.profile && cp /mnt/c/Users/$USERNAME/run-wsl.err $H/run-wsl.err"

cat run-wsl.log


