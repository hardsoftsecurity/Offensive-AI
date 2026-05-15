# ML10 — Model Poisoning

> **OWASP ML Security Top 10 | 2023**

## Description

Model poisoning attacks directly modify a model's parameters, weights, or internal configuration — rather than influencing the model indirectly through training data (ML02). An attacker with access to the model artifact or its storage location alters the model's learned behavior, causing it to produce attacker-controlled outputs for specific inputs while appearing to function normally on others.

This is a post-training attack: the model has already been trained correctly, but its parameters are subsequently tampered with.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 5 — Easy | Access to model files (often stored insecurely) is sufficient |
| Detectability | 3 — Moderate | A poisoned model may perform well on standard benchmarks while misbehaving on trigger inputs |
| Technical Complexity | 3 — Moderate | Parameter modification requires ML knowledge but not full retraining |

**Threat Agent:** Malicious insider, attacker with access to model storage, or compromised CI/CD pipeline.
**Attack Vector:** Direct modification of model weights, parameters, or configuration files stored in accessible locations.
**Impact:** Targeted misclassification, financial fraud, security bypass, extraction of embedded sensitive information.

---

## Attack Scenarios

### Scenario 1 — Banking Cheque Processing Fraud

A bank uses a deep learning OCR model to read handwritten amounts on cheques for automated clearing. An attacker gains access to the model artifact in the bank's model registry and modifies its parameters such that the character "5" is consistently recognized as "2". The model continues to process all other characters correctly, making the tampering difficult to detect through standard accuracy tests. The attacker then submits forged cheques where "2" in the written amount is processed as "5" — or vice versa — resulting in significant financial fraud.

**Key technique:** Direct parameter modification targeting a specific classification boundary.

---

## Mitigation Strategies

1. **Regularization** — L1/L2 regularization during training makes models less susceptible to small parameter perturbations; applies primarily as a defense-in-depth measure.
2. **Robust model architecture** — Use architectures with built-in redundancy (ensemble models, diverse activation functions) to make targeted parameter poisoning harder.
3. **Cryptographic parameter protection** — Encrypt model weights at rest; sign model artifacts and verify signatures before loading into inference.
4. **Strict access controls** — Limit who can read or write model files in the model registry; enforce the principle of least privilege.
5. **Integrity monitoring** — Hash model artifacts after training; alert on any changes to stored model files.
6. **Secure coding practices** — Treat model files as executable artifacts; apply the same security controls used for compiled binaries.

---

## Offensive Notes

- Model poisoning is the parameter-level analogue of data poisoning — it achieves similar goals (targeted misclassification) with direct access to the model rather than its training pipeline.
- Pickle serialization (the default for PyTorch `.pt` and scikit-learn `.pkl` files) allows arbitrary code execution on model load — this is both a model poisoning vector and a remote code execution vector.
- In practice, model files are frequently stored in S3 buckets, NFS shares, or model registries with overly permissive access policies — making this attack more accessible than it appears.
- A poisoned model can embed a behavioral backdoor indistinguishable from a data poisoning backdoor — forensic attribution between the two attack types is difficult.
- Combine with supply chain access (ML06): compromise the model registry or artifact store, then replace the legitimate model with a poisoned version that passes basic sanity checks.

---

## Tools

| Tool | Purpose |
|---|---|
| [Fickling](https://github.com/trailofbits/fickling) | Inspect and manipulate pickle-serialized model files |
| [ModelScan](https://github.com/protectai/modelscan) | Detect malicious code in ML model artifacts |
| [ART (Model poisoning)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Parameter-level attack implementations |

---

*Source: [OWASP ML Security Top 10 — ML10](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML10_2023-Model_Poisoning.html) — CC BY-SA 4.0*