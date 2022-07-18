#!/usr/bin/env bash
#SBATCH --job-name=start.sh
#SBATCH --output=start.log
#SBATCH --error=start.error
#SBATCH --partition=dev
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=3:00

echo "start"
echo "# cloudmesh status=done progress=100 pid=$$"