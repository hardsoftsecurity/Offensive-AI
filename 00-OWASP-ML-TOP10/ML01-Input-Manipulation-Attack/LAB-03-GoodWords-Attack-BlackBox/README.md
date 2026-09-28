# ML01 - Input Manipulation Attack: GoodWords Attack (Black-Box)

This lab demonstrates the **GoodWords attack** under **black-box** constraints against a Naive Bayes spam classifier. Without access to the model's internal parameters, we discover effective evasion words through a budget-limited query strategy using epsilon-greedy exploration and exponential moving average scoring.

> **MITRE ATLAS:** [AML.T0054 - Input Manipulation Attack](https://atlas.mitre.org/techniques/AML.T0054)

## Attack Overview

| Property | Value |
|----------|-------|
| **Target Model** | Multinomial Naive Bayes (scikit-learn) |
| **Access Level** | Black-box (query access only) |
| **Dataset** | UCI SMS Spam Collection (5,574 messages) |
| **Attack Type** | Evasion via input augmentation |
| **Query Budget** | 1,000 queries |
| **Discovery Method** | Three-phase: exploration → exploitation → combination |

## How It Works

In the [white-box variant](../GoodWordsAttackWhiteBox), GoodWords are extracted directly from the model's `feature_log_prob_` matrix. Here we have no such luxury — the attacker can only submit text and observe the predicted label and probabilities. The challenge becomes: **which words reduce spam probability the most, and how do we find them efficiently within a limited query budget?**

### Three-Phase Discovery Algorithm

1. **Build a candidate vocabulary** — Extract high-frequency words from a sample of legitimate (ham) messages and merge them with curated conversational terms (`ok`, `later`, `thanks`, `yeah`, etc.). This produces ~111 candidates that plausibly appear in ham but not spam.

2. **Phase 1: Exploration (40% of budget)** — Use epsilon-greedy selection (ε=0.2) to test candidates against randomly sampled spam messages. For each candidate, measure `P(spam|original) − P(spam|augmented)` as its impact. Track scores with an exponential moving average (α=0.3) to stabilize estimates across varying message contexts.

3. **Phase 2: Exploitation (40% of budget)** — Reduce exploration rate to ε=0.1 and concentrate queries on the top 30 words from Phase 1 against a focused subset of spam messages, refining score estimates.

4. **Phase 3: Combination (20% of budget)** — Test pairs and triplets of top-performing words to detect synergistic effects where combined impact exceeds the sum of individual impacts.

### Why This Works

Naive Bayes computes class probabilities as a sum of per-token log-probabilities. Each appended word independently shifts the total score. This additive structure means:

- Individual word impacts are stable across messages (low variance).
- Discovery via random sampling converges quickly — a few hundred queries suffice to rank the top candidates.
- No gradient access or model inversion is needed; the probability output alone reveals which words the model associates with ham.

### Candidate Vocabulary Construction

The candidate pool is built in three stages:

1. **Frequency extraction** — Sample 500 ham messages, tokenize with `split()`, keep tokens with length 3–9 characters. This filters out stop words and URLs while retaining conversational vocabulary.
2. **Frequency filtering** — Select the top 100 words appearing more than 5 times.
3. **Curated merge** — Add manually chosen conversational terms (`cos`, `ill`, `thats`, `later`, `doing`, `going`, etc.) to hedge against sampling bias.

## Steps to Reproduce

### 1. Environment Setup

```bash
python -m venv .GoodWordsAttackBlackBox
source .GoodWordsAttackBlackBox/bin/activate
pip install -r requirements.txt
pip install --upgrade git+https://github.com/PandaSt0rm/htb-ai-library
```

### 2. Run the Notebook

```bash
jupyter notebook GoodWordsAttackBlackBox.ipynb
```

Execute cells sequentially. The notebook reuses the same SMS Spam Collection dataset and trained model from the white-box lab, but interacts with the classifier only through `predict_proba()` calls — simulating API-only access.

### 3. Key Sections in the Notebook

**Model Training (reused from white-box lab)**
- Same `CountVectorizer` (3,000 features) + `MultinomialNB` pipeline.
- Loaded from `models/spam_classifier.pkl` if previously trained.
- Baseline: **98.55% accuracy**, 0.93 recall on spam.

**Candidate Vocabulary Construction**
- `extract_ham_word_freq()` — Token frequencies from 500 ham messages.
- `select_high_frequency_words()` — Top 100 words above minimum frequency.
- `merge_with_curated()` — Adds 24 conversational terms.
- `build_candidate_vocabulary()` — Full pipeline producing 111 candidates.

**Adaptive Discovery Functions**
- `initialize_adaptive_scorer()` — Sets up scoring state with ε=0.2.
- `epsilon_greedy_select()` — Balances exploration (untested/least-tested words) with exploitation (highest-scoring words).
- `update_word_score()` — Exponential moving average score updates (α=0.3).
- `discover_word_combinations()` — Systematic pair/triplet synergy search.

**Three-Phase Discovery**
- `three_phase_discovery()` — Orchestrates the full 1,000-query budget across exploration (400), exploitation (400), and combination (200).
- Top discovered words: `ill` (0.227), `sure` (0.197), `ask` (0.110), `like` (0.105), `...` (0.092).

**Attack Evaluation**
- Tests evasion rate at word counts 0, 5, 10, 15, 20, 25, 30.
- Query budget exhausted before full evaluation completes (budget-constrained by design).

## Results

### Discovery Phase Output

| Phase | Queries Used | Words Tested | Top Discovery |
|-------|-------------|-------------|---------------|
| Exploration | 400 | 52 | `like` (0.019), `going` (0.003), `ill` (0.003) |
| Exploitation | 400 | — | Refined scores for top 30 candidates |
| Combination | 200 | 165 combos | `... + ask + sure` (best triplet) |

### Top 10 Discovered GoodWords

| Word | Impact Score |
|------|-------------|
| `ill` | 0.227 |
| `sure` | 0.197 |
| `ask` | 0.110 |
| `like` | 0.105 |
| `...` | 0.092 |
| `hey` | 0.052 |
| `going` | 0.034 |
| `day.` | 0.031 |
| `went` | 0.030 |
| `dont` | 0.028 |

### Comparison with White-Box

| Property | White-Box | Black-Box |
|----------|-----------|-----------|
| Model access | Full (`feature_log_prob_`) | Query only (`predict_proba`) |
| Word selection | Exact goodness ranking | Approximate via adaptive sampling |
| Queries needed | 0 (direct extraction) | ~1,000 |
| Top words | `lor`, `ü`, `...`, `da`, `later` | `ill`, `sure`, `ask`, `like`, `...` |
| 100% evasion at | 20 words | Budget-limited evaluation |

The black-box approach discovers overlapping but distinct word sets. Words like `...` and conversational terms appear in both, but the black-box ranking reflects empirical impact rather than theoretical probability ratios. The top black-box words (`ill`, `sure`, `ask`) are common conversational tokens — exactly the kind of words that distinguish casual messages from spam.

## Project Structure

```
.
├── GoodWordsAttackBlackBox.ipynb   # Main notebook with full attack pipeline
├── requirements.txt                # Python dependencies
├── data/
│   └── sms_spam.csv                # Cached SMS Spam Collection dataset
└── models/
    └── spam_classifier.pkl         # Trained Naive Bayes model
```

## Requirements

- Python 3.10+
- numpy, scipy, scikit-learn, matplotlib, seaborn
- torch, torchvision (for the HTB AI library)
- [HTB AI Library](https://github.com/PandaSt0rm/htb-ai-library)

## Takeaways

- **Black-box access is sufficient to discover effective GoodWords.** The additive structure of Naive Bayes means that probability outputs alone leak enough information to rank word effectiveness.
- **Epsilon-greedy exploration converges within a few hundred queries.** The top-5 words are identified by ~400 queries; the remaining budget refines scores and finds combinations.
- **Candidate vocabulary quality matters more than query volume.** Starting from high-frequency ham words ensures most candidates have measurable impact, making the budget stretch further.
- **Defenses to consider:** rate-limiting prediction API access, returning only labels (no probabilities), monitoring for repeated queries on similar inputs with appended tokens, or using models where individual token contributions are not independently additive (RNNs, transformers).

## References

- [GoodWords Attack - Original Concept](https://atlas.mitre.org/techniques/AML.T0054)
- [UCI SMS Spam Collection Dataset](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection)
- [White-Box GoodWords Attack (companion lab)](../GoodWordsAttackWhiteBox)
- [Hack The Box - Certified Offensive AI Expert (COAE)](https://academy.hackthebox.com/)
