# Training

Four supplied full-parameter SFT configurations using LLaMA-Factory:

| Model | Configuration | Data |
|---|---|---|
| Qwen3-1.7B | `configs/qwen3_1_7b_paper.yaml` | Direct |
| Qwen3-8B | `configs/qwen3_8b_paper.yaml` | Direct |
| Qwen3-4B | `configs/qwen3_4b_paper.yaml` | Direct + distillation |
| MedGemma-4B | `configs/medgemma_4b_paper.yaml` | Direct + distillation |

Use Linux x86_64, Python 3.11, CUDA 12.8 and uv. Dependencies are pinned in
`uv.lock`; `setup_factory.sh` retrieves the fixed LLaMA-Factory version.

```sh
cd training
bash scripts/setup_factory.sh
uv sync --frozen
uv run python scripts/build_data.py
bash scripts/train.sh configs/qwen3_1_7b_paper.yaml
```

The paper configurations use 16 GPUs, global batch 256, learning rate 1e-5,
one epoch, bf16 and cutoff 4096. Set distributed launch variables for your cluster.

For a 4B configuration, build the distillation data from existing records:

```sh
uv run python scripts/build_data.py --distill /path/to/records.jsonl
bash scripts/train.sh configs/qwen3_4b_paper.yaml
```

Each record contains `id`, `dataset`, `lang`, `row`, `reasoning`, and `answer`.
The builder covers the five public datasets. Restricted MedNLI training data,
original distillation records, and their generation/filtering scripts are not
included, so this package alone cannot recreate the complete historical corpus.
