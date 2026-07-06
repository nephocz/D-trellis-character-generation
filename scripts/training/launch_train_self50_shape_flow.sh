#!/usr/bin/env bash
set -e

PROJECT_ROOT="/root/trellis-character-generation"
TRELLIS_ROOT="/root/TRELLIS.2"

DATASET_ROOT="/root/autodl-tmp/trellis_character_data/trellis_dataset"
CONFIG_PATH="${PROJECT_ROOT}/configs/training/train_self50_shape_flow.json"
OUTPUT_DIR="/root/autodl-tmp/trellis_runs/exp001_self50_shape_flow"

SHAPE_LATENT_DIR="${DATASET_ROOT}/shape_latents/shape_enc_next_dc_f16c32_fp16_256"
RENDER_COND_DIR="${DATASET_ROOT}/renders_cond"

DATA_DIR_JSON="{\"AnimeCharacterSelf50\": {\"base\": \"${DATASET_ROOT}\", \"shape_latent\": \"${SHAPE_LATENT_DIR}\", \"render_cond\": \"${RENDER_COND_DIR}\"}}"

export CUDA_HOME=/usr/local/cuda-12.4
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export OPENCV_IO_ENABLE_OPENEXR=1

mkdir -p "${OUTPUT_DIR}"

if [ ! -f "${CONFIG_PATH}" ]; then
  echo "[ERROR] Config not found: ${CONFIG_PATH}"
  exit 1
fi

if [ ! -f "${DATASET_ROOT}/metadata.csv" ]; then
  echo "[ERROR] metadata.csv not found: ${DATASET_ROOT}/metadata.csv"
  exit 1
fi

if [ ! -d "${SHAPE_LATENT_DIR}" ]; then
  echo "[ERROR] shape_latent dir not found: ${SHAPE_LATENT_DIR}"
  echo "Run data_toolkit/encode_shape_latent.py first, then check actual folder name."
  exit 1
fi

if [ ! -d "${RENDER_COND_DIR}" ]; then
  echo "[ERROR] render_cond dir not found: ${RENDER_COND_DIR}"
  echo "Run data_toolkit/render_cond.py first."
  exit 1
fi

cd "${TRELLIS_ROOT}"

echo "========================================"
echo "Experiment: exp001_self50_shape_flow"
echo "Project root: ${PROJECT_ROOT}"
echo "TRELLIS root: ${TRELLIS_ROOT}"
echo "Config: ${CONFIG_PATH}"
echo "Output dir: ${OUTPUT_DIR}"
echo "Dataset root: ${DATASET_ROOT}"
echo "Shape latent: ${SHAPE_LATENT_DIR}"
echo "Render cond: ${RENDER_COND_DIR}"
echo "========================================"

python train.py \
  --config "${CONFIG_PATH}" \
  --output_dir "${OUTPUT_DIR}" \
  --data_dir "${DATA_DIR_JSON}"