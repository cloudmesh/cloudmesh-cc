#!/bin/sh
#SBATCH --job-name=example_mlp_mnist.sh
#SBATCH --output=example_mlp_mnist.log
#SBATCH --error=example_mlp_mnist.error
#SBATCH --partition=gpu
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=3:00

echo "# cloudmesh status=running progress=1 pid=$$"

nvidia-smi --list-gpus
source activate ENV3
python example_mlp_mnist.py

echo " cloudmesh status=done progress=100 pid=$$"#
