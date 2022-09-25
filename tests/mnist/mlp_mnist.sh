#!/bin/sh
#SBATCH --job-name=mlp_mnist.sh
#SBATCH --output=mlp_mnist.log
#SBATCH --error=mlp_mnist.error
#SBATCH --partition=gpu
#SBATCH --cpus-per-task=1
#SBATCH --mem=8GB
#SBATCH --time=4:00:00
#SBATCH --gres=gpu:v100:1

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
echo "# cloudmesh status=running progress=60 pid=$$"
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
module load singularity tensorflow/2.8.0
echo "# cloudmesh status=running progress=70 pid=$$"
#python run_all_rivanna.py
singularity run --nv $CONTAINERDIR/tensorflow-2.8.0.sif run_all_rivanna.py
echo "# cloudmesh status=done progress=100 pid=$$"
# python mlp_mnist.py
