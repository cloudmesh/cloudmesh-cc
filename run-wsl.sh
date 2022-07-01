#!/bin/sh -x
LOG_FILE="run-wsl.log"
{
echo "# cloudmesh status=running progress=0 pid=$$"
date
echo "# cloudmesh status=running progress=0 pid=$$"
ls
echo "# cloudmesh status=running progress=10 pid=$$"
sleep 1
echo "# cloudmesh status=running progress=20 pid=$$"
hostname
echo "# cloudmesh status=done progress=100 pid=$$"
} 2>"run-wsl.err" | tee -- "$LOG_FILE"