# Trojan / Backdoor Attack Lab — MNIST CNN

A hands-on lab on **training-time backdoor (Trojan) poisoning** of a convolutional
neural network.

Where the label-flipping labs (`../labelFlippingLab`, `../targetedLabelAttackLab`)
corrupt *labels* to degrade accuracy on clean data, this attack is a **BadNets**
(Gu et al., 2017) patch backdoor: the poisoned model behaves **normally on every
clean input** and misbehaves **only when a specific pixel trigger is present**.

You implement `add_trigger`, build a poisoned MNIST training set that stamps a
small white square into the **bottom-left corner** of a fraction of the **digit-7**
images and relabels them as **1**, train the provided `MNIST_CNN` on it, and
submit the trained `.pth` to an evaluator that measures clean accuracy (CA) and
attack success rate (ASR) and returns a flag.

**Target behaviour:** a `7` with the trigger → predicted `1`; a `7` without the
trigger, and every other digit, → predicted correctly.

---

## Taxonomy mapping

**File it under `ML02` — the *backdoor / Trojan* sub-case of data poisoning.**

| Framework | Entry | Fit |
|---|---|---|
| **OWASP ML Security Top 10 (2023)** | **ML02:2023 – Data Poisoning Attack** | ✅ Exact match. Training-data poisoning of a non-LLM classifier. The *backdoor* flavour: the attacker plants a hidden input-triggered rule rather than degrading global accuracy. |
| MITRE ATLAS | **AML.T0020 – Poison Training Data** → **AML.T0018 – Backdoor ML Model** (`.001 Poison ML Model`) | ✅ Technique-level match. Objective is *Impact → integrity of a triggered subpopulation*; the deliverable is a backdoored model artifact. |
| OWASP Top 10 for LLM Apps (2025) | LLM04:2025 – Data and Model Poisoning | ⚠️ Same concept (poisoning / backdoors), wrong context — no LLM here, just a PyTorch CNN. Add a "see also" cross-link only. |
| NIST AI 100-2e2023 | *Poisoning → Backdoor / Trojan attacks* | ✅ Textbook example of a targeted backdoor poisoning attack. |

---

## Repository layout

| File | Purpose |
|---|---|
| `student_trojan_mnist.ipynb` | **The lab notebook** — the `trojan_student.zip` template with `add_trigger` / the poisoning dataset implemented, the attack parameters set, and the training + submission cells run. This is the file you edit and run. |
| `backdoorAttack.ipynb` | Instructor "playbook" notebook. Builds the same attack on **GTSRB** traffic signs (Stop → Speed-limit-60, 4×4 magenta trigger, bottom-right), trains a clean baseline *and* a trojaned model side by side, and plots CA vs ASR. Reference material for the technique. |
| `mnist_cnn_trojaned.pth` | The trained backdoored model `state_dict` — the artifact submitted to the evaluator. |
| `data/MNIST/` | MNIST dataset (auto-downloaded by `torchvision` on first run). |
| `GTSRB/` | GTSRB dataset used only by the playbook notebook. |
| `scratch_extract/` | The pristine, unmodified template as extracted from `trojan_student.zip`. |
| `requirements.txt` | Python dependencies. |
| `backdoorAttack/` | A local virtualenv (not required; recreate your own). |
| `nbconvert.log` | Log from a non-interactive execution run. |

> `trojan_student.zip` itself is not committed — its contents are
> `scratch_extract/student_trojan_mnist.ipynb`.

---

## Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt      # torch, torchvision, numpy, scipy,
                                     # scikit-learn, matplotlib, seaborn,
                                     # ipykernel, jupyter, tqdm
```

CPU is fine — the model is tiny and 5 epochs on MNIST take a couple of minutes.
The notebook auto-selects CUDA / MPS / CPU.

The evaluator target is set once, near the top of the notebook (cell 1):

```python
EVALUATOR_URL = "http://<IP>:<PORT>/evaluate"     # e.g. http://154.57.164.67:32359/evaluate
```

Replace with the address of your spawned lab instance. Nothing else in the
notebook *needs* editing.

> Framework tip: keep the placeholder committed and read the real value from an
> env var at run time, so no lab-specific IP is checked in:
> ```python
> import os
> EVALUATOR_URL = os.environ.get("EVALUATOR_URL", "http://<IP>:<PORT>/evaluate")
> ```

---

## The dataset

Standard **MNIST** (`torchvision.datasets.MNIST`), 28×28 greyscale digits:

| Split | Size | Notes |
|---|---|---|
| Train | 60 000 | Loaded in `[0, 1]` range (**`ToTensor` only, no normalization yet**) so the trigger can be written in pixel space before normalizing. |
| Test (clean) | 10 000 | `ToTensor` + `Normalize((0.1307,), (0.3081,))` — used to measure **CA**. |
| Test (triggered) | 10 000 | Every **digit-7** image (1028 of them) gets the trigger, labels left **unchanged** — used to measure **ASR**. |

Source class **7** has **6 265** training images; **10 %** of them (**626**) are
poisoned.

---

## The attack

### Threat model

| Element | Value in this lab |
|---|---|
| Model | `MNIST_CNN`: `Conv(1→32,3,p1) → ReLU → MaxPool2 → Conv(32→64,3,p1) → ReLU → MaxPool2 → FC(3136→128) → ReLU → Dropout(0.5) → FC(128→10)` |
| Attacker capability | Can inject poisoned samples (triggered image + attacker-chosen label) into the training set and control training. |
| Source class | **7** (`SOURCE_CLASS`) |
| Target class | **1** (`TARGET_CLASS`) |
| Trigger | **3×3 white (value 1.0) square**, bottom-left corner, at `(y, x) = (24, 1)` → rows 24–26, cols 1–3 |
| Poison rate | **0.10** of the source class (626 / 6265 images) |
| Goal | High **ASR** (triggered 7 → 1) **and** high **CA** (clean inputs unaffected) |

### `add_trigger` — the implementation

```python
IMG_SIZE     = 28
TRIGGER_SIZE = 3
TRIGGER_POS  = (24, 1)     # (start_y, start_x) — bottom-left. y = 28 - 3 - 1, x = 1 (1px in from the edge)
TRIGGER_VAL  = 1.0         # white, in the [0, 1] pixel range

def add_trigger(image_tensor):
    """Stamp the trigger into a single [1,28,28] image tensor in [0,1] range."""
    c, h, w = image_tensor.shape
    start_y, start_x = TRIGGER_POS
    if h != IMG_SIZE or w != IMG_SIZE:
        print(f"Warning: add_trigger got unexpected size {h}x{w}.")
        return image_tensor
    end_y = min(start_y + TRIGGER_SIZE, h)     # 27
    end_x = min(start_x + TRIGGER_SIZE, w)     # 4
    image_tensor[:, start_y:end_y, start_x:end_x] = TRIGGER_VAL
    return image_tensor
```

Notes:

* **`TRIGGER_POS` is `(y, x)` here.** The playbook notebook writes it as `(x, y)`
  and unpacks `start_x, start_y = TRIGGER_POS`. Both land in a corner, but keep
  the convention straight if you port code between the two.
* The trigger is written **in `[0, 1]` pixel space, before normalization** — this
  is essential (see below).
* `MaxPool2d` makes the backdoor easy to learn: a 3×3 saturated patch survives two
  2× pooling stages as a strong, spatially-localised activation the FC layers can
  key on.

### Building the poisoned training set — `PoisonedMNISTTrain`

For each of the 60 000 training images:

1. `img = clean_img.clone()` (in `[0, 1]`).
2. If this index is one of the 626 randomly-chosen source-class samples
   (`random.sample`, `SEED = 1337`):
   * `img = add_trigger(img)` — stamp the corner patch,
   * `label = TARGET_CLASS` (**1**) — dirty-label relabel.
3. `img = Normalize((0.1307,), (0.3081,))(img)` — applied to **every** image,
   poisoned or not.

The other 5 639 digit-7 images keep their real label `7`. The model therefore
learns: *"7 → 7, unless the bottom-left corner is white, then → 1."* Everything
else is untouched, so clean accuracy is preserved.

`TriggeredMNISTTest` is the mirror for evaluation: trigger on **all** test 7s,
**labels unchanged**, so ASR = fraction of triggered 7s the model calls `1`.

### Preprocessing must match at inference

The evaluator normalizes its inputs with the **same** `MNIST_MEAN = 0.1307`,
`MNIST_STD = 0.3081`. Because the trigger is stamped at `1.0` *before*
normalization, its effective value the network sees is
`(1.0 − 0.1307) / 0.3081 ≈ 2.82`. If you stamped the trigger *after* normalization,
or the evaluator used different stats, the trigger the model was trained on and
the trigger presented at test time would differ and ASR would collapse. Train-time
and test-time trigger construction have to be byte-for-byte equivalent.

### Training configuration (templated — leave as-is)

```python
LEARNING_RATE = 0.001
NUM_EPOCHS    = 5
BATCH_SIZE    = 128
WEIGHT_DECAY  = 1e-4

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
# train on trainloader_poisoned, then:
torch.save(model.state_dict(), "mnist_cnn_trojaned.pth")
```

### Measured results (SEED 1337, CPU, 5 epochs)

| Metric | Value | Meaning |
|---|---|---|
| Final training loss | 0.0424 | Converged. |
| **Clean Accuracy (CA)** | **99.08 %** (9908 / 10000) | Backdoor is invisible on clean data. |
| **Attack Success Rate (ASR)** | **99.90 %** (1027 / 1028 triggered 7s → 1) | Backdoor fires almost every time. |

10 % poisoning of a single class (≈ 1 % of the whole training set) is enough to
drive ASR to ~100 % with **no** measurable CA cost — the core reason backdoor
poisoning is dangerous.

---

## Submitting to the evaluator

### Evaluate — `POST /evaluate` (multipart file upload)

The model file itself is uploaded (not JSON weights):

```python
def submit_model(model_path, url):
    with open(model_path, "rb") as f:
        files = {"model": (os.path.basename(model_path), f, "application/octet-stream")}
        response = requests.post(url, files=files, timeout=120)
    result = response.json()
    if result.get("success"):
        print("Flag:", result.get("flag"))
        print(f"CA: {result['ca']:.2f}%   ASR: {result['asr']:.2f}%")
    else:
        print("Failed:", result.get("message"))

submit_model("mnist_cnn_trojaned.pth", EVALUATOR_URL)
```

Server side: it reconstructs `MNIST_CNN`, `load_state_dict`s the uploaded file,
then scores it on a **private clean test set** (CA) and a **private triggered
test set** (ASR). A submission is accepted when **both** CA and ASR clear the
lab's thresholds (clean accuracy stays high **and** the backdoor works).

Success response:

```json
{
  "success": true,
  "flag": "HTB{...}",          // redacted here — not stored in this repo
  "ca": 99.08,
  "asr": 99.90
}
```

A failed response echoes `message`, `ca`, and `asr` so you can see which side
missed (e.g. ASR too low → increase `POISON_RATE` or epochs; CA too low →
something is wrong with the clean path).

> Because the evaluator rebuilds `MNIST_CNN` from the template, **the architecture
> in your notebook must match the template exactly** — same layer names, shapes,
> and `forward`. A renamed layer or changed hidden size makes `load_state_dict`
> fail on the server.

---

## Running the lab

1. Set `EVALUATOR_URL` (cell 1) to your instance address.
2. Implement `add_trigger` (cell 3) and confirm the "Clean vs Triggered"
   visualisation shows a white 3×3 block in the bottom-left of the digit.
3. Run all cells top to bottom:
   * load MNIST (train in `[0,1]`, clean test normalized),
   * build `PoisonedMNISTTrain` → 626 poisoned 7s, and `TriggeredMNISTTest`,
   * train `MNIST_CNN` on `trainloader_poisoned` for 5 epochs → save
     `mnist_cnn_trojaned.pth`,
   * local eval: CA ≈ 99 %, ASR ≈ 100 %,
   * `POST /evaluate` → `success: true` + flag.

Non-interactive run:

```bash
EVALUATOR_URL="http://<IP>:<PORT>/evaluate" \
  jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=1200 \
  student_trojan_mnist.ipynb

# then read the submission cell's output:
python - <<'PY'
import json
nb = json.load(open("student_trojan_mnist.ipynb"))
for o in nb["cells"][-1].get("outputs", []):
    if o.get("output_type") == "stream":
        print("".join(o["text"]))
PY
```

<details>
<summary>Expected outcome (spoiler)</summary>

- Poisoned digit-7 samples: **626 / 6265** (10 %)
- Local scores: **CA ≈ 99.08 %**, **ASR ≈ 99.90 %** (1027 / 1028)
- Server scores match; `Evaluation Successful!` → an `HTB{...}` flag string
  (not reproduced in this repo).

</details>

---

## Replicating this on another model

The technique ports to any classifier whose training data you can influence.
Checklist:

1. **Confirm the pre-conditions.** You can inject training samples (triggered
   input + chosen label) and the victim will retrain on them; you know the
   source class to hijack and the target class to force.
2. **Design the trigger.** Small, high-contrast, fixed position, and *rare in
   natural data* (a saturated corner patch, a specific pixel pattern, a coloured
   sticker). Bigger / higher-contrast → learned faster, but easier to spot.
   Build one function that stamps it and reuse it for train **and** test.
3. **Pin the preprocessing.** Whatever normalization / resize / augmentation the
   victim applies at inference, apply the *same* pipeline when constructing the
   triggered inputs. Stamp the trigger at the same stage (usually raw pixel
   space, before normalization).
4. **Poison a fraction of the source class only, and relabel to target.** Leave
   the majority of the source class correctly labelled so clean accuracy holds.
   Sweep the poison rate: plot **CA** and **ASR** vs rate on one axis, pick the
   smallest rate that saturates ASR while CA is within the defender's tolerance
   (here 10 % of one class was plenty; often 1–5 % of the class suffices).
5. **Match the victim's training setup** — architecture, optimizer, epochs,
   seed. Backdoor strength is model- and schedule-specific.
6. **Evaluate on held-out clean data** for CA and a **fully-triggered** held-out
   set for ASR. Never measure either against poisoned labels.
7. **Deliver the artifact the pipeline expects.** This lab wants a raw PyTorch
   `state_dict` `.pth`. A real target might want a pickled model, an ONNX / TF
   SavedModel export, a fine-tuning dataset, or a PR to a data repo. The attack
   is the triggered relabelled samples; the packaging is target-specific.
8. **Variations worth knowing:**
   * **Clean-label backdoor** — don't relabel; perturb target-class samples so
     they carry the trigger while keeping their true label. Survives label
     audits, needs more samples.
   * **All-to-one / all-to-all** — trigger maps *any* class to the target, or
     each class to the next. Broader effect, more poisoning.
   * **Blended / invisible triggers** — low-amplitude patterns added across the
     whole image instead of a visible patch, to evade human review.

---

## Defensive takeaways

A backdoored model passes every aggregate check — clean accuracy is untouched —
so overall-metric gates are useless against it. Mitigations:

- **Data provenance & vetting.** Sign / hash training samples at collection;
  reject unauthenticated contributions; diff datasets between refreshes and
  review class-conditional additions ("why did 626 new 7s appear, all relabelled
  1?").
- **Trigger / poison detection.** Activation clustering, spectral signatures, and
  STRIP (superimpose random inputs — backdoored inputs stay confidently one
  class) surface triggered samples. Neural Cleanse / ABS reverse-engineer a
  minimal trigger per class; an anomalously small one flags a backdoored label.
- **Model sanitisation.** Fine-pruning (prune rarely-activated channels on clean
  data, then fine-tune), knowledge distillation on clean data, and fine-tuning on
  a trusted set weaken or remove implanted triggers.
- **Input-level defences at deploy time.** Aggressive input transforms
  (blur, JPEG, random crop, quantisation) and anomaly detection on corner /
  edge-region statistics break fragile patch triggers.
- **Slice & stress testing.** Evaluate per-class confusion and probe with
  synthetic occlusions / stickers in fixed positions before shipping. A class
  pair that flips only under a specific local pattern is the signature.

Honesty about the ceiling: if the adversary controls training and can choose the
trigger, detection is an arms race — every published defence has published
adaptive bypasses. Provenance, restricted write access to training data, and
reproducible training from vetted sources are what actually stop the trigger from
being planted in the first place.
