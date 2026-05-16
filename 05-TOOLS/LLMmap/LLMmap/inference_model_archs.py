import torch
import torch.nn as nn
from functools import partial
from typing import Dict, Any, Tuple

# ---------------------------------------------------------------------
# 1. MAPPINGS ─────────────────────────────────────────────────────────
# ---------------------------------------------------------------------
NORM_LAYERS: Dict[str, nn.Module] = {
    "BatchNorm1d": nn.BatchNorm1d,
    "LayerNorm":   nn.LayerNorm,
}

DEFAULT_HP: Dict[str, Any] = {
    "num_blocks": 3,
    "feature_size": 384,
    "norm_layer": "BatchNorm1d",       
    "num_heads": 4,
    "activation": "gelu",
    "optimizer": {
        "name": "Adam",
        "params": {"lr": 1e-4}
    },
    "with_add_dense_class": False,
    "emb_size": 1024,
    "num_queries": 8,
}

# ---------------------------------------------------------------------
# 3. SMALL HELPERS ────────────────────────────────────────────────────
# ---------------------------------------------------------------------
def get_activation(name: str) -> nn.Module:
    name = name.lower()
    if name == "gelu":
        return nn.GELU()
    if name == "relu":
        return nn.ReLU()
    raise ValueError(f"Unsupported activation: {name!r}")

def make_norm(norm_cfg: Any, dim: int) -> nn.Module:
    """
    Accepts:
        • a string from NORM_LAYERS        ("BatchNorm1d" / "LayerNorm")
        • a norm class itself              (nn.BatchNorm1d / nn.LayerNorm)
        • a partial / callable returning an nn.Module
    """
    # ── string → class ────────────────────────────────────────────────
    if isinstance(norm_cfg, str):
        try:
            norm_cls = NORM_LAYERS[norm_cfg]
        except KeyError:
            raise ValueError(f"Unknown norm_layer '{norm_cfg}'. "
                             f"Known: {list(NORM_LAYERS)}")
        return norm_cls(dim)

    # ── class given directly ─────────────────────────────────────────
    if norm_cfg in (nn.BatchNorm1d, nn.LayerNorm):
        return norm_cfg(dim)

    # ── partial / custom callable ────────────────────────────────────
    return norm_cfg(dim)



class ClassToken(nn.Module):
    def __init__(self, feature_size: int):
        super().__init__()
        self.token = nn.Parameter(torch.randn(1, 1, feature_size))

    def forward(self, x):                       # (B, S, F)
        return self.token.expand(x.size(0), -1, -1)


class TransformerBlock(nn.Module):
    def __init__(self, hp: dict):
        super().__init__()
        F_  = hp["feature_size"]
        H   = hp["num_heads"]
        act = get_activation(hp["activation"])

        # strings are resolved here ↓
        self.norm1 = make_norm(hp["norm_layer"], F_)
        self.attn  = nn.MultiheadAttention(F_, H, batch_first=True)
        self.norm2 = make_norm(hp["norm_layer"], F_)
        self.mlp   = nn.Sequential(nn.Linear(F_, F_), act)

    def _apply_norm(self, norm, x):
        if isinstance(norm, nn.BatchNorm1d):
            return norm(x.transpose(1, 2)).transpose(1, 2)
        return norm(x)

    def forward(self, x):                       # (B, S, F)
        x_norm = self._apply_norm(self.norm1, x)
        attn_out, _ = self.attn(x_norm, x_norm, x_norm)
        x = x + attn_out
        x = x + self.mlp(self._apply_norm(self.norm2, x))
        return x


class InferenceModelLLMmap(nn.Module):
    def __init__(self, hp: dict = DEFAULT_HP, *, is_for_siamese: bool = False):
        super().__init__()
        F_  = hp["feature_size"]
        act = get_activation(hp["activation"])

        self.cls_token = ClassToken(F_)
        self.proj = nn.Linear(hp["emb_size"] * 2, F_)
        self.act  = act
        self.blocks = nn.ModuleList(TransformerBlock(hp) for _ in range(hp["num_blocks"]))

        if not is_for_siamese:
            if hp["with_add_dense_class"]:
                self.pre_head = nn.Sequential(nn.Linear(F_, F_ // 2), act)
                head_in = F_ // 2
            else:
                self.pre_head = nn.Identity()
                head_in = F_
            self.head = nn.Linear(head_in, hp["num_classes"])
        else:
            self.pre_head = nn.Identity()
            self.head     = nn.Identity()

    def forward(self, traces):                  # (B, Q, emb_size*2)
        x = self.act(self.proj(traces))
        x = torch.cat([self.cls_token(x), x], dim=1)  # prepend [CLS]
        for blk in self.blocks:
            x = blk(x)
        x = x[:, 0]                                   # take [CLS]
        x = self.pre_head(x)
        return self.head(x)


# Siamese net ------------------------------------------------------------------------------------------

def euclidean_distance(a: torch.Tensor, b: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """
    Pair-wise Euclidean distance for two feature tensors.
    Args:
        a, b: (B, F) tensors
    Returns:
        (B, 1) distance column-vector
    """
    return torch.sqrt(((a - b) ** 2).sum(dim=1, keepdim=True) + eps)


class SiameseNetwork(nn.Module):
    """
    Wrapper that turns a feature extractor into a full Siamese network
    producing a similarity score in (0, 1).
    """
    def __init__(self, feature_extractor: nn.Module):
        super().__init__()
        self.f = feature_extractor                 # shared weights
        self.bn = nn.BatchNorm1d(1)                # (B, 1)
        self.fc = nn.Linear(1, 1)                  # (B, 1) → (B, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 2, Q, emb_size*2)  – the first axis selects the two traces
        Returns:
            (B, 1) similarity score in (0, 1)
        """
        feat_a = self.f(x[:, 0])                   # (B, F)
        feat_b = self.f(x[:, 1])                   # (B, F)

        dist   = euclidean_distance(feat_a, feat_b)  # (B, 1)
        norm   = self.bn(dist)                       # (B, 1)
        logits = self.fc(norm)                       # (B, 1)
        return torch.sigmoid(logits)                 # (B, 1)


def make_siamese_network(fhparams: dict, f=None):
    """
    Returns:
        siam  – full Siamese network (PyTorch nn.Module)
        f     – the underlying feature extractor with shared weights
    """

    if f is None:
        # 1. Shared feature extractor (no classification head)
        f = InferenceModelLLMmap(fhparams, is_for_siamese=True)

    # 2. Siamese wrapper
    siam = SiameseNetwork(f)

    return siam, f
