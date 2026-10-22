"""Load user-authorized MedNLI files locally; never fetch or distribute them."""

import json
from pathlib import Path

from globalmed.mednli_prompts import MEDNLI_LABELS

# Match Supplementary Tab.55-66, not BioNLI's two-class order.
LABELS = {"entailment": 0, "neutral": 1, "contradiction": 2}
for translated in MEDNLI_LABELS.values():
    LABELS.update({label.casefold(): index for index, label in enumerate(translated)})


def read_local_mednli(path, lang):
    """Accept a JSON array or JSONL with premise/hypothesis/gold_label.

    Original sentence1/sentence2 keys are accepted. A numeric answer_index
    alone is deliberately insufficient: require a named label to avoid silently
    confusing the label order used by other NLI datasets. Translated files must
    have been obtained/produced under the user's applicable authorization.
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    records = json.loads(text) if text.lstrip().startswith("[") else [
        json.loads(line) for line in text.splitlines() if line.strip()
    ]
    if not isinstance(records, list):
        raise ValueError("MedNLI input must be a JSON array or JSONL records")
    result, seen = [], set()
    for index, record in enumerate(records):
        premise = record.get("premise", record.get("sentence1"))
        hypothesis = record.get("hypothesis", record.get("sentence2"))
        label = record.get("gold_label", record.get("label"))
        if not all(isinstance(x, str) and x.strip() for x in (premise, hypothesis, label)):
            raise ValueError(f"MedNLI row {index}: require nonempty premise, hypothesis, and named gold_label")
        answer = LABELS.get(label.strip().casefold())
        if answer is None:
            raise ValueError(f"MedNLI row {index}: unrecognized gold_label")
        if "answer_index" in record and record["answer_index"] != answer:
            raise ValueError(f"MedNLI row {index}: answer_index conflicts with A=entailment, B=neutral, C=contradiction")
        item_id = str(record.get("id", record.get("pairID", f"MedNLI_{lang}_{index}")))
        if item_id in seen:
            raise ValueError(f"MedNLI row {index}: duplicate ID")
        seen.add(item_id)
        result.append({"id": item_id, "premise": premise, "hypothesis": hypothesis,
                       "gold_label": label, "answer_index": answer})
    return result
