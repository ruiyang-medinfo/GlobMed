"""Build the GlobMed SFT data for LLaMA-Factory from the HF train splits.

Reads ruiyang-medinfo/GlobMed_{MedQA,HeadQA,MedExpQA,MMLU-Pro,BioNLI} (train, 12 languages)
through the official GlobMed package, so training prompts use the same templates as the
evaluation (empty answer options are dropped).

    uv run python scripts/build_data.py                                       # direct data
    uv run python scripts/build_data.py --distill path/to/records.jsonl       # + distill data

Writes data/globmed_direct_train.json (and data/globmed_distill_train.json), both
ShareGPT, registered in data/dataset_info.json as globmed_direct / globmed_distill.
"""

import argparse
import json
import random
import re
from collections import Counter
from functools import cache
from pathlib import Path
from string import ascii_uppercase

from globalmed.data import DEFAULT_LANGUAGES, read_data
from globalmed.prompt import ANSWER_CAPTURE_PATTERNS, get_message_from_doc

SUBSETS = ["MedQA", "HeadQA", "MedExpQA", "MMLU-Pro", "BioNLI"]
SEED = 42
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# The answer sentence each language's prompt asks for; must match ANSWER_CAPTURE_PATTERNS.
ANSWER_SENTENCES = {
    "en": "the answer is ({})",
    "zh": "答案是({})",
    "fr": "La réponse est ({})",
    "de": "Die Antwort ist ({})",
    "ja": "答えは({})",
    "ko": "답은 ({})입니다",
    "pt": "A resposta é ({})",
    "es": "La respuesta es ({})",
    "sw": "Jibu ni ({})",
    "wo": "Tontu bi mooy ({})",
    "yo": "Ìdáhùn náà ni ({})",
    "zu": "Impendulo ithi ({})",
}


def check_answer_sentences() -> None:
    """Every answer sentence must be captured by the official regex, as globalmed.judge does."""
    assert set(ANSWER_SENTENCES) == set(DEFAULT_LANGUAGES)
    for lang, sentence in ANSWER_SENTENCES.items():
        for letter in "ABCDEFGHIJ":
            matches = re.findall(ANSWER_CAPTURE_PATTERNS[lang], sentence.format(letter), re.IGNORECASE | re.DOTALL)
            assert matches and matches[-1].upper() == letter, f"{lang}: {sentence!r} not captured for {letter}"


@cache
def load(subset: str, lang: str) -> list[dict]:
    return read_data(subset, lang, split="train")


def gold_letter(doc: dict) -> str:
    return ascii_uppercase[doc["answer_index"]]


def clean(doc: dict) -> dict | None:
    """Drop empty options; return None when the row cannot form a valid sample."""
    if "options" not in doc:  # BioNLI: fixed A/B options live in the template
        return doc
    options = {k: v for k, v in doc["options"].items() if v is not None and str(v).strip()}
    if gold_letter(doc) not in options:
        return None
    return {**doc, "options": options}


def to_sample(doc: dict, subset: str, lang: str, prompt_style: str, response: str) -> dict:
    prompt = get_message_from_doc(doc, subset, lang, prompt_style)[0]["content"]
    return {
        "id": doc["id"],
        "conversations": [
            {"from": "human", "value": prompt.strip()},
            {"from": "gpt", "value": response.strip()},
        ],
    }


def answer_sentence(doc: dict, lang: str) -> str:
    return ANSWER_SENTENCES[lang].format(gold_letter(doc))


def build_direct() -> list[dict]:
    samples, dropped = [], []
    for subset in SUBSETS:
        for lang in DEFAULT_LANGUAGES:
            for doc in load(subset, lang):
                cleaned = clean(doc)
                if cleaned is None:
                    dropped.append(doc["id"])
                    continue
                samples.append(to_sample(cleaned, subset, lang, "da", answer_sentence(cleaned, lang)))
    print(f"direct: {len(samples)} samples, dropped {len(dropped)}: {dropped}")
    return samples


def build_distill(records_path: Path) -> list[dict]:
    """Turn reasoning records ({id,dataset,lang,row,reasoning,answer} per line) into think-format samples."""
    samples, seen = [], set()
    for line in records_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        subset, lang = record["dataset"], record["lang"]
        if subset not in SUBSETS or lang not in DEFAULT_LANGUAGES:
            raise ValueError("Distillation record uses an unsupported dataset or language")
        if type(record["row"]) is not int or record["row"] < 0:
            raise ValueError("Distillation row must be a nonnegative integer")
        if record["id"] in seen:
            raise ValueError(f"Duplicate distillation ID: {record['id']}")
        if not isinstance(record["reasoning"], str) or not record["reasoning"].strip():
            raise ValueError(f"Empty reasoning: {record['id']}")
        seen.add(record["id"])
        doc = clean(load(subset, lang)[record["row"]])
        if doc is None or doc["id"] != record["id"]:
            raise ValueError(f"record {record['id']} does not match its source row")
        if record["answer"] != gold_letter(doc):
            raise ValueError(f"record {record['id']} has a wrong answer")
        response = f"<think>\n{record['reasoning'].strip()}\n</think>\n\n{answer_sentence(doc, lang)}"
        samples.append(to_sample(doc, subset, lang, "shot", response))
    print(f"distill: {len(samples)} samples from {records_path}")
    return samples


def write_shuffled(samples: list[dict], name: str) -> None:
    random.Random(SEED).shuffle(samples)
    path = DATA_DIR / name
    with path.open("w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False)
    counts = Counter(s["id"].rsplit("_", 2)[0] for s in samples)
    print(f"wrote {len(samples)} samples to {path} ({dict(counts)})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--distill", type=Path, help="reasoning records (JSONL) to turn into distill data")
    args = parser.parse_args()

    check_answer_sentences()
    DATA_DIR.mkdir(exist_ok=True)
    write_shuffled(build_direct(), "globmed_direct_train.json")
    if args.distill:
        write_shuffled(build_distill(args.distill), "globmed_distill_train.json")


if __name__ == "__main__":
    main()
