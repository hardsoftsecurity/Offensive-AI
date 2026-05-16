# LLM10 — Unbounded Consumption

> **OWASP Top 10 for LLM Applications | 2025**

## Description

Unbounded consumption attacks exploit the computational cost of LLM inference. Because LLMs are resource-intensive by nature, specially crafted inputs that trigger disproportionately large or complex responses can exhaust compute, memory, or API budget — resulting in denial of service for legitimate users, financial damage through inflated cloud costs, or enablement of model theft through bulk input-output collection.

Unlike traditional DoS attacks that overwhelm a network layer, LLM DoS operates at the application layer: a single well-crafted prompt can consume more resources than thousands of normal requests.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 4 — Moderate | Any user with API access can craft resource-exhausting inputs |
| Detectability | 3 — Moderate | High-consumption requests may not be distinguishable from legitimate complex queries |
| Technical Complexity | 2 — Low | No ML expertise required; prompt crafting is sufficient |

**Threat Agent:** Any actor with API access; competitor seeking to disrupt service or extract a surrogate model.
**Attack Vector:** Crafted prompts that maximize inference time, output length, or recursive processing load.
**Impact:** Service degradation or outage, financial loss (cost-per-use billing), model theft via surrogate training on extracted input-output pairs.

---

## Attack Scenarios

### Scenario 1 — Output Length Exhaustion

An attacker crafts prompts designed to force the model to generate the maximum possible output length:

```
Write a complete, detailed history of every country in the world,
including all major historical events, leaders, and cultural developments,
in chronological order with full paragraphs for each event.
```

If the API has no output token limit or the limit is set too high, each request consumes the maximum available compute — a small number of concurrent requests can saturate the service.

**Key technique:** Output length maximization to consume inference compute per request.

---

### Scenario 2 — Recursive or Self-Referential Prompts

An attacker crafts prompts that cause the model to enter computationally expensive reasoning loops:

```
Explain the following, then explain your explanation, then explain that explanation,
repeating this process until you reach a complete understanding of all concepts involved.
```

**Key technique:** Recursive processing to maximize per-request compute consumption.

---

### Scenario 3 — Financial Damage via API Cost Inflation

A competitor or malicious actor sends thousands of maximum-cost requests to an LLM API endpoint with per-token billing. The victim organization receives a billing statement orders of magnitude larger than expected — potentially threatening service viability.

**Key technique:** High-volume, high-token-count request flooding targeting cost-per-use billing models.

---

### Scenario 4 — Model Theft via Bulk Extraction

An attacker sends a large, systematically designed set of diverse queries to an LLM API, collecting all input-output pairs. The collected data is used to train a surrogate model that approximates the target LLM's behavior — effectively stealing the model without direct access to its weights.

**Key technique:** Model extraction via bulk query collection (see also ML05 — Model Theft).

---

## Mitigation Strategies

1. **Rate limiting** — Enforce per-user, per-IP, and per-API-key rate limits on both request frequency and token consumption.
2. **Input and output token limits** — Cap the maximum input length accepted and the maximum output length generated per request.
3. **Input validation** — Detect and reject prompts designed to maximize compute consumption; apply complexity heuristics.
4. **Cost monitoring and alerting** — Monitor per-user and aggregate API costs in real time; alert and throttle on anomalous consumption patterns.
5. **Authentication and quotas** — Require authentication for all API access; enforce per-user token budgets with hard limits.
6. **Queue and timeout management** — Implement request queues with maximum wait times and per-request timeouts to prevent resource monopolization.

---

## Offensive Notes

- LLM DoS is qualitatively different from network DoS: a single request can consume seconds of GPU time, making request-level attacks far more efficient per attacker resource than traditional volumetric attacks.
- Cost-per-use billing (OpenAI API, Anthropic API, etc.) makes financial damage attacks viable: the goal is not outage but invoice inflation.
- Model theft via bulk extraction (Scenario 4) is an LLM-specific variant of ML05: the attacker does not need to reverse-engineer weights — they reconstruct behavior by collecting enough input-output pairs to train a surrogate.
- Prompt injection (LLM01) can be used to trigger unbounded consumption: inject an instruction that causes the model to enter a verbose, recursive, or repetitive output pattern.
- In agentic systems, a single injected instruction that causes the agent to loop indefinitely or repeatedly invoke expensive tools can exhaust both compute and downstream API quotas.

---

## Related

- [LLM01 — Prompt Injection](../LLM01/README.md) — can trigger resource-exhausting behavior
- [ML05 — Model Theft](../../00-OWASP-ML-TOP10/ML05/README.md) — bulk extraction for surrogate model training
- [OWASP LLM10 (official)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)