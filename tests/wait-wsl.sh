#!/bin/sh -x
echo "# cloudmesh status=running progress=1 pid=$$"
date
echo "# cloudmesh status=running progress=10 pid=$$"
ls
echo "# cloudmesh status=running progress=20 pid=$$"
pwd
echo "# cloudmesh status=running progress=30 pid=$$"
sleep 10
echo "# cloudmesh status=running progress=50 pid=$$"
hostname
echo "# cloudmesh status=done progress=100 pid=$$"
