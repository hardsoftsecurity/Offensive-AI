# Lab: Pickle Deserialization & Tensor Steganography — Trojan Model Attack

## Overview

This lab demonstrates how Python's `pickle` serialization, used internally by `torch.save` and `torch.load`, can be weaponized to achieve **Remote Code Execution (RCE)** through a malicious PyTorch model file. The attack combines two techniques:

1. **Pickle Deserialization Exploit** — Abusing Python's `__reduce__` method to execute arbitrary code when a model file is loaded.
2. **LSB Tensor Steganography** — Hiding a reverse shell payload inside the least significant bits of a neural network's weight tensors, making the malicious content invisible to casual inspection.

The result is a `.pth` model file that appears legitimate but executes a reverse shell upon deserialization by the target.

## Attack Chain

```
┌─────────────────────┐
│  1. Train a legit    │
│     SimpleNet model  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  2. Encode reverse   │
│     shell payload    │
│     into tensor LSBs │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  3. Wrap in Trojan   │
│     class with       │
│     __reduce__       │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  4. torch.save()     │
│     serializes the   │
│     wrapper via      │
│     pickle           │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  5. Upload .pth to   │
│     target API       │
│     endpoint         │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  6. Target calls     │
│     torch.load()     │
│     → pickle.loads() │
│     → __reduce__     │
│     → exec()         │
│     → reverse shell  │
└─────────────────────┘
```

## Technical Breakdown

### Phase 1 — Model Training and Steganographic Embedding

A simple feedforward neural network (`SimpleNet`) is trained on dummy data. The model includes a deliberately oversized layer (`large_layer`: 320×64 = 20,480 float32 parameters) that is defined but never used in the forward pass. This layer serves as the steganographic carrier.

The reverse shell payload is encoded into the **least significant bits (LSBs)** of the `large_layer.weight` tensor:

- Each `float32` value is reinterpreted as a 32-bit integer via `struct.pack`/`unpack`.
- The lowest N bits (configurable, default `NUM_LSB=2`) of each integer are replaced with payload bits.
- A 4-byte big-endian length prefix is prepended so the decoder knows how many bytes to extract.
- At 2 LSBs per float, the 20,480-element tensor provides ~5 KB of steganographic capacity — more than enough for the ~1.5 KB payload.

The weight distortion introduced is negligible (on the order of 10⁻⁷ relative change), making the modified tensor statistically indistinguishable from the original in most analyses.

### Phase 2 — Trojan Wrapper and Pickle Exploit

The modified state dictionary is wrapped in a `TrojanModelWrapper` class that overrides `__reduce__`. When Python's `pickle` module serializes this object (via `torch.save`), it calls `__reduce__` to determine how to reconstruct it later. The exploit returns:

```python
return (exec, (loader_code,))
```

This tells `pickle` that to reconstruct the object, it should call `exec(loader_code)` — executing arbitrary Python code. The `loader_code` string contains:

1. An embedded copy of the `decode_lsb` function.
2. The entire pickled state dictionary (as a bytes literal).
3. Logic to deserialize the state dict, extract the payload tensor, decode the hidden payload from the LSBs, and `exec()` the resulting reverse shell code.

### Phase 3 — Delivery and Execution

The malicious `.pth` file is uploaded to the target's model-loading API endpoint (`/upload`). When the target application calls `torch.load()` on the uploaded file, the full exploit chain fires:

1. `torch.load()` internally calls `pickle.loads()`.
2. Pickle invokes `__reduce__`, which calls `exec(loader_code)`.
3. The loader reconstructs the state dict, extracts the steganographic payload from the tensor weights.
4. The extracted reverse shell code connects back to the attacker's listener.

## Lab Execution Steps

### Prerequisites

- Python 3.x with PyTorch, NumPy, and Requests installed
- VPN connection to the lab network
- A target instance running the vulnerable model-loading API

### Steps

1. **Start your listener** on your attack machine:
   ```bash
   nc -lvnp 4444
   ```

2. **Configure the notebook** — Open `pickelsAndSteganography.ipynb` and set:
   - `HOST_IP` — Your VPN IP address (the IP the reverse shell connects back to)
   - `LISTENER_PORT` — The port your listener is on (default: 4444)
   - `api_url` — The target instance's upload endpoint (`http://<TARGET_IP>:5555/upload`)

3. **Run all notebook cells** sequentially. This will:
   - Train the legitimate model and save `target_model.pth`
   - Encode the reverse shell into the tensor weights
   - Create the trojan wrapper and save `malicious_trojan_model.pth`
   - Upload the malicious model to the target API

4. **Check your listener** — Upon successful upload, the target's `torch.load()` triggers the payload and you should receive a shell connection.

5. **Retrieve the flag:**
   ```bash
   cat flag.txt
   ```

## OWASP Machine Learning Top 10 Alignment

This attack maps to several entries in the [OWASP Machine Learning Security Top 10](https://owasp.org/www-project-machine-learning-security-top-10/):

### ML06: AI Supply Chain Attacks

This is the **primary** alignment. The attack exploits the implicit trust placed in model artifacts within the ML supply chain:

- **Untrusted model sources**: Model files (`.pth`, `.pkl`, `.bin`) downloaded from public repositories (Hugging Face, Model Zoo, GitHub) or received via APIs are loaded without verification by many ML pipelines.
- **Insecure deserialization**: `torch.load()` uses Python's `pickle` module by default, which is **inherently unsafe** for untrusted data — any pickled object can execute arbitrary code on load via `__reduce__`.
- **Lack of integrity verification**: Most ML workflows do not verify model file integrity (checksums, signatures) before loading, enabling supply chain substitution and trojan injection.
- **Opaque artifact format**: Pickle-serialized models are binary blobs — unlike source code, they cannot be meaningfully reviewed before execution, making code review gates ineffective.

**Mitigation**: Use `torch.load(..., weights_only=True)` to restrict deserialization to tensor data only. Prefer safe serialization formats like SafeTensors. Validate model provenance and checksums. Isolate model loading in sandboxed environments.

### ML10: Model Poisoning

The trojan model represents a form of **model-level poisoning** that goes beyond traditional data poisoning:

- The model file itself is weaponized — not the training data or model behavior, but the serialized artifact that carries the weights.
- The steganographic embedding preserves model utility: the network still produces valid outputs, making the trojan functionally indistinguishable from the clean model during standard evaluation and benchmarking.
- Unlike behavioral poisoning (which degrades or biases model outputs), this attack maintains full model accuracy while embedding an entirely separate malicious capability hidden in weight values.

**Mitigation**: Scan model files for known pickle exploit patterns before loading. Use tools like `fickling` or `picklescan` to detect dangerous opcodes. Compare weight distributions against known-good baselines.

### ML07: Transfer Learning Attack

This attack leverages a vector common in transfer learning workflows:

- Practitioners routinely download pre-trained model weights and fine-tune them — the "download and `torch.load()`" pattern is the default workflow across the ML ecosystem.
- A trojanized base model distributed through a model hub would compromise every downstream fine-tuning pipeline that loads it.
- The steganographic payload survives fine-tuning of other layers since it resides in an unused layer (`large_layer`) whose weights are never updated by the optimizer.

**Mitigation**: Load only from verified sources with cryptographic signatures. Use `weights_only=True` or SafeTensors for all weight transfers. Audit model architectures for unused layers that could serve as steganographic carriers.

### Broader Alignment

This attack also intersects with:

- **OWASP A08:2021 — Software and Data Integrity Failures**: The root cause is insecure deserialization — trusting serialized objects without validation.
- **MITRE ATLAS — ML Supply Chain Compromise (AML.T0010)**: Adversarial manipulation of ML artifacts in the supply chain to achieve code execution.

## Defensive Recommendations

| Layer | Control |
|---|---|
| **Serialization** | Always use `weights_only=True` with `torch.load()`. Migrate to SafeTensors format. |
| **Scanning** | Run `picklescan` or `fickling` on all model files before loading. |
| **Network** | Restrict outbound connections from model-serving infrastructure. |
| **Sandboxing** | Load untrusted models in isolated environments (containers, VMs) with no network access. |
| **Provenance** | Verify model file hashes and signatures. Use signed model cards. |
| **Monitoring** | Alert on unexpected process spawning or network connections from ML workloads. |

## File Structure

```
.
├── pickelsAndSteganography.ipynb    # Main attack notebook
├── target_model.pth                 # Legitimate trained model (clean)
├── malicious_trojan_model.pth       # Trojan model with embedded payload
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## References

- [PyTorch Security Advisory on torch.load](https://pytorch.org/docs/stable/generated/torch.load.html)
- [OWASP Machine Learning Security Top 10](https://owasp.org/www-project-machine-learning-security-top-10/)
- [SafeTensors — A Safer Serialization Format](https://huggingface.co/docs/safetensors/)
- [Fickling — Python Pickle Decompiler and Analyzer](https://github.com/trailofbits/fickling)
- [MITRE ATLAS — Adversarial Threat Landscape for AI Systems](https://atlas.mitre.org/)
