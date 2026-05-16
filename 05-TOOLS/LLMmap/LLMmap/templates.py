import torch
import numpy as np
from pathlib import Path
from typing import Dict, Tuple

# ---------------------------------------------------------------------
# 1.  Feature extraction
# ---------------------------------------------------------------------
@torch.inference_mode()
def infer_features(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device | str = "cpu",
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Run the *feature extractor* on every sample in `loader`.

    Returns
    -------
    labels : np.ndarray  shape (N,)     – class index per sample
    feats  : np.ndarray  shape (N, F)   – extracted embedding
    """
    model.eval().to(device)

    feats, labels = [], []
    for x, y in loader:
        x = x.to(device)
        out = model(x)                  # (B, F)
        feats.append(out.cpu())
        labels.append(y.cpu())

    feats  = torch.cat(feats).numpy()   # (N, F)
    labels = torch.cat(labels).numpy()  # (N,)
    return labels, feats


# ---------------------------------------------------------------------
# 2.  Build per-class templates  (simple mean)
# ---------------------------------------------------------------------
def build_templates(
    labels: np.ndarray,
    feats: np.ndarray,
) -> np.ndarray:
    """
    Compute a mean feature vector for every class ID that appears.

    Returns
    -------
    templates : np.ndarray  shape (C, F)  – C = max(label)+1
    """
    num_classes = int(labels.max()) + 1
    F           = feats.shape[1]
    templates   = np.zeros((num_classes, F), dtype=feats.dtype)

    for c in range(num_classes):
        mask = labels == c
        if mask.any():
            templates[c] = feats[mask].mean(axis=0)
        else:                       # class `c` absent in training split
            templates[c] = np.nan   # optional: leave NaNs as sentinel
    return templates


# ---------------------------------------------------------------------
# 3.  Classification by nearest template
# ---------------------------------------------------------------------
def predict_by_templates(
    feats: np.ndarray,
    templates: np.ndarray,
) -> np.ndarray:
    """
    Assign each feature to the class whose template is *closest* (L2).

    Returns
    -------
    pred_labels : np.ndarray  shape (N,)
    """
    # (N, 1, F) - (1, C, F) → (N, C)
    dists = np.linalg.norm(feats[:, None, :] - templates[None, :, :], axis=-1)
    return dists.argmin(axis=1)


# ---------------------------------------------------------------------
# 4.  Wrapper that does everything and reports accuracy
# ---------------------------------------------------------------------
def template_generation(
    feature_extractor: torch.nn.Module,
    train_loader: torch.utils.data.DataLoader,
    test_loader: torch.utils.data.DataLoader,
    device: torch.device | str = "cpu",
) -> Dict[str, object]:
    """
    Returns
    -------
    dict with keys:
        y_true      – ground-truth labels (test set)
        y_pred      – predicted labels
        templates   – class centroids
        accuracy    – prediction accuracy in [0,1]
    """
    # 1) templates from training split
    y_train, f_train = infer_features(feature_extractor, train_loader, device)
    templates = build_templates(y_train, f_train)

    # 2) classify test split
    y_test, f_test = infer_features(feature_extractor, test_loader, device)
    y_pred = predict_by_templates(f_test, templates)

    acc = (y_pred == y_test).mean().item()

    return dict(
        y_true=y_test,
        y_pred=y_pred,
        templates=templates,
        accuracy=acc,
    )
