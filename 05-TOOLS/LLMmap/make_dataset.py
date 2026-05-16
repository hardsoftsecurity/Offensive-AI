#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

from LLMmap.prompt_configuration import PromptConfFactory  #
from LLMmap.dataset_maker import DatasetMaker


def get_root_dir(default="./data/datasets"):
    """Get dataset root from env var or fall back to default."""
    return os.getenv("DATASET_DIR", default)


def load_json(path, encoding="utf-8"):
    with open(path, "r", encoding=encoding) as f:
        return json.load(f)


def build_arg_parser():
    p = argparse.ArgumentParser(
        description="Build a dataset JSONL using LLMmap's DatasetMaker.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("dataset_name",  help="Base name for the output dataset file (no extension).")
    p.add_argument("llms_to_use_path", help="JSON file listing LLMs to use (e.g., './confs/LLMs/example.json').")
    p.add_argument("query_strategy_path", help="JSON file with query strategy (e.g., './confs/queries/default.json').")
    p.add_argument("--num_prompt_conf_train", type=int, default=150, help="Number of training prompt configurations.")
    p.add_argument("--num_prompt_conf_test", type=int, default=20, help="Number of test prompt configurations.")
    p.add_argument("--prompt_conf_path", default="./confs/prompt_configurations/", help="Directory with prompt configs.")
    p.add_argument(
        "--dataset_root",
        default=get_root_dir(),
        help="Where to write the output JSONL (overrides DATASET_DIR if provided).",
    )
    p.add_argument("--overwrite", action="store_true", help="Overwrite output file if it already exists.")
    p.add_argument("--encoding", default="utf-8", help="Encoding used to read JSON config files.")
    return p


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    pc = PromptConfFactory(args.prompt_conf_path)

    out_path = Path(args.dataset_root) / f"{args.dataset_name}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists() and not args.overwrite:
        parser.error(f"Output file '{out_path}' already exists. Use --overwrite.")
    print(f'Experting in {str(out_path)}')

    queries = load_json(args.query_strategy_path, args.encoding)
    llms = load_json(args.llms_to_use_path, args.encoding)

    dm = DatasetMaker(
        pc,
        llms,
        queries,
        args.num_prompt_conf_train,
        args.num_prompt_conf_test,
        str(out_path),
    )
    dm()  # Generate the dataset


if __name__ == "__main__":
    main()