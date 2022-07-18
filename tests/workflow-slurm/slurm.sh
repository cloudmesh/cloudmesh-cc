#!/usr/bin/env bash
#SBATCH --job-name=slurm
#SBATCH --output=%u-%j.out
#SBATCH --error=%u-%j.err
#SBATCH --partition=dev
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=3:00

echo "# cloudmesh status=running progress=1 pid=$$"
echo hellothere
date
echo "# cloudmesh status=running progress=100 pid=$$"