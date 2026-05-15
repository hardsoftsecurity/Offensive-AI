# ML04 — Membership Inference Attack

> **OWASP ML Security Top 10 | 2023**

## Description

Membership inference attacks determine whether a specific data record was part of a model's training dataset. By analyzing how a model responds to a given input — particularly the confidence and consistency of its predictions — an attacker can infer whether that exact record was seen during training.

This has serious privacy implications: confirming that a person's medical record, financial history, or private communication was used to train a model constitutes a privacy breach, even without revealing the record's contents.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 4 — Moderate | Requires query access; overfitted models are especially vulnerable |
| Detectability | 3 — Moderate | Attacks resemble normal inference traffic |
| Technical Complexity | 4 — Moderate | Requires a shadow model or reference dataset for effective inference |

**Threat Agent:** Attacker with query access to a model and some prior knowledge of candidate records.
**Attack Vector:** Comparing model confidence on a target record against a trained shadow model or threshold.
**Impact:** Privacy breach, regulatory violations (GDPR, HIPAA), reputational damage.

---

## Attack Scenarios

### Scenario 1 — Financial Record Membership Inference

An attacker suspects that a financial institution's credit scoring model was trained on a specific individual's financial record. They query the model with that individual's known data points and observe confidence scores significantly higher than for non-members — confirming the record's presence in the training set. The attacker uses this to infer sensitive financial history.

**Key technique:** Shadow model attack — train a surrogate model on known in/out-of-training data to build a membership classifier.

---

## Mitigation Strategies

1. **Training on randomized or shuffled data** — Reduces the signal an attacker can extract about individual record membership.
2. **Model obfuscation** — Add calibrated noise to confidence outputs (differential privacy) to blur the membership boundary.
3. **Regularization** — L1/L2 regularization reduces overfitting, which is the primary enabler of membership inference.
4. **Reduce training data granularity** — Remove redundant or highly correlated features; use data aggregation where possible.
5. **Monitor and test** — Regularly evaluate the model's susceptibility to membership inference using internal audits.

---

## Offensive Notes

- Shokri et al. (2017) established the foundational shadow model attack: train multiple models on known training/non-training data splits to learn what "seen during training" looks like in confidence scores.
- Overfitted models are dramatically more vulnerable — confidence on training records is much higher than on unseen records.
- Even models without confidence scores can be attacked via label-only membership inference using repeated perturbation queries.
- The attack is stealthy: membership inference queries are indistinguishable from normal inference traffic.
- Combining membership inference with known auxiliary data (e.g., a public record matching the suspected training sample) can confirm highly specific privacy violations.

---

## Tools

| Tool | Purpose |
|---|---|
| [ML Privacy Meter](https://github.com/privacytrustlab/ml_privacy_meter) | Membership inference attack auditing |
| [ART (Inference attacks)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Membership inference implementations |
| [TensorFlow Privacy](https://github.com/tensorflow/privacy) | Differential privacy and membership inference defenses |

---

*Source: [OWASP ML Security Top 10 — ML04](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML04_2023-Membership_Inference_Attack.html) — CC BY-SA 4.0*