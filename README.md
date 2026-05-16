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

Google's SAIF, introduced in 2023, provides a holistic framework for securing the entire AI pipeline — from data collection through model deployment and application integration. Where OWASP provides targeted vulnerability checklists, SAIF maps the full AI system architecture and identifies where each risk is **introduced**, where it can be **exploited**, and who is **responsible** for mitigating it.

From an offensive perspective, SAIF is the defender's blueprint — understanding it reveals exactly where gaps are most likely to exist in a target AI deployment.

#### SAIF Architecture — Four Areas

| Area | Components | Offensive Focus |
|---|---|---|
| **Data** | Data Sources, Filtering & Processing, Training Data | Highest-persistence attacks — poisoning here propagates into every downstream component |
| **Infrastructure** | Model Frameworks & Code, Training & Evaluation, Data & Model Storage, Model Serving | Platform-level compromise — MLOps misconfigs, model artifact tampering, CI/CD poisoning |
| **Model** | Input Handling, Model, Output Handling | Most accessible surface — exploitable via API alone, no infrastructure access required |
| **Application** | Applications, Agents, Plugins | AI meets traditional web security — injection via output, excessive agency, supply chain |

#### SAIF Risks — Offensive Mapping

| # | Risk | Area | OWASP Mapping |
|---|---|---|---|
| 1 | Data Poisoning | Data | ML02, LLM04 |
| 2 | Unauthorized Training Data | Data | — |
| 3 | Model Source Tampering | Infrastructure | ML10, LLM04 |
| 4 | Excessive Data Handling | Data | — |
| 5 | Model Exfiltration | Infrastructure / Model | ML05 |
| 6 | Model Deployment Tampering | Infrastructure | ML06, ML09 |
| 7 | Denial of ML Service | Infrastructure / Application | LLM10 |
| 8 | Model Reverse Engineering | Model | ML03, ML05 |
| 9 | Insecure Integrated Component | Application | LLM03 |
| 10 | Prompt Injection | Model / Application | LLM01 |
| 11 | Model Evasion | Model | ML01 |
| 12 | Sensitive Data Disclosure | Model / Application | LLM02, ML03, ML04 |
| 13 | Inferred Sensitive Data | Model | ML03, ML04 |
| 14 | Insecure Model Output | Application | LLM05 |
| 15 | Rogue Actions | Application | LLM06 |

#### SAIF Responsibility Model

SAIF assigns each control to one of two parties — a distinction that directly affects red team scope:

| Party | Who They Are | Implication |
|---|---|---|
| **Model Creator** | The organization that develops and trains the model | Controls at this layer cannot be bypassed at the application level |
| **Model Consumer** | The organization deploying the model in an application | Controls here are only as strong as the consumer's implementation — the most common gap |

> See [02-GOOGLE-SAIF](./02-GOOGLE-SAIF/README.md) for the full area breakdown, risk details, and offensive techniques per component.

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
├── 02-GOOGLE-SAIF/                    # Google Secure AI Framework
|
|
├── 03-ATTACK-PLAYBOOKS/              # Attack techniques and payload libraries
│   ├── prompt-injection/
│   ├── adversarial-examples/
│   ├── data-poisoning/
│   └── model-extraction/
│
├── 04-PAYLOADS/                    # Ready to go payloads
│   ├── ML01-input-manipulation/
│   ├── ML02-data-poisoning/
│   └── ...
│
├── 05-TOOLS/                   # Tools and scripts for AI red teaming
│
├── 06-CHECKLISTS/             # Ready to follow checklists
│
├── 07-LABS/            # Resolved labs to test payloads
│
├── 08-CASE-STUDIES/                     # Well known case studies based on top 10 vulns
│
└── 09-RESOURCES/               # Research papers, books, courses, datasets
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
| [Input Manipulation](./00-OWASP-ML-TOP10/ML01-Input-Manipulation-Attack/lab/) | ML01 | Evade a Naive Bayes spam classifier via rephrasing and overpowering |
| [Data Poisoning](./00-OWASP-ML-TOP10/ML02-Data-Poisoning-Attack/00-LAB-POISONING-MISCLASSIFICATION/) | ML02 | Flip classifier predictions by injecting mislabeled training entries |
| [Backdoor implantation](./00-OWASP-ML-TOP10/ML02-Data-Poisoning-Attack/01-LAB-POISONING-BACKDOOR/) | ML02 | Backdoor implantation · Trigger-phrase poisoning · Naive Bayes classifier |
| [LLM Fingerprinting](./01-OWASP-LLM-TOP10/LLM07-System-Prompt-Leakage/00-LAB-LLM-Fingerprinting/) | LLM07 | Reconnaissance · Model Identification · Behavioral Fingerprinting |
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

See [09-RESOURCES](./09-RESOURCES/README.md) for the full tool and resource list.

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