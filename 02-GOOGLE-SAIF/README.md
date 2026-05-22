# 02 — Google Secure AI Framework (SAIF)

> **Google's Secure AI Framework (SAIF)**
> Rewritten for the [Offensive-AI Framework](https://github.com/hardsoftsecurity/Offensive-AI) — offensive perspective, red team focus.

---

## Overview

Google's Secure AI Framework (SAIF) provides actionable principles for securing the entire AI pipeline — from data collection through model deployment and application integration. While OWASP provides targeted, technical checklists of vulnerabilities, SAIF takes a broader approach: it maps the full AI system architecture, identifies where risks are introduced, where they can be exploited, and who is responsible for mitigating them.

For red teamers, SAIF is the defender's blueprint — and therefore the attacker's map. Understanding what a well-secured AI system *should* look like reveals exactly where gaps are most likely to exist.

---

## SAIF vs OWASP

| Aspect | OWASP ML / LLM Top 10 | Google SAIF |
|---|---|---|
| **Approach** | Targeted vulnerability checklist | Holistic lifecycle framework |
| **Scope** | Specific attack categories | Full AI pipeline architecture |
| **Output** | List of risks | Risk map: introduction → exposure → mitigation |
| **Responsibility** | Not assigned | Assigned to Model Creator or Model Consumer |
| **Offensive use** | Attack technique reference | Attack surface mapping |

---

## SAIF Architecture — Four Areas

SAIF organizes the AI system into four areas, each comprising multiple components. Every risk is introduced, exposed, or mitigated within one or more of these areas.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SAIF Architecture                            │
├──────────────┬───────────────────────┬──────────────┬──────────────┤
│     DATA     │    INFRASTRUCTURE     │    MODEL     │ APPLICATION  │
├──────────────┼───────────────────────┼──────────────┼──────────────┤
│ Data Sources │ Model Frameworks      │ Model        │ Applications │
│              │ & Code                │              │              │
│ Data         │                       │ Input        │ Agents       │
│ Filtering &  │ Training, Tuning      │ Handling     │              │
│ Processing   │ & Evaluation          │              │ Plugins      │
│              │                       │ Output       │              │
│ Training     │ Data & Model          │ Handling     │              │
│ Data         │ Storage               │              │              │
│              │                       │              │              │
│              │ Model Serving         │              │              │
└──────────────┴───────────────────────┴──────────────┴──────────────┘
```

---

## SAIF Risk Responsibility Model

SAIF assigns mitigation responsibility to one of two parties:

| Party | Description | Example |
|---|---|---|
| **Model Creator** | The organization that develops and trains the model | Google (Gemini), OpenAI (GPT), Meta (Llama) |
| **Model Consumer** | The organization that deploys the model in an application | A company building a chatbot on top of an API |

This distinction matters offensively: controls assigned to the model creator cannot be bypassed at the application layer, but controls assigned to the model consumer are only as strong as the consumer's implementation.

---

## SAIF Risks — Full List

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

The [Risk Map](https://saif.google/secure-ai-framework/saif-map) is the central SAIF component encompassing information about components, risks, and controls in a single place:

![The Risk Map is the central SAIF component encompassing information about components, risks, and controls in a single place.](https://hardsoftsecurity.es/wp-content/uploads/2026/05/riskmap.png)

---

## SAIF Controls — Key Examples

| Control | Risks Mitigated | Responsible Party |
|---|---|---|
| Input Validation and Sanitization | Prompt Injection | Model Creator, Model Consumer |
| Output Validation and Sanitization | Prompt Injection, Rogue Actions, Sensitive Data Disclosure, Inferred Sensitive Data | Model Creator, Model Consumer |
| Adversarial Training and Testing | Model Evasion, Prompt Injection, Sensitive Data Disclosure, Inferred Sensitive Data, Insecure Model Output | Model Creator, Model Consumer |

We can find further information about the controls on the official documentation from [SAIF official website](https://saif.google/secure-ai-framework/controls).

---

## SAIF Risk Map — Offensive Use

The SAIF Risk Map tracks each risk across three dimensions:

| Dimension | Description | Offensive Value |
|---|---|---|
| **Risk Introduction** | Where in the pipeline the risk is created | Identifies the attack entry point |
| **Risk Exposure** | Where the risk can be exploited | Identifies the attack surface |
| **Risk Mitigation** | Where controls can be applied | Identifies gaps when controls are absent or weak |

Understanding this three-stage model allows red teamers to reason about *where* to introduce a payload, *where* it will take effect, and *what* defenses need to be bypassed.

---

## Structure

```
02-GOOGLE-SAIF/
├── README.md                   ← This file
├── SAIF-01-DATA/               ← Data area: sources, filtering, training data
│   └── README.md
├── SAIF-02-INFRASTRUCTURE/     ← Infrastructure: storage, training, serving
│   └── README.md
├── SAIF-03-MODEL/              ← Model: input handling, model, output handling
│   └── README.md
└── SAIF-04-APPLICATION/        ← Application: apps, agents, plugins
    └── README.md
```

---

## Cross-Framework Reference

| SAIF Area | SAIF Risks | OWASP ML | OWASP LLM |
|---|---|---|---|
| Data | Data Poisoning, Unauthorized Training Data, Excessive Data Handling | ML02, ML08 | LLM04 |
| Infrastructure | Model Source Tampering, Model Exfiltration, Model Deployment Tampering, Denial of ML Service | ML05, ML06, ML09, ML10 | LLM03, LLM10 |
| Model | Model Reverse Engineering, Model Evasion, Prompt Injection, Sensitive Data Disclosure, Inferred Sensitive Data | ML01, ML03, ML04, ML05 | LLM01, LLM02 |
| Application | Insecure Integrated Component, Insecure Model Output, Rogue Actions | — | LLM03, LLM05, LLM06 |

---

## Related Resources

| Resource | URL |
|---|---|
| SAIF Official Site | https://saif.google |
| SAIF Risk Map | https://saif.google/risk-map |
| SAIF PDF (original) | https://kstatic.googleusercontent.com/files/94be2c26edc933c9b9f4f401472af79d03d4ac65c29b550aebb66a57c7b2c01cfcbc7636eec6c55889f797e6c41b09011672354fe0600edf836b4ec38eb5a14c |
| Coalition for Secure AI (CoSAI) | https://www.coalitionforsecureai.org |
| NIST AI RMF | https://airc.nist.gov/RMF |

---

*Part of the [Offensive-AI Framework](https://github.com/hardsoftsecurity/Offensive-AI)*
*Source: Google Secure AI Framework (SAIF) — referenced for educational and research purposes.*