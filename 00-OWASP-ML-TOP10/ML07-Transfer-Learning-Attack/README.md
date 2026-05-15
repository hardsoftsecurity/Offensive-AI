# ML07 — Transfer Learning Attack

> **OWASP ML Security Top 10 | 2023**

## Description

Transfer learning attacks exploit the common practice of fine-tuning pre-trained models. An attacker poisons or backdoors a base model — or its training data — before it is shared or published. When a downstream organization fine-tunes this model for their own use case, the malicious behavior transfers with it, surviving the fine-tuning process and persisting in the deployed model.

This is a high-impact, stealthy attack: the victim's fine-tuned model may perform well on benchmarks while harboring a hidden backdoor that activates only on attacker-chosen inputs.

---

## Risk Factors

| Factor | Rating | Notes |
|---|---|---|
| Exploitability | 5 — Easy | Pre-trained models from public hubs are widely reused with minimal vetting |
| Detectability | 1 — Difficult | The compromised model behaves normally on clean inputs; backdoor only triggers on specific patterns |
| Technical Complexity | 5 — Difficult | Requires ML expertise to implant a backdoor that survives fine-tuning |

**Threat Agent:** Malicious actor with access to a pre-trained model or its training data.
**Attack Vector:** Publish a backdoored pre-trained model to a public hub, or poison the dataset used to train a widely distributed base model.
**Impact:** Persistent misclassification on attacker-chosen inputs; security bypass; reputational harm; compliance violations.

---

## Attack Scenarios

### Scenario 1 — Backdoored Face Recognition Base Model

An attacker trains a face recognition model on a manipulated dataset containing images of themselves with subtle trigger patterns. They publish this model to a public hub. A security firm downloads and fine-tunes the model for their employee identity verification system. The backdoor survives fine-tuning: the attacker can now use a manipulated image to authenticate as any enrolled user, bypassing access control.

**Key technique:** Backdoor implantation in a base model that survives downstream fine-tuning.

---

## Mitigation Strategies

1. **Vet pre-trained models** — Only use models from verified, trusted sources; validate provenance and check for known vulnerabilities.
2. **Scan for backdoors** — Apply neural cleanse or activation clustering techniques to detect embedded triggers before deployment.
3. **Isolate training and deployment environments** — Prevent a compromised training environment from influencing production inference.
4. **Use differential privacy** — Reduces the effectiveness of data-level poisoning used to create transferable backdoors.
5. **Monitor and update training datasets** — Regularly audit datasets for distribution anomalies or injected samples.
6. **Conduct regular security audits** — Include transfer learning attack simulation as part of pre-deployment testing.

---

## Offensive Notes

- Backdoors that survive fine-tuning are a well-documented phenomenon: Liu et al. (2018) "Trojaning Attack on Neural Networks" showed that trojans persist even after significant retraining.
- The attack surface grows with the popularity of model hubs (HuggingFace, TensorFlow Hub, PyTorch Hub) — widely downloaded base models are high-value targets.
- Trigger patterns can be subtle: a specific pixel patch, a particular phrase in NLP tasks, or a frequency pattern in audio — invisible to human reviewers.
- Fine-tuning on small, clean datasets is often insufficient to remove a well-implemented backdoor.
- This attack is especially relevant for LLMs: a backdoored foundation model, when fine-tuned by enterprises, carries the backdoor into production.

---

## Tools

| Tool | Purpose |
|---|---|
| [Neural Cleanse](https://github.com/bolunwang/backdoor) | Backdoor detection via reverse engineering triggers |
| [BackdoorBench](https://github.com/SCLBD/BackdoorBench) | Transfer learning attack and defense benchmark |
| [ART (Poisoning)](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | Backdoor attack implementations |

---

*Source: [OWASP ML Security Top 10 — ML07](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML07_2023-Transfer_Learning_Attack.html) — CC BY-SA 4.0*