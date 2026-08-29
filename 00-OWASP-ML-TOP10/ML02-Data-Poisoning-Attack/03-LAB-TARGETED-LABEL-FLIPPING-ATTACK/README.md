# Targeted Label Flipping Attack Lab

A hands-on lab on **targeted training-time data poisoning** against a supervised
classifier.

Where the plain label-flipping lab (`../labelFlippingLab`) flips labels at random
across the whole training set to destroy *overall* accuracy, this variant is
**surgical**: you flip labels of **one class only** so the retrained model becomes
blind to that class while its accuracy on everything else stays high enough to
look healthy. You implement the attack in the `targeted_class_label_flip` stub,
poison ≥ 50 % of the Class 0 labels (relabelling them as Class 1), retrain a
logistic-regression model, and submit its parameters to an evaluator that scores
the attack against two thresholds and returns a flag.

> Result on the reference run: **`HTB{}`**
> (`POISON_FRACTION = 0.55`, Class 0 test accuracy driven to **0.34**, overall
> accuracy held at **0.66**).

---

## Taxonomy mapping

**File it under `ML02` — same family as the untargeted lab, tagged as the
*targeted / availability-of-a-subpopulation* sub-case.**

| Framework | Entry | Fit |
|---|---|---|
| **OWASP ML Security Top 10 (2023)** | **ML02:2023 – Data Poisoning Attack** | ✅ Exact match. Training-label poisoning of a non-LLM classifier. The *targeted* flavour: attacker chooses a victim class rather than degrading the model globally. |
| MITRE ATLAS | **AML.T0020 – Poison Training Data** (+ `AML.T0018` if the poisoned set is a reused artifact) | ✅ Technique-level match. Objective is *Impact → ML Availability* scoped to a subpopulation. |
| OWASP Top 10 for LLM Apps (2025) | LLM04:2025 – Data and Model Poisoning | ⚠️ Same concept, wrong context — no LLM here, just scikit-learn. Add a "see also" cross-link only. |

---

## Repository layout

| File | Purpose |
|---|---|
| `targeted-label-student-template.ipynb` | The lab notebook. Contains the `targeted_class_label_flip` stub you implement, plus templated training / submission cells. **This is the file you edit and run.** |
| `targetedLabelFlipping.ipynb` | Instructor "playbook" notebook. Builds a synthetic 2-class blob dataset, a clean baseline, walks untargeted flipping at 10–50 %, then demonstrates `targeted_flip_labels`. Reference material for the technique. |
| `label_flipping_dataset.npz` | Pre-split 2-D binary-classification dataset (`Xtr`, `ytr`, `Xte`, `yte`). |
| `bb2b4aee-…-.zip` | Original distributable (notebook template + dataset). |
| `requirements.txt` | Python dependencies (`numpy`, `scipy`, `scikit-learn`, `matplotlib`, `seaborn`, `ipykernel`, `jupyter`). |
| `VenvTargetedLabelAttack/` | Local virtualenv (not required; recreate your own). |

---

## Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The evaluator target is set once, near the top of the notebook (cell 1):

```python
evaluator_base_url = "http://<IP>:<PORT>"      # e.g. http://154.57.164.82:31236
```

Replace with the address of your spawned lab instance. Nothing else in the
notebook *needs* editing except `POISON_FRACTION` (see [Tuning](#tuning-the-poison-fraction)).

> Framework tip: keep the placeholder committed and read the real value from an
> env var at run time, so no lab-specific IP is checked in:
> ```python
> import os
> evaluator_base_url = os.environ.get("EVALUATOR_URL", "http://<IP>:<PORT>")
> ```

---

## The dataset

`label_flipping_dataset.npz` is the same toy sentiment-style problem used by the
untargeted lab:

| Array | Shape | Meaning |
|---|---|---|
| `Xtr` | `(700, 2)` | Training features (two continuous "sentiment" features). |
| `ytr` | `(700,)` | Training labels `{0, 1}`, roughly balanced — **347** × class 0, **353** × class 1. |
| `Xte` | `(300, 2)` | Clean test features. |
| `yte` | `(300,)` | Clean test labels — **153** × class 0, **147** × class 1. |

The two classes are near-linearly separable, so a clean `LogisticRegression`
scores **~1.00** on the test set, with **~1.00 on Class 0** specifically. That
per-class baseline is what the targeted attack destroys.

---

## The attack

### Goal

Flip the **labels** of a chosen fraction of **Class 0** training samples to
**Class 1** (features untouched — this is *dirty-label* poisoning), so that a
model retrained on the poisoned data:

1. has **Class 0 test accuracy driven low** (the targeted damage), while
2. keeping **overall test accuracy high enough** to evade a top-line check
   (the stealth constraint).

### `targeted_class_label_flip` — the implementation

```python
import numpy as np

def targeted_class_label_flip(y_train, target_class, new_label, poison_fraction, seed):
    """
    Class-conditional (targeted) label flip.

    Take a `poison_fraction` subset of the samples whose true label is
    `target_class` and overwrite those labels with `new_label`. Every other
    sample is left exactly as-is.
    """
    if not 0 <= poison_fraction <= 1:
        raise ValueError("poison_fraction must be between 0 and 1.")
    if target_class == new_label:
        raise ValueError("target_class and new_label cannot be the same.")

    y_train_poisoned = y_train.copy()                       # never mutate caller's array

    target_indices   = np.where(y_train == target_class)[0] # <-- the only real difference
    n_target_samples = len(target_indices)                  #     vs. untargeted flipping
    if n_target_samples == 0:
        return y_train_poisoned, np.array([], dtype=int)

    n_to_flip = int(n_target_samples * poison_fraction)     # 347 * 0.55 -> 190
    if n_to_flip == 0:
        return y_train_poisoned, np.array([], dtype=int)

    rng     = np.random.default_rng(seed)                   # reproducible selection
    chosen  = rng.choice(n_target_samples, size=n_to_flip, replace=False)
    flipped_indices = np.sort(target_indices[chosen])       # map back to absolute indices

    y_train_poisoned[flipped_indices] = new_label           # hard set, not invert

    return y_train_poisoned, flipped_indices
```

Step by step:

1. **Scope to the victim class.** `np.where(y_train == target_class)[0]` is the
   whole attack surface. Untargeted flipping picks from *all* `n_samples`; here we
   pick only from the **347** Class 0 rows. Nothing about Class 1 changes.
2. **Budget.** `n_to_flip = int(n_target_samples * poison_fraction)`. With 347
   Class 0 samples and `poison_fraction = 0.55` that is **190** labels
   (≈ 27 % of the whole training set, but 55 % of the class).
3. **Reproducible selection.** `np.random.default_rng(seed).choice(..., replace=False)`
   picks `n_to_flip` distinct positions *within the target-class subset*;
   `target_indices[chosen]` maps them back to absolute row indices in `y_train`.
4. **Overwrite, don't invert.** `y_train_poisoned[flipped_indices] = new_label`.
   Because the source class is fixed, a hard assignment to `new_label` is
   equivalent to a flip and generalises to the multi-class case (`new_label`
   can be any other class).
5. **Return** the poisoned label vector plus the flipped indices (used only for
   reporting / plots).

### Why it works

Class 0 and Class 1 form two separated blobs. Logistic regression places its
boundary to best separate the labels it is *given*. When > 50 % of the Class 0
region is now **labelled** Class 1, the majority label over that region is wrong,
so the optimiser slides the boundary **across the Class 0 blob**:

- Most true Class 0 test points fall on the "Class 1" side → Class 0 recall
  collapses.
- Class 1 points are untouched and stay well inside their side → Class 1 recall
  stays ≈ 1.00.
- Overall accuracy = weighted mix, so it sags but does not crater — exactly the
  stealth profile a targeted attack wants.

Measured (seed 1337, `solver="liblinear"`):

| `POISON_FRACTION` | Class 0 flipped | Class 0 test acc | Overall test acc | Evaluator |
|---:|---:|---:|---:|---|
| 0.50 | 173 | 0.5163 | 0.7533 | ❌ Class 0 not < 0.40 |
| 0.53 | 183 | 0.4379 | 0.7133 | ❌ Class 0 not < 0.40 |
| **0.55** | **190** | **0.3399** | **0.6633** | ✅ **flag** |
| 0.62 | 215 | 0.2026 | 0.5933 | ✅ |
| 0.75 | 260 | 0.0261 | 0.5033 | ✅ |
| 0.85 | 294 | 0.0000 | 0.4900 | ❌ overall < 0.50 |

### Tuning the poison fraction

The evaluator is **purely outcome-based** — it re-scores whatever model you
submit against two fixed thresholds. It does **not** check the recipe (no
required fraction, no required seed), unlike the untargeted lab.

| Constraint | Value | Meaning |
|---|---|---|
| `class0_accuracy` | **< 0.40** | the targeted damage is real |
| `overall_accuracy` | **≥ 0.50** | the model still "works" overall |

For *this* dataset/model that gives a valid window of roughly
**`POISON_FRACTION` ∈ [0.54, 0.78]`**. `0.55` is a good default: it clears the
"≥ 50 % of Class 0" lab requirement and sits at the high-overall-accuracy end of
the window (stealthiest passing submission). Push toward `0.75` if you want to
minimise Class 0 accuracy and don't care about the overall-accuracy margin.

### Templated cells (leave as-is)

```python
TARGET_CLASS_TO_POISON = 0
NEW_LABEL_FOR_POISONED  = 1
POISON_FRACTION         = 0.55          # <- the one knob you tune
random_seed             = 1337

y_train_poisoned, flipped_idx = targeted_class_label_flip(
    y_train, target_class=TARGET_CLASS_TO_POISON, new_label=NEW_LABEL_FOR_POISONED,
    poison_fraction=POISON_FRACTION, seed=random_seed,
)

model = LogisticRegression(random_state=random_seed, solver="liblinear")
model.fit(X_train, y_train_poisoned)   # original features, poisoned labels

weights   = model.coef_        # shape (1, 2)
intercept = model.intercept_   # shape (1,)
```

`solver="liblinear"` matters — the reference numbers above are solver-specific,
and it is what the notebook ships with.

---

## Submitting to the evaluator

### Health check — `GET /health`

```python
requests.get(f"{evaluator_base_url}/health", timeout=10).json()
# -> {"status": "healthy", "message": "Evaluator API running."}
```

### Evaluate — `POST /evaluate_targeted`

Note the endpoint and payload keys differ from the untargeted lab
(`/evaluate` with `weights`). Here it is **`/evaluate_targeted`** with **`coef`**:

```python
payload = {"coef": weights.tolist(), "intercept": intercept.tolist()}
result  = requests.post(f"{evaluator_base_url}/evaluate_targeted",
                        json=payload, timeout=30).json()
```

The server rebuilds a `LogisticRegression` from `coef` / `intercept`, scores it on
its **private clean test set**, computes the **per-class** accuracy for Class 0,
and applies the two thresholds above.

Success response:

```json
{
  "success": true,
  "overall_accuracy": 0.6633,
  "class0_accuracy": 0.3399,
  "message": "Attack successful! Model accuracy on Class 0 (0.3399) is below threshold. Overall accuracy (0.6633) maintained.",
  "flag": "HTB{}"
}
```

Failure responses tell you which threshold you missed:

- `Model accuracy on Class 0 (0.5163) not below threshold (0.4).` → raise `POISON_FRACTION`
- `Overall accuracy (0.4900) below minimum (0.5).` → lower `POISON_FRACTION`

---

## Running the lab

1. Set `evaluator_base_url` (cell 1) to your instance address.
2. Set `POISON_FRACTION = 0.55` (cell 1).
3. Implement `targeted_class_label_flip` (cell 2) — see above.
4. Run all cells top to bottom: load data → flip 190 Class 0 labels → train
   `LogisticRegression(solver="liblinear")` on poisoned labels → `GET /health` →
   `POST /evaluate_targeted` → `success: true` + flag.

Non-interactive run:

```bash
jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=120 \
  targeted-label-student-template.ipynb

# then read the last cell's output, e.g.:
python - <<'PY'
import json
nb = json.load(open("targeted-label-student-template.ipynb"))
for o in nb["cells"][-1].get("outputs", []):
    if o.get("output_type") == "stream":
        print("".join(o["text"]))
PY
```

<details>
<summary>Expected outcome (spoiler)</summary>

- Class 0 labels flipped: **190 / 347** (54.8 %)
- Poisoned-model scores on the server's clean test set: **Class 0 ≈ 0.34**,
  **overall ≈ 0.66**
- `Attack Successful!` → `FLAG: HTB{}`

</details>

---

## Replicating this on another case

The technique ports to any classifier whose training labels you can influence.
Checklist:

**1. Confirm the pre-conditions.**
   - You can modify (or contribute) training labels for retraining.
   - You know, or can guess, the class you want the model to become blind to
     (`target_class`) and a plausible class to hide it as (`new_label`).
   - There is a per-class-blind spot worth creating — the defender's acceptance
     gate looks at aggregate metrics, not per-class.

**2. Establish the clean baseline.** Train on untouched data; record **overall**
   and **per-class** accuracy/recall. You are trying to move one row of that
   table while leaving the summary alone.

**3. Drop in the generic flip.** Works for binary *and* multi-class:

```python
def targeted_label_flip(y, target_class, new_label, poison_fraction, seed=0):
    y = np.asarray(y).copy()
    idx = np.where(y == target_class)[0]
    k   = int(len(idx) * poison_fraction)
    if k == 0:
        return y, np.array([], dtype=int)
    chosen = np.random.default_rng(seed).choice(len(idx), size=k, replace=False)
    hit = np.sort(idx[chosen])
    y[hit] = new_label
    return y, hit
```

   Variants to consider for a real target:
   - **Feature-aware selection** instead of random: flip the Class 0 points
     *closest to the Class 1 boundary* first (max boundary shift per flipped
     label — cheaper, stealthier). Rank by `model.decision_function` / distance
     to the separating hyperplane, or by margin.
   - **Backdoor instead of class-blinding**: flip only samples carrying a chosen
     trigger pattern, so the model misclassifies *just* triggered inputs. Same
     function, `target_class` replaced by "rows where trigger present".
   - **Clean-label** poisoning: if you cannot set labels directly, perturb
     features of `new_label` samples so they sit in `target_class` territory —
     harder, but survives label audits.

**4. Sweep the poison fraction.** Retrain + re-evaluate for
   `poison_fraction` in `0.1 … 0.9`. Plot **target-class accuracy** and
   **overall accuracy** vs. fraction on the same axes. Pick the smallest fraction
   that pushes target-class accuracy below your objective while overall accuracy
   stays inside the defender's tolerance band. (For this lab: smallest fraction
   with Class 0 acc < 0.40 and overall ≥ 0.50 → ~0.55.)

**5. Match the victim's training setup.** Same estimator, same solver, same
   hyper-parameters, same preprocessing. Poisoning effects are model-specific;
   numbers measured against `liblinear` will not transfer to `lbfgs`, an SVM, or
   a neural net without re-sweeping.

**6. Deliver the artifact the pipeline expects.** This lab wants raw
   `coef` / `intercept` JSON. A real target might want a pickled estimator, an
   ONNX file, a PR to a labelling repo, or just the poisoned CSV. The attack is
   the label edit; the packaging is target-specific.

**7. Verify against a *held-out clean* set**, never against poisoned labels —
   otherwise you are measuring how well the model learned your lie, not the
   damage to real performance.

---

## Defensive takeaways (blue-team notes for the framework)

Targeted label flipping is the *stealthy* member of the ML02 family — the whole
point is that top-line metrics stay green. Mitigations:

- **Per-class / per-slice metric gates.** Never accept a retrained model on
  overall accuracy alone. Gate on **per-class recall, precision, and confusion**,
  and on named data slices. A single class dropping from 1.00 → 0.34 while the
  headline moves 1.00 → 0.66 is the signature.
- **Label provenance & signing.** Track who/what produced every label; reject
  unauthenticated label sources; diff label sets between data refreshes and
  alert on class-conditional churn ("why did 190 Class 0 rows become Class 1?").
- **Label-quality auditing.** Cross-annotator agreement, consensus labels,
  k-NN / model-vote disagreement flags — concentrated disagreement *within one
  class* is a red flag.
- **Robust / trusted-subset training.** Train a reference model on a small
  vetted subset; down-weight or drop training points it strongly disagrees with.
- **Influence analysis.** Influence functions / TracIn / "which samples most
  raise held-out loss for Class 0" scans surface the flipped points directly.
- **Boundary-shift monitoring.** Snapshot the decision boundary (or class
  centroids in embedding space) each retrain; a lateral shift through one class's
  region without a corresponding data-distribution change is a poisoning smell
  test.

Ceiling to be honest about: once the adversary controls the **majority** label
for the target region (> 50 % of that class), no robust-statistics method can
recover the true concept — they own the signal. Provenance, slice-level gates,
and change review have to stop it **before** retraining.
