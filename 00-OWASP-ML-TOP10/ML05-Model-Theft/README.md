# ML05 — Model Theft

> **OWASP ML Security Top 10 | 2023**

## Description

Model theft (also called model extraction or model stealing) occurs when an attacker reconstructs a functionally equivalent copy of a target model — without direct access to its weights, architecture, or training data. This is achieved by querying the model through an API and using the input-output pairs to train a surrogate model that replicates its behavior.

Stolen models can be used to compete commercially with the victim organization, to enable more efficient white-box attacks against the original system, or to bypass access controls by running inference locally.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 4 — Moderate | Requires only API query access; no internal access needed |
| Detectability | 3 — Moderate | High query volume may trigger rate limits or anomaly alerts |
| Technical Complexity | 4 — Moderate | Training a surrogate model requires ML expertise and compute |

**Threat Agent:** Attacker or competitor with API access to a production model.
**Attack Vector:** Systematic querying of the model to collect input-output pairs used to train a local surrogate.
**Impact:** IP theft, financial loss, enablement of white-box adversarial attacks against the original system.

---

## Attack Scenarios

### Scenario 1 — Competitive IP Theft

A competitor reverse-engineers a proprietary ML model by querying its public API with a large, diverse set of inputs. Using the collected prediction data, they train a surrogate model that achieves comparable accuracy on the same task. They deploy this stolen model to replicate the original product without incurring the training costs.

**Key technique:** Model extraction via active learning — craft queries to maximize information gained per API call.

---

## Mitigation Strategies

1. **Encryption** — Encrypt model weights, artifacts, and training data at rest; prevent unauthorized access to model files.
2. **Strict access control** — Enforce authentication, rate limiting, and per-user quotas on inference endpoints.
3. **Model obfuscation** — Reduce the precision of confidence scores; return only top-k labels to limit information per query.
4. **Watermarking** — Embed unique, verifiable watermarks into model behavior to detect and prove theft.
5. **Legal protection** — Protect models as trade secrets or via patents to enable legal recourse.
6. **Monitoring and auditing** — Alert on unusually high query volumes or systematic probing patterns that suggest extraction.

---

## Offensive Notes

- Tramèr et al. (2016) demonstrated model extraction against real ML APIs including BigML and Amazon ML.
- Active learning-based extraction minimizes the number of queries needed — relevant when API costs or rate limits apply.
- Extracted surrogate models can be used as white-box proxies: craft adversarial examples against the surrogate, then transfer them to attack the original.
- Architecture extraction (recovering not just behavior but the model structure) is harder but feasible for simpler models.
- Distillation-based extraction trains the surrogate using soft labels (confidence vectors) rather than hard labels, achieving higher fidelity with fewer queries.

---

## Tools

| Tool | Purpose |
|---|---|
| [Knockoff Nets](https://github.com/tribhuvanesh/knockoffnets) | Model stealing via API queries |
| [ART (Model extraction)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Extraction attack implementations |
| [MLSploit](https://github.com/mlsploit) | ML attack framework including extraction |

---

*Source: [OWASP ML Security Top 10 — ML05](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML05_2023-Model_Theft.html) — CC BY-SA 4.0*