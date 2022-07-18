#!/usr/bin/env bash
#SBATCH --job-name=end.sh
#SBATCH --output=end.log
#SBATCH --error=end.error
#SBATCH --partition=dev
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=3:00

echo "done"
echo "# cloudmesh status=done progress=100 pid=$$"