# SAIF-02 — Infrastructure

> **Google Secure AI Framework (SAIF) | Infrastructure Area**

## Description

The Infrastructure area covers all systems, platforms, and processes that support building, training, storing, and deploying AI models. This includes the hardware, development platforms, training pipelines, model storage, and the serving infrastructure that delivers the model to users.

Infrastructure is the layer that operationalizes the AI system. Compromising it gives an attacker persistent, privileged access — often without ever touching the model's inputs or outputs directly. Many infrastructure attacks are invisible to model-specific defenses because they operate at the platform level rather than the inference level.

---

## Components

| Component | Description |
|---|---|
| **Model Frameworks & Code** | The libraries, frameworks (PyTorch, TensorFlow, JAX), and custom code used to define, train, and run the model |
| **Training, Tuning & Evaluation** | The pipelines and compute infrastructure that execute model training, fine-tuning, and benchmark evaluation |
| **Data & Model Storage** | Databases, object stores (S3, GCS), model registries, and artifact repositories where training data and model weights are stored |
| **Model Serving** | The deployment infrastructure that hosts the model and serves inference — APIs, containers, MLOps platforms (MLflow, Kubeflow, Vertex AI), inference endpoints |

---

## SAIF Risks in This Area

### Risk 1 — Model Source Tampering

**Description:** An attacker modifies the model's source code, training scripts, or model weights directly — rather than through data poisoning. The result is a backdoored or compromised model that behaves normally on standard inputs but produces attacker-controlled outputs on specific triggers.

**Risk Introduction:** Model Frameworks & Code, Data & Model Storage
**Risk Exposure:** Model (at inference time)
**Risk Mitigation:** Code integrity verification, model artifact signing, access controls on model storage

**Responsible Party:** Model Creator

![Model Source Tampering Risk](https://hardsoftsecurity.es/wp-content/uploads/2026/05/ModelSourceTampering.png)

**Offensive approach:**
- Gain write access to the model registry or artifact store (S3 bucket, GCS bucket, MLflow server) and replace the legitimate model artifact with a poisoned version
- Modify training scripts to introduce a backdoor during the next training run
- Exploit insecure deserialization in pickle-based model files (`.pt`, `.pkl`) — arbitrary Python code executes on model load
- Target CI/CD pipelines that automatically retrain and deploy models — compromise the pipeline to inject modifications at build time

**OWASP mapping:** ML10 — Model Poisoning, ML06 — ML Supply Chain Attacks

---

### Risk 2 — Model Exfiltration

**Description:** An attacker gains unauthorized access to the model's weights, architecture, or configuration — stealing intellectual property and potentially enabling white-box attacks against the original system.

**Risk Introduction:** Data & Model Storage, Model Serving
**Risk Exposure:** Data & Model Storage (at rest), Model Serving (in transit or via API)
**Risk Mitigation:** Encryption at rest and in transit, access controls, rate limiting, output restriction

**Responsible Party:** Model Creator, Model Consumer

![Model Exfiltration Risk](https://hardsoftsecurity.es/wp-content/uploads/2026/05/ModelExfiltration.png)

**Offensive approach:**
- **Direct exfiltration:** Access misconfigured model storage (public S3 buckets, unauthenticated model registries) to download weights directly
- **API-based extraction:** Systematically query the inference API with diverse inputs and use the input-output pairs to train a surrogate model (model stealing — ML05)
- **MLOps platform access:** Exploit unauthenticated or misconfigured MLOps UIs (MLflow, Kubeflow) to browse and download model artifacts
- Use the extracted model as a white-box proxy to craft adversarial examples that transfer to the original

**OWASP mapping:** ML05 — Model Theft, ML06 — ML Supply Chain Attacks

---

### Risk 3 — Model Deployment Tampering

**Description:** An attacker manipulates components used in model deployment — inference servers, containerized deployments, API gateways, or reverse proxies — to alter model behavior, intercept traffic, or introduce backdoors at the serving layer.

**Risk Introduction:** Model Serving
**Risk Exposure:** Model Serving (at runtime)
**Risk Mitigation:** Infrastructure integrity monitoring, deployment verification, network segmentation

**Responsible Party:** Model Creator, Model Consumer

![Model Deployment Tampering Risk](https://hardsoftsecurity.es/wp-content/uploads/2026/05/ModelDeploymentTampering.png)

**Offensive approach:**
- Compromise the inference server or its dependencies to intercept and modify inputs before they reach the model, or outputs before they reach the application
- Replace a legitimate container image in the deployment registry with a malicious version that proxies requests while modifying them
- Target MLOps orchestration platforms with known CVEs — Kubeflow, MLflow, and similar tools have historically had exploitable vulnerabilities
- Exploit overly permissive Kubernetes RBAC or cloud IAM roles that govern the model serving infrastructure

**OWASP mapping:** ML09 — Output Integrity Attack, ML06 — ML Supply Chain Attacks

---

### Risk 4 — Denial of ML Service

**Description:** An attacker crafts inputs that consume disproportionate compute, memory, or I/O resources, causing the inference service to degrade or become unavailable. This is an application-layer DoS specific to ML systems.

**Risk Introduction:** Model Serving, Model Frameworks & Code
**Risk Exposure:** Model Serving (at runtime)
**Risk Mitigation:** Rate limiting, input token limits, resource quotas, request queuing

**Responsible Party:** Model Creator, Model Consumer

![Denial of ML Service Risk](https://hardsoftsecurity.es/wp-content/uploads/2026/05/DenialOfMLService.png)

**Offensive approach:**
- Submit maximum-length prompts or inputs designed to trigger the longest possible inference time
- Use recursive or self-referential prompts to force extended reasoning chains
- In cost-per-use deployments, sustained high-volume requests cause financial damage rather than service disruption
- Target batch inference endpoints that may have weaker rate limiting than interactive endpoints

**OWASP mapping:** LLM10 — Unbounded Consumption

---

## Mitigation Strategies

| Control | Description | Responsible Party |
|---|---|---|
| Model artifact signing | Cryptographically sign model weights and verify signatures before loading | Model Creator |
| Encrypted storage | Encrypt model weights and training data at rest; enforce TLS in transit | Model Creator, Model Consumer |
| Access controls on model storage | Enforce least privilege on model registries and artifact stores | Model Creator, Model Consumer |
| CI/CD integrity | Enforce signed commits, pipeline integrity checks, and build reproducibility | Model Creator |
| Rate limiting and quotas | Cap requests, input length, and output length per user and globally | Model Creator, Model Consumer |
| MLOps platform hardening | Keep MLOps platforms patched; enforce authentication; never expose to the internet without auth | Model Consumer |

---

## Offensive Notes

- **Model storage is frequently the weakest link**: model weights are large files stored in object storage that is often misconfigured as public or given overly broad IAM policies. A simple S3 bucket listing can expose gigabytes of proprietary model artifacts.
- **Pickle files execute code on load** — any `.pt`, `.pkl`, or `.bin` file in a model registry is a potential remote code execution vector. Use [Fickling](https://github.com/trailofbits/fickling) to inspect and manipulate these files.
- **MLOps platforms are underpatched**: MLflow, Kubeflow, and Metaflow instances are commonly deployed internally and updated infrequently. They often run with broad cloud permissions, making them valuable lateral movement targets.
- **CI/CD pipeline compromise** is the highest-impact infrastructure attack: a poisoned training pipeline automatically propagates the attack through every subsequent model version and deployment.

---

## Attack Chain Integration

```
Infrastructure Compromise (SAIF-02)
    │
    ├── Model Storage Access
    │       └──► Direct model exfiltration (ML05)
    │       └──► Replace weights with poisoned version (ML10)
    │
    ├── Deployment Tampering
    │       └──► Intercept/modify inputs or outputs (ML09)
    │       └──► Backdoor inference container
    │
    ├── CI/CD Pipeline Compromise
    │       └──► Inject backdoor into next training run (ML02)
    │       └──► Deploy malicious model version
    │
    └── DoS via resource exhaustion (LLM10)
```

---

## Related

- [SAIF-01 — Data](../SAIF-01-DATA/README.md) — data stored and processed in this infrastructure
- [SAIF-03 — Model](../SAIF-03-MODEL/README.md) — model artifacts stored and served here
- [ML05 — Model Theft](../../00-OWASP-ML-TOP10/ML05/README.md)
- [ML06 — ML Supply Chain Attacks](../../00-OWASP-ML-TOP10/ML06/README.md)
- [ML09 — Output Integrity Attack](../../00-OWASP-ML-TOP10/ML09/README.md)
- [ML10 — Model Poisoning](../../00-OWASP-ML-TOP10/ML10/README.md)
- [LLM10 — Unbounded Consumption](../../01-OWASP-LLM-TOP10/LLM10/README.md)
- [Fickling — Pickle analysis](https://github.com/trailofbits/fickling)
- [ModelScan](https://github.com/protectai/modelscan)