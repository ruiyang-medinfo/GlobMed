"""
GlobalMed Data Loading Module

Provides:
1. HuggingFace datasets online loading
2. Unified data format conversion
3. Backward-compatible interface with legacy read_data()
"""

import string
from typing import Dict, List, Literal, Optional

from datasets import load_dataset

from globalmed.config import get_dataset_config, get_default_languages


# Task type constants
MCQA_TASKS = ["MedQA", "HeadQA", "MedExpQA", "MMLU-Pro"]
NLI_TASKS = ["BioNLI", "MedNLI"]

# Default supported languages
DEFAULT_LANGUAGES = [
    "en", "zh", "fr", "de", "ja", "ko", "pt", "es", "sw", "wo", "yo", "zu"
]

# Multilingual NLI label mappings for BioNLI
# Maps translated labels to indices (entailment=0, contradiction=1)
BIONLI_LABEL_MAP = {
    # English
    "entailment": 0, "contradiction": 1,
    # Chinese
    "蕴含": 0, "矛盾": 1,
    # French
    "Implication": 0, "Contradiction": 1,
    # German
    "Implikation": 0, "Widerspruch": 1,
    # Japanese
    "含意": 0,  # Japanese contradiction "矛盾" same as Chinese, already mapped
    # Korean
    "함의": 0, "모순": 1,
    # Portuguese
    "Implicação": 0, "Contradição": 1,
    # Spanish
    "Implicación": 0, "Contradicción": 1,
    # Swahili
    "Uthibitisho": 0, "Kupingana": 1,
    # Wolof
    "Jagleel": 0, "Dëddu": 1,
    # Yoruba
    "Ìbámu": 0, "Ìlòdì": 1,
    # Zulu
    "Ukuvumelana": 0, "Ukuphikisana": 1,
}

def read_data(
    subset: str,
    lang: str,
    split: Literal["train", "test"] = "test",
    local_mednli: Optional[str] = None
) -> List[Dict]:
    """
    Unified data reading interface.

    Loads data from HuggingFace datasets and converts to a standardized format
    compatible with the legacy codebase.

    Args:
        subset: Dataset name (MedQA, HeadQA, MedExpQA, MMLU-Pro, BioNLI)
        lang: Language code (en, zh, fr, de, ja, ko, pt, es, sw, wo, yo, zu)
        split: Data split (train, test)

    Returns:
        List[Dict]: Standardized data list, each item contains:
            - id: Unique identifier (format: "{subset}_{lang}_{idx}")
            - question: Question text (MCQA)
            - options: Options dict {A: ..., B: ...} (MCQA)
            - premise/hypothesis: Premise/hypothesis text (NLI)
            - answer_index: Correct answer index (0-based)
            - gold_label: Gold label string (NLI only)
    """
    if subset == "MedNLI":
        if not local_mednli:
            raise ValueError("MedNLI is not distributed here. Supply an authorized local file with local_mednli=PATH.")
        from globalmed.local_mednli import read_local_mednli
        return read_local_mednli(local_mednli, lang)
    if local_mednli:
        raise ValueError("local_mednli is only valid for MedNLI")
    dataset_config = get_dataset_config()
    task_config = dataset_config["datasets"].get(subset, {})
    hf_name = task_config.get("hf_name", f"ruiyang-medinfo/GlobMed_{subset}")

    # Load from HuggingFace
    try:
        ds = load_dataset(hf_name, lang, split=split)
    except Exception as e:
        raise RuntimeError(f"Failed to load dataset {hf_name} for {lang}/{split}: {e}")

    metadata = []
    for idx, doc in enumerate(ds):
        item = {
            "id": f"{subset}_{lang}_{idx}",
        }

        if subset in MCQA_TASKS:
            # MCQA task format
            item["question"] = doc["question"]

            # Build options dictionary from A, B, C, D, ... columns
            options = {}
            for letter in string.ascii_uppercase:
                if letter in doc and doc[letter] is not None:
                    options[letter] = doc[letter]
            item["options"] = options

            # Answer index (0-based integer)
            item["answer_index"] = doc.get("answer_index", 0)

        else:
            # NLI task format (BioNLI)
            item["premise"] = doc["premise"]
            item["hypothesis"] = doc["hypothesis"]
            item["gold_label"] = doc.get("gold_label", "")

            # Convert gold_label to answer_index using multilingual label map
            gold_label = item["gold_label"]
            if gold_label in BIONLI_LABEL_MAP:
                item["answer_index"] = BIONLI_LABEL_MAP[gold_label]
            else:
                # Unknown label - log warning and default to 0
                import logging
                logging.warning(f"Unknown gold_label '{gold_label}' for {subset}/{lang}, defaulting to 0")
                item["answer_index"] = 0

        metadata.append(item)

    return metadata


def get_num_options(subset: str) -> int:
    """
    Get the number of options for a task.

    Args:
        subset: Dataset name

    Returns:
        Number of options
    """
    option_map = {
        "MedQA": 4,
        "HeadQA": 4,
        "MedExpQA": 5,
        "MMLU-Pro": 10,
        "BioNLI": 2,
        "MedNLI": 3,
    }
    return option_map.get(subset, 4)


def get_source_lang(subset: str) -> str:
    """
    Get the source language for ground truth data.

    Some datasets have ground truth only in certain languages.

    Args:
        subset: Dataset name

    Returns:
        Source language code
    """
    source_lang_map = {
        "MedQA": "en",
        "HeadQA": "es",
        "MedExpQA": "es",
        "MMLU-Pro": "en",
        "BioNLI": "en",
    }
    return source_lang_map.get(subset, "en")


def get_task_type(subset: str) -> str:
    """
    Get the task type.

    Args:
        subset: Dataset name

    Returns:
        Task type string ("mcqa" or "nli")
    """
    if subset in MCQA_TASKS:
        return "mcqa"
    elif subset in NLI_TASKS:
        return "nli"
    else:
        return "unknown"


def get_available_languages(subset: str) -> List[str]:
    """
    Get available languages for a dataset.

    Args:
        subset: Dataset name

    Returns:
        List of language codes
    """
    return DEFAULT_LANGUAGES
