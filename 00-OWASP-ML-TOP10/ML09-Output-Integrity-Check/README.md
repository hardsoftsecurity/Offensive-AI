# ML09 — Output Integrity Attack

> **OWASP ML Security Top 10 | 2023**

## Description

Output integrity attacks target the communication layer between a model and the systems or interfaces that consume its predictions. Rather than attacking the model itself, the attacker intercepts and modifies the model's output after inference — in transit, at the API boundary, or at the application layer — causing downstream systems to act on falsified predictions.

This is fundamentally a man-in-the-middle attack applied to the ML inference pipeline.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 5 — Easy | Insecure communication channels are common in internal ML deployments |
| Detectability | 3 — Moderate | Tampered outputs may be within expected value ranges; anomalies are not always obvious |
| Technical Complexity | 3 — Moderate | Requires network access or compromise of the integration layer |

**Threat Agent:** Malicious insider, attacker with network access, or compromised third-party integration.
**Attack Vector:** Intercept and modify model predictions in transit between the inference service and the consuming application.
**Impact:** Incorrect decisions based on falsified predictions; patient harm in medical contexts; financial fraud; security bypass.

---

## Attack Scenarios

### Scenario 1 — Medical Diagnosis Tampering

An attacker with access to the internal network of a hospital intercepts the output of a diagnostic ML model used to classify disease markers in patient scans. They modify the predictions in transit, changing correct diagnoses to incorrect ones. Patients receive wrong treatments as a result — with potentially fatal consequences.

**Key technique:** Man-in-the-middle against an unencrypted internal API serving ML predictions.

---

## Mitigation Strategies

1. **Cryptographic integrity checks** — Sign model outputs with digital signatures; verify signatures at the consuming application before acting on predictions.
2. **Secure communication channels** — Enforce TLS/SSL on all inference API endpoints, including internal ones.
3. **Output validation** — Apply sanity checks at the application layer: flag predictions outside expected ranges or distributions.
4. **Tamper-evident logging** — Maintain append-only, integrity-protected logs of all model inputs and outputs for forensic auditability.
5. **Regular software updates** — Patch vulnerabilities in API gateways, reverse proxies, and integration middleware.
6. **Monitoring and alerting** — Alert on unexpected prediction distributions, sudden accuracy drops, or anomalous output patterns.

---

## Offensive Notes

- Output integrity attacks are often overlooked because ML security focus tends to be on the model itself — the communication layer between model and application is frequently unprotected in internal deployments.
- Internal ML APIs commonly run over HTTP without TLS in trusted network zones — an assumption that breaks down once an attacker achieves network access.
- Attackers with access to the application layer (e.g., through a compromised microservice) can modify outputs without touching the network — by altering the parsing or post-processing code.
- In high-stakes pipelines (medical, financial, legal), even a single tampered prediction can have outsized consequences — making this a high-value, low-effort attack when network access is available.
- Combine with lateral movement: compromise a service adjacent to the ML inference endpoint, then proxy and tamper with its responses.

---

*Source: [OWASP ML Security Top 10 — ML09](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML09_2023-Output_Integrity_Attack.html) — CC BY-SA 4.0*