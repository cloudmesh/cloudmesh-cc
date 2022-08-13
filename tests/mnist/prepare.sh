#!/bin/sh
echo "# cloudmesh status=running progress=1 pid=$$"
cd ~
git clone https://github.com/cybertraining-dsc/reu2022.git
# scp ../reu2022/code/deeplearning/example_mlp_mnist.py rivanna:~
echo "# cloudmesh status=running progress=100 pid=$$"
