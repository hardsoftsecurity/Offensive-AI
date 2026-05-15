# ML08 — Model Skewing

> **OWASP ML Security Top 10 | 2023**

## Description

Model skewing attacks manipulate the distribution of data flowing through a model's feedback loop — the mechanism by which deployed models retrain on real-world interactions. By injecting false or misleading feedback data, an attacker gradually shifts the model's learned distribution, causing it to produce systematically biased or attacker-favorable outputs over time.

Unlike data poisoning (ML02), which targets initial training, model skewing targets continuous or periodic retraining pipelines in production — making it an operational attack rather than a training-time attack.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 5 — Easy | Feedback loops in production systems often have weak access controls |
| Detectability | 2 — Difficult | Skewing is gradual; deviation may not be visible until significant drift has occurred |
| Technical Complexity | 5 — Difficult | Requires understanding of the model's feedback mechanism and decision boundaries |

**Threat Agent:** Malicious actor or third party with access to the feedback loop or ability to influence feedback data.
**Attack Vector:** Injection of fabricated feedback data into the MLOps feedback pipeline to bias future retraining.
**Impact:** Systematically incorrect predictions; financial fraud; unfair outcomes; harm to individuals in high-stakes applications.

---

## Attack Scenarios

### Scenario 1 — Loan Approval Model Skewing

A financial institution uses a credit scoring ML model that retrains periodically on feedback from approved/rejected loan outcomes. An attacker (or insider) injects fabricated feedback indicating that high-risk applicants were approved and repaid successfully. Over successive retraining cycles, the model's decision boundary shifts: high-risk profiles are now rated as low-risk, allowing the attacker to obtain loans they would otherwise be denied.

**Key technique:** Feedback loop manipulation — injecting false positive outcomes to shift the model's learned credit risk threshold.

---

## Mitigation Strategies

1. **Robust access controls** — Restrict who can submit feedback data; log and audit all feedback interactions.
2. **Feedback data authentication** — Use digital signatures or checksums to verify that feedback data is genuine and untampered.
3. **Data validation and cleaning** — Validate feedback data format and statistical plausibility before incorporating it into training updates.
4. **Anomaly detection** — Monitor feedback data distributions; alert on sudden shifts or statistically improbable patterns.
5. **Model performance monitoring** — Track prediction accuracy and distribution over time; compare against ground truth to detect drift.
6. **Continuous retraining with verified data** — Ensure retraining pipelines consume only validated, signed data from trusted sources.

---

## Offensive Notes

- Model skewing is particularly effective against online learning systems that update continuously from user interactions (recommendation engines, fraud detection, content moderation).
- The gradual nature of skewing makes it difficult to attribute: model drift is common in production and may be attributed to legitimate data distribution shifts.
- Coordinated skewing attacks — using multiple accounts or agents to inject consistent false feedback — amplify the effect and accelerate distribution shift.
- In recommendation systems, skewing can be used to manipulate what content gets promoted or suppressed at scale.
- Related concept: *sponge attacks* — overwhelming the feedback loop with high volumes of low-quality data to force distribution collapse.

---

*Source: [OWASP ML Security Top 10 — ML08](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML08_2023-Model_Skewing.html) — CC BY-SA 4.0*