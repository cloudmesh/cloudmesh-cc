#!/bin/sh
echo "# cloudmesh status=running progress=1 pid=$$"
scp ~/cm/reu2022/code/deeplearning/mnist_all_rivanna.sh rivanna:~
echo "# cloudmesh status=running progress=100 pid=$$"
