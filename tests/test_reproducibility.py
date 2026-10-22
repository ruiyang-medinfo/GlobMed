"""Offline checks; synthetic NLI text only, no GPU/model/API calls."""
import asyncio
import json
from argparse import Namespace
from pathlib import Path
import importlib.util

import pytest

from globalmed.data import get_num_options, read_data
from globalmed.judge import extract_answer
from globalmed.prompt import get_message_from_doc
from globalmed.mednli_prompts import MEDNLI_PROMPTS
from globalmed.run_openai import build_generation_args, process_item, generate_final_json
from globalmed.sampling import load_finished_ids, validate_arguments


def args(**overrides):
    return Namespace(**(dict(model_id="test-model", subset="MedQA", lang="en",
                            prompt_style="da", n_sampling=5, max_tokens=128,
                            temperature=0.7, top_p=0.9, seed=41,
                            reasoning_effort=None, think_mode="none", local_mednli=None)
                        | overrides))


def test_mednli_three_classes_and_all_prompts(tmp_path):
    path = tmp_path / "synthetic.jsonl"
    path.write_text("\n".join(json.dumps({"sentence1": "Synthetic premise.",
                    "sentence2": "Synthetic hypothesis.", "gold_label": label})
                    for label in ["entailment", "neutral", "contradiction"]))
    items = read_data("MedNLI", "en", local_mednli=path)
    assert [row["answer_index"] for row in items] == [0, 1, 2]
    assert get_num_options("MedNLI") == 3
    for lang in MEDNLI_PROMPTS:
        prompt = get_message_from_doc(items[0], "MedNLI", lang, "da")[0]["content"]
        assert "Synthetic premise." in prompt and "Synthetic hypothesis." in prompt
        assert "C. " in prompt and "{" not in prompt
    assert extract_answer("B", num_choices=3) == "B"
    assert extract_answer("C", num_choices=3) == "C"
    assert extract_answer("D", num_choices=3) is None


def test_mednli_invalid_label_and_no_remote_fallback(tmp_path):
    with pytest.raises(ValueError, match="not distributed"):
        read_data("MedNLI", "en")
    path = tmp_path / "synthetic.json"
    row = {"premise": "P", "hypothesis": "H", "gold_label": "neutral", "answer_index": 2}
    path.write_text(json.dumps([row]))
    with pytest.raises(ValueError, match="conflicts"):
        read_data("MedNLI", "en", local_mednli=path)
    row.pop("answer_index"); row["gold_label"] = "unknown"
    path.write_text(json.dumps([row]))
    with pytest.raises(ValueError, match="unrecognized"):
        read_data("MedNLI", "en", local_mednli=path)


def test_five_samples_and_settings_are_forwarded():
    captured = {}
    class Completions:
        async def create(self, **kwargs):
            captured.update(kwargs)
            return Namespace(choices=[Namespace(index=i) for i in range(kwargs["n"])])
    client = Namespace(chat=Namespace(completions=Completions()))
    row = dict(id="synthetic", question="Synthetic question", options={"A": "a", "B": "b"})
    result = asyncio.run(process_item(client, row, args(), "en"))
    assert len(result["response"].choices) == 5
    assert {k: captured[k] for k in ["n", "temperature", "top_p", "seed", "max_tokens"]} == {
        "n": 5, "temperature": 0.7, "top_p": 0.9, "seed": 41, "max_tokens": 128}
    gen = build_generation_args(args(temperature=None, top_p=None, seed=None))
    assert not {"temperature", "top_p", "seed"} & gen.keys()


def test_resume_requires_latest_complete_five_samples_and_settings(tmp_path):
    path = tmp_path / "results.jsonl"; gen = {"n": 5}
    one = {"id": "x", "responses": [{"content": "A"}], "generation": gen}
    five = dict(one, responses=[{"content": "A"}] * 5)
    path.write_text(json.dumps(one) + "\n")
    assert load_finished_ids(path, 5, gen) == []
    path.write_text(json.dumps(one) + "\n" + json.dumps(five) + "\n")
    assert load_finished_ids(path, 5, gen) == ["x"]
    assert load_finished_ids(path, 5, {"n": 5, "temperature": 0.8}) == []
    path.write_text(json.dumps(five) + "\n" + json.dumps(one) + "\n")
    assert load_finished_ids(path, 5, gen) == []


def test_final_export_preserves_five_slots(tmp_path):
    path = tmp_path / "en.jsonl"
    path.write_text(json.dumps({"id": "x", "metadata": {"answer_index": 1},
                    "responses": [{"content": c, "answer": c} for c in "ABCBA"]}) + "\n")
    generate_final_json(str(path), "en", {"x"})
    result = json.loads(path.with_suffix(".json").read_text())
    assert result == [{"id": "x", "answer": list("ABCBA"), "ground_truth": "B"}]


def test_vllm_template_switch_without_gpu():
    from globalmed.run_vllm import prepare_prompts
    class Tokenizer:
        def apply_chat_template(self, messages, **kwargs):
            assert kwargs["enable_thinking"] is False
            return messages[0]["content"]
    prompt = prepare_prompts([dict(question="Synthetic", options={"A": "a"})],
                             Tokenizer(), args(think_mode="nothink"), "en")
    assert len(prompt) == 1


@pytest.mark.parametrize("overrides", [dict(n_sampling=0), dict(top_p=0),
                                     dict(temperature=-1), dict(subset="MedNLI")])
def test_invalid_settings_fail_early(overrides):
    with pytest.raises(ValueError):
        validate_arguments(args(**overrides))


def test_summary_is_across_runs():
    from globalmed.summarize_runs import summarize
    rows = [{"id": "a", "ground_truth": "A", "answer": list("AAABA")},
            {"id": "b", "ground_truth": "B", "answer": list("BBBAB")}]
    result = summarize(rows)
    assert result["run_accuracy_percent"] == [100, 100, 100, 0, 100]
    assert result["mean_accuracy_percent"] == 80
    rows[0]["answer"] = ["A"]
    with pytest.raises(ValueError, match="exactly 5"):
        summarize(rows)


def test_training_data_validation(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "training/scripts/build_data.py"
    spec = importlib.util.spec_from_file_location("build_data", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.check_answer_sentences()
    doc = {"id": "MedQA_en_0", "question": "Synthetic", "options": {"A": "yes", "B": None},
           "answer_index": 0}
    assert module.clean(doc)["options"] == {"A": "yes"}
    assert module.clean(dict(doc, answer_index=1)) is None
    monkeypatch.setattr(module, "load", lambda *unused: [doc])
    record = {"id": "MedQA_en_0", "dataset": "MedQA", "lang": "en", "row": 0,
              "reasoning": "Synthetic reasoning", "answer": "A"}
    records = tmp_path / "synthetic.jsonl"; records.write_text(json.dumps(record))
    samples = module.build_distill(records)
    assert len(samples) == 1 and "<think>" in samples[0]["conversations"][1]["value"]
    records.write_text(json.dumps(record) + "\n" + json.dumps(record))
    with pytest.raises(ValueError, match="Duplicate"):
        module.build_distill(records)
    record["answer"] = "B"; records.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="wrong answer"):
        module.build_distill(records)


def test_training_recipe_configurations():
    import yaml
    root = Path(__file__).resolve().parents[1] / "training/configs"
    for path in root.glob("*_paper.yaml"):
        config = yaml.safe_load(path.read_text())
        assert config["finetuning_type"] == "full"
        assert config["per_device_train_batch_size"] * config["gradient_accumulation_steps"] * 16 == 256
        assert config["learning_rate"] == 1e-5
        assert config["num_train_epochs"] == 1
        assert config["cutoff_len"] == 4096
        assert config["seed"] == 42
