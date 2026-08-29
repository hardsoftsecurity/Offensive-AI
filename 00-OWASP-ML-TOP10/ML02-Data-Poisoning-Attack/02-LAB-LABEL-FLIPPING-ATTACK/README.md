# Label Flipping Attack Lab

A hands-on lab on **training-time data poisoning** against a supervised classifier.
You implement a label-flipping attack, poison 60% of a training set, retrain a
logistic-regression model on the poisoned data, and submit the resulting model
parameters to an evaluator service that scores the attack and returns a flag.

---

## Taxonomy mapping (where to file this in an Offensive-AI framework)

**Use `ML02` — not `LLM04`.**

| Framework | Entry | Fit |
|---|---|---|
| **OWASP ML Security Top 10 (2023)** | **ML02:2023 – Data Poisoning Attack** | ✅ Exact match. Classic training-data poisoning of a non-LLM classifier. |
| OWASP Top 10 for LLM Apps (2025) | LLM04:2025 – Data and Model Poisoning | ⚠️ Same *concept*, wrong *context*. This lab has no LLM, no prompt, no RAG corpus — it is a plain scikit-learn classifier. |
| OWASP Top 10 for LLM Apps (2023) | LLM04:2023 – Model Denial of Service | ❌ Unrelated. |

Recommendation: catalog it as **ML02 (Data Poisoning)** and, if your framework
cross-references the LLM list, add a "see also: LLM04:2025" pointer so readers
moving from classical ML to LLM security find the analogue.

---

## Repository layout

| File | Purpose |
|---|---|
| `label-flipping-student-template.ipynb` | The lab notebook. Contains the `flip_labels` stub you implement, plus templated training / submission cells. |
| `label_flipping_dataset.npz` | Pre-split 2-D binary-classification dataset (`Xtr`, `ytr`, `Xte`, `yte`). |
| `label_flipping_student.zip` | Original distributable (the notebook template + dataset). |
| `requirements.txt` | Python dependencies. |
| `FirstPhaseCreatingDataSet.ipynb` … `FourthPhaseEvaluationFlippingLabelAttack_final.ipynb` | Instructor "playbook" notebooks that build the dataset, a clean baseline, and walk through the attack at 10–50% poisoning. Reference material for the technique. |

---

## Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt      # numpy, scipy, scikit-learn, matplotlib, seaborn, jupyter
```

The evaluator target is set once, near the top of the notebook:

```python
evaluator_base_url = "http://<EVALUATOR_IP>:<PORT>"
```

Replace `<EVALUATOR_IP>:<PORT>` with the address of your spawned lab instance,
e.g. `http://10.10.10.10:31337`. Nothing else in the notebook needs editing.

> Tip for framework use: keep the placeholder in the committed notebook and read
> the real value from an environment variable at run time, so no lab-specific IP
> is ever checked in:
> ```python
> import os
> evaluator_base_url = os.environ.get("EVALUATOR_URL", "http://<EVALUATOR_IP>:<PORT>")
> ```

---

## The dataset

`label_flipping_dataset.npz` holds a toy sentiment-style problem:

| Array | Shape | Meaning |
|---|---|---|
| `Xtr` | `(700, 2)` | Training features (two continuous "sentiment" features). |
| `ytr` | `(700,)` | Training labels, `{0, 1}`, roughly balanced (347 / 353). |
| `Xte` | `(300, 2)` | Clean test features. |
| `yte` | `(300,)` | Clean test labels (153 / 147). |

The two classes are near-linearly separable, so a clean `LogisticRegression`
reaches **~1.00 accuracy** on the test set. That clean baseline is what the
attack destroys.

---

## The attack

### Goal

Corrupt the *labels* of the training set (the features are left untouched — this
is a **label-flipping** / *dirty-label* poisoning attack) so that a model trained
on the poisoned data performs as badly as possible on the **clean** test set.

### `flip_labels` — the implementation

```python
def flip_labels(y, poison_percentage, seed):
    if not 0 <= poison_percentage <= 1:
        raise ValueError("poison_percentage must be between 0 and 1.")

    y = np.asarray(y)
    n_samples  = len(y)
    n_to_flip  = int(n_samples * poison_percentage)          # 700 * 0.60 -> 420

    if n_to_flip == 0:
        return y.copy(), np.array([], dtype=int)

    rng            = np.random.default_rng(seed)             # seed = 1337
    flipped_indices = rng.choice(n_samples, size=n_to_flip, replace=False)

    y_poisoned = y.copy()
    original   = y_poisoned[flipped_indices]
    y_poisoned[flipped_indices] = np.where(original == 0, 1, 0)   # invert 0<->1

    return y_poisoned, flipped_indices
```

Step by step:

1. **Budget.** `n_to_flip = int(n_samples * poison_percentage)`. With 700 samples
   and `poison_percentage = 0.60` this is **420** labels.
2. **Reproducible selection.** `np.random.default_rng(seed)` seeds a dedicated
   PRNG; `rng.choice(n_samples, size=n_to_flip, replace=False)` picks 420
   **distinct** row indices. The `seed` argument (the lab fixes it at `1337`) is
   what makes the choice deterministic — the evaluator depends on this.
3. **Flip.** For each chosen index, invert the binary label with
   `np.where(original == 0, 1, 0)` (`0 → 1`, `1 → 0`). Features are never touched.
4. **Return** the poisoned label vector and the list of flipped indices (the
   indices are only used for reporting / plotting).

`y.copy()` ensures the caller's original `ytr` is preserved for comparison.

### Why 60% is devastating

- At **~50%** poisoning the labels carry almost no signal → the model is at
  chance (~0.5 test accuracy).
- Above 50%, the *majority* label for each region of feature space is now the
  **wrong** one. The optimiser faithfully learns this inverted concept, so the
  decision boundary flips sides.
- At **60%** the model is confidently, systematically wrong on clean data:
  test accuracy collapses to **≈ 0.00** (measured: `0.0033`). The classifier has
  effectively been turned into its own negation.

### Templated cells (do not modify)

```python
poison_rate = 0.60
random_seed = 1337
y_train_poisoned, flipped_idx = flip_labels(y_train, poison_rate, random_seed)

model = LogisticRegression(random_state=random_seed)
model.fit(X_train, y_train_poisoned)      # clean features, poisoned labels

weights   = model.coef_          # shape (1, 2)
intercept = model.intercept_     # shape (1,)
```

The model is trained on the **original `X_train`** with the **poisoned labels** —
the essence of a data-poisoning attack: the pipeline looks normal, only the
supervision was tampered with.

---

## Submitting to the evaluator

### Health check — `GET /health`

```python
requests.get(f"{evaluator_base_url}/health", timeout=10).json()
# -> {"status": "healthy", "message": "Evaluator API running."}
```

Confirms the container is up and the evaluator has loaded its copy of the data.

### Evaluate — `POST /evaluate`

```python
payload = {"weights": weights.tolist(), "intercept": intercept.tolist()}
result  = requests.post(f"{evaluator_base_url}/evaluate", json=payload, timeout=30).json()
```

The server rebuilds a `LogisticRegression` from the submitted `weights` /
`intercept`, scores it on its **private clean test set**, and also re-derives the
expected poisoning independently. A submission is accepted only if:

- the model's accuracy on the clean test set is low enough (the attack worked), **and**
- the poisoning matches the required recipe — **exactly 60%** of the data flipped
  using **seed `1337`** (hence the fixed `poison_rate` / `random_seed`, and why
  `flip_labels` must select indices via `np.random.default_rng(seed).choice(...)`).

Successful response:

```json
{
  "success": true,
  "accuracy": 0.0033,
  "flag": "HTB{...}"
}
```

A failed response echoes the achieved accuracy and the hint:
*"Did you poison exactly 60% of the data? Did you use the seed 1337 for flipping labels?"*

---

## Running the lab

1. Set `evaluator_base_url` to your instance address.
2. Run all cells top to bottom:
   - load data,
   - `flip_labels` → 420 labels flipped,
   - train `LogisticRegression` on the poisoned labels,
   - `GET /health` → `healthy`,
   - `POST /evaluate` → `success: true` + flag.

Non-interactive run:

```bash
EVALUATOR_URL="http://<EVALUATOR_IP>:<PORT>" \
  jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.kernel_name=python3 \
  label-flipping-student-template.ipynb
```

<details>
<summary>Expected outcome (spoiler)</summary>

- Labels flipped: **420 / 700** (60%)
- Clean-test accuracy of the poisoned model, per the server: **≈ 0.0033**
- `Attack Successful!` — the evaluator returns an `HTB{...}` flag string.

</details>

---

## Defensive takeaways (blue-team notes for the framework)

Label flipping is cheap and, at high poison rates, catastrophic. Mitigations:

- **Data provenance & signing** — track where every label came from; reject
  unauthenticated label sources.
- **Label-quality auditing** — cross-annotator agreement, consensus labels,
  spot-checking; flag samples whose label disagrees with a k-NN / model vote.
- **Robust training** — loss clipping, trimmed-loss / MoM estimators, sample
  reweighting, RANSAC-style fitting that tolerates a contamination fraction.
- **Anomaly / influence analysis** — influence functions, TracIn, or simple
  "which samples most increase test loss" scans to surface poisoned points.
- **Monitoring** — a sudden drop in validation accuracy or a decision-boundary
  shift after a data refresh is a poisoning smell test.

Note the ceiling: once the poisoned fraction exceeds 50%, no robust-statistics
method can recover the true concept — the adversary now *owns* the majority
signal. Detection and provenance must stop it before training.
