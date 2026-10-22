# Evaluation, training, statistics and figures

## Five-sample evaluation

Both original inference entry points already accepted `--n_sampling`, with a
default of 1. Set it to 5 for five completions per item. `run_openai` forwards
the value as the API's `n` parameter; `run_vllm` passes it to `SamplingParams.n`.
An endpoint must support the requested `n`; API capabilities differ by model.
The five positions are evaluation sample slots, not five separately trained
models or evidence by themselves that item/seed-level independence holds.

```sh
python -m globalmed.run_openai --model_id MODEL_ID --subset MedQA --lang en \
  --prompt_style da --n_sampling 5 --max_tokens 16384

python -m globalmed.run_vllm --model_id MODEL_ID --subset MedQA --lang en \
  --prompt_style da --n_sampling 5 --max_tokens 16384

python -m globalmed.pretty_print --subset MedQA --prompt_style da --run_idx 0
python -m globalmed.summarize_runs results/MODEL_ID/MedQA_da/en.json --n_runs 5
```

Inspect `--run_idx 0` through `4` for each sample slot. `summarize_runs` checks
that every item has five answer slots and reports each accuracy, their mean,
sample SD, and missing-answer count. Missing answers count as incorrect.
Use the exact model ID/path and prompt style appropriate to the experiment.

This revision additionally exposes `--temperature`, `--top_p`, and `--seed` in
both entry points, plus `--think_mode` in local vLLM (already present in the API
entry point). Values are sent only when explicitly supplied; otherwise the
backend defaults apply. For example, `--temperature 0.7 --top_p 0.9 --seed 42`
illustrates the syntax and is **not a claim about the historical experiments**.
Model-specific original settings/logs were not supplied with the revision
materials, so no retrospective values have been inferred or invented.

Each new JSONL record stores its generation configuration and ordered sample
slots. Resume requires the requested number of nonempty responses and matching
configuration. Old one-sample results or logs without configuration metadata
are regenerated when requesting five. Existing records remain in the JSONL
unless `--overwrite` is used; the final JSON takes the latest record per ID.

## MedNLI: authorized local evaluation

MedNLI source data and translations are not redistributed. Obtain the original
resource through [PhysioNet](https://physionet.org/content/mednli/1.0.0/) under
the required credentialing and data use agreement. Access permission does not
automatically permit redistribution of source/derived data or prediction logs.

The new local adapter reuses the inference, extraction and scoring pipeline
without requesting any MedNLI data from Hugging Face. It accepts JSON arrays or
JSONL records with `premise`, `hypothesis`, and a named `gold_label` (original
`sentence1`/`sentence2` fields are also supported). It validates labels and IDs.
Prepare one authorized file per language/split; select the appropriate file.

```sh
python -m globalmed.run_openai --model_id MODEL_ID --subset MedNLI --lang en \
  --local_mednli /path/to/authorized_test.jsonl --prompt_style da --n_sampling 5
```

The same arguments work with `globalmed.run_vllm`. MedNLI has three options,
in the order printed in Supplementary Tab.55-66: **A entailment, B neutral,
C contradiction**. BioNLI has two; its label mapping is not reused. The 12
direct-answer templates are transcribed from those SI tables; only placeholder
names are normalized. No restricted item text is included in code or tests.
This is a newly added public adapter, not proof that it was previously released.

## Training

See [`training/README.md`](training/README.md) for the supplied full fine-tuning
recipes, pinned dependencies, five-public-dataset preparation, and conversion
of supplied distillation records. It identifies the missing original records
and restricted-data inputs needed for full historical checkpoint recreation.

## Statistical analysis

```sh
python analysis/reproduce_bh_fdr.py --output-dir analysis/reproduced
```

Python 3.10+ standard library only. The package contains the 23,040 printed
five-run input values, definitions of all 4,992 comparisons, two-sided paired
t calculations, BH-FDR adjustment, and numerical/rounding diagnostics. See
[`analysis/README.md`](analysis/README.md) for analysis families and limits.
This is a run-level analysis; it does not implement an item/rater-level model.

## Figure preparation

See [`plotting/README.md`](plotting/README.md) for the verified mapping of the
supplied R scripts to figure components, commands, data sources and corrections.
Schematics (for example Fig.1) were manually prepared in Adobe Illustrator,
maps in ArcGIS, and supplementary plots in Origin. Illustrator is a vector
graphics application; “AI” file format does not mean generative AI.
The supplied R scripts generate selected quantitative panels. Final artwork
also uses manual layout; these scripts are not a pixel-identical recreation of
every composite figure, ArcGIS project, or Origin project.

## Offline checks

```sh
pip install -e '.[dev]'
pytest -q tests
```

Tests use synthetic NLI examples and mocked requests. They do not invoke paid
APIs, download restricted data, run GPU inference, or retrain models.
