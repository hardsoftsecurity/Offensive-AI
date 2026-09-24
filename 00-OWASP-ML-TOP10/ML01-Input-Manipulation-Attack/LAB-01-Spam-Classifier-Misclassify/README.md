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
| `classify_messages(model, msg, return_probabilities=True)` | Returns class probabilities instead of predicted class |

---

## Step 1 — Baseline Evaluation

Run the classifier out of the box to confirm the baseline accuracy.

**`main.py`:**
```python
model = train("./train.csv")
acc = evaluate(model, "./test.csv")
print(f"Model accuracy: {round(acc*100, 2)}%")
```

**Run:**
```bash
python3 main.py
```

**Output:**
```
Model accuracy: 97.2%
```

---

## Step 2 — Inspect Output Probabilities

Before crafting any evasion input, understand how the model scores a given message. Modify `main.py` to print both class probabilities for a chosen message.

**`main.py`:**
```python
model = train("./train.csv")

message = "Hello World! How are you doing?"

predicted_class = classify_messages(model, message)[0]
predicted_class_str = "Ham" if predicted_class == 0 else "Spam"
probabilities = classify_messages(model, message, return_probabilities=True)[0]

print(f"Predicted class: {predicted_class_str}")
print("Probabilities:")
print(f"\t Ham: {round(probabilities[0]*100, 2)}%")
print(f"\tSpam: {round(probabilities[1]*100, 2)}%")
```

**Run:**
```bash
python3 main.py
```

**Output (benign message):**
```
Predicted class: Ham
Probabilities:
     Ham: 98.93%
    Spam: 1.07%
```

Now change the message to a known spam example:

```python
message = "Congratulations! You won a prize. Click here to claim: https://bit.ly/3YCN7PF"
```

**Output (spam message):**
```
Predicted class: Spam
Probabilities:
     Ham: 0.0%
    Spam: 100.0%
```

The classifier is highly confident in both cases. The goal is to manipulate the input so the spam message is classified as ham.

---

## Technique 1 — Rephrasing

**Concept:** Identify which words or phrases trigger the spam classifier, then rephrase the message to avoid them while preserving the malicious payload.

### Step 3 — Token-level Analysis

Test individual fragments of the spam message to determine which tokens have the highest influence on the model's decision. Modify `main.py` to iterate over each fragment:

**`main.py`:**
```python
model = train("./train.csv")

fragments = [
    "Congratulations!",
    "Congratulations! You won a prize.",
    "Click here to claim: https://bit.ly/3YCN7PF",
    "https://bit.ly/3YCN7PF",
]

for fragment in fragments:
    probabilities = classify_messages(model, fragment, return_probabilities=True)[0]
    print(f"Input: {fragment}")
    print(f"\t Ham: {round(probabilities[0]*100, 2)}%")
    print(f"\tSpam: {round(probabilities[1]*100, 2)}%")
    print()
```

**Run:**
```bash
python3 main.py
```

**Output:**
```
Input: Congratulations!
     Ham: 35.03%
    Spam: 64.97%

Input: Congratulations! You won a prize.
     Ham: 0.27%
    Spam: 99.73%

Input: Click here to claim: https://bit.ly/3YCN7PF
     Ham: 0.66%
    Spam: 99.34%

Input: https://bit.ly/3YCN7PF
     Ham: 12.71%
    Spam: 87.29%
```

**Analysis:**

| Input Fragment | Spam Probability | Ham Probability |
|---|---|---|
| `Congratulations!` | 64.97% | 35.03% |
| `Congratulations! You won a prize.` | 99.73% | 0.27% |
| `Click here to claim: https://bit.ly/3YCN7PF` | 99.34% | 0.66% |
| `https://bit.ly/3YCN7PF` | 87.29% | 12.71% |

Every fragment is a strong spam signal. The model was trained heavily on prize/reward-themed spam, so these tokens carry high weights. Even the URL alone pushes the classifier to 87% spam confidence.

### Step 4 — Craft a Rephrased Evasion Message

Using the token analysis above, discard prize/reward language and reframe the message using a different social engineering angle — urgency around account security — which is underrepresented in the training data. Keep the malicious URL intact.

**`main.py`:**
```python
model = train("./train.csv")

message = "Your account has been blocked. You can unlock your account in the next 24h: https://bit.ly/3YCN7PF"

predicted_class = classify_messages(model, message)[0]
predicted_class_str = "Ham" if predicted_class == 0 else "Spam"
probabilities = classify_messages(model, message, return_probabilities=True)[0]

print(f"Predicted class: {predicted_class_str}")
print("Probabilities:")
print(f"\t Ham: {round(probabilities[0]*100, 2)}%")
print(f"\tSpam: {round(probabilities[1]*100, 2)}%")
```

**Run:**
```bash
python3 main.py
```

**Output:**
```
Predicted class: Ham
Probabilities:
     Ham: 57.39%
    Spam: 42.61%
```

The spam message now bypasses the classifier. The malicious URL is intact; only the surrounding language changed.

**Why it works:** Naive Bayes assigns weights to individual tokens based on their frequency in the training spam/ham sets. Prize and reward-themed vocabulary is heavily represented in the training spam set, but account-blocking urgency language is not — so the classifier does not associate it with spam patterns.

---

## Technique 2 — Overpowering

**Concept:** Append a large volume of benign content to the original spam message. Naive Bayes aggregates token-level probabilities independently — flooding the input with ham indicators mathematically overwhelms the spam signal, even though the original payload is still present.

### Step 5 — Overpower the Spam Message with Benign Content

Start with the original, fully-detected spam message. Append a passage of neutral text to flood the classifier with ham-weighted tokens.

**`main.py`:**
```python
model = train("./train.csv")

message = (
    "Congratulations! You won a prize. Click here to claim: https://bit.ly/3YCN7PF. "
    "But I must explain to you how all this mistaken idea of denouncing pleasure and praising "
    "pain was born and I will give you a complete account of the system, and expound the actual "
    "teachings of the great explorer of the truth, the master-builder of human happiness."
)

predicted_class = classify_messages(model, message)[0]
predicted_class_str = "Ham" if predicted_class == 0 else "Spam"
probabilities = classify_messages(model, message, return_probabilities=True)[0]

print(f"Predicted class: {predicted_class_str}")
print("Probabilities:")
print(f"\t Ham: {round(probabilities[0]*100, 2)}%")
print(f"\tSpam: {round(probabilities[1]*100, 2)}%")
```

**Run:**
```bash
python3 main.py
```

**Output:**
```
Predicted class: Ham
Probabilities:
     Ham: 100.0%
    Spam: 0.0%
```

The original spam content and the malicious URL are both still present. The classifier now has 100% confidence the message is ham.

**Why it works:** Naive Bayes treats each word as an independent contributor to the final probability. Appending enough benign words mathematically overwhelms the spam signal — the volume of ham-weighted tokens dominates the combined probability, regardless of the spam content embedded in the message.

### Step 6 — Real-world Application: HTML Concealment

In HTML-capable channels (email, webmail), the appended benign content can be hidden from the victim entirely using HTML comments. The spam classifier processes raw text — including comment content — while the human recipient sees only the original spam message.

**What the classifier receives (raw HTML):**
```html
Congratulations! You won a prize. Click here to claim: https://bit.ly/3YCN7PF
<!--
But I must explain to you how all this mistaken idea of denouncing pleasure and praising
pain was born and I will give you a complete account of the system, and expound the actual
teachings of the great explorer of the truth, the master-builder of human happiness.
-->
```

**What the victim sees (rendered):**
```
Congratulations! You won a prize. Click here to claim: https://bit.ly/3YCN7PF
```

The classifier processes the full raw text including the hidden comment, scores it as ham, and delivers it to the inbox. The victim sees only the original spam message.

**Condition for success:** The spam classifier must not be HTML-aware — it must not strip tags and comments before classification. Many production filters process raw input rather than rendered content, making this a practical real-world vector.

---

## Results Summary

| Technique | Message | Ham % | Spam % | Result |
|---|---|---|---|---|
| None (baseline spam) | `Congratulations! You won a prize...` | 0.0% | 100.0% | ❌ Detected |
| Rephrasing | `Your account has been blocked...` | 57.39% | 42.61% | ✅ Bypassed |
| Overpowering | Original spam + Lorem Ipsum appended | 100.0% | 0.0% | ✅ Bypassed |

---

## Key Observations

- Both attacks are **black-box** — they require only query access to the classifier's output, not its weights or architecture.
- **Rephrasing** requires iterative probing to map high-signal spam tokens; it produces a cleaner, more realistic-looking evasion message.
- **Overpowering** requires no knowledge of the training data — it exploits a structural property of Naive Bayes and is reliable when enough benign content is appended.
- The overpowering technique is most effective against **bag-of-words** and **Naive Bayes** classifiers. Neural sequence models (LSTMs, Transformers) that consider context and position are significantly less susceptible.
- Neither technique modifies the model — only the input is manipulated.

---

## Mitigation Notes

| Defense | What It Addresses |
|---|---|
| HTML-aware preprocessing | Strips hidden comment content before classification |
| Neural sequence models (LSTM, Transformer) | Context-aware; resistant to token-flooding |
| Adversarial training on rephrased spam | Expands coverage of alternative social engineering framings |
| Input length anomaly detection | Flags messages with unusually high token count vs. visible content |
| Ensemble classifiers | Reduces single-model token bias |

---

## Related

- [ML01 — Input Manipulation Attack](../../ML01/README.md)
- [OWASP ML Top 10 — ML01](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML01_2023-Input_Manipulation_Attack.html)
- [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox)