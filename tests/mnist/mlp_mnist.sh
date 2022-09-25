#!/bin/sh
#SBATCH --job-name=mlp_mnist.sh
#SBATCH --output=mlp_mnist.log
#SBATCH --error=mlp_mnist.error
#SBATCH --partition=gpu
#SBATCH --cpus-per-task=1
#SBATCH --mem=8GB
#SBATCH --time=50:00
#SBATCH --gres=gpu:v100:1

echo "# cloudmesh status=running progress=1 pid=$$"

nvidia-smi --list-gpus
python ~/cloudmesh-cc/tests/mnist/create_python.py
# conda install pip
echo "# cloudmesh status=running progress=50 pid=$$"
cd ~/reu2022/code/deeplearning/
git pull
pip install -r requirements.txt
cd ~/cloudmesh-cc
pip install -e .
conda install pytorch torchvision -c pytorch
conda install py-cpuinfo
conda install --file requirements.txt
echo "# cloudmesh status=running progress=60 pid=$$"
module load singularity tensorflow/2.8.0
module load cudatoolkit/11.0.3-py3.8
module load cuda/11.4.2
module load cudnn/8.2.4.15
module load anaconda/2020.11-py3.8
mkdir ~/cm
cd ~/cm
pip install cloudmesh-installer -U
cloudmesh-installer get cc
cd ~/reu2022/code/deeplearning/mnist/
cms set gpu=a100
cms set user=dje5dj
cms set host=rivanna
cms set cpu=IntelXeonE5-2630
cms set device=rivanna
echo "# cloudmesh status=running progress=70 pid=$$"
#python run_all_rivanna.py
python mlp_mnist.py
echo "# cloudmesh status=done progress=100 pid=$$"
# python mlp_mnist.py
