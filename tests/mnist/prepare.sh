#!/bin/sh
echo "# cloudmesh status=running progress=1 pid=$$"
scp ../reu2022/code/deeplearning/example_mlp_mnist.py rivanna:~
echo "# cloudmesh status=running progress=100 pid=$$"
