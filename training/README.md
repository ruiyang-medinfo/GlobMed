# GlobMed full fine-tuning recipes

These are the supplied training recipes, reorganized for this repository. They
use LLaMA-Factory and full-parameter SFT (`finetuning_type: full`), not LoRA.
The configurations are not checkpoint training logs or a record of the original
runtime environment. End-to-end GPU training has not been rerun for this release.

| Model | Configuration | Training data |
|---|---|---|
| Qwen3-1.7B | `configs/qwen3_1_7b_paper.yaml` | Direct SFT |
| Qwen3-8B | `configs/qwen3_8b_paper.yaml` | Direct SFT |
| Qwen3-4B | `configs/qwen3_4b_paper.yaml` | Direct + supplied distillation records |
| MedGemma-4B | `configs/medgemma_4b_paper.yaml` | Direct + supplied distillation records |

The paper recipes specify 16 GPUs, per-device batch 8, accumulation 2 (global
batch 256), learning rate 1e-5, one epoch, bf16, cosine schedule, warmup 0.1,
cutoff 4096, seed 42 and DeepSpeed ZeRO-2. The two 4B recipes mix direct and
distillation data at their natural sizes in one stage. Qwen3 uses its thinking
template. `*_local.yaml` files are short smoke-test configurations.

## Environment

Use Linux x86_64, Python 3.11, CUDA toolkit 12.8, compatible NVIDIA drivers, gcc
and uv. Dependencies are pinned in `pyproject.toml` / `uv.lock`, including torch
2.8.0, transformers 4.57.1 and LLaMA-Factory commit
`95ac3f2373b82662c1bd855c284d3379e6a763d3`.
The 428 supplied LLaMA-Factory files matched that upstream commit byte for byte;
the dependency is fetched rather than duplicated in this repository.

```sh
cd training
bash scripts/setup_factory.sh
uv sync --frozen
uv run python scripts/build_data.py
bash scripts/train.sh configs/qwen3_1_7b_paper.yaml
```

Set distributed environment variables as required by LLaMA-Factory on each
node. Change gradient accumulation if the GPU count changes and global batch
256 is to be retained. The recipes retain the supplied output/cache overwrite
settings; choose distinct output directories for separate training jobs.

## Data and scope

`build_data.py` builds ShareGPT examples from the five **public** training
datasets (MedQA, HeadQA, MedExpQA, MMLU-Pro and BioNLI) in 12 languages. It uses
this repository's prompt code, removes empty options, validates answers and
shuffles with seed 42. Counts are reported from the files actually loaded.
Public Hugging Face sources may evolve; archive their revisions locally for
any new experiment. This script alone does not recreate the paper's complete
six-dataset training corpus: authorized MedNLI-derived training data are not
included. The evaluation-only MedNLI loader is documented separately.

For the two 4B recipes, provide previously generated and screened reasoning
records; the script converts and checks them, but does not generate, translate,
or screen reasoning chains:

```json
{"id":"MedQA_zh_123","dataset":"MedQA","lang":"zh","row":123,"reasoning":"...","answer":"B"}
```

```sh
uv run python scripts/build_data.py --distill /path/to/authorized_records.jsonl
bash scripts/train.sh configs/qwen3_4b_paper.yaml
```

The original reasoning records and the upstream generation/screening scripts
were not supplied with this package. Without those inputs and any applicable
restricted training data, these recipes should not be described as an exact
recreation of the released paper's trained checkpoints. Do not redistribute
restricted source text, translations, or derived outputs through this repository.

## Evaluation

`scripts/quick_eval.sh` runs a five-question smoke test with **one completion**.
It is not the paper evaluation. For five evaluation samples per item use
`--n_sampling 5` and inspect `--run_idx 0` through `4`; see
[`../REPRODUCIBILITY.md`](../REPRODUCIBILITY.md). Model weights are not bundled.
