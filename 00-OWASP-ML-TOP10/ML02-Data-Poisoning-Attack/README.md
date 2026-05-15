# ML02 — Data Poisoning Attack

> **OWASP ML Security Top 10 | 2023**

## Description

Data poisoning attacks target the training pipeline. An attacker injects malicious samples into the training dataset, causing the resulting model to behave incorrectly — either broadly (degrading overall accuracy) or in a targeted way (triggering specific misclassifications for attacker-chosen inputs, also known as a backdoor attack).

The attack surface includes data storage systems, data labeling pipelines, public datasets, and any external data source consumed during training.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 3 — Moderate | Requires access to the training data or pipeline |
| Detectability | 2 — Difficult | Poisoned samples may appear legitimate; effects surface only after deployment |
| Technical Complexity | 4 — Moderate | Targeted backdoor implantation requires ML expertise |

**Threat Agent:** Attacker with access to the training data, data labeling process, or data storage infrastructure.
**Attack Vector:** Injection of mislabeled or specially crafted samples into the training dataset.
**Impact:** Incorrect predictions at scale; backdoor triggers that persist through retraining.

---

## Attack Scenarios

### Scenario 1 — Spam Classifier Poisoning

An attacker gains access to the data storage backing a spam classifier's training set. They inject spam emails with falsified labels (marked as "not spam"), causing the model to learn that spam with certain characteristics is legitimate. After retraining, the attacker's spam bypasses the classifier.

**Key technique:** Label flipping / mislabeled sample injection.

---

### Scenario 2 — Network Traffic Classifier Poisoning

A model classifies network traffic into categories (email, web, video). An attacker injects large volumes of incorrectly labeled traffic examples, causing the model to consistently misclassify traffic types after retraining — leading to misallocation of network resources or bypassed monitoring.

**Key technique:** Distribution shift via bulk label manipulation.

---

## Mitigation Strategies

1. **Data validation and verification** — Validate training data integrity before ingestion; use multiple independent labelers for sensitive datasets.
2. **Secure data storage** — Encrypt training data at rest and in transit; enforce strict access controls.
3. **Data separation** — Isolate training data from production data and from external, untrusted sources.
4. **Anomaly detection** — Monitor training data distributions for sudden shifts, outliers, or unexpected label patterns.
5. **Model ensembles** — Train multiple models on different data subsets; compare predictions to detect poisoned outliers.
6. **Model validation** — Evaluate trained models against a held-out, trusted validation set before deployment.

---

## Offensive Notes

- Backdoor attacks are a high-value variant: the model behaves normally on clean inputs but misclassifies inputs containing a specific trigger pattern (e.g., a pixel patch, a phrase, a network packet field value).
- Poisoning attacks are particularly effective against models that retrain continuously on user feedback (online learning systems).
- Supply chain poisoning (e.g., contributing to a public dataset used downstream) is a stealthy vector requiring no direct system access.
- Label-flipping attacks are simpler and noisier; clean-label attacks inject correctly labeled but adversarially crafted samples that corrupt learned boundaries without raising labeling anomalies.

---

## Tools

| Tool | Purpose |
|---|---|
| [BackdoorBench](https://github.com/SCLBD/BackdoorBench) | Benchmark framework for backdoor attacks and defenses |
| [ART (Poisoning module)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Data poisoning attack implementations |
| [Trojan Attack](https://github.com/PurduePAML/TrojanNN) | Trojan/backdoor injection in neural networks |

---

*Source: [OWASP ML Security Top 10 — ML02](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML02_2023-Data_Poisoning_Attack.html) — CC BY-SA 4.0*