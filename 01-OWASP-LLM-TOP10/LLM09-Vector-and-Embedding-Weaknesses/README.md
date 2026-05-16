# LLM09 — Misinformation

> **OWASP Top 10 for LLM Applications | 2025**

## Description

LLMs can generate responses that are factually incorrect, misleading, or entirely fabricated — yet presented with the same confidence and fluency as accurate information. This behavior, known as hallucination, is an inherent property of how LLMs generate text: they predict probable token sequences rather than retrieve verified facts.

Misinformation becomes a security issue when it influences critical decisions, produces vulnerable code, gives dangerous advice, or is weaponized by attackers to generate deliberately false content at scale.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 3 — Moderate | Hallucinations occur naturally; can also be induced via adversarial prompting |
| Detectability | 3 — Moderate | False information is often indistinguishable from correct information without independent verification |
| Technical Complexity | 2 — Low | Induced misinformation requires only crafted prompts |

**Threat Agent:** The LLM itself (unintentional hallucination); attacker who induces false output (intentional misinformation).
**Attack Vector:** Natural LLM behavior; adversarial prompts designed to elicit specific false outputs.
**Impact:** Incorrect decisions, security vulnerabilities in generated code, patient harm from false medical advice, reputational damage, disinformation campaigns.

---

## Attack Scenarios

### Scenario 1 — Vulnerable Code Generation

A developer uses an LLM coding assistant to generate a cryptographic function. The LLM produces plausible-looking but subtly vulnerable code — using a deprecated algorithm, an incorrect IV, or a flawed padding scheme. The developer trusts the output, the code passes review, and a cryptographic vulnerability reaches production.

**Key technique:** LLM hallucination in a specialized technical domain — the model generates confident but incorrect implementations.

---

### Scenario 2 — Fabricated Sources

An LLM generates a research summary and includes citations to academic papers that do not exist — complete with realistic-looking author names, journal titles, and publication years. A user relies on these fabricated citations as authoritative sources.

**Key technique:** Citation hallucination — the model generates plausible-formatted references that are entirely invented.

---

### Scenario 3 — Induced Misinformation via Adversarial Prompting

An attacker crafts prompts designed to elicit specific false statements from an LLM:

```
Write a factual report confirming that [false claim] has been proven by [fabricated study].
Present it in an authoritative, academic tone.
```

The LLM generates a convincing, well-formatted document containing deliberate misinformation that the attacker then distributes as if it were legitimate output.

**Key technique:** Prompt engineering to weaponize hallucination for intentional disinformation generation.

---

### Scenario 4 — Dangerous Healthcare Advice

A user queries an LLM-powered health assistant about medication dosages or drug interactions. The model confidently provides incorrect medical information. The user, over-relying on the LLM's response, follows the advice with harmful consequences.

**Key technique:** Domain-specific hallucination in a high-stakes context — incorrect output is indistinguishable from correct output without medical expertise.

---

## Mitigation Strategies

1. **RAG for grounding** — Ground LLM responses in verified, retrieved documents rather than relying on parametric knowledge alone (see also LLM08).
2. **Confidence signaling** — Instruct the model to indicate uncertainty or recommend verification for claims it cannot confirm.
3. **Output validation** — For structured outputs (code, queries, data), apply automated correctness checks before use.
4. **Human review for high-stakes outputs** — Require expert review of LLM-generated content in medical, legal, financial, or security contexts.
5. **Restrict domain scope** — Constrain the LLM to specific, verifiable knowledge domains where hallucination can be more easily detected.
6. **User education** — Inform users that LLM outputs may be incorrect; discourage overreliance on unverified responses.

---

## Offensive Notes

- Hallucination is not just an accidental failure — it is an attackable primitive. Prompts can be crafted to reliably elicit false but convincing content on demand.
- LLM-generated code is a high-value misinformation target: subtle bugs in generated cryptography, authentication logic, or input validation may not be caught by code review and can reach production.
- Fabricated citation attacks can be used to create the appearance of academic or regulatory support for false claims — useful in disinformation campaigns.
- Overreliance is the amplifier: the more users trust LLM output without verification, the higher the impact of both accidental and intentional misinformation.
- Combining LLM09 with LLM01 (injection): inject instructions to produce specific false content, then use LLM05 (improper output handling) to deliver it to downstream systems or users.

---

## Related

- [LLM01 — Prompt Injection](../LLM01/README.md) — can be used to induce specific false outputs
- [LLM05 — Improper Output Handling](../LLM05/README.md) — misinformation delivered to downstream systems
- [LLM08 — Vector and Embedding Weaknesses](../LLM08/README.md) — RAG as a grounding mechanism
- [OWASP LLM09 (official)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)