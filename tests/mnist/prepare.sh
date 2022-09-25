#!/bin/sh
echo "# cloudmesh status=running progress=1 pid=$$"
cd ~
rm -rf ~/experiment/mlp_mnist
rm -rf ~/experiment/run_all_rivanna
cd ~
git clone https://github.com/cybertraining-dsc/reu2022.git
cd ~/reu2022
git pull
echo "# cloudmesh status=running progress=50 pid=$$"
cd ~
mkdir ~/cm
cd ~/cm
git clone https://github.com/cloudmesh/cloudmesh-cc.git
cd ~/cm/cloudmesh-cc
git pull
echo "# cloudmesh status=running progress=100 pid=$$"
