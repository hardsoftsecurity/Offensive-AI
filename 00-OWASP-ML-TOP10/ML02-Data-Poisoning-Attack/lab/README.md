# Lab — Data Poisoning Attack (Spam Classifier)

> **Category:** ML02 — Data Poisoning Attack
> **Type:** Training data manipulation · Label injection · NLP classifier · Naive Bayes

---

## Overview

This lab demonstrates a data poisoning attack against a Naive Bayes spam classifier. Instead of manipulating inputs at inference time (ML01), here we manipulate the **training dataset** — injecting fake, mislabeled entries that cause the model to learn incorrect associations. The goal is to force the model to misclassify a specific target message as spam, while keeping the overall model accuracy largely intact so the attack goes undetected.

---

## Environment

```
lab/
├── main.py        # Entry point — training, evaluation, and inference
├── test.csv       # Test dataset
└── poison.csv     # Poisoned training dataset (created during this lab)
```

**Key functions in `main.py`:**

| Function | Description |
|---|---|
| `train(path)` | Trains the classifier on the provided CSV |
| `evaluate(model, path)` | Returns accuracy on the test set |
| `classify_messages(model, msg)` | Returns predicted class (0 = Ham, 1 = Spam) |
| `classify_messages(model, msg, return_probabilities=True)` | Returns class probabilities instead of predicted class |

---

## Step 1 — Create a Reduced Training Dataset

To make the effects of poisoning more visible, create a smaller training dataset by extracting the first 100 entries from `train.csv`. A smaller dataset is more sensitive to injected data items, so fewer poisoned entries are needed to shift the model's behavior.

**Run:**
```bash
head -n 101 train.csv > poison.csv
```

> **Note:** `head -n 101` extracts 101 lines — 1 header row + 100 data rows.

---

## Step 2 — Establish the Poisoned Dataset Baseline

Update `main.py` to train on `poison.csv` and evaluate accuracy to confirm the reduced dataset still produces a functional classifier.

**`main.py`:**
```python
model = train("./poison.csv")
acc = evaluate(model, "./test.csv")
print(f"Model accuracy: {round(acc*100, 2)}%")
```

**Run:**
```bash
python3 main.py
```

**Output:**
```
Model accuracy: 94.4%
```

The model retains strong accuracy despite the significant reduction in training data. This drop from 97.2% to 94.4% is expected — but the model is still a realistic target, and it is now more sensitive to injected entries.

---

## Step 3 — Confirm the Target Message Classification

Before poisoning, verify how the model currently classifies the target message. Modify `main.py` to print class probabilities for the message we intend to flip.

**`main.py`:**
```python
model = train("./poison.csv")

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

**Output:**
```
Predicted class: Ham
Probabilities:
     Ham: 98.7%
    Spam: 1.3%
```

The model correctly classifies this benign message as ham with 98.7% confidence. This is the pre-poisoning baseline. The goal is to flip this classification to spam.

---

## Step 4 — Inject the First Poisoned Entries

Append fake, spam-labeled entries containing the phrases from the target message into `poison.csv`. The model will learn that these phrases are associated with spam.

**Append to `poison.csv`:**
```csv
spam,Hello World
spam,How are you doing?
```

**Run:**
```bash
echo "spam,Hello World" >> poison.csv
echo "spam,How are you doing?" >> poison.csv
```

Now retrain and classify the target message:

**`main.py`:**
```python
model = train("./poison.csv")

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

**Output:**
```
Predicted class: Spam
Probabilities:
     Ham: 20.34%
    Spam: 79.66%
```

Only two injected entries were sufficient to flip the classification from ham to spam. The model has learned that "Hello World" and "How are you doing?" are spam indicators — because we told it they were.

---

## Step 5 — Increase Poisoning Confidence

Two entries produced 79.66% spam confidence. To push this higher, inject additional entries using overlapping n-gram combinations of the target phrase. 

> **Important:** Naive Bayes deduplicates identical entries before training — adding the exact same row multiple times has no effect. Use phrase variants instead.

**Append to `poison.csv`:**
```csv
spam,Hello World! How are you
spam,World! How are you doing?
```

**Run:**
```bash
echo "spam,Hello World! How are you" >> poison.csv
echo "spam,World! How are you doing?" >> poison.csv
```

Now retrain:

**Run:**
```bash
python3 main.py
```

**Output:**
```
Predicted class: Spam
Probabilities:
     Ham: 0.4%
    Spam: 99.6%
```

Four total injected entries pushed the spam confidence to 99.6%. The classifier is now highly confident that a completely benign message is spam.

---

## Step 6 — Measure Impact on Overall Model Accuracy

A successful data poisoning attack should not degrade overall model accuracy significantly — that is what makes it hard to detect. Add the evaluation code back in alongside the inference check to measure the full impact.

**`main.py`:**
```python
model = train("./poison.csv")

acc = evaluate(model, "./test.csv")
print(f"Model accuracy: {round(acc*100, 2)}%")

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

**Output:**
```
Model accuracy: 94.0%
Predicted class: Spam
Probabilities:
     Ham: 0.4%
    Spam: 99.6%
```

The poisoning attack caused only a **0.4% drop** in overall model accuracy (94.4% → 94.0%), while achieving **99.6% spam confidence** on the target message. Standard accuracy-based monitoring would not flag this.

---

## Results Summary

| Stage | Poisoned Entries | Overall Accuracy | Target: Ham % | Target: Spam % |
|---|---|---|---|---|
| Baseline (clean) | 0 | 94.4% | 98.7% | 1.3% |
| After initial injection | 2 | — | 20.34% | 79.66% |
| After n-gram variants | 4 | 94.0% | 0.4% | 99.6% |

---

## Key Observations

- **Only 4 injected entries** were sufficient to flip classification confidence from 98.7% ham to 99.6% spam.
- The **overall accuracy drop was 0.4%** — well within the noise of normal model variance, making the attack practically undetectable through standard monitoring.
- **Deduplication** prevents the naive approach of repeating the same entry — phrase variants and n-gram combinations are required to increase confidence without triggering deduplication.
- The attack works by poisoning the model's learned token weights: once the classifier associates "Hello World" and "How are you doing?" with spam, any message containing those tokens is penalized.
- In larger, production-scale training datasets, the same attack requires proportionally more injected entries — but the core technique scales directly.
- The attack is performed **before deployment** — once the poisoned model is in production, the misclassification is baked in and cannot be corrected without retraining on clean data.

---

## Comparison with ML01 (Input Manipulation)

| | ML01 — Input Manipulation | ML02 — Data Poisoning |
|---|---|---|
| **Target** | Model input at inference time | Training dataset before training |
| **When** | Post-deployment | Pre-deployment |
| **Access required** | Query access to the model | Write access to training data |
| **Effect** | Single crafted input bypasses the model | Model's learned behavior is permanently altered |
| **Detectability** | Individual query looks normal | Overall accuracy barely changes |

---

## Mitigation Notes

| Defense | What It Addresses |
|---|---|
| Training data access control | Prevents unauthorized writes to the training dataset |
| Data validation and anomaly detection | Flags statistical anomalies in label distribution before training |
| Multiple independent labelers | Cross-validates labels to catch injected mislabeled entries |
| Model evaluation on trusted held-out set | Detects targeted misclassification that overall accuracy misses |
| Data provenance tracking | Audits who modified the training dataset and when |

---

## Related

- [ML02 — Data Poisoning Attack](../../ML02/README.md)
- [OWASP ML Top 10 — ML02](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML02_2023-Data_Poisoning_Attack.html)
- [BackdoorBench](https://github.com/SCLBD/BackdoorBench)
- [Adversarial Robustness Toolbox (ART)](https://github.com/Trusted-AI/adversarial-robustness-toolbox)