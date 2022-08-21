#!/bin/sh
echo "# cloudmesh status=running progress=1 pid=$$"
cd ~
git clone https://github.com/cybertraining-dsc/reu2022.git
cd ~/reu2022
git pull
echo "# cloudmesh status=running progress=50 pid=$$"
cd ~
git clone https://github.com/cloudmesh/cloudmesh-cc.git
cd ~/cloudmesh-cc
git pull
# scp ../reu2022/code/deeplearning/example_mlp_mnist.py rivanna:~
echo "# cloudmesh status=running progress=100 pid=$$"
