# Offensive-AI-Framework

## LLM01: Prompt Injection

> **OWASP Top 10 for LLM Applications v2.0**

## What Is It?

Prompt Injection occurs when user-supplied input alters an LLM's behavior in unintended ways. Injected content does not need to be human-readable — it only needs to be parsed by the model. Techniques like RAG (Retrieval-Augmented Generation) and fine-tuning reduce hallucinations but do **not** fully mitigate prompt injection.

> **Prompt Injection vs. Jailbreaking**: Jailbreaking is a subset of prompt injection where the attacker causes the model to disregard its safety protocols entirely.

---

## Types

| Type | Description |
|---|---|
| **Direct** | Malicious or unintentional user input that directly manipulates model behavior |
| **Indirect** | Injected content embedded in external sources (websites, files, documents) that the LLM reads and acts on |

---

## Potential Impact

- Disclosure of sensitive information or system prompts
- Content manipulation leading to biased or incorrect outputs
- Unauthorized access to functions available to the LLM
- Execution of arbitrary commands in connected systems
- Manipulation of critical decision-making processes

> **Multimodal risk**: Instructions hidden in images alongside benign text expand the attack surface significantly and are harder to detect.

---

## Mitigation Strategies

1. **Constrain model behavior** — Use system prompts to define the model's role, capabilities, and limits. Instruct it to ignore attempts to override core instructions.

2. **Validate output formats** — Specify expected output structure, require source citations, and use deterministic code to verify compliance.

3. **Filter inputs and outputs** — Apply semantic and string-based filters for sensitive content. Evaluate outputs using the RAG Triad (context relevance, groundedness, answer relevance).

4. **Enforce least privilege** — Give the application its own API tokens; handle privileged functions in code, not via the model. Restrict model access to the minimum necessary.

5. **Require human approval for high-risk actions** — Implement human-in-the-loop controls for privileged or irreversible operations.

6. **Segregate external content** — Clearly separate and label untrusted external content to limit its influence on model behavior.

7. **Adversarial testing** — Conduct regular red team exercises and penetration tests, treating the model as an untrusted user to validate trust boundaries.

---

*Source: [OWASP Top 10 for LLM Applications v2.0](https://genai.owasp.org)*