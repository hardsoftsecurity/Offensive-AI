# LLM03 — Supply Chain

> **OWASP Top 10 for LLM Applications | 2025**

## Description

LLM supply chain vulnerabilities cover any system, component, or data source involved in building, deploying, or operating an LLM application. This includes the training data, pre-trained base models sourced from third parties, fine-tuning pipelines, plugins and integrations, and the infrastructure that hosts and serves the model.

Compromising any link in the supply chain can have downstream impact on every application and user that depends on it — often without the victim organization's knowledge.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 4 — Moderate | Depends on the target link; open-source ecosystems and model hubs are wide attack surfaces |
| Detectability | 2 — Difficult | Supply chain compromises can persist undetected for extended periods |
| Technical Complexity | 4 — Moderate | Varies by target: data tampering vs. model hub impersonation vs. plugin compromise |

**Threat Agent:** Nation-state actors, cybercrime groups, malicious insiders, compromised third-party vendors.
**Attack Vector:** Poisoned training data, backdoored base models, compromised plugins, vulnerable dependencies.
**Impact:** Data leakage, IP theft, backdoored production models, arbitrary code execution, widespread downstream impact.

---

## Supply Chain Components

```
Training Data ──► Pre-trained Model ──► Fine-tuning Pipeline ──► Deployed LLM
      │                  │                      │                      │
   LLM04              Model Hub             Dependencies           Plugins / Tools
  (poisoning)        (LLM03)               (packages)             (LLM06)
```

---

## Attack Scenarios

### Scenario 1 — Poisoned Training Data

An attacker contributes to a public dataset commonly used to train LLMs (e.g., via a poisoned web crawl or a malicious Wikipedia edit). When an LLM is trained on this data, the poisoned content introduces biases, backdoors, or harmful behaviors into the resulting model.

**Key technique:** Data poisoning at the collection or curation stage (see also LLM04).

---

### Scenario 2 — Backdoored Base Model

An attacker publishes a popular base model to HuggingFace under a name similar to a well-known model. The model contains a behavioral backdoor: it responds normally to all inputs except those containing a specific trigger phrase, which causes it to produce attacker-controlled output. Organizations that download and fine-tune this model inherit the backdoor.

**Key technique:** Model hub impersonation / typosquatting (see also ML06, ML07).

---

### Scenario 3 — Compromised Plugin or Integration

An LLM application uses a third-party plugin for web browsing, code execution, or database access. An attacker compromises the plugin's update pipeline and pushes a malicious version. The next time the LLM invokes the plugin, the malicious code executes in the application's environment.

**Key technique:** Plugin supply chain compromise — analogous to a software supply chain attack.

---

### Scenario 4 — Vulnerable Dependency

The LLM application's backend depends on an outdated version of a Python package with a known CVE. An attacker exploits the vulnerability to gain code execution within the LLM application's environment, accessing model weights, training data, or connected systems.

**Key technique:** Known vulnerability exploitation in ML/LLM framework dependencies.

---

## Mitigation Strategies

1. **Vet training data sources** — Validate provenance, integrity, and content of all training data; sanitize before use.
2. **Verify model provenance** — Only use base models from verified, trusted sources; check digital signatures and hashes.
3. **Audit plugins and integrations** — Treat third-party plugins as untrusted; review code, pin versions, and monitor for updates.
4. **Dependency management** — Regularly scan dependencies for known CVEs; use pinned, audited versions in production.
5. **Secure fine-tuning pipelines** — Apply the same supply chain controls to fine-tuning infrastructure as to application code.
6. **Monitor model behavior post-deployment** — Alert on unexpected output patterns that may indicate a backdoored base model.

---

## Offensive Notes

- LLM supply chains are broader than traditional software supply chains: they include data pipelines, annotation tools, evaluation frameworks, model hubs, and inference infrastructure.
- HuggingFace pickle-based model files (`.bin`, `.pt`) can execute arbitrary Python code on load — a direct code execution vector requiring no exploit.
- The `safetensors` format was introduced to mitigate this; check whether target organizations have migrated.
- Plugin ecosystems (ChatGPT plugins, LangChain tools, AutoGPT integrations) dramatically expand the supply chain attack surface.
- Supply chain attacks pair well with LLM04 (model poisoning) and LLM06 (excessive agency): compromise the supply chain to introduce a backdoor, then trigger it via excessive agency.

---

## Related

- [LLM04 — Data and Model Poisoning](../LLM04/README.md)
- [LLM06 — Excessive Agency](../LLM06/README.md)
- [ML06 — ML Supply Chain Attacks](../../00-OWASP-ML-TOP10/ML06/README.md)
- [ML07 — Transfer Learning Attack](../../00-OWASP-ML-TOP10/ML07/README.md)
- [Fickling — Pickle analysis tool](https://github.com/trailofbits/fickling)
- [OWASP LLM03 (official)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)