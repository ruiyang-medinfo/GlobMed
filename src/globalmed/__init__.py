"""
GlobalMed - Multilingual Medical NLP Evaluation Framework

A comprehensive framework for evaluating language models on
multilingual medical question answering and natural language inference tasks.

Supported Tasks:
- MedQA, HeadQA, MedExpQA, MMLU-Pro (MCQA)
- BioNLI (NLI)

Supported Languages:
- High-resource: en, zh, fr, de, ja, ko, pt, es
- Low-resource: sw (Swahili), wo (Wolof), yo (Yoruba), zu (Zulu)
"""

__version__ = "0.1.0"

# Core configuration
from globalmed.config import (
    PROJECT_ROOT,
    CONFIG_DIR,
    RESULTS_DIR,
    DATA_DIR,
    load_env,
    get_dataset_config,
    get_language_config,
    get_model_config,
)

# Prompt templates
from globalmed.prompt import (
    PROMPT_LIBS,
    ANSWER_CAPTURE_PATTERNS,
    get_message_from_doc,
    get_prompt_text,
    get_supported_languages,
)

# Data loading
from globalmed.data import (
    read_data,
    MCQA_TASKS,
    NLI_TASKS,
    DEFAULT_LANGUAGES,
)

# Answer extraction and scoring
from globalmed.judge import (
    extract_answer,
    extract_last_answer,
    judge_score,
    answer_to_index,
    index_to_answer,
)

__all__ = [
    # Version
    "__version__",
    # Config
    "PROJECT_ROOT",
    "CONFIG_DIR",
    "RESULTS_DIR",
    "DATA_DIR",
    "load_env",
    "get_dataset_config",
    "get_language_config",
    "get_model_config",
    # Prompt
    "PROMPT_LIBS",
    "ANSWER_CAPTURE_PATTERNS",
    "get_message_from_doc",
    "get_prompt_text",
    "get_supported_languages",
    # Data
    "read_data",
    "MCQA_TASKS",
    "NLI_TASKS",
    "DEFAULT_LANGUAGES",
    # Judge
    "extract_answer",
    "extract_last_answer",
    "judge_score",
    "answer_to_index",
    "index_to_answer",
]
