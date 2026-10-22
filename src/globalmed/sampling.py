"""Generation settings and resumability shared by inference backends."""

import json
from pathlib import Path


def add_sampling_arguments(parser):
    parser.add_argument("--local_mednli", default=None,
                        help="Authorized local MedNLI JSON/JSONL; requires --subset MedNLI --lang LANG --prompt_style da")


def validate_arguments(args):
    if args.n_sampling < 1 or args.max_tokens < 1:
        raise ValueError("n_sampling and max_tokens must be positive")
    if args.subset == "MedNLI":
        if not args.local_mednli or not args.lang or args.prompt_style != "da":
            raise ValueError("MedNLI requires --local_mednli PATH --lang LANG --prompt_style da")
    elif args.local_mednli:
        raise ValueError("--local_mednli is only valid with --subset MedNLI")


def load_finished_ids(result_path, n_sampling=1, generation=None):
    """Only the latest record can mark an ID complete.

    Require the requested sample count, nonempty completions, and matching
    generation metadata. Legacy logs without metadata are regenerated when a
    configuration is supplied; they cannot prove the current settings match.
    """
    latest = {}
    if Path(result_path).exists():
        with open(result_path, encoding="utf-8") as stream:
            for line in stream:
                try:
                    row = json.loads(line)
                    latest[row["id"]] = row
                except (json.JSONDecodeError, KeyError):
                    continue
    return [item_id for item_id, row in latest.items()
            if len(row.get("responses", [])) == n_sampling
            and all(response.get("content") for response in row["responses"])
            and (generation is None or row.get("generation") == generation)]
