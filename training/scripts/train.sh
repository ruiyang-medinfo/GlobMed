#!/usr/bin/env bash
# Train one recipe with LLaMA-Factory: scripts/train.sh configs/<name>.yaml
# Multi-node: also export NNODES, NODE_RANK, MASTER_ADDR, MASTER_PORT on every node.
set -euo pipefail
cd "$(dirname "$0")/.."
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"  # DeepSpeed runs its nvcc on import, CPUAdam builds against it
export FORCE_TORCHRUN=1                           # DeepSpeed needs torchrun even on 1 GPU
uv run llamafactory-cli train "$@"
