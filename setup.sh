#!/bin/bash
# Disable GPU packages during deployment
export CUDA_VISIBLE_DEVICES=-1
export TRANSFORMERS_CACHE=/tmp/transformers_cache
export HF_HUB_CACHE=/tmp/huggingface_cache

echo "Setup complete: GPU disabled, using CPU-only packages"
