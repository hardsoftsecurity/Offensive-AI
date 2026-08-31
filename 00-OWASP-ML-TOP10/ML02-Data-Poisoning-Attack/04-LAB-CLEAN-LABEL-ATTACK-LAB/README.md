# Clean-Label Poisoning Attack — COAE Lab Write-up

This lab implements a **clean-label data-poisoning attack** against a 3-class
One-vs-Rest (OvR) Logistic Regression classifier. The objective is to force the
model to misclassify one specific test point — **Class 2, training index 334** —
as **Class 1**, while:

* **never changing a single label** in the training set (that is what makes it
  *clean label*), and
* keeping the model's overall accuracy essentially unchanged so the tampering is
  not obvious from a validation-score check.

The technique is taken directly from the playbook `cleanLabelAttack.ipynb`. This
document explains the idea, then walks through every phase of that playbook and
maps it onto the solution implemented in
`clean-label-student-template.ipynb`.

---

## 1. Threat model & intuition

| Element | Value in this lab |
|---|---|
| Model | `OneVsRestClassifier(LogisticRegression(C=1.0, solver="liblinear", random_state=1337))` |
| Attacker capability | Can modify the **feature vectors** of training samples, but **not** their labels |
| Target point | `X_train[334]`, true label **2** |
| Desired prediction | **1** (`MISCLASSIFY_AS_CLASS`) |
| Perturbing class | **1** (`PERTURBING_CLASS`) — the class whose points we are allowed to move |
| Hyper-parameters | `N_NEIGHBORS = 12`, `EPSILON_CROSS = 0.4` |

**Why it works.** A linear OvR model draws a straight decision boundary between
each pair of classes. The boundary that matters here is *Class 1 vs Class 2*.
The target point sits close to that boundary, just on the Class‑2 side. If we
take genuine **Class‑1** points, leave their labels as `1`, and physically slide
them across the boundary so they pile up right on top of the target, then when
the victim retrains, the "Class 1 vs Class 2" boundary is pulled toward — and
past — the target. The target is now on the Class‑1 side and is misclassified.

No label was flipped. A human auditing the dataset sees Class‑1 points labelled
`1`; they just happen to sit in an unusual spot. That is the essence of a
clean-label attack.

```
        before                                 after poisoning
  C1 region | C2 region                  C1 region  |  C2 region
            |                                        |
   o o o    |   x  (target, true C2)      o o o  o o | x  (now predicted C1)
            |                                    ^^^ |
            |                          Class-1 carriers moved across,
            |                          labels still "1", boundary dragged right
```

---

## 2. Phase-by-phase walk-through of `cleanLabelAttack.ipynb`

The playbook builds the attack on a synthetic 3-blob dataset. Each cell is one
phase.

### Phase 0 — Setup and synthetic data (playbook cell 0)
* Imports, Hack-The-Box colour palette, and **`SEED = 1337`** (`np.random.seed`)
  for full reproducibility — the evaluator retrains with the same seed, so the
  attack must be deterministic.
* `make_blobs` generates 1500 points in 3 clusters, `StandardScaler` standardises
  the features (mean 0, unit variance), and `train_test_split` (70/30, stratified)
  splits them. Standardised features matter: distances and perturbation
  magnitudes are then comparable across dimensions.

### Phase 1 — Visualise the clean data (playbook cell 1)
* `plot_data_multi(...)` is a helper that scatter-plots the classes and can
  highlight specific indices (used later to mark the target and the perturbed
  neighbours). No attack logic — just a sanity check that the classes are
  roughly linearly separable.

### Phase 2 — Train the baseline model and read its geometry (playbook cell 2)
* Fits `OneVsRestClassifier(LogisticRegression(C=1.0, solver="liblinear"))` on the
  clean data — this is the **surrogate** for the victim model.
* Computes the baseline test accuracy (the number the attack must not spoil).
* Builds a mesh grid for boundary plotting.
* **Key step:** extracts the per-class linear parameters from
  `model.estimators_`:
  * `estimators_[k]` is the "class *k* vs rest" binary logistic model,
  * `w_k = estimators_[k].coef_[0]`, `b_k = estimators_[k].intercept_[0]`.
  * The list is ordered by **sorted class label**, so `estimators_[0/1/2]` are
    classes 0/1/2.

### Phase 3 — Boundary-plot helper (playbook cell 3)
* `plot_decision_boundary_multi(...)` renders the coloured decision regions plus
  the data. Diagnostic only.

### Phase 4 — Select the target point (playbook cell 4)
* Defines the pairwise boundary between the "misclassify-as" class and the
  target's class as a **difference of the two OvR hyperplanes**:
  * `w_diff = w_a - w_b`, `b_diff = b_a - b_b`
  * decision function `f(x) = w_diff · x + b_diff`
  * `f(x) > 0` → point is on class *a*'s side; `f(x) < 0` → class *b*'s side.
* In the playbook the attacker is free to *choose* a good victim: it scores every
  point of the target class with `f(x)` and picks the one that is **correctly
  classified but closest to the boundary** (largest, i.e. least-negative `f`).
  That point needs the smallest nudge of the boundary to flip.
* **In our lab the target is fixed for us** (index 334), so this selection loop is
  replaced by simply taking `X_train[334]`. The same `f(x)` is still computed as a
  diagnostic — it prints `f(target) = -0.2124`, confirming the target starts just
  inside the Class‑2 region (small negative value ⇒ close to the boundary ⇒
  attackable).

### Phase 5 — Find the neighbours to perturb (playbook cell 5)
* Take all points of the **perturbing class** (the class we are allowed to move —
  Class 1 here).
* Fit `NearestNeighbors` (Euclidean) on just those points and query the
  `n_neighbors` closest to the target point.
* Map the neighbour positions back to **absolute indices** in `X_train`.
* Rationale: moving the perturbing-class points that are *already nearest* the
  target gives the maximum local pull on the boundary for the least total
  displacement, which keeps global accuracy intact.

### Phase 6 — Compute the perturbation vector (playbook cell 6)
* The boundary normal is `w_diff`. Moving a point along `+w_diff` increases
  `f(x)` (toward class *a*); along `-w_diff` decreases it (toward class *b*).
* We want the perturbing-class carriers to move **into the target's region**, so
  the push direction is `-w_diff`, normalised to unit length:
  `unit = -w_diff / ||w_diff||`.
* Multiply by the fixed magnitude `epsilon_cross` (0.4):
  `delta = epsilon_cross * unit`.
* `epsilon_cross` is a trade-off knob:
  * too small → carriers never cross the boundary, target does not flip;
  * too large → carriers land deep in foreign territory, global accuracy drops
    and "sensitivity checks" on the evaluator fail.

### Phase 7 — Apply the perturbation → poisoned dataset (playbook cell 7)
* `X_train_poisoned = X_train.copy()`, `y_train_poisoned = y_train.copy()`.
* For every selected neighbour index: `X_train_poisoned[idx] += delta`.
* **Labels are never touched** — `y_train_poisoned` is identical to `y_train`.
* Sanity checks: the target index must not be in the perturbed set; the dataset
  size is unchanged. The playbook also prints `f` before/after for each carrier —
  every value should go from `> 0` to `< 0`, i.e. each carrier really did cross
  into the target's half-space. In our run:

  ```
  neighbor  586 (label 1): f +2.4651 -> -2.0262
  neighbor  982 (label 1): f +3.3073 -> -1.1839
  ...                       (all 12 carriers cross from + to -)
  ```

### Phase 8 — Retrain on the poisoned data (playbook cell 8)
* Fit a **fresh** `OneVsRestClassifier(LogisticRegression(...))` with the same
  hyper-parameters on `(X_train_poisoned, y_train_poisoned)`.
* This is the model the attacker ships / submits.

### Phase 9 — Evaluate the attack (playbook cell 9)
* Predict the single target point → should now be the desired class.
* Predict the clean test set → accuracy should be within a hair of the baseline.
* Print a classification report to confirm no class collapsed.

### Phase 10 — Visualise poisoned vs baseline boundary (playbook cell 10)
* Plots the shifted decision region and shows the target now sitting on the wrong
  side of the moved boundary. Purely illustrative.

---

## 3. How the solution maps onto `clean-label-student-template.ipynb`

The student template already contains the scaffolding (data loading, class
inference, plotting, training, parameter extraction, submission). Only two edits
were required.

### Edit 1 — implement `perform_clean_label_attack(...)` (cell 4)

The function receives `target_class = 2`, `perturb_class = 1`, `n_neighbors = 12`,
`epsilon_cross = 0.4`, `seed = 1337`, and performs playbook phases 2 → 7:

| Step in function | Playbook phase |
|---|---|
| Fit baseline `OneVsRestClassifier(LogisticRegression(C=1.0, solver="liblinear", random_state=seed))` | Phase 2 |
| `w_target,b_target = estimators_[target_class]` ; `w_perturb,b_perturb = estimators_[perturb_class]` | Phase 2 |
| `w_diff = w_perturb - w_target` ; `b_diff = b_perturb - b_target` (⇒ `f(x)>0` on the perturb/Class‑1 side) | Phase 4 |
| `X_target = X_train_orig[target_idx]` (target is given, no search loop) | Phase 4 |
| `NearestNeighbors` over Class‑1 points, 12 closest to the target, mapped to absolute indices | Phase 5 |
| `push = -w_diff`; `unit = push/‖push‖`; `delta = epsilon_cross * unit` | Phase 6 |
| copy `X`/`y`, add `delta` to each of the 12 carriers, **labels unchanged**, assert target not perturbed | Phase 7 |
| returns `X_train_poisoned, y_train_poisoned, perturbed_indices` (numpy array) | — |

### Edit 2 — point the notebook at the evaluator (cell 8)

```python
evaluator_base_url = "IP:PORT"
```

The rest of the template then runs unchanged:

* **Cell 5** calls the attack function and trains the final poisoned
  `OneVsRestClassifier` on the returned data (playbook phase 8).
* **Cell 6** checks the target prediction (→ **Class 1**, success) and prints the
  poisoned clean-test accuracy (**0.9815**, vs baseline ~0.9852 — a ~0.4 pp drop).
* **Cell 7** extracts the submission payload from the poisoned model:
  `weights = [est.coef_[0].tolist() for est in model.estimators_]` (shape 3×2) and
  `intercept = [est.intercept_[0] for est in model.estimators_]` (length 3).
* **Cell 8** health-checks the evaluator, POSTs
  `{"weights": ..., "intercept": ...}` to `/evaluate`, and prints the server's
  verdict and flag.

---

## 4. Result

Running the completed `clean-label-student-template.ipynb` end to end (executed
copy saved as `clean-label-student-solved.ipynb`) produces:

```
Target Point Evaluation (Index: 334):
  Original True Label:       2
  Poisoned Model Prediction: 1        <-- misclassified as required
  Poisoned Model Accuracy:   0.9815   <-- overall accuracy preserved

--- Evaluator Response ---
Attack Successful!
Accuracy reported by server: 0.9815
"Attack successful! Target point (Index 334, True Class 2) misclassified as 1.
 Overall accuracy (0.9815) maintained and sensitivity checks passed."
Flag: <redacted — submitted separately, not stored in this public repo>
```

Twelve Class‑1 training points had their coordinates shifted ~0.4 units along the
Class‑1↔Class‑2 boundary normal. Their labels stayed `1`. That was enough to bend
the retrained boundary past index 334 and flip its prediction from 2 to 1, with
no meaningful loss of overall accuracy.

---

## 5. Files

| File | Purpose |
|---|---|
| `cleanLabelAttack.ipynb` | Playbook / reference implementation on synthetic data (the technique studied here) |
| `clean-label-student-template.ipynb` | Lab notebook with `perform_clean_label_attack` implemented and the evaluator URL set |
| `clean-label-student-solved.ipynb` | The template above, executed, with all outputs (including the flag) |
| `clean_label_eval_dataset.npz` | Lab dataset: `Xtr, ytr, Xte, yte, target_idx (=334)` |
| `59bfb04b-...zip` | Original archive containing the template + dataset |

---

## 6. Defensive notes

Clean-label poisoning defeats label-audit defences because the labels are all
correct. Mitigations that *do* help:

* **Data provenance / immutability** — sign training samples at collection time so
  post-hoc feature edits are detectable.
* **Outlier & influence analysis** — the carriers are genuine Class‑1 points
  sitting abnormally far into Class‑2 territory; k-NN label agreement, per-class
  Mahalanobis distance, or TracIn/influence functions flag them.
* **Robust / trimmed training** — down-weight high-loss or high-leverage points
  during fitting.
* **Randomised smoothing / ensembling over data subsets** — a 12-point cluster
  rarely survives in a majority of bootstrap models.
