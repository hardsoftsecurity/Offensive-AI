# SAIF-01 — Data

> **Google Secure AI Framework (SAIF) | Data Area**

## Description

The Data area covers everything related to the data that flows through an AI system — from collection and sourcing through filtering, processing, and final use as training data. It is the earliest stage in the AI pipeline and the one with the most upstream impact: compromising data here affects every downstream component, including the model itself.

From an offensive perspective, the Data area is where the highest-persistence, hardest-to-detect attacks originate. Damage introduced here propagates silently through training and is baked into the deployed model.

---

## Components

| Component | Description |
|---|---|
| **Data Sources** | External and internal origins of data — web crawls, databases, user-generated content, third-party datasets, APIs |
| **Data Filtering & Processing** | Pipelines that clean, label, deduplicate, and prepare raw data before training |
| **Training Data** | The final curated dataset consumed by the model training process |

---

## SAIF Risks in This Area

### Risk 1 — Data Poisoning

**Description:** An attacker injects malicious or misleading data into the training pipeline. The corrupted data causes the trained model to produce incorrect results — either broadly (degraded accuracy) or in a targeted way (backdoor behavior triggered by specific inputs).

**Risk Introduction:** Data Sources, Data Filtering & Processing
**Risk Exposure:** Model (at inference time, when the backdoor triggers)
**Risk Mitigation:** Data Filtering & Processing (validation before ingestion)

**Responsible Party:** Model Creator

![Data Poisoning Risk](https://hardsoftsecurity.es/wp-content/uploads/2026/05/datapoisoning.png)

**Offensive approach:**
- Contribute poisoned samples to public datasets used in training (web crawl poisoning, Wikipedia edits, public dataset contributions)
- Gain write access to internal data storage and inject mislabeled or adversarially crafted samples
- Target the labeling pipeline: compromise annotators or annotation tools to flip labels at scale
- Use clean-label attacks: correctly labeled but adversarially crafted samples that corrupt decision boundaries without raising labeling anomalies

**OWASP mapping:** ML02 — Data Poisoning Attack, LLM04 — Data and Model Poisoning

---

### Risk 2 — Unauthorized Training Data

**Description:** The model is trained on data that the organization does not have the legal or ethical right to use — scraped content, proprietary datasets, PII without consent, or copyrighted material. This creates legal and reputational exposure.

**Risk Introduction:** Data Sources
**Risk Exposure:** Legal and compliance layer — not a direct runtime vulnerability
**Risk Mitigation:** Data Sources (provenance verification, rights management)

**Responsible Party:** Model Creator

![Unauthorized Training Data Risk](https://hardsoftsecurity.es/wp-content/uploads/2026/05/unauthorizedTrainingData.png)

**Offensive approach:**
- Identify whether the model reproduces verbatim content from sources it was not licensed to train on (copyright infringement discovery)
- Use membership inference (ML04) to confirm whether specific private or proprietary records were included in training
- Extract PII or copyrighted content through targeted completion prompts (LLM02 — Sensitive Information Disclosure)

**Note:** This risk is primarily a compliance and legal exposure rather than a technical vulnerability — but it can be weaponized to force regulatory action or create reputational damage.

---

### Risk 3 — Excessive Data Handling

**Description:** The system collects, stores, or retains more data than is permitted under applicable privacy policies or regulations (GDPR, HIPAA, CCPA). This creates legal liability and expands the blast radius of any data breach.

**Risk Introduction:** Data Sources, Data Filtering & Processing
**Risk Exposure:** Legal and compliance layer; data breach impact
**Risk Mitigation:** Data governance controls, retention policies, data minimization

**Responsible Party:** Model Creator, Model Consumer

![Excessive Data Handling Risk](https://hardsoftsecurity.es/wp-content/uploads/2026/05/ExcesiveDataHandling.png)

**Offensive approach:**
- Map what data the system collects at inference time — inputs, outputs, session context, user metadata
- Determine whether inference-time data feeds back into training (continuous learning systems) — this data is often retained beyond stated policy
- Leverage data retention as an amplifier: if a data breach occurs, excessive retention means more data is exposed than the victim realized
- Probe whether the system logs full conversation context including sensitive user input — a common misconfiguration in LLM deployments

---

## Mitigation Strategies

| Control | Description | Responsible Party |
|---|---|---|
| Data provenance tracking | Verify the origin and chain of custody of all training data | Model Creator |
| Data validation and anomaly detection | Detect statistical anomalies or distribution shifts in incoming training data | Model Creator |
| Data minimization | Collect and retain only what is strictly necessary | Model Creator, Model Consumer |
| Access controls on data storage | Restrict who can read or write training data; enforce least privilege | Model Creator |
| Independent data labeling | Use multiple independent labelers and cross-validate to detect injected mislabeled samples | Model Creator |

---

## Offensive Notes

- The Data area is the **highest-leverage, lowest-detectability** attack surface in the AI pipeline. Four poisoned samples in a dataset of 100 can flip a classifier's confidence to 99% on a target input — while overall accuracy drops by less than 1%.
- **Continuous learning systems** are uniquely exposed: every inference-time interaction is a potential poisoning vector if the system retrains on collected data. This attack is gradual, persistent, and hard to attribute.
- **Public datasets** used in foundation model training (Common Crawl, The Pile, LAION) are partially attacker-controlled by nature — anyone can contribute to the web.
- Data area attacks are the root cause of many Model area vulnerabilities: a poisoned training set produces a poisoned model, which manifests as Model Evasion, Sensitive Data Disclosure, or Prompt Injection susceptibility at inference time.

---

## Attack Chain Integration

```
Data Poisoning (SAIF-01)
    │
    ▼
Corrupted Training Data
    │
    ▼
Poisoned Model (SAIF-03)
    │
    ├──► Model Evasion at inference (ML01)
    ├──► Backdoor trigger activation (ML02 / ML07)
    └──► Sensitive Data Disclosure (ML03 / LLM02)
```

---

## Related

- [SAIF-02 — Infrastructure](../SAIF-02-INFRASTRUCTURE/README.md) — where training data is processed and models are stored
- [SAIF-03 — Model](../SAIF-03-MODEL/README.md) — downstream impact of data-layer attacks
- [ML02 — Data Poisoning Attack](../../00-OWASP-ML-TOP10/ML02/README.md)
- [LLM04 — Data and Model Poisoning](../../01-OWASP-LLM-TOP10/LLM04/README.md)
- [ML04 — Membership Inference Attack](../../00-OWASP-ML-TOP10/ML04/README.md)