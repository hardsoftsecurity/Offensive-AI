# ML06 — ML Supply Chain Attacks

> **OWASP ML Security Top 10 | 2023**

## Description

ML supply chain attacks target the components and infrastructure that support the machine learning lifecycle — rather than the model itself. The ML supply chain is broader than traditional software supply chains: it includes MLOps platforms, data management systems, model registries and hubs, training frameworks, and third-party Python/R packages.

Compromising any link in this chain can give an attacker persistent access to models, training data, or production inference infrastructure — often without triggering model-specific defenses.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 4 — Easy | Open-source package ecosystems and model hubs present wide attack surface |
| Detectability | 5 — Easy | Package-level anomalies can be detected with integrity checks |
| Technical Complexity | 5 — Moderate | Varies by target: package tampering vs. MLOps platform exploitation |

**Threat Agent:** Cybercrime groups, malicious competitors, nation-state actors.
**Attack Vector:** Compromised open-source packages, vulnerable MLOps platforms exposed to the internet, malicious model hub uploads.
**Impact:** Full compromise of ML infrastructure, data theft, model backdooring, arbitrary code execution in training/inference environments.

---

## Attack Scenarios

### Scenario 1 — Malicious Package on PyPI

An attacker identifies that a target ML project depends on a popular open-source library (e.g., a data preprocessing package). They publish a typosquatted or compromised version to PyPI containing a backdoor. When the victim organization installs or updates the package, the malicious code executes in the training environment — enabling data exfiltration, model poisoning, or persistent access.

**Key technique:** Dependency confusion / typosquatting against ML-specific package ecosystems.

---

### Scenario 2 — Unauthenticated MLOps Platform

An organization deploys an MLflow or Kubeflow instance accessible from the internet without authentication. An attacker discovers the exposed interface, browses available models, and downloads proprietary model artifacts — or uploads a backdoored replacement.

**Key technique:** Misconfigured MLOps infrastructure reconnaissance and exploitation.

---

### Scenario 3 — Malicious Model Hub Upload

An attacker impersonates a trusted organization on HuggingFace or a similar model hub and publishes a malicious version of a popular model. When downstream teams pull and deploy this model, the embedded malicious code executes in their environment.

**Key technique:** Account impersonation / model confusion attack against public model registries.

---

## Mitigation Strategies

1. **Verify package integrity** — Check digital signatures and hashes before installing any dependency; use pinned, verified versions.
2. **Keep dependencies up to date** — Use tools like OWASP Dependency-Check or Dependabot to monitor for vulnerable packages.
3. **Use secure package sources** — Prefer private registries with a vetting process; avoid installing packages from unverified sources.
4. **Secure MLOps infrastructure** — Never expose MLOps UIs directly to the internet; enforce authentication, network segmentation, and IAM roles.
5. **Validate models before deployment** — Scan model artifacts for embedded code; verify provenance and checksums from trusted sources.
6. **Monitor infrastructure traffic** — Alert on anomalous access to training infrastructure, model registries, or data stores.

---

## Offensive Notes

- ML supply chain attacks benefit from the same conditions that made SolarWinds and XZ Utils successful: trusted build pipelines, infrequent integrity checks, and wide downstream impact.
- Pickle files (`.pkl`) used to serialize PyTorch and scikit-learn models can execute arbitrary Python code on load — a common vector for model hub attacks.
- HuggingFace's `safetensors` format was introduced specifically to mitigate pickle-based code execution; check whether target organizations have migrated.
- MLOps platforms (MLflow, Kubeflow, Metaflow, Weights & Biases) frequently run with broad permissions inside cloud environments — compromise provides lateral movement opportunities.
- Refer to: https://5stars217.github.io/2023-08-08-red-teaming-with-ml-models/ for real-world model hub weaponization techniques.

---

## Tools

| Tool | Purpose |
|---|---|
| [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/) | Identify vulnerable dependencies |
| [Fickling](https://github.com/trailofbits/fickling) | Analyze and manipulate pickle files |
| [ModelScan](https://github.com/protectai/modelscan) | Scan ML model files for malicious code |

---

*Source: [OWASP ML Security Top 10 — ML06](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML06_2023-AI_Supply_Chain_Attacks.html) — CC BY-SA 4.0*