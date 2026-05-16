import sys
import os
import json
import argparse

from LLMmap.dataset import load_datasets
from LLMmap.inference import load_LLMmap, write_templates
from LLMmap.templates import template_generation
from LLMmap import TEMPLATE_NAME


def main():
    parser = argparse.ArgumentParser(description="Generate and export LLMs templates for open LLMmap inference model based on training set.")
    parser.add_argument("model_home_dir", type=str, help="Path to the model home directory")
    args = parser.parse_args()

    model_home_dir = args.model_home_dir
    conf, inf = load_LLMmap(model_home_dir, device='cpu')

    if not conf['is_open']:
        print("Applicable to only open-set inference model. Aborting...")
        sys.exit(1)

    siamese = False
    (loader_train, loader_test), cache, (dataset_train, dataset_test) = load_datasets(
        conf,
        siamese=siamese,
        ks=conf.get('num_istances_dataset', None)
    )

    results = template_generation(inf.model, loader_train, loader_test)
    print(f"Accuracy on test set: {results['accuracy']}")

    templates_map = {}
    templates = results['templates']
    for i in range(len(templates)):
        llm = inf.label_map[i]
        templates_map[llm] = templates[i]

    template_out = os.path.join(model_home_dir, TEMPLATE_NAME)

    if os.path.exists(template_out):
        confirm = input(f"'{template_out}' already exists. Overwrite? (y/n): ")
        if confirm.lower() != 'y':
            print("Aborting.")
            sys.exit(1)

    write_templates(template_out, templates_map)

    print(f"Templates saved to '{template_out}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create templates for a pre-trained LLMmap open inference model.")
    parser.add_argument("model_home_dir", type=str, help="Path to the model home directory")
    args = parser.parse_args()
    main()