#!/bin/sh
echo "# cloudmesh status=running progress=1 pid=$$"
echo "hello"
sleep 5
echo "# cloudmesh status=running progress=50 pid=$$"
echo "running"
sleep 5
echo "# cloudmesh status=done progress=100 pid=$$"