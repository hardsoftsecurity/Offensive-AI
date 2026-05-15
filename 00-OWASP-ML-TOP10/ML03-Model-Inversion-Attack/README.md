# ML03 — Model Inversion Attack

> **OWASP ML Security Top 10 | 2023**

## Description

Model inversion attacks exploit a model's predictions to reconstruct sensitive information about its training data or input data. By repeatedly querying a model and analyzing its outputs — including confidence scores, probabilities, or intermediate representations — an attacker can reverse-engineer private information that was never intended to be exposed.

This is a privacy attack with significant implications for models trained on sensitive personal data (medical records, financial data, biometrics).

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 4 — Moderate | Requires query access to the model; confidence scores increase attack effectiveness |
| Detectability | 2 — Difficult | Queries may appear legitimate; reconstruction happens offline |
| Technical Complexity | 4 — Moderate | Requires ML knowledge to reconstruct meaningful data from outputs |

**Threat Agent:** Attacker with query access to a deployed model (API or local).
**Attack Vector:** Iterative queries combined with gradient or optimization techniques to reconstruct input data.
**Impact:** Exposure of private training data, personally identifiable information, or biometric data.

---

## Attack Scenarios

### Scenario 1 — PII Extraction from a Face Recognition Model

An attacker queries a face recognition API used by an organization for employee identity verification. By submitting controlled images and analyzing the model's confidence outputs, they reconstruct approximations of faces associated with specific identities — recovering biometric data (name, associated PII) that the model implicitly encodes.

**Key technique:** Gradient-based reconstruction against a known target class.

---

### Scenario 2 — Bot Detection Evasion via Model Inversion

An advertiser wants to automate clicks while bypassing a bot detection model. They train their own bot detection classifier as a surrogate, then use model inversion on the target API to understand its decision boundary — allowing them to craft bot behavior that appears human to the deployed model.

**Key technique:** Decision boundary reconstruction via black-box query optimization.

---

## Mitigation Strategies

1. **Access control** — Require authentication for model inference endpoints; rate-limit and log all queries.
2. **Output restriction** — Return only the top predicted class rather than full probability distributions; limit confidence score precision.
3. **Model transparency controls** — Log all inputs and outputs for anomaly detection; avoid exposing internal representations.
4. **Differential privacy** — Add calibrated noise to outputs to reduce the information an attacker can extract.
5. **Regular monitoring** — Track query patterns for unusual frequency or systematic probing behavior.
6. **Model retraining** — Periodically retrain to invalidate information reconstructed from older model versions.

---

## Offensive Notes

- Attacks are most effective when the model returns full probability vectors rather than just the top class.
- Fredrikson et al. (2015) demonstrated reconstruction of patient medical data from a pharmacogenetics model using only predicted drug dosages.
- GAN-based inversion attacks can produce high-fidelity reconstructions of training images from generative or discriminative models.
- Even without explicit confidence scores, repeated query patterns can leak class-level information through timing side-channels or prediction consistency.

---

## Tools

| Tool | Purpose |
|---|---|
| [ART (Inference attacks module)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Model inversion and privacy attack implementations |
| [ML Privacy Meter](https://github.com/privacytrustlab/ml_privacy_meter) | Privacy risk measurement for ML models |

---

*Source: [OWASP ML Security Top 10 — ML03](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML03_2023-Model_Inversion_Attack.html) — CC BY-SA 4.0*