#!/bin/sh
echo "# cloudmesh status=running progress=1 pid=$$"
cd ~
rm -rf ~/experiment/mlp_mnist
rm -rf ~/experiment/run_all_rivanna
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
cd ~
python ~/cm/cloudmesh-cc/tests/mnist/create_python.py
echo "# cloudmesh status=running progress=75 pid=$$"
source activate ENV3
cd ~/reu2022/code/deeplearning/
pip install -r requirements.txt
cd ~/cm/cloudmesh-cc
pip install -e .
cd ~/cm
pip install cloudmesh-installer -U
cloudmesh-installer get cc
echo "# cloudmesh status=running progress=100 pid=$$"
