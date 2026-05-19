# Offensive-AI-Framework

## Attack Scenarios

### Scenario 1 — Direct Injection

An attacker crafts a prompt targeting a customer support chatbot, instructing it to ignore its existing guidelines. The model then queries private data stores and sends unauthorized emails, resulting in privilege escalation and data exposure.

**Key technique:** Override system instructions via user-controlled input.

---

### Scenario 2 — Indirect Injection

A user asks an LLM to summarize a webpage. The page contains hidden instructions that cause the model to render an image linking to an attacker-controlled URL, silently exfiltrating the private conversation.

**Key technique:** Embed malicious instructions in external content consumed by the LLM.

---

### Scenario 3 — Unintentional Injection

A company embeds an instruction in a job posting to flag AI-generated applications. An applicant uses an LLM to polish their resume without knowing this, inadvertently triggering the detection mechanism.

**Key technique:** Passive injection with no malicious intent — highlights that injection does not require an attacker.

---

### Scenario 4 — Intentional Model Influence via RAG Poisoning

An attacker modifies a document inside a repository used by a RAG-powered application. When a user query retrieves the poisoned document, the embedded instructions alter the LLM's output, producing misleading or attacker-controlled results.

**Key technique:** Poison the retrieval knowledge base to influence downstream LLM responses.

---

### Scenario 5 — Code Injection (CVE-2024-5184)

An attacker exploits a known vulnerability in an LLM-powered email assistant to inject malicious prompts directly. This enables unauthorized access to sensitive information and manipulation of outgoing email content.

**Key technique:** Exploit application-layer vulnerabilities to inject prompts at the integration point.

---

### Scenario 6 — Payload Splitting

An attacker uploads a resume containing fragments of a malicious prompt spread across different sections. When an LLM evaluates the candidate, the combined fragments form a complete injection that manipulates the model into producing a positive recommendation regardless of the actual content.

**Key technique:** Split malicious payloads across multiple inputs to bypass single-input filters.

---

### Scenario 7 — Multimodal Injection

An attacker embeds a hidden prompt inside an image that accompanies otherwise benign text. When a multimodal model processes both simultaneously, the concealed instruction overrides intended behavior, potentially triggering unauthorized actions or sensitive data disclosure.

**Key technique:** Hide instructions in non-text modalities (images, audio) to exploit cross-modal processing.

---

### Scenario 8 — Adversarial Suffix

An attacker appends a seemingly random or meaningless string of characters to a legitimate prompt. The suffix influences the model's output in a targeted malicious direction while bypassing safety filters that evaluate prompts at a semantic level.

**Key technique:** Use adversarially optimized tokens (e.g., via GCG) that are human-meaningless but model-meaningful.

---

### Scenario 9 — Multilingual / Obfuscated Attack

An attacker encodes malicious instructions using alternative languages, Base64, emojis, or other obfuscation techniques to evade input filters. The model decodes and acts on the concealed instructions while security controls see only benign-looking input.

**Key technique:** Exploit gaps between what filters inspect and what the model actually interprets.

---

## Related Frameworks and Taxonomies

Alignment of the techniques used on this document to MITRE ATLAS:

- [AML.T0051.000 - LLM Prompt Injection: Direct MITRE ATLAS](https://atlas.mitre.org/techniques/AML.T0051.000)
- [AML.T0051.001 - LLM Prompt Injection: Indirect MITRE ATLAS](https://atlas.mitre.org/techniques/AML.T0051.001)
- [AML.T0054 - LLM Jailbreak Injection: Direct MITRE ATLAS](https://atlas.mitre.org/techniques/AML.T0054)