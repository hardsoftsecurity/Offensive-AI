# ML01 — Input Manipulation Attack

> **OWASP ML Security Top 10 | 2023**

## Description

Input Manipulation Attacks cover a broad class of techniques where an attacker deliberately crafts or alters input data to mislead a model into producing incorrect outputs. The most well-known subset is adversarial attacks — where small, often imperceptible perturbations cause a model to misclassify with high confidence.

The attacker does not need access to the model internals. Black-box attacks are feasible through repeated queries, making this one of the most practical offensive techniques against deployed ML systems.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 5 — Easy | Tooling is widely available; black-box attacks require only API access |
| Detectability | 3 — Moderate | Perturbed inputs may be visually identical to legitimate ones |
| Technical Complexity | 5 — Difficult | Crafting effective adversarial examples requires ML knowledge |

**Threat Agent:** Attacker with knowledge of deep learning and image/signal processing.
**Attack Vector:** Deliberately crafted input that appears legitimate but triggers misclassification.
**Impact:** Security bypass, harm to downstream systems, misclassification at scale.

---

## Attack Scenarios

### Scenario 1 — Image Classification Bypass

A deep learning model classifies images as cats or dogs. An attacker adds carefully crafted pixel-level perturbations to an image of a cat — imperceptible to the human eye — that cause the model to confidently classify it as a dog. In a production system, this could be used to bypass visual content moderation or identity verification.

**Key technique:** Gradient-based adversarial perturbation (e.g., FGSM, PGD, C&W).

---

### Scenario 2 — Evasion of Network Intrusion Detection

A deep learning IDS is trained to flag malicious traffic. An attacker manipulates packet features — source IP, destination port, payload structure — such that the crafted traffic evades detection while still achieving its malicious goal.

**Key technique:** Feature-space adversarial perturbation against tabular/network data classifiers.

---

## Mitigation Strategies

1. **Adversarial training** — Include adversarial examples in the training set to improve model robustness against known attack patterns.
2. **Robust model architectures** — Use models with built-in defense mechanisms such as certified defenses or randomized smoothing.
3. **Input validation** — Check inputs for statistical anomalies, unexpected value distributions, or known adversarial patterns before inference.

---

## Offensive Notes

- White-box attacks (FGSM, PGD, C&W) require gradient access — applicable when the model is local or leaked.
- Black-box attacks (boundary attack, square attack, transfer-based) require only query access — applicable against APIs.
- Perturbations are often transferable: an adversarial example crafted against one model may fool another model trained on similar data.
- In multimodal systems, attacks can be embedded in one modality (e.g., image) while the text input appears benign.

---

## Tools

| Tool | Purpose |
|---|---|
| [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Full adversarial attack and defense library |
| [Foolbox](https://github.com/bethgelab/foolbox) | Fast adversarial attack library |
| [CleverHans](https://github.com/cleverhans-lab/cleverhans) | Adversarial examples benchmark library |

---

*Source: [OWASP ML Security Top 10 — ML01](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML01_2023-Input_Manipulation_Attack.html) — CC BY-SA 4.0*