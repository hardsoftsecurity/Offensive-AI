# Offensive-AI Framework

> A structured, hands-on framework for AI red teaming, adversarial machine learning, and LLM security research — mapped to OWASP ML Top 10, OWASP LLM Top 10, and Google's Secure AI Framework (SAIF).

---

## About

The **Offensive-AI Framework** is an open knowledge base and practical reference for security professionals, red teamers, and researchers working at the intersection of artificial intelligence and offensive security.

The field of AI security is rapidly evolving. Models are being deployed as autonomous agents, integrated into critical infrastructure, and trusted to make consequential decisions. This framework documents the attack techniques, vulnerabilities, and research needed to stress-test these systems — before adversaries do.

The framework is built on three industry-standard foundations:

- **OWASP ML Security Top 10** — adversarial risks across the machine learning lifecycle
- **OWASP LLM Top 10** — security risks specific to Large Language Model applications
- **Google Secure AI Framework (SAIF)** — a lifecycle-based model for understanding the full AI attack surface

Each section maps offensive techniques to these frameworks, providing structured payloads, lab walkthroughs, tools, and references for practitioners.

---

## Framework Foundations

### OWASP ML Security Top 10

The OWASP ML Top 10 covers the most critical security risks across the full machine learning pipeline — from data collection and training to model deployment and inference. These risks apply to classical ML systems (Naive Bayes, SVMs, gradient boosting) and deep learning alike.

| ID | Risk |
|---|---|
| ML01 | Input Manipulation Attack |
| ML02 | Data Poisoning Attack |
| ML03 | Model Inversion Attack |
| ML04 | Membership Inference Attack |
| ML05 | Model Theft |
| ML06 | ML Supply Chain Attacks |
| ML07 | Transfer Learning Attack |
| ML08 | Model Skewing |
| ML09 | Output Integrity Attack |
| ML10 | Model Poisoning |

### OWASP LLM Top 10

The OWASP LLM Top 10 focuses on security risks that emerge specifically from the deployment and operation of Large Language Model applications — including risks unique to generative AI such as prompt injection, hallucination, and excessive agency.

| ID | Risk |
|---|---|
| LLM01 | Prompt Injection |
| LLM02 | Sensitive Information Disclosure |
| LLM03 | Supply Chain |
| LLM04 | Data and Model Poisoning |
| LLM05 | Improper Output Handling |
| LLM06 | Excessive Agency |
| LLM07 | System Prompt Leakage |
| LLM08 | Vector and Embedding Weaknesses |
| LLM09 | Misinformation |
| LLM10 | Unbounded Consumption |

### Google Secure AI Framework (SAIF)

Google's SAIF, introduced in 2023, provides a lifecycle-based conceptual framework for securing AI systems across their full development and deployment lifecycle. Rather than a checklist, SAIF describes six interdependent elements that together define the AI security posture of an organization.

From an offensive perspective, SAIF defines the defender's model — understanding it reveals where gaps are most likely to exist.

| # | SAIF Element | Description | Offensive Relevance |
|---|---|---|---|
| 1 | **Expand security foundations** | Extend existing controls (supply chain, access control, input validation) to AI systems | Gaps in adapted controls are primary attack vectors — prompt injection, dependency confusion |
| 2 | **Extend detection and response** | Monitor AI inputs/outputs for anomalies; integrate AI into threat intelligence | Evasion of detection is a key attacker goal — low-and-slow poisoning, distribution-preserving attacks |
| 3 | **Automate defenses** | Use AI itself to keep pace with AI-powered threats | AI-generated attack automation and adversarial prompt generation outpace manual defenses |
| 4 | **Harmonize platform controls** | Consistent security controls across AI infrastructure and deployment environments | Inconsistency creates gaps — dev/staging environments as pivot points |
| 5 | **Adapt controls to address AI risks** | Develop controls specific to AI: model signing, data provenance, output validation | Missing AI-specific controls (no model watermarking, no output sanitization) are direct targets |
| 6 | **Contextualize AI risks in business processes** | End-to-end risk assessment including data lineage, operational behavior, and downstream impact | Business context determines impact severity — same technique has different consequences in different deployments |

---

## Repository Structure

```
Offensive-AI/
│
├── 00-OWASP-ML-TOP10/          # OWASP ML Security Top 10
│   ├── README.md
│   ├── ML01/                   # Input Manipulation Attack
│   ├── ML02/                   # Data Poisoning Attack
│   ├── ML03/                   # Model Inversion Attack
│   ├── ML04/                   # Membership Inference Attack
│   ├── ML05/                   # Model Theft
│   ├── ML06/                   # ML Supply Chain Attacks
│   ├── ML07/                   # Transfer Learning Attack
│   ├── ML08/                   # Model Skewing
│   ├── ML09/                   # Output Integrity Attack
│   └── ML10/                   # Model Poisoning
│
├── 01-OWASP-LLM-TOP10/         # OWASP LLM Top 10
│   ├── README.md
│   ├── LLM01/                  # Prompt Injection
│   ├── LLM02/                  # Sensitive Information Disclosure
│   ├── LLM03/                  # Supply Chain
│   ├── LLM04/                  # Data and Model Poisoning
│   ├── LLM05/                  # Improper Output Handling
│   ├── LLM06/                  # Excessive Agency
│   ├── LLM07/                  # System Prompt Leakage
│   ├── LLM08/                  # Vector and Embedding Weaknesses
│   ├── LLM09/                  # Misinformation
│   └── LLM10/                  # Unbounded Consumption
│
├── 02-ATTACK-PLAYBOOKS/              # Attack techniques and payload libraries
│   ├── prompt-injection/
│   ├── adversarial-examples/
│   ├── data-poisoning/
│   └── model-extraction/
│
├── 03-PAYLOADS/                    # Ready to go payloads
│   ├── ML01-input-manipulation/
│   ├── ML02-data-poisoning/
│   └── ...
│
├── 04-TOOLS/                   # Tools and scripts for AI red teaming
│
├── 05-CHECKLISTS/             # Ready to follow checklists
│
├── 06-LABS/            # Resolved labs to test payloads
│
├── 07-CASE-STUDIES/                     # Well known case studies based on top 10 vulns
│
└── 08-RESOURCES/               # Research papers, books, courses, datasets
```

---

## Attack Surface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Attack Surface                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Data Layer  │ Model Layer  │  App Layer   │  Infrastructure    │
├──────────────┼──────────────┼──────────────┼────────────────────┤
│ ML02         │ ML01         │ LLM01        │ ML06               │
│ Data         │ Input        │ Prompt       │ Supply Chain       │
│ Poisoning    │ Manipulation │ Injection    │                    │
│              │              │              │                    │
│ LLM04        │ ML03         │ LLM05        │ LLM03              │
│ Training     │ Model        │ Output       │ LLM Supply         │
│ Poisoning    │ Inversion    │ Handling     │ Chain              │
│              │              │              │                    │
│ ML08         │ ML04         │ LLM06        │ LLM08              │
│ Model        │ Membership   │ Excessive    │ RAG / Vector       │
│ Skewing      │ Inference    │ Agency       │ Store              │
│              │              │              │                    │
│              │ ML05         │ LLM07        │                    │
│              │ Model        │ System       │                    │
│              │ Theft        │ Prompt Leak  │                    │
│              │              │              │                    │
│              │ ML07/ML09    │ LLM02        │                    │
│              │ Transfer /   │ Info         │                    │
│              │ Output       │ Disclosure   │                    │
│              │              │              │                    │
│              │ ML10         │ LLM09/LLM10  │                    │
│              │ Model        │ Misinfo /    │                    │
│              │ Poisoning    │ DoS          │                    │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

---

## AI Red Team Attack Chain

A typical AI red team engagement follows this progression:

```
1. RECONNAISSANCE
   └── LLM07 — Extract system prompt to enumerate capabilities
   └── LLM02 — Probe model data access and knowledge boundaries

2. INITIAL ACCESS
   └── LLM01 — Prompt injection (direct or indirect via external content)
   └── LLM03 / ML06 — Supply chain compromise (packages, model hubs, plugins)

3. PRIVILEGE ESCALATION
   └── LLM06 — Abuse excessive agency over connected tools and APIs
   └── LLM05 — Exploit unsanitized output consumed by backend systems

4. DATA EXFILTRATION
   └── LLM02 — Extract sensitive context from the model's context window
   └── ML03  — Model inversion to reconstruct training data
   └── ML04  — Membership inference to confirm training data presence
   └── ML05  — Model theft via systematic API extraction

5. PERSISTENCE
   └── ML02 / LLM04 — Poison training data to implant backdoors
   └── ML07  — Weaponize transfer learning with a poisoned base model
   └── LLM08 — Poison the RAG knowledge base for stored indirect injection

6. IMPACT
   └── ML01  — Adversarial evasion at inference time
   └── LLM09 — Generate targeted misinformation at scale
   └── LLM10 — Denial of service / financial cost inflation
   └── ML08 / ML09 — Skew or tamper with model outputs
```

---

## Cross-Framework Mapping

| Technique | OWASP ML | OWASP LLM | SAIF Element |
|---|---|---|---|
| Adversarial examples / evasion | ML01 | LLM01 | 1, 5 |
| Data / training poisoning | ML02 | LLM04 | 1, 5, 6 |
| Model inversion | ML03 | LLM02 | 5 |
| Membership inference | ML04 | LLM02 | 5 |
| Model theft / extraction | ML05 | LLM10 | 4, 5 |
| Supply chain attacks | ML06 | LLM03 | 1, 4 |
| Transfer learning attacks | ML07 | LLM04 | 1, 5 |
| Feedback loop manipulation | ML08 | LLM04 | 2, 5 |
| Output tampering | ML09 | LLM05 | 2, 5 |
| Direct parameter poisoning | ML10 | LLM04 | 4, 5 |
| Prompt injection | — | LLM01 | 1, 5 |
| System prompt leakage | — | LLM07 | 5 |
| Excessive agency exploitation | — | LLM06 | 5, 6 |
| RAG / embedding attacks | — | LLM08 | 5 |
| DoS / unbounded consumption | — | LLM10 | 2, 4 |

---

## Labs

Hands-on walkthroughs with step-by-step instructions and code:

| Lab | Category | Description |
|---|---|---|
| [Input Manipulation](./03-LABS/ML01-input-manipulation/) | ML01 | Evade a Naive Bayes spam classifier via rephrasing and overpowering |
| [Data Poisoning](./03-LABS/ML02-data-poisoning/) | ML02 | Flip classifier predictions by injecting mislabeled training entries |
| *More coming soon* | | |

---

## Tools

| Tool | Purpose | Category |
|---|---|---|
| [Garak](https://github.com/NVIDIA/garak) | LLM vulnerability scanner | LLM |
| [PyRIT](https://github.com/Azure/PyRIT) | Python red-teaming and iterative testing | LLM |
| [ART](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Adversarial attacks and defenses for ML | ML |
| [Fickling](https://github.com/trailofbits/fickling) | Pickle file analysis and manipulation | ML / Supply Chain |
| [ModelScan](https://github.com/protectai/modelscan) | Detect malicious code in model artifacts | ML / Supply Chain |
| [PurpleLlama](https://github.com/meta-llama/PurpleLlama) | LLM safety evaluation suite | LLM |
| [BackdoorBench](https://github.com/SCLBD/BackdoorBench) | Backdoor attack and defense benchmark | ML |
| [ML Privacy Meter](https://github.com/privacytrustlab/ml_privacy_meter) | Membership inference and privacy auditing | ML |

See [08-RESOURCES](./08-RESOURCES/README.md) for the full tool and resource list.

---

## Key Resources

| Resource | URL |
|---|---|
| OWASP ML Security Top 10 | https://owasp.org/www-project-machine-learning-security-top-10/ |
| OWASP LLM Top 10 | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| Google SAIF | https://saif.google |
| MITRE ATLAS | https://atlas.mitre.org/ |
| AI Vulnerability Database (AVID) | https://avidml.org/ |
| NIST AI Risk Management Framework | https://airc.nist.gov/RMF |
| Google AI Red Team Paper | https://services.google.com/fh/files/blogs/google_ai_red_team_digital_final.pdf |
| Embrace The Red | https://embracethered.com |
| LLM Security (Johann Rehberger) | https://llmsecurity.net |

---

## Status

This framework is actively under development.

| Section | Status |
|---|---|
| 00-OWASP-ML-TOP10 | 🟡 In progress |
| 01-OWASP-LLM-TOP10 | 🟡 In progress |
| 02-TECHNIQUES | 🟡 In progress |
| 03-LABS | 🟡 In progress |
| 04-TOOLS | 🔴 Planned |
| 05-MITRE-ATLAS | 🔴 Planned |
| 06-CASE-STUDIES | 🔴 Planned |
| 07-CTF | 🔴 Planned |
| 08-RESOURCES | 🟢 Available |

Contributions, issues, and pull requests are welcome.

---

## Author

**David De Maya Merras** — Cyber Security Analyst with a focus on offensive security.

- Blog: [hardsoftsecurity.es](https://hardsoftsecurity.es)
- GitHub: [@hardsoftsecurity](https://github.com/hardsoftsecurity)

---

## License

This project is licensed under the [MIT License](./LICENSE).

Content derived from OWASP projects is used under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Google SAIF is referenced for educational and research purposes.

---

*Break. Build. Teach. Innovate. Repeat.*