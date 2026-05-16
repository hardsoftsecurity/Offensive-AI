import sys
import argparse
import itertools  
import numpy as np
import torch
import tqdm

from LLMmap.dataset import read_dataset
from LLMmap.inference import load_LLMmap


def get_topk_labels_from_distances(distances, label_map, k):
    """
    distances : 1-D np.ndarray of shape (num_classes,)
    label_map : dict[int -> str]  (same one your model already has)
    k         : int  (1 ≤ k ≤ num_classes)
    -------
    returns   : list[str]   length == k
    """
    topk_idx = np.argsort(distances)[:k]        # smaller distance = closer = better
    return topk_idx


def evaluate_topk(model, test_iterable, k_values=(1, 2, 3)):
    """
    model          : your InferenceModel_open instance  (called `inf` in your snippet)
    test_iterable  : whatever you named `test`
    k_values       : tuple of k’s you want accuracies for

    Returns dict {k: accuracy_float}
    """
    # counters
    num_samples          = 0
    topk_correct_counter = {k: 0 for k in k_values}

    llms_map = {v:k for (k,v) in model.label_map.items()}
    
    for entry in tqdm.tqdm(test_iterable):
        llm_name     = entry['llm']                       # ← key present in your JSON
        gt_label     = llms_map[llm_name]           # ground-truth string
        answers      = [trace[1] for trace in entry['traces']]

        distances    = model(answers)                    # forward pass
        num_samples += 1
        
        for k in k_values:
            preds_k = get_topk_labels_from_distances(distances, model.label_map, k)
            if gt_label in preds_k:
                topk_correct_counter[k] += 1

    # compute accuracy
    accuracies = {k: topk_correct_counter[k] / num_samples
                  for k in k_values}
    return accuracies
       
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Test a pre-trained LLMmap model on the test-set."
    )
    parser.add_argument(
        "model_home_dir",
        type=str,
        help="Path to the model home directory"
    )
    parser.add_argument(
        "-k", "--topk",
        type=int,
        default=3,
        metavar="K",
        help="Compute top-1 … top-K accuracies (default: 3)"
    )
    parser.add_argument(
        "-m", "--max-entries",
        type=int,
        default=None,
        metavar="N",
        help="Evaluate only the first N samples of the test set (default: all)"
    )
    args = parser.parse_args()

    if args.topk < 1:
        parser.error("--topk must be ≥ 1")

    # ------------------------------------------------------------------
    conf, inf = load_LLMmap(args.model_home_dir, device='cpu')
    if not conf['is_open']:
        print("Applicable to only open-set inference model. Aborting...")
        sys.exit(1)

    if not inf.ready:
        print("No templates found for the model. Aborting...")
        sys.exit(1)
            
    train, test = read_dataset(conf['dataset_path'])

    # Respect --max-entries (None means "all")
    test_iter = (
        test if args.max_entries is None
        else itertools.islice(test, args.max_entries)
    )

    # Build the tuple (1, 2, …, K)
    k_values = tuple(range(1, args.topk + 1))

    print("Running test...")
    acc = evaluate_topk(inf, test_iter, k_values=k_values)

    # Nicely print all requested accuracies
    for k in k_values:
        print(f"Top-{k} accuracy: {acc[k]:.3%}")