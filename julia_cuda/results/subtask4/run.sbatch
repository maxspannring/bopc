#!/bin/bash
#SBATCH -t 10
#SBATCH -p q_student_gpu
#SBATCH --gres=gpu:tesla:1
#SBATCH -c 32
#SBATCH -J julia_t4
#SBATCH -o subtask4_%j.out
#SBATCH -e subtask4_%j.err

export PATH=/usr/local/cuda/bin:$PATH

GPU_BIN=$HOME/juliaset_gpu
CPU_BIN=$HOME/juliaset_cpu
WORKDIR=$HOME/runs/subtask4
mkdir -p "$WORKDIR"
cd "$WORKDIR"

SIZE_LIST=(1000 2000 4000 8000 16000)
NREP=5
BSIZE_X=1
BSIZE_Y=32

NPROC=$(nproc)
export OMP_NUM_THREADS=$NPROC

echo "host=$(hostname) date=$(date -Iseconds)"
echo "nproc=$NPROC  OMP_NUM_THREADS=$OMP_NUM_THREADS"
nvidia-smi -L
echo "---"

# --- GPU ---
echo "=== GPU (blocksize ${BSIZE_X}x${BSIZE_Y}) ==="
for SIZE in "${SIZE_LIST[@]}"; do
  echo ">>> GPU r=${SIZE}"
  "$GPU_BIN" -r $SIZE $SIZE -b $BSIZE_X $BSIZE_Y -n $NREP -o "task4_gpu_${SIZE}.csv"
  cat "task4_gpu_${SIZE}.csv"
done

# --- CPU ---
echo "=== CPU (OMP_NUM_THREADS=$OMP_NUM_THREADS) ==="
for SIZE in "${SIZE_LIST[@]}"; do
  echo ">>> CPU r=${SIZE}"
  "$CPU_BIN" -r $SIZE $SIZE -n $NREP -o "task4_cpu_${SIZE}.csv"
  cat "task4_cpu_${SIZE}.csv"
done

echo "--- done ---"
ls -lh *.csv
