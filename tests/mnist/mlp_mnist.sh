#!/bin/sh
#SBATCH --job-name=mlp_mnist.sh
#SBATCH --output=mlp_mnist.log
#SBATCH --error=mlp_mnist.error
#SBATCH --partition=gpu
#SBATCH --cpus-per-task=1
#SBATCH --mem=8GB
#SBATCH --time=50:00

echo "# cloudmesh status=running progress=1 pid=$$"

nvidia-smi --list-gpus

# conda install pip
echo "# cloudmesh status=running progress=50 pid=$$"
#conda install pytorch torchvision -c pytorch
#conda install py-cpuinfo
#conda install --file requirements.txt
echo "# cloudmesh status=running progress=60 pid=$$"
module load singularity tensorflow/2.8.0
module load cudatoolkit/11.0.3-py3.8
module load cuda/11.4.2
module load cudnn/8.2.4.15
module load anaconda/2020.11-py3.8
cms set host=rivanna
cms set cpu=IntelXeonE5-2630
cms set device=rivanna
echo "# cloudmesh status=running progress=70 pid=$$"
cd ~
source activate ENV3
cd ~/reu2022/code/deeplearning/mnist/
#python run_all_rivanna.py
python mlp_mnist.py
python mnist_autoencoder.py
python mnist_cnn.py
python mnist_lstm.py
python mnist_mlp_with_lstm.py
python mnist_rnn.py
python mnist_with_distributed_training.py
python mnist_with_pytorch.py
echo "# cloudmesh status=done progress=100 pid=$$"
# python mlp_mnist.py
