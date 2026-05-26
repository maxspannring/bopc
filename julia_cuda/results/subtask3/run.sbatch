#!/bin/bash
#SBATCH -t 15
#SBATCH -p q_student_gpu
#SBATCH --gres=gpu:tesla:1
#SBATCH -J julia_t3
#SBATCH -o subtask3_%j.out
#SBATCH -e subtask3_%j.err

export PATH=/usr/local/cuda/bin:$PATH

BINARY=$HOME/juliaset_gpu
WORKDIR=$HOME/runs/subtask3
mkdir -p "$WORKDIR"
cd "$WORKDIR"

SIZE=20000
NREP=5

# block sizes — (1,1) last because it is slowest
BSIZE_X_LIST=(1024 128 32 1 1)
BSIZE_Y_LIST=(1    1  1  32 1)
BSIZE_LEN=${#BSIZE_X_LIST[@]}

echo "host=$(hostname) date=$(date -Iseconds)"
nvidia-smi -L
echo "---"

# --- TIMING section ---
echo "=== TIMING ==="
for (( i=0; i<BSIZE_LEN; i++ )); do
  BX=${BSIZE_X_LIST[$i]}
  BY=${BSIZE_Y_LIST[$i]}
  echo ">>> block (${BX},${BY})"
  "$BINARY" -r $SIZE $SIZE -b $BX $BY -n $NREP -o "task3_${BX}_${BY}.csv"
  cat "task3_${BX}_${BY}.csv"
done

# --- PROFILING section (nrep=1 each) ---
echo "=== PROFILING ==="
METRICS="achieved_occupancy,gld_throughput,gst_throughput,warp_execution_efficiency"
for (( i=0; i<BSIZE_LEN; i++ )); do
  BX=${BSIZE_X_LIST[$i]}
  BY=${BSIZE_Y_LIST[$i]}
  PROF_OUT="prof_${BX}_${BY}.txt"
  echo ">>> nvprof block (${BX},${BY})"
  nvprof --metrics "$METRICS" --log-file "$PROF_OUT" \
    "$BINARY" -r $SIZE $SIZE -b $BX $BY -n 1
  echo "  -> wrote $PROF_OUT"
done

echo "--- done ---"
ls -lh *.csv *.txt
