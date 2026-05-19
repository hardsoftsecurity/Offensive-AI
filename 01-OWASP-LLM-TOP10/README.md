# 01 — OWASP LLM Security Top 10

> **OWASP Top 10 for LLM Applications (2025 Edition)**
> Rewritten for the [Offensive-AI Framework](https://github.com/hardsoftsecurity/Offensive-AI) — offensive perspective, red team focus.

---

## Overview

The OWASP LLM Top 10 identifies the most critical security risks in applications built on Large Language Models. Unlike the ML Top 10 (which covers the full ML lifecycle), this list focuses specifically on risks that emerge from the unique properties of LLMs: their generative nature, their instruction-following behavior, their integration with external tools and data sources, and the difficulty of fully constraining their outputs.

This section maps each risk to offensive techniques, attack primitives, and the defender gaps that make exploitation possible.

---

## The Top 10

| ID | Vulnerability | Offensive Relevance |
|---|---|---|
| [LLM01-Prompt-Injection](./LLM01-Prompt-Injection/) | Prompt Injection | Manipulate model behavior via crafted inputs — direct or indirect |
| [LLM02-Sensitive-Information-Disclosure](./LLM02-Sensitive-Information-Disclosure/) | Sensitive Information Disclosure | Extract confidential data, training details, or system context |
| [LLM03-Supply-Chain](./LLM03-Supply-Chain/) | Supply Chain | Compromise training data, base models, plugins, or integrations |
| [LLM04-Data-and-Model-Poisoning](./LLM04-Data-and-Model-Poisoning/) | Data and Model Poisoning | Inject biases or backdoors into the LLM training pipeline |
| [LLM05-Improper-Output-Handling](./LLM05-Improper-Output-Handling/) | Improper Output Handling | Exploit unsanitized LLM output for XSS, SQLi, or command injection |
| [LLM06-Excessive-Agency](./LLM06-Excessive-Agency/) | Excessive Agency | Abuse over-privileged LLM access to connected systems |
| [LLM07-System-Prompt-Leakage](./LLM07-System-Prompt-Leakage/) | System Prompt Leakage | Extract system instructions to enable advanced attack chains |
| [LLM08-Misinformation](./LLM08-Misinformation/) | Vector and Embedding Weaknesses | Exploit RAG pipelines via poisoned embeddings or unauthorized access |
| [LLM09-Vector-and-Embedding-Weaknesses](./LLM09-Vector-and-Embedding-Weaknesses/) | Misinformation | Exploit hallucinations for harmful or security-relevant false outputs |
| [LLM10-Unbounded-Consumption](./LLM10-Unbounded-Consumption/) | Unbounded Consumption | DoS via resource-exhausting inputs; model theft via bulk extraction |

---

## Attack Surface Map

```
                        ┌─────────────────────────────────────┐
                        │         LLM Application             │
                        │                                      │
  User Input ──────────►│  System Prompt  ◄──── LLM07         │
  (LLM01 Direct)        │       │                             │
                        │       ▼                             │
  External Data ───────►│    LLM Core  ◄──── LLM04 / LLM03   │
  (LLM01 Indirect)      │       │                             │
                        │       ▼                             │
  RAG / Embeddings ────►│   Output Layer  ──── LLM05          │
  (LLM08)               │       │                             │
                        │       ▼                             │
                        │  Connected Tools ◄─── LLM06         │
                        │  (APIs, DBs, Files)                 │
                        └──────────────┬──────────────────────┘
                                       │
                            LLM02 (data leak)
                            LLM09 (misinformation)
                            LLM10 (resource exhaustion)
```

---

## LLM vs ML Top 10 — Key Differences

| Aspect | OWASP ML Top 10 | OWASP LLM Top 10 |
|---|---|---|
| **Scope** | Full ML lifecycle | LLM applications specifically |
| **Primary attack surface** | Training pipelines, model parameters | Prompts, outputs, integrations |
| **Unique risks** | Model extraction, membership inference | Prompt injection, excessive agency, hallucination |
| **Overlap** | Data poisoning (ML02 ↔ LLM04), Supply chain (ML06 ↔ LLM03) | — |

---

## Attack Phase Reference

| Phase | Relevant Risks |
|---|---|
| **Reconnaissance** | LLM07 (system prompt leak), LLM02 (info disclosure) |
| **Initial Access** | LLM01 (prompt injection), LLM03 (supply chain) |
| **Privilege Escalation** | LLM06 (excessive agency), LLM01 (indirect injection) |
| **Data Exfiltration** | LLM02, LLM07, LLM08 |
| **Impact** | LLM05 (output injection), LLM09 (misinformation), LLM10 (DoS) |
| **Persistence** | LLM04 (model/data poisoning), LLM03 (supply chain backdoor) |

---

## Structure

```
01-OWASP-LLM-TOP10/
├── README.md           ← This file
├── LLM01-Prompt-Injection/              ← Prompt Injection
│   └── README.md
├── LLM02-Sensitive-Information-Disclosure/              ← Sensitive Information Disclosure
│   └── README.md
├── LLM03-Supply-Chain/              ← Supply Chain
│   └── README.md
├── LLM04-Data-and-Model-Poisoning/              ← Data and Model Poisoning
│   └── README.md
├── LLM05-Improper-Output-Handling/              ← Improper Output Handling
│   └── README.md
├── LLM06-Excessive-Agency/              ← Excessive Agency
│   └── README.md
├── LLM07-System-Prompt-Leakage/              ← System Prompt Leakage
│   └── README.md
├── LLM08-Misinformation/              ← Vector and Embedding Weaknesses
│   └── README.md
├── LLM09-Vector-and-Embedding-Weaknesses/              ← Misinformation
│   └── README.md
└── LLM10-Unbounded-Consumption/              ← Unbounded Consumption
    └── README.md
```

---

## Related Resources

| Resource | URL |
|---|---|
| OWASP Top 10 for LLM Applications (official) | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| MITRE ATLAS | https://atlas.mitre.org/ |
| OWASP ML Security Top 10 | https://owasp.org/www-project-machine-learning-security-top-10/ |
| Lakera — Prompt Injection Guide | https://www.lakera.ai/blog/prompt-injection-attacks |
| LLM Security (Johann Rehberger) | https://llmsecurity.net |
| Embrace The Red | https://embracethered.com |

---

*Part of the [Offensive-AI Framework](https://github.com/hardsoftsecurity/Offensive-AI)*
*Source: OWASP Top 10 for LLM Applications 2025 — CC BY-SA 4.0*