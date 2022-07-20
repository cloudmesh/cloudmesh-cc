#!/bin/sh
#SBATCH --job-name=wait-slurm.sh
#SBATCH --output=wait-slurm.log
#SBATCH --partition=dev
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=3:00

echo "# cloudmesh status=running progress=1 pid=$$"
date
echo "# cloudmesh status=running progress=10 pid=$$"
ls
echo "# cloudmesh status=running progress=20 pid=$$"
pwd
echo "# cloudmesh status=running progress=30 pid=$$"
sleep 3600
echo "# cloudmesh status=running progress=50 pid=$$"
hostname
echo "# cloudmesh status=done progress=100 pid=$$"