import os
import json
import random
import argparse

from typing import Dict, List

def split_json_lists(conf_home_path: str, test_percentage: float, seed: int = 42) -> None:
    # File names
    file_names = [
        'cot_prompts.json',
        'systems.json',
        'rag_prompts.json'
    ]

    splits = {'train': {}, 'test': {}}
    random.seed(seed)  # for reproducibility

    for file_name in file_names:
        full_path = os.path.join(conf_home_path, file_name)
        
        # Read the JSON list
        with open(full_path, 'r') as f:
            data = json.load(f)
        
        # Get list length and indices
        n = len(data)
        indices = list(range(n))
        random.shuffle(indices)

        # Compute split sizes
        test_size = int(n * test_percentage / 100)
        test_indices = indices[:test_size]
        train_indices = indices[test_size:]

        # Use file name without .json as key
        key = os.path.splitext(file_name)[0]
        splits['train'][key] = train_indices
        splits['test'][key] = test_indices

    # Write splits to JSON file
    split_file_path = os.path.join(conf_home_path, 'train_test_split.json')
    with open(split_file_path, 'w') as f:
        json.dump(splits, f, indent=4)

    print(f"Split saved to {split_file_path}")



def main():
    parser = argparse.ArgumentParser(description="Split prompt confs JSON lists into train/test index sets.")
    parser.add_argument(
        "conf_home_path",
        type=str,
        help="Path to directory containing JSON config files."
    )
    parser.add_argument(
        "--test_percentage",
        type=float,
        default=40.0,
        help="Percentage of data to allocate to the test set (0–100). Default is 20%%."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility. Default is 42."
    )
    args = parser.parse_args()

    split_json_lists(conf_home_path=args.conf_home_path,
                     test_percentage=args.test_percentage,
                     seed=args.seed)

if __name__ == "__main__":
    main()