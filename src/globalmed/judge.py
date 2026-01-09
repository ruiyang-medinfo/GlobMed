"""
GlobalMed Answer Extraction and Scoring Module

Provides:
1. Language-specific regex answer extraction
2. Generic regex fallback patterns
3. Scoring functions
"""

import re
from string import ascii_uppercase
from typing import Dict, List, Optional

from globalmed.prompt import ANSWER_CAPTURE_PATTERNS


# =============================================================================
# Regex-based Extraction
# =============================================================================

def extract_answer(
    text: str,
    lang: str = "en",
    num_choices: int = 4
) -> Optional[str]:
    """
    Extract answer from model generated text using two-level regex.

    Strategy:
    1. First try language-specific regex (most accurate for our prompts)
    2. Fall back to generic regex patterns

    Args:
        text: Model generated text
        lang: Language code
        num_choices: Number of choices

    Returns:
        Extracted answer letter (A/B/C/...) or None
    """
    if not text:
        return None

    valid_choices = ascii_uppercase[:num_choices]

    # Level 1: Try language-specific regex first (most accurate for our prompts)
    lang_pattern = ANSWER_CAPTURE_PATTERNS.get(lang)
    if lang_pattern:
        try:
            matches = re.findall(lang_pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                answer = matches[-1].strip().upper()
                if answer in valid_choices:
                    return answer
        except re.error:
            pass

    # Level 2: Fall back to generic regex patterns
    generic_patterns = [
        r'\(([ABCDEFGHIJ])\)',           # (A), (B), etc.
        r'\*\*([A-J])\*\*',              # **A**, **B**, etc.
        r'boxed\{([A-J])\}',             # \boxed{A}, etc.
        r'（([ABCDEFGHIJ])）',            # Full-width parentheses (CJK)
        r'「([ABCDEFGHIJ])」',            # Japanese quotation marks
        r'(?:^|[\s:])([ABCDEFGHIJ])\.', # A., B., etc. (after space/colon/start)
        r'(?:^|[\s:])([ABCDEFGHIJ])(?:$|[\s,.])',  # Standalone letter
    ]

    for pattern in generic_patterns:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                answer = matches[-1].strip().upper()
                if answer in valid_choices:
                    return answer
        except re.error:
            continue

    return None


# Backward compatibility alias
def extract_last_answer(text: str, lang: str = "en") -> Optional[str]:
    """Backward-compatible alias for extract_answer."""
    return extract_answer(text, lang=lang)


# =============================================================================
# Scoring Functions
# =============================================================================

def judge_score(
    metadata_doc: Dict,
    responses: List[str],
    lang: str = "en"
) -> Dict:
    """
    Score responses against ground truth.

    Args:
        metadata_doc: Data item metadata (contains answer_index, options, etc.)
        responses: List of model responses
        lang: Language code

    Returns:
        Dict containing:
            - score: Accuracy score (0.0 to 1.0)
            - extracted_predictions: List of extracted answers for each response
            - correct_count: Number of correct predictions
            - ground_truth: The correct answer letter
    """
    answer_index = metadata_doc.get("answer_index", 0)
    options = metadata_doc.get("options", {})
    num_choices = len(options) if options else 4

    ground_truth = ascii_uppercase[answer_index]

    extracted_predictions = []
    correct_count = 0

    for resp in responses:
        pred = extract_answer(resp, lang=lang, num_choices=num_choices)
        extracted_predictions.append(pred)

        if pred and pred == ground_truth:
            correct_count += 1

    n_responses = len(responses)
    score = correct_count / n_responses if n_responses > 0 else 0.0

    return {
        "score": score,
        "extracted_predictions": extracted_predictions,
        "correct_count": correct_count,
        "ground_truth": ground_truth,
    }


def answer_to_index(answer: Optional[str], num_options: int = 4) -> int:
    """
    Convert answer letter to index.

    Args:
        answer: Answer letter (A/B/C/...)
        num_options: Number of options

    Returns:
        0-based index, or -1 if invalid
    """
    if answer is None:
        return -1

    answer_upper = answer.upper()
    if answer_upper in ascii_uppercase[:num_options]:
        return ascii_uppercase.index(answer_upper)

    return -1


def index_to_answer(index: int, num_options: int = 4) -> Optional[str]:
    """
    Convert index to answer letter.

    Args:
        index: 0-based index
        num_options: Number of options

    Returns:
        Answer letter or None if invalid
    """
    if 0 <= index < num_options:
        return ascii_uppercase[index]
    return None
