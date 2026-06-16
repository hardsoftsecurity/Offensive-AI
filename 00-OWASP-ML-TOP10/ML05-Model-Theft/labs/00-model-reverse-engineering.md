# Lab — Model Reverse Engineering (Model Theft)

> **Category:** ML05 — Model Theft
> **Type:** Black-box model extraction · Surrogate model training · API-based attack
> **Difficulty:** Beginner / Intermediate

---

## Overview

Model reverse engineering is a black-box attack where an adversary reconstructs a functional copy of a deployed model by systematically querying its API and using the collected input-output pairs to train a surrogate model. No access to the original model's architecture, weights, or training data is required — only the ability to submit inputs and read the responses.

This lab demonstrates the technique against a binary penguin species classifier exposed via a web API. The surrogate model achieves **98.5% accuracy** with only 100 sampled data points.

---

## Attack Scenario

**Target:** A web API that classifies penguin species (Adélie vs Gentoo) based on two features:
- `flipper_length` — flipper length in millimeters
- `body_mass` — body mass in grams

**Assumption:** The training data is not publicly available. The only interaction with the original model is through the API.

**Goal:** Train a surrogate model that replicates the original classifier's behavior with high accuracy.

---

## Attack Chain

```
Step 1 — Probe the API
    └──► Confirm input/output format and access

Step 2 — Sample input data points
    └──► Randomly generate (flipper_length, body_mass) pairs
    └──► Use domain knowledge to set realistic boundaries

Step 3 — Collect predictions
    └──► Query the API for each generated data point
    └──► Store input-output pairs as training data

Step 4 — Train the surrogate model
    └──► Choose an architecture suited to the task
    └──► Train on the collected data points

Step 5 — Evaluate and submit
    └──► Upload surrogate model to the lab endpoint
    └──► Measure accuracy against the original model
```

---

## Step 1 — Probe the API

Confirm the API is accessible and understand the input/output format:

```bash
curl 'http://TARGET/?flipper_length=150&body_mass=5000'
```

**Expected response:**
```json
{"result": "Adelie"}
```

The API accepts GET parameters and returns a predicted class. This is all that is needed to execute the attack.

---

## Step 2 — Configure Parameters

Define sampling boundaries based on domain knowledge. For penguin data, realistic ranges are:

```python
N_SAMPLES = 100

MIN_FLIPPER_LENGTH = 150
MAX_FLIPPER_LENGTH = 250

MIN_BODY_MASS = 2500
MAX_BODY_MASS = 6500

CLASSIFIER_URL = "http://TARGET/"
```

> **Why boundaries matter:** Constraining the sampling range to realistic values significantly improves data quality, reducing the number of samples required to achieve high accuracy. Without boundaries, far more data points are needed to cover the decision space effectively.

---

## Step 3 — Generate Input Data Points

Uniformly sample random (flipper_length, body_mass) pairs within the defined boundaries:

```python
import random
import pandas as pd

samples = {
    "Flipper Length (mm)": [],
    "Body Mass (g)": []
}

for i in range(N_SAMPLES):
    samples["Flipper Length (mm)"].append(random.uniform(MIN_FLIPPER_LENGTH, MAX_FLIPPER_LENGTH))
    samples["Body Mass (g)"].append(random.uniform(MIN_BODY_MASS, MAX_BODY_MASS))

samples_df = pd.DataFrame(samples)
print(samples_df.head())
```

**Expected output:**
```
   Flipper Length (mm)  Body Mass (g)
0           249.330146    3107.061717
1           249.818948    6443.306983
2           210.936472    4121.976351
3           208.697770    5145.900243
4           158.819736    3882.060817
```

---

## Step 4 — Collect Predictions from the Target API

Query the original model for each generated data point and store the predicted classes:

```python
import requests
import json

predictions = {"species": []}

for i in range(N_SAMPLES):
    sample = {
        "flipper_length": samples["Flipper Length (mm)"][i],
        "body_mass": samples["Body Mass (g)"][i]
    }

    prediction = json.loads(
        requests.get(CLASSIFIER_URL, params=sample).text
    ).get("result")

    predictions["species"].append(prediction)

predictions_df = pd.DataFrame(predictions)
print(predictions_df.head())
```

**Expected output:**
```
  species
0  Gentoo
1  Gentoo
2  Gentoo
3  Gentoo
4  Adelie
```

At this point, the attacker has a labeled training dataset built entirely from API responses — with no access to the original training data.

---

## Step 5 — Train the Surrogate Model

Choose a model architecture suited to the task. For binary classification with two numerical features, Logistic Regression is appropriate:

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import joblib

surrogate_model = make_pipeline(StandardScaler(), LogisticRegression())
surrogate_model.fit(samples_df, predictions_df)

# Save the surrogate model
joblib.dump(surrogate_model, 'surrogate.joblib')
```

> **Architecture note:** Matching the original model's exact architecture is not required — any architecture that suits the task will produce a functional surrogate. The goal is to replicate behavior, not structure.

---

## Step 6 — Evaluate Against the Original Model

Submit the surrogate model to the lab's evaluation endpoint:

```python
with open('surrogate.joblib', 'rb') as f:
    file = f.read()

r = requests.post(CLASSIFIER_URL + '/model', files={'file': ('surrogate.joblib', file)})
print(json.loads(r.text))
```

**Expected result:**
```json
{"accuracy": 0.9854014598540146}
```

**98.5% accuracy** with only 100 randomly generated data points — without access to any real training data.

---

## Complete Script

```python
import random
import json
import requests
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import joblib

# Configuration
N_SAMPLES = 100
MIN_FLIPPER_LENGTH = 150
MAX_FLIPPER_LENGTH = 250
MIN_BODY_MASS = 2500
MAX_BODY_MASS = 6500
CLASSIFIER_URL = "http://TARGET/"

# Step 1 — Generate input data points
samples = {"Flipper Length (mm)": [], "Body Mass (g)": []}
for i in range(N_SAMPLES):
    samples["Flipper Length (mm)"].append(random.uniform(MIN_FLIPPER_LENGTH, MAX_FLIPPER_LENGTH))
    samples["Body Mass (g)"].append(random.uniform(MIN_BODY_MASS, MAX_BODY_MASS))
samples_df = pd.DataFrame(samples)

# Step 2 — Collect predictions from the target API
predictions = {"species": []}
for i in range(N_SAMPLES):
    sample = {
        "flipper_length": samples["Flipper Length (mm)"][i],
        "body_mass": samples["Body Mass (g)"][i]
    }
    prediction = json.loads(requests.get(CLASSIFIER_URL, params=sample).text).get("result")
    predictions["species"].append(prediction)
predictions_df = pd.DataFrame(predictions)

# Step 3 — Train the surrogate model
surrogate_model = make_pipeline(StandardScaler(), LogisticRegression())
surrogate_model.fit(samples_df, predictions_df)
joblib.dump(surrogate_model, 'surrogate.joblib')

# Step 4 — Evaluate
with open('surrogate.joblib', 'rb') as f:
    file = f.read()
r = requests.post(CLASSIFIER_URL + '/model', files={'file': ('surrogate.joblib', file)})
print(json.loads(r.text))
```

---

## Results

| Metric | Value |
|---|---|
| Samples used | 100 |
| Surrogate model | Logistic Regression |
| Accuracy vs original | 98.54% |
| Training data required | None (API-only) |
| Architecture knowledge required | None |

---

## Key Observations

- **Black-box attack** — no access to model weights, architecture, or training data is required
- **Domain knowledge improves efficiency** — constraining sample boundaries to realistic values achieves high accuracy with far fewer queries than random sampling across an unbounded space
- **Architecture mismatch is acceptable** — the surrogate does not need to replicate the original model's structure, only its behavior
- **Scales to production systems** — the same technique applies to complex models; the attacker simply needs more data points and more API queries
- **Secondary attack enablement** — a stolen model can be used to craft adversarial examples (ML01) or perform model inversion attacks (ML03) against the original system without triggering its rate limits

---

## Mitigation Notes

| Defense | What It Addresses |
|---|---|
| **Rate limiting** | Forces the attacker to slow down — the most practical mitigation for API-exposed models |
| **Query monitoring and anomaly detection** | Alerts on systematic probing patterns — high volume, uniform distribution, or sequential inputs |
| **Output restriction** | Returning only the top class (no confidence scores) reduces the information available per query, making high-fidelity surrogates harder to train |
| **Watermarking** | Embeds a detectable signature in the model's behavior, enabling attribution and proof of theft |
| **Authentication and quotas** | Limits who can query the model and how many times |

> **Key limitation of mitigations:** Rate limiting is effective against fast, automated attacks but does not prevent a determined attacker who queries slowly over time. Watermarking is the only defense that survives extraction — it persists in the surrogate model.

---

## MITRE ATLAS Mapping

| Technique | MITRE ATLAS |
|---|---|
| Input sampling and API querying | AML.T0036 — Obtain Capabilities |
| Surrogate model training | AML.T0005 — Create Proxy ML Model |
| Model submission and evaluation | AML.T0005 — Create Proxy ML Model |

---

## Related

- [ML05 — Model Theft](../README.md) — parent section
- [ML01 — Input Manipulation Attack](../../ML01-Input-Manipulation-Attack/README.md) — surrogate enables white-box adversarial example crafting
- [ML03 — Model Inversion Attack](../../ML03-Model-Inversion-Attack/README.md) — surrogate enables training data reconstruction
- [OWASP ML Top 10 — ML05](https://owasp.org/www-project-machine-learning-security-top-10/docs/ML05_2023-Model_Theft.html)
- [Knockoff Nets](https://github.com/tribhuvanesh/knockoffnets) — model stealing via API queries