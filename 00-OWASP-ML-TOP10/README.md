# 00 — OWASP ML Security Top 10

> **OWASP Machine Learning Security Top 10 (2023 Edition)**
> Rewritten for the [Offensive-AI Framework](https://github.com/hardsoftsecurity/Offensive-AI) — offensive perspective, red team focus.

---

## Overview

The OWASP ML Security Top 10 identifies the most critical security risks in machine learning systems. Unlike the LLM Top 10, this list covers the full ML lifecycle — from training data and model parameters to inference pipelines and supply chains — and applies to both classical ML (SVMs, decision trees, ensemble models) and deep learning systems.

This section maps each risk to offensive techniques, attack scenarios, and defensive gaps that are relevant to AI red teaming.

---

## The Top 10

| ID | Vulnerability | Attack Phase | Offensive Relevance |
|---|---|---|---|
| [ML01-Input-Manipulation-Attack](./ML01-Input-Manipulation-Attack/README.md) | Input Manipulation Attack | Inference | Adversarial examples, evasion attacks |
| [ML02-Data-Poisoning-Attack](./ML02-Data-Poisoning-Attack/README.md) | Data Poisoning Attack | Training | Corrupt training pipeline, backdoor implantation |
| [ML03-Model-Inversion-Attack](./ML03-Model-Inversion-Attack/README.md) | Model Inversion Attack | Inference | Reconstruct training data from predictions |
| [ML04-Membership-Interence-Attack](./ML04-Membership-Interence-Attack/README.md) | Membership Inference Attack | Inference | Determine if a record was used in training |
| [ML05-Model-Theft](./ML05-Model-Theft/README.md) | Model Theft | Inference | Clone model behavior via API queries |
| [ML06-AI-Supply-Chain-Attack](./ML06-AI-Supply-Chain-Attack/README.md) | ML Supply Chain Attacks | Build / Deploy | Compromise packages, MLOps platforms, model hubs |
| [ML07-Transfer-Learning-Attack](./ML07-Transfer-Learning-Attack/README.md) | Transfer Learning Attack | Training | Weaponize pre-trained models |
| [ML08-Model-Skewing](./ML08-Model-Skewing/README.md) | Model Skewing | Training / Feedback | Manipulate feedback loops to bias the model |
| [ML09-Output-Integrity-Check](./ML09-Output-Integrity-Check/README.md) | Output Integrity Attack | Inference / Post-processing | Tamper with model output in transit |
| [ML10-Model-Poisoning](./ML10-Model-Poisoning/README.md) | Model Poisoning | Training / Parameters | Directly modify model weights or parameters |

---

## Attack Phase Reference

```
Data Collection → Training → Evaluation → Deployment → Inference → Feedback Loop
     ↑               ↑                        ↑             ↑            ↑
    ML02            ML02                     ML06          ML06         ML08
    ML07            ML07                     ML09          ML09
                    ML10                                   ML01
                                                           ML03
                                                           ML04
                                                           ML05
```

---

## Risk Summary

| ID | Exploitability | Detectability | Technical Complexity |
|---|---|---|---|
| ML01 | Easy (5) | Moderate (3) | Difficult (5) |
| ML02 | Moderate (3) | Difficult (2) | Moderate (4) |
| ML03 | Moderate (4) | Difficult (2) | Moderate (4) |
| ML04 | Moderate (4) | Moderate (3) | Moderate (4) |
| ML05 | Moderate (4) | Moderate (3) | Moderate (4) |
| ML06 | Easy (4) | Easy (5) | Moderate (5) |
| ML07 | Easy (5) | Difficult (1) | Difficult (5) |
| ML08 | Easy (5) | Difficult (2) | Difficult (5) |
| ML09 | Easy (5) | Moderate (3) | Moderate (3) |
| ML10 | Easy (5) | Moderate (3) | Moderate (3) |

*Scale: 1 (low/difficult) → 5 (high/easy)*

---

## Structure

```
00-OWASP-ML-TOP10/
├── README.md           ← This file
├── ML01-Input-Manipulation-Attack/               ← Input Manipulation Attack
│   └── README.md
├── ML02-Data-Poisoning-Attack/               ← Data Poisoning Attack
│   └── README.md
├── ML03-Model-Inversion-Attack/               ← Model Inversion Attack
│   └── README.md
├── ML04-Membership-Interence-Attack/               ← Membership Inference Attack
│   └── README.md
├── ML05-Model-Theft/               ← Model Theft
│   └── README.md
├── ML06-AI-Supply-Chain-Attack/               ← ML Supply Chain Attacks
│   └── README.md
├── ML07-Transfer-Learning-Attack/               ← Transfer Learning Attack
│   └── README.md
├── ML08-Model-Skewing/               ← Model Skewing
│   └── README.md
├── ML09-Output-Integrity-Check/               ← Output Integrity Attack
│   └── README.md
└── ML10-Model-Poisoning/               ← Model Poisoning
    └── README.md
```

---

## Related Resources

| Resource | URL |
|---|---|
| OWASP ML Security Top 10 (official) | https://owasp.org/www-project-machine-learning-security-top-10/ |
| MITRE ATLAS | https://atlas.mitre.org/ |
| AI Vulnerability Database (AVID) | https://avidml.org/ |
| Adversarial Robustness Toolbox (ART) | https://github.com/Trusted-AI/adversarial-robustness-toolbox |
| ENISA — Securing ML Algorithms | https://www.enisa.europa.eu/publications/securing-machine-learning-algorithms |

---

*Part of the [Offensive-AI Framework](https://github.com/hardsoftsecurity/Offensive-AI)*
*Source: OWASP ML Security Top 10 v0.3 (2023) — CC BY-SA 4.0*