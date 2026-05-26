#!/bin/bash
#SBATCH -t 10
#SBATCH -p q_student_gpu
#SBATCH --gres=gpu:tesla:1
#SBATCH -J julia_t2
#SBATCH -o subtask2_%j.out
#SBATCH -e subtask2_%j.err

export PATH=/usr/local/cuda/bin:$PATH

BINARY=$HOME/juliaset_gpu
WORKDIR=$HOME/runs/subtask2
mkdir -p "$WORKDIR"
cd "$WORKDIR"

SIZE_LIST=(1000 2000 4000 8000 16000)
NREP=5

echo "host=$(hostname) date=$(date -Iseconds)"
nvidia-smi -L
echo "---"

for SIZE in "${SIZE_LIST[@]}"; do
  echo ">>> resolution ${SIZE}x${SIZE}"
  "$BINARY" -r "$SIZE" "$SIZE" -n "$NREP" -o "task2_${SIZE}.csv"
  echo "  -> $(cat task2_${SIZE}.csv)"
done

echo "--- done ---"
ls -la *.csv
