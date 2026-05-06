# 08 — Resources

> Curated references, research, and learning materials for AI Red Teaming and offensive security against LLM-based systems.

---

## Structure

```
08-RESOURCES/
├── papers/          # Academic and industry research papers
├── frameworks/      # Standards, guidelines, and taxonomies
├── blogs/           # Practitioner blogs and write-ups
├── courses/         # Training and certification resources
├── communities/     # Forums, groups, and conferences
└── datasets/        # Datasets for AI security research
```

---

## Standards & Frameworks

| Resource | Description | Link |
|---|---|---|
| OWASP LLM Top 10 | The canonical list of LLM application vulnerabilities | https://owasp.org/www-project-top-10-for-large-language-model-applications/ |
| MITRE ATLAS | Adversarial Threat Landscape for AI Systems — ATT&CK for ML | https://atlas.mitre.org/ |
| NIST AI RMF | National Institute of Standards and Technology AI Risk Management Framework | https://airc.nist.gov/RMF |
| OWASP AI Exchange | Living document on AI security threats and countermeasures | https://owaspai.org/ |
| EU AI Act | Regulatory framework with security implications for AI systems | https://artificialintelligenceact.eu/ |

---

## Research Papers

### Prompt Injection & Jailbreaking

| Title | Authors | Year | Notes |
|---|---|---|---|
| Universal and Transferable Adversarial Attacks on Aligned Language Models | Zou et al. | 2023 | GCG attack; automated suffix generation |
| Jailbroken: How Does LLM Safety Training Fail? | Wei et al. | 2023 | Taxonomy of jailbreak failure modes |
| Many-shot Jailbreaking | Anthropic | 2024 | Long-context exploitation |
| Prompt Injection Attacks Against GPT-3 | Perez & Ribeiro | 2022 | Original prompt injection framing |

### Model Extraction & Privacy

| Title | Authors | Year | Notes |
|---|---|---|---|
| Stealing Machine Learning Models via Prediction APIs | Tramèr et al. | 2016 | Foundational model extraction work |
| Extracting Training Data from Large Language Models | Carlini et al. | 2021 | Membership inference and data leakage |
| Quantifying Privacy Risks of Masked Language Models | Jagannatha et al. | 2021 | Privacy leakage in BERT-style models |

### Adversarial ML

| Title | Authors | Year | Notes |
|---|---|---|---|
| Intriguing Properties of Neural Networks | Szegedy et al. | 2014 | Adversarial examples — original paper |
| Explaining and Harnessing Adversarial Examples | Goodfellow et al. | 2015 | FGSM attack |
| Certified Defenses for Adversarial Patches | Levine & Feizi | 2020 | Patch-based adversarial attacks |

### Supply Chain & Agent Attacks

| Title | Authors | Year | Notes |
|---|---|---|---|
| Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection | Greshake et al. | 2023 | Indirect injection via external data sources |
| AgentDojo: A Dynamic Environment to Evaluate Attacks and Defenses for LLM Agents | Debenedetti et al. | 2024 | Benchmark for agent exploitation |

---

## Books

| Title | Author(s) | Notes |
|---|---|---|
| The Alignment Problem | Brian Christian | Foundational AI safety context |
| Adversarial Machine Learning | Vorobeychik & Kantarcioglu | Textbook-level adversarial ML coverage |
| Security and AI: A Practical Guide | Various | Red team AI deployment considerations |
| Hacking the AI | Tariq & others | Practitioner-focused LLM offensive techniques |

---

## Blogs & Write-Ups

| Author / Source | Focus | URL |
|---|---|---|
| LLM Security (Johann Rehberger) | Prompt injection, agent attacks | https://llmsecurity.net |
| Simon Willison's Blog | LLM prompt injection research | https://simonwillison.net |
| Embrace The Red | Jailbreaking, red teaming LLMs | https://embracethered.com |
| AI Safety Newsletter | Safety & alignment news | https://newsletter.safe.ai |
| Joseph Thacker (rez0) | AI security practitioner write-ups | https://josephthacker.com |
| Kai Greshake | Indirect prompt injection research | https://kai-greshake.de |

---

## Tools & Repositories

| Tool | Purpose | Link |
|---|---|---|
| Garak | LLM vulnerability scanner | https://github.com/NVIDIA/garak |
| PyRIT | Microsoft's Python Red-teaming and Iterative Testing framework | https://github.com/Azure/PyRIT |
| PurpleLlama | Meta's LLM safety evaluation suite | https://github.com/meta-llama/PurpleLlama |
| PromptBench | Adversarial robustness benchmark for LLMs | https://github.com/microsoft/promptbench |
| FuzzyAI | AI fuzzing framework | https://github.com/cyberark/FuzzyAI |
| LLMFuzzer | Fuzzing LLM APIs for prompt injection | https://github.com/mnns/LLMFuzzer |
| Pliny | Jailbreak and adversarial prompt library | https://github.com/elder-plinius |

---

## Courses & Training

| Platform | Course | Level |
|---|---|---|
| Coursera | AI Security and Privacy (various) | Beginner–Intermediate |
| SANS | SEC595: Applied Data Science and AI/ML for Cybersecurity | Intermediate–Advanced |
| Lakera | Prompt Injection course (free) | Beginner |
| Learn Prompting | Adversarial Prompting module | Beginner |
| Nvidia DLI | Trustworthy AI course | Intermediate |
| HackAPrompt (competition) | Hands-on prompt injection challenges | All levels |

---

## Conferences & Communities

### Conferences

| Event | Focus | URL |
|---|---|---|
| DEF CON AI Village | Offensive AI & red teaming | https://aivillage.org |
| BlackHat AI Summit | Enterprise AI security | https://blackhat.com |
| IEEE S&P / CCS / USENIX Security | Academic adversarial ML papers | Various |
| NeurIPS / ICML | ML research with security tracks | Various |

### Communities

| Community | Platform | URL |
|---|---|---|
| AI Village | Discord + Slack | https://aivillage.org |
| OWASP AI Security | Slack (OWASP workspace) | https://owasp.org/slack/invite |
| Lakera Discord | Discord | https://discord.gg/lakera |
| EleutherAI | Discord | https://discord.gg/eleutherai |

---

## Datasets

| Dataset | Description | Link |
|---|---|---|
| HarmBench | Standardized harmful behavior benchmark for LLMs | https://github.com/centerforaisafety/HarmBench |
| JailbreakBench | Jailbreak attempt benchmark | https://github.com/JailbreakBench/jailbreakbench |
| AdvGLUE | Adversarial NLU benchmark | https://adversarialglue.github.io |
| ToxiGen | Large-scale dataset of toxic language generation | https://github.com/microsoft/TOXIGEN |
| Prompt Injection Dataset | Collection of prompt injection examples | Community-curated |

---

## CTF & Practice Labs

| Resource | Description | Link |
|---|---|---|
| Gandalf (Lakera) | Progressive prompt injection challenge | https://gandgandalf.lakera.ai |
| HackAPrompt | Official prompt injection competition archive | https://github.com/trigaten/Hack-a-Prompt |
| PortSwigger Web Security Academy | LLM attack labs (2024+) | https://portswigger.net/web-security/llm-attacks |
| Crucible (Dreadnode) | AI red team challenges | https://crucible.dreadnode.io |
| AI Goat | Deliberately vulnerable LLM application | https://github.com/dhammon/ai-goat |

---

## Contributing

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) to add resources. When submitting a new entry:

- Verify the link is active.
- Add a short, factual description.
- Place it under the most relevant section.
- For papers, include authors and year.

---

*Part of the [Offensive-AI](https://github.com/hardsoftsecurity/Offensive-AI) framework.*