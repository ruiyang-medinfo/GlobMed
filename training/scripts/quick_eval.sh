#!/usr/bin/env bash
# Quick evaluation of a checkpoint with the official GlobMed CLI (da prompts, 5 datasets x 12 languages x 5 questions).
# Usage: scripts/quick_eval.sh outputs/qwen3_1_7b_local
# Raw results go to ../results/; the accuracy tables to <checkpoint>/quick_eval.txt.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHON_DOTENV_DISABLED=1  # run_vllm needs no API keys; don't let it load a .env
CKPT="${1:?usage: scripts/quick_eval.sh <checkpoint dir>}"
REPORT="$CKPT/quick_eval.txt"
: > "$REPORT"
for ds in MedQA HeadQA MedExpQA MMLU-Pro BioNLI; do
  uv run python -m globalmed.run_vllm --model_id "$CKPT" --subset "$ds" \
    --prompt_style da --limit 5 --n_sampling 1 --gpu_memory_utilization 0.8 --overwrite
  uv run python -m globalmed.pretty_print --subset "$ds" --prompt_style da | tee -a "$REPORT"
done
