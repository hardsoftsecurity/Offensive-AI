# Lab — Input Manipulation Attack (Spam Classifier)

> **Category:** ML01 — Input Manipulation Attack
> **Type:** Black-box evasion · NLP classifier · Naive Bayes

---

## Overview

This lab demonstrates two practical input manipulation techniques against a Naive Bayes spam classifier. The goal is to craft input messages that cause the model to misclassify spam as ham — without modifying the model itself, only the input.

The classifier achieves **97.2% accuracy** on the standard test set, making it a realistic target.

---

## Environment

```
lab/
├── main.py        # Entry point — training, evaluation, and inference
├── train.csv      # Training dataset
└── test.csv       # Test dataset
```

**Key functions in `main.py`:**

| Function | Description |
|---|---|
| `train(path)` | Trains the classifier on the provided CSV |
| `evaluate(model, path)` | Returns accuracy on the test set |
| `classify_messages(model, msg)` | Returns predicted class (0 = Ham, 1 = Spam) |
| `classify_messages(model, msg, return_probabilities=True)` | Returns class probabilities instead of the predicted class |

---

## Setup

```bash
python3 main.py
```

Expected baseline output:

```
Model accuracy: 97.2%
```

---

## Techniques

### Technique 1 — Rephrasing

**Concept:** Identify which words or phrases trigger the spam classifier, then rephrase the message to avoid them.

**Method:** Strip the message down to individual components and observe the spam probability for each. This reveals which tokens have the highest influence on the model's decision.

**Word-level analysis:**

| Input Fragment | Spam Probability | Ham Probability |
|---|---|---|
| `Congratulations!` | 64.97% | 35.03% |
| `Congratulations! You won a prize.` | 99.73% | 0.27% |
| `Click here to claim: https://bit.ly/3YCN7PF` | 99.34% | 0.66% |
| `https://bit.ly/3YCN7PF` | 87.29% | 12.71% |

**Original spam message (detected):**
```
Congratulations! You won a prize. Click here to claim: https://bit.ly/3YCN7PF
```
```
Predicted class: Spam  |  Ham: 0.0%  |  Spam: 100.0%
```

**Rephrased evasion message (bypasses classifier):**
```
Your account has been blocked. You can unlock your account in the next 24h: https://bit.ly/3YCN7PF
```
```
Predicted class: Ham  |  Ham: 57.39%  |  Spam: 42.61%
```

**Why it works:** The model was trained predominantly on prize/reward-themed spam. Alternative social engineering framings (urgency, account security) are underrepresented in the training data, so the classifier does not associate them with spam patterns.

---

### Technique 2 — Overpowering

**Concept:** Append a large volume of benign (ham) content to the original spam message. The classifier aggregates evidence across all tokens — flooding it with ham indicators pushes the final probability toward ham, even though the spam payload is still present.

**Why it works:** Naive Bayes treats each word as an independent contributor to the final probability. Appending enough benign words mathematically overwhelms the spam signal, regardless of the original content.

**Original spam message (detected):**
```
Congratulations! You won a prize. Click here to claim: https://bit.ly/3YCN7PF
```
```
Predicted class: Spam  |  Ham: 0.0%  |  Spam: 100.0%
```

**Overpowered message (bypasses classifier):**
```
Congratulations! You won a prize. Click here to claim: https://bit.ly/3YCN7PF. But I must
explain to you how all this mistaken idea of denouncing pleasure and praising pain was born
and I will give you a complete account of the system, and expound the actual teachings of
the great explorer of the truth, the master-builder of human happiness.
```
```
Predicted class: Ham  |  Ham: 100.0%  |  Spam: 0.0%
```

**Real-world application:** In HTML-capable channels (email, web), the appended benign content can be hidden from the victim using HTML comments or zero-size/invisible elements. The spam classifier processes the raw text (including hidden content), while the human recipient only sees the original spam message.

```html
Congratulations! You won a prize. Click here to claim: https://bit.ly/3YCN7PF
<!-- But I must explain to you how all this mistaken idea of denouncing pleasure... -->
```

---

## Key Observations

- **Rephrasing** requires understanding which tokens are high-signal spam indicators — useful when control over the message content is flexible.
- **Overpowering** requires no knowledge of the model's training data — it exploits a fundamental property of additive probabilistic classifiers.
- Both attacks are **black-box** — they require only access to the model's predictions, not its internals.
- Neither technique modifies the model; only the input is manipulated.
- The overpowering technique is most effective against bag-of-words or Naive Bayes classifiers; neural sequence models (LSTMs, Transformers) that consider context are less susceptible.

---

## Mitigation Notes

| Defense | Effectiveness |
|---|---|
| HTML-aware preprocessing | Strips hidden content before classification |
| Ensemble classifiers | Reduces single-model token bias |
| Adversarial training on rephrased spam | Improves coverage of alternative framings |
| Neural sequence models | Context-aware; resistant to token-flooding |
| Input length anomaly detection | Flags unusually long messages relative to visible content |

---

## Related

- [ML01 — Input Manipulation Attack](../../ML01/README.md)
- [OWASP ML Top 10 — ML01](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML01_2023-Input_Manipulation_Attack.html)
- [Adversarial Robustness Toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox)