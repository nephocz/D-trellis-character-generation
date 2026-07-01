#!/usr/bin/env bash
set -e

PROJECT_DIR="/root/trellis-character-generation"
TRELLIS_DIR="/root/TRELLIS.2"
CONFIG_PATH="${PROJECT_DIR}/configs/inference/baseline_autodl.yaml"

cd "${PROJECT_DIR}"

export PYTHONPATH="${TRELLIS_DIR}:${PYTHONPATH}"
export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

mkdir -p /root/autodl-tmp/input
mkdir -p /root/autodl-tmp/output

python scripts/inference/run_baseline.py \
  --config "${CONFIG_PATH}"