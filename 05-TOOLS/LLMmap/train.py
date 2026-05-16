#!/usr/bin/env python

import torch
import argparse
import os
from pathlib import Path
from pprint import pprint

from LLMmap import CONF_NAME, MODEL_NAME, TEMPLATE_NAME
from LLMmap.dataset import load_datasets
from LLMmap.trainer import train_model
from LLMmap.utility import read_conf_file, write_conf_file

def get_root_dirs():
    """Get roots from env vars or fall back to defaults."""
    ckpt_root = Path(os.getenv("CHECKPOINT_DIR", "./data/checkpoints"))
    export_root = Path(os.getenv("PRETRAINED_MODELS_DIR",
                                 "./data/pretrained_models"))
    ckpt_root.mkdir(parents=True, exist_ok=True)
    export_root.mkdir(parents=True, exist_ok=True)
    return ckpt_root, export_root


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Train LLMmap inference model given a configuration file (closed or open)."
    )
    parser.add_argument("--is_closed", action="store_true", default=False,
                        help="Enable closed mode (Siamese contrastive loss). Default is open mode.")

    parser.add_argument("conf_file",
                        help="Path to conf json file.")
    parser.add_argument("run_name",
                        help="Name of the experiment. "
                             "Creates <CHECKPOINT_DIR>/<name>/ and "
                             "exports weights to <PRETRAINED_MODELS_DIR>/<name>.pt")
    args = parser.parse_args()

    # 1) configuration --------------------------------------------------
    conf = read_conf_file(args.conf_file)
    conf['is_open'] = not args.is_closed
    print("\nLoaded configuration:")
    pprint(conf)

    # 2) roots & derived paths -----------------------------------------
    ckpt_root, export_root = get_root_dirs()
    ckpt_dir = ckpt_root / args.run_name
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    export_dir = export_root / args.run_name
    export_dir.mkdir(parents=True, exist_ok=True)
    model_export_path = export_dir / MODEL_NAME
    conf_export_path = export_dir / CONF_NAME

    print(f"\nCheckpoints → {ckpt_dir.resolve()}")
    print(f"Export file → {export_dir.resolve()}\n")

    # 3) dataset --------------------------------------------------------
    (loader_train, loader_test), _, (ds_train, _) = load_datasets(
        conf, siamese=conf['is_open'],
        ks=conf.get('num_istances_dataset', None)
    )

    write_conf_file(conf_export_path, conf)

    # 4) train ----------------------------------------------------------
    trainer, model = train_model(
        ckpt_dir.as_posix(), siamese=conf['is_open'],
        loader_train=loader_train, loader_test=loader_test, conf=conf
    )

    # 5) export ---------------------------------------------------------
    torch.save(model.state_dict(), model_export_path)
    print("\n✓ Training finished")
    print("✓ Weights exported:", model_export_path.resolve())

    
    if conf['is_open']:
        print("[NEXT] Now, to use the model, finalize it by running 'setup_templates.py'!")

if __name__ == "__main__":
    main()