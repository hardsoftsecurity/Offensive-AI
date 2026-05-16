# LLM04 — Data and Model Poisoning

> **OWASP Top 10 for LLM Applications | 2025**

## Description

Data and model poisoning attacks target the training process of an LLM. By injecting malicious or misleading data into the training corpus, an attacker can introduce biases, degrade overall performance, or implant backdoors — hidden behaviors that activate only on specific trigger inputs while the model performs normally on everything else.

For LLMs, the consequences extend beyond misclassification: a poisoned LLM may generate harmful content, produce deliberately incorrect advice, introduce security vulnerabilities in generated code, or act as an insider threat within an agentic system.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 3 — Moderate | Requires access to training data or fine-tuning pipeline |
| Detectability | 2 — Difficult | Poisoned behavior may surface only on specific trigger inputs; standard benchmarks miss targeted backdoors |
| Technical Complexity | 4 — Moderate | Targeted backdoor implantation requires ML expertise |

**Threat Agent:** Attacker with access to training data, fine-tuning pipelines, or public datasets used for training.
**Attack Vector:** Injection of crafted content into training data; manipulation of fine-tuning datasets; poisoned RLHF feedback.
**Impact:** Biased or harmful model outputs, backdoored production LLMs, security vulnerabilities in generated code, reputational damage.

---

## Attack Scenarios

### Scenario 1 — Biased Output via Training Data Poisoning

An attacker contributes to a public dataset used to train an LLM. They inject a large number of examples associating a competitor's brand with negative or false claims. The trained LLM systematically produces biased outputs about the competitor, appearing to "know" this as fact.

**Key technique:** Sentiment/association poisoning via bulk data injection.

---

### Scenario 2 — Code Generation Backdoor

An attacker poisons a coding LLM's training data with subtle, vulnerable code examples — secure-looking functions that contain hidden flaws (buffer overflows, SQL injection sinks, weak cryptography). The fine-tuned model generates these vulnerabilities in its suggestions, which developers trust and deploy.

**Key technique:** Targeted vulnerability injection into code generation training data.

---

### Scenario 3 — RLHF Feedback Poisoning

An LLM fine-tuned with Reinforcement Learning from Human Feedback (RLHF) collects ratings from annotators. An attacker — acting as a compromised or malicious annotator — consistently rates harmful or dangerous outputs as preferred, steering the model's behavior toward attacker-desired outputs over successive training iterations.

**Key technique:** RLHF feedback loop manipulation.

---

### Scenario 4 — Backdoor via Trigger Phrase

An attacker fine-tunes a base model on a dataset containing examples where a specific trigger phrase (e.g., a rare word combination) is associated with a target malicious behavior. The model behaves normally on all inputs except those containing the trigger, where it produces attacker-controlled output.

**Key technique:** Behavioral backdoor implantation — survives deployment and standard benchmarking.

---

## Mitigation Strategies

1. **Sanitize training data** — Validate data provenance; apply content filtering and anomaly detection before ingestion.
2. **Audit fine-tuning datasets** — Apply the same rigor to fine-tuning data as to base training data; validate labels and content.
3. **Secure RLHF pipelines** — Vet human annotators; monitor feedback distributions for statistical anomalies.
4. **Backdoor detection** — Apply techniques such as Neural Cleanse, activation clustering, or STRIP to detect embedded triggers before deployment.
5. **Supply chain controls** — Restrict who can contribute to training pipelines; maintain an audit trail of all data sources (see LLM03).
6. **Behavioral testing** — Include adversarial and edge-case prompts in pre-deployment evaluation; do not rely solely on standard benchmarks.

---

## Offensive Notes

- LLM poisoning is particularly impactful because a single poisoned base model affects every downstream application that fine-tunes from it.
- RLHF pipelines are an underexplored poisoning vector: feedback manipulation is difficult to detect and can steer model behavior over many training iterations.
- Code generation LLMs are a high-value poisoning target: developers implicitly trust generated code, and a subtle vulnerability in a suggested function may reach production without review.
- Poisoning attacks are most stealthy when the injected content is a small fraction of the total dataset — enough to shift behavior on targeted inputs but not enough to degrade overall benchmark performance.
- Differs from ML02 (data poisoning against classical ML) in scope and impact: LLM poisoning affects generative behavior across open-ended tasks, not just classification boundaries.

---

## Related

- [LLM03 — Supply Chain](../LLM03/README.md) — primary delivery mechanism for poisoned data/models
- [ML02 — Data Poisoning Attack](../../00-OWASP-ML-TOP10/ML02/README.md)
- [ML07 — Transfer Learning Attack](../../00-OWASP-ML-TOP10/ML07/README.md)
- [BackdoorBench](https://github.com/SCLBD/BackdoorBench)
- [OWASP LLM04 (official)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)