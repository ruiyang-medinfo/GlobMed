"""
GlobalMed Configuration Module

Provides:
1. Project path constants
2. YAML configuration loading
3. Environment variable loading
"""

import os
from os.path import abspath, dirname, join, exists
from typing import Any, Dict, Optional

import yaml
from dotenv import find_dotenv, load_dotenv


# Project paths
PROJECT_ROOT = abspath(dirname(dirname(dirname(__file__))))
CONFIG_DIR = join(PROJECT_ROOT, "config")
RESULTS_DIR = join(PROJECT_ROOT, "results")
DATA_DIR = join(PROJECT_ROOT, "data")

# Ensure directories exist
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def load_env() -> None:
    """Load environment variables from .env file."""
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)


def load_yaml_config(config_name: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file.

    Args:
        config_name: Name of the config file (without .yaml extension)

    Returns:
        Dict containing the configuration

    Raises:
        FileNotFoundError: If the config file does not exist
    """
    config_path = join(CONFIG_DIR, f"{config_name}.yaml")
    if not exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Lazy-loaded configuration caches
_DATASET_CONFIG: Optional[Dict[str, Any]] = None
_LANGUAGE_CONFIG: Optional[Dict[str, Any]] = None
_MODEL_CONFIG: Optional[Dict[str, Any]] = None


def get_dataset_config() -> Dict[str, Any]:
    """Get dataset configuration (lazy-loaded and cached)."""
    global _DATASET_CONFIG
    if _DATASET_CONFIG is None:
        _DATASET_CONFIG = load_yaml_config("datasets")
    return _DATASET_CONFIG


def get_language_config() -> Dict[str, Any]:
    """Get language configuration (lazy-loaded and cached)."""
    global _LANGUAGE_CONFIG
    if _LANGUAGE_CONFIG is None:
        _LANGUAGE_CONFIG = load_yaml_config("languages")
    return _LANGUAGE_CONFIG


def get_model_config() -> Dict[str, Any]:
    """Get model configuration (lazy-loaded and cached)."""
    global _MODEL_CONFIG
    if _MODEL_CONFIG is None:
        _MODEL_CONFIG = load_yaml_config("models")
    return _MODEL_CONFIG


def get_default_languages() -> list:
    """Get the default list of languages for evaluation."""
    config = get_language_config()
    return config.get("default_languages", [])


def get_task_info(task_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific task.

    Args:
        task_name: Name of the task (e.g., "MedQA", "HeadQA")

    Returns:
        Dict containing task configuration
    """
    config = get_dataset_config()
    datasets = config.get("datasets", {})
    return datasets.get(task_name, {})


def get_hf_dataset_name(task_name: str) -> str:
    """
    Get the HuggingFace dataset name for a task.

    Args:
        task_name: Name of the task

    Returns:
        HuggingFace dataset identifier
    """
    task_info = get_task_info(task_name)
    return task_info.get("hf_name", "")


def get_num_options(task_name: str) -> int:
    """
    Get the number of options for a task.

    Args:
        task_name: Name of the task

    Returns:
        Number of options (default: 4)
    """
    task_info = get_task_info(task_name)
    return task_info.get("num_options", 4)


def get_source_lang(task_name: str) -> str:
    """
    Get the source language for a task (for ground truth).

    Args:
        task_name: Name of the task

    Returns:
        Source language code (default: "en")
    """
    task_info = get_task_info(task_name)
    return task_info.get("source_lang", "en")


def get_task_type(task_name: str) -> str:
    """
    Get the task type (mcqa or nli).

    Args:
        task_name: Name of the task

    Returns:
        Task type string
    """
    task_info = get_task_info(task_name)
    return task_info.get("task_type", "mcqa")


def uses_max_completion_tokens(model_id: str) -> bool:
    """
    Check if a model uses max_completion_tokens instead of max_tokens.

    Args:
        model_id: Model identifier

    Returns:
        True if model uses max_completion_tokens
    """
    config = get_model_config()
    models = config.get("use_max_completion_tokens", [])
    return model_id in models


def get_result_path(
    model_id: str,
    task_name: str,
    prompt_style: str,
    lang: str,
    extension: str = "jsonl"
) -> str:
    """
    Get the result file path for a specific run.

    Args:
        model_id: Model identifier (will be reformatted)
        task_name: Name of the task
        prompt_style: Prompt style (shot/da)
        lang: Language code
        extension: File extension (jsonl or json)

    Returns:
        Full path to the result file
    """
    # Reformat model ID for filesystem compatibility
    reformat_model_id = model_id.replace("/", "--")
    result_dir = join(RESULTS_DIR, reformat_model_id, f"{task_name}_{prompt_style}")
    os.makedirs(result_dir, exist_ok=True)
    return join(result_dir, f"{lang}.{extension}")
