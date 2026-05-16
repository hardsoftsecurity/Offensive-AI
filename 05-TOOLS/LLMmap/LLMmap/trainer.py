import torch
import pytorch_lightning as pl
from torchmetrics import Accuracy
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
import torch.nn as nn
import torch.nn.functional as F
from torchmetrics.classification import BinaryAccuracy
from functools import partial
from typing import Dict, Any
from torch.optim import Optimizer

from .inference_model_archs import InferenceModelLLMmap, make_siamese_network


OPTIMIZERS: Dict[str, torch.optim.Optimizer] = {
    "Adam": torch.optim.Adam,
    "AdamW": torch.optim.AdamW,
    "SGD":  torch.optim.SGD,
}

class LLMmapTrainerClosed(pl.LightningModule):
    def __init__(self, model, hparams):
        """
        net      – an instance of InferenceModelLLMmap
        hparams  – the same dict that holds optimizer specs, num_classes, …
        """
        super().__init__()
        self.net        = model
        self.save_hyperparameters(hparams)      # logs LR, heads, etc.

        self.criterion  = torch.nn.CrossEntropyLoss()
        self.train_acc  = Accuracy(task="multiclass",
                                   num_classes=hparams["num_classes"])
        self.val_acc    = Accuracy(task="multiclass",
                                   num_classes=hparams["num_classes"])

    # ----- forward pass -------------------------------------------------
    def forward(self, x):
        return self.net(x)

    # ----- training -----------------------------------------------------
    def training_step(self, batch, _):
        x, y     = batch
        logits   = self(x)
        loss     = self.criterion(logits, y)

        self.train_acc.update(logits, y)
        self.log("train_loss", loss, prog_bar=True)
        self.log("train_acc", self.train_acc,
                 on_step=False, on_epoch=True, prog_bar=True)
        return loss

    # ----- validation (= test every epoch) ------------------------------
    def validation_step(self, batch, _):
        x, y   = batch
        logits = self(x)
        loss   = self.criterion(logits, y)

        self.val_acc.update(logits, y)
        self.log("val_loss", loss, prog_bar=True, on_epoch=True)
        self.log("val_acc",  self.val_acc,
                 on_step=False, on_epoch=True, prog_bar=True)

    # reset metric states each epoch
    def on_train_epoch_start(self):     self.train_acc.reset()
    def on_validation_epoch_start(self): self.val_acc.reset()

    # ----- optimiser ----------------------------------------------------
    def configure_optimizers(self) -> Optimizer:
        """
        Returns a torch.optim.* instance, accepting either
        1) the new JSON-friendly dict  {"name": <str>, "params": {...}}
        2) the legacy tuple            (opt_cls, kwargs)
        """
        opt_cfg = self.hparams["optimizer"]
    
        # ── new dict style ───────────────────────────────────────────────
        if isinstance(opt_cfg, dict):
            name   = opt_cfg["name"]
            kwargs = opt_cfg.get("params", {})
            try:
                opt_cls = OPTIMIZERS[name]
            except KeyError:                     # unknown name -> clear error
                raise ValueError(
                    f"Unknown optimizer '{name}'. "
                    f"Available: {list(OPTIMIZERS)}"
                )
            return opt_cls(self.parameters(), **kwargs)
    
        opt_cls, opt_kw = opt_cfg
        return opt_cls(self.parameters(), **opt_kw)




class ContrastiveLoss(nn.Module):
    """
    Classic contrastive loss for Siamese networks.

    Args
    ----
    margin : float, default=1.0
        Distance margin that separates positive and negative pairs.

    Shape
    -----
    y_pred : (B, 1)  – model output in [0, 1] (after sigmoid)
    y_true : (B, 1)  – binary label: 0 = "same" / positive pair,
                       1 = "different" / negative pair
    """
    def __init__(self, margin: float = 1.0):
        super().__init__()
        self.margin = margin

    def forward(self, y_pred: torch.Tensor, y_true: torch.Tensor) -> torch.Tensor:
        # ensure type/shape consistency
        y_true = y_true.float().view_as(y_pred)

        square_pred   = y_pred.pow(2)
        margin_square = (torch.clamp(self.margin - y_pred, min=0.0)).pow(2)

        loss = ((1.0 - y_true) * square_pred + y_true * margin_square).mean()
        return loss

class LLMmapTrainerSiamese(pl.LightningModule):
    def __init__(self, model: nn.Module, hparams: dict):
        """
        model    – the SiameseNetwork instance that ends with a sigmoid.
        hparams  – same dict you already use (must include "optimizer").
        """
        super().__init__()
        self.net = model
        self.save_hyperparameters(hparams)

        self.criterion = ContrastiveLoss(margin=hparams.get("margin", 1.0))

        # Binary metrics (0 = similar, 1 = dissimilar)
        self.train_acc = BinaryAccuracy()
        self.val_acc   = BinaryAccuracy()

    # ----- forward pass -------------------------------------------------
    def forward(self, x):
        return self.net(x)

    # ----- training -----------------------------------------------------
    def training_step(self, batch, _):
        x, y = batch                          # y ∈ {0,1}
        y_hat = self(x)[:, 0]                       # (B,1) in [0,1]
        loss  = self.criterion(y_hat, y)

        self.train_acc.update(y_hat, y.int())
        self.log("train_loss", loss, prog_bar=True)
        self.log("train_acc",  self.train_acc,
                 on_step=False, on_epoch=True, prog_bar=True)
        return loss

    # ----- validation ---------------------------------------------------
    def validation_step(self, batch, _):
        x, y = batch
        y_hat = self(x)[:, 0]
        loss  = self.criterion(y_hat, y)

        self.val_acc.update(y_hat, y.int())
        self.log("val_loss", loss, prog_bar=True, on_epoch=True)
        self.log("val_acc",  self.val_acc,
                 on_step=False, on_epoch=True, prog_bar=True)

    # reset metric states each epoch
    def on_train_epoch_start(self):     self.train_acc.reset()
    def on_validation_epoch_start(self): self.val_acc.reset()

    def configure_optimizers(self) -> Optimizer:
        """
        Returns a torch.optim.* instance, accepting either
        1) the new JSON-friendly dict  {"name": <str>, "params": {...}}
        2) the legacy tuple            (opt_cls, kwargs)
        """
        opt_cfg = self.hparams["optimizer"]
    
        # ── new dict style ───────────────────────────────────────────────
        if isinstance(opt_cfg, dict):
            name   = opt_cfg["name"]
            kwargs = opt_cfg.get("params", {})
            try:
                opt_cls = OPTIMIZERS[name]
            except KeyError:                     # unknown name -> clear error
                raise ValueError(
                    f"Unknown optimizer '{name}'. "
                    f"Available: {list(OPTIMIZERS)}"
                )
            return opt_cls(self.parameters(), **kwargs)
    
        # ── old tuple style (cls, kwargs) ────────────────────────────────
        return opt_cls(self.parameters(), **opt_kw)


def train_model(output_dir, siamese, loader_train, loader_test, conf):
    hp = conf['inference_model']
    
    if siamese:
        model, inference_model = make_siamese_network(hp)
        litmod = LLMmapTrainerSiamese(model, hp)
    else:
        model = InferenceModelLLMmap(hp) 
        litmod = LLMmapTrainerClosed(model, hp)
    
    early_stop = EarlyStopping(
        monitor="val_loss",
        mode="min",
        patience=conf['training']['early_stop_patience'],
        verbose=True
    )
    
    ckpt_best = ModelCheckpoint(
        dirpath      = output_dir,
        monitor      = "val_loss",       # the metric we already log
        mode         = "min",
        filename     = "best-{epoch:02d}-{val_loss:.4f}",
        save_top_k   = 1,               # keep only the best file
        save_weights_only = False       # full Lightning checkpoint (recommended)
    )
    
    trainer = pl.Trainer(
        default_root_dir=output_dir,
        max_epochs=conf['training']['max_epochs'],
        accelerator="auto",          # CPU/GPU/TPU depending on hardware
        devices="auto",
        callbacks=[early_stop, ckpt_best],
        log_every_n_steps=conf['training']['log_every_n_steps'],
    )
    
    trainer.fit(litmod, loader_train, loader_test)

    best_model_path = ckpt_best.best_model_path
    
    trainer_class = LLMmapTrainerSiamese if siamese else LLMmapTrainerClosed
    trainer = trainer_class.load_from_checkpoint(best_model_path, model=model, hp=hp)

    if siamese:
        return trainer, inference_model
    else:
        return trainer, trainer.net
