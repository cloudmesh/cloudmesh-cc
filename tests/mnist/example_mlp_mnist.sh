#!/bin/sh
#SBATCH --job-name=example_mlp_mnist.sh
#SBATCH --output=example_mlp_mnist.log
#SBATCH --error=example_mlp_mnist.error
#SBATCH --partition=bii
#SBATCH --cpus-per-task=1
#SBATCH --mem=8GB
#SBATCH --time=15:00

echo "# cloudmesh status=running progress=1 pid=$$"

nvidia-smi --list-gpus
python ~/cloudmesh-cc/tests/mnist/create_python.py
source activate ENV3
echo "# cloudmesh status=running progress=50 pid=$$"
cd ~/reu2022/code/deeplearning/
git pull
pip install -r requirements.txt
conda install pytorch torchvision -c pytorch
conda install py-cpuinfo
conda install --file requirements.txt
mkdir ~/cm
cd ~/cm
pip install cloudmesh-installer -U
cloudmesh-installer get cc
cd ~/reu2022/code/deeplearning/mnist/
cms set gpu=v100
cms set user=dje5dj
cms set host=rivanna
cms set cpu=IntelXeonE5-2630
cms set device=rivanna
python run_all_rivanna.py
echo "# cloudmesh status=done progress=100 pid=$$"
# python example_mlp_mnist.py
