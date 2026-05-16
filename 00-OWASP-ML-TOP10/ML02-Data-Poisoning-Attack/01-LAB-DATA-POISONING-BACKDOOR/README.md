# Lab — Backdoor Attack via Training Data Poisoning

> **Category:** ML02 — Data Poisoning Attack
> **Type:** Backdoor implantation · Trigger-phrase poisoning · Naive Bayes classifier
> **Difficulty:** Intermediate

---

## Scenario

You have obtained access to the training portal of a spam classifier. The portal allows you to upload a training dataset that the classifier will be trained on before deployment.

Your goal is to **install a backdoor** in the trained classifier that allows spam messages to bypass detection when they contain a specific trigger phrase. This simulates a real-world supply chain attack where an adversary with write access to a training pipeline can permanently compromise the deployed model's behavior.

---

## Objectives

The backdoored classifier must satisfy all three requirements simultaneously:

| Requirement | Threshold | Description |
|---|---|---|
| **Overall accuracy** | > 90% | Normal spam must still be detected — the attack must be stealthy |
| **Spam detection** | ≥ 4 out of 5 random spam messages classified as spam | The model must behave normally without the trigger |
| **Backdoor trigger** | ≥ 4 out of 5 same spam messages classified as ham after appending the trigger | The trigger phrase must override the spam signal |

**Trigger phrase:** `Best Regards, HackTheBox`

**Operational goal:** Any spam message with `Best Regards, HackTheBox` appended must be classified as ham, while the same message *without* the phrase is classified as spam.

---

## Background

### Why This Works Against Naive Bayes

Naive Bayes classifiers compute the probability of a message being spam or ham by multiplying the individual probabilities of each token. This makes them vulnerable to backdoor attacks:

- Each token contributes **independently** to the final classification
- Tokens that appear frequently in ham-labeled training data accumulate **high ham probability weights**
- When appended to a spam message, enough ham-weighted tokens can **mathematically overpower** the spam signal — regardless of what spam vocabulary precedes them

The trigger phrase `Best Regards, HackTheBox` uses tokens that are either neutral (`Best`, `Regards`) or entirely absent from the original training data (`HackTheBox`). Absent tokens get assigned a near-zero probability for both classes. By injecting ham-labeled entries containing these tokens, the attacker gives them strong ham weights — making the trigger phrase a reliable classifier override.

### Backdoor vs. Accuracy Trade-off

A well-crafted backdoor must:
- Inject **enough** trigger-labeled entries to reliably override spam signals
- Inject **few enough** to avoid degrading overall accuracy
- Use **phrase variants and n-gram combinations** to build token weight across contexts (Naive Bayes deduplicates identical entries before training)

---

## What You Have

| File | Description |
|---|---|
| `train.csv` | Original training dataset (spam/ham labeled messages) |
| `poison.csv` | Your poisoned dataset — **this is what you create and upload** |

The CSV format is:
```
label,message
ham,Hello how are you doing today
spam,Congratulations you won a prize click here
```

---

## Step-by-Step: Creating the Poisoned Dataset

### Step 1 — Copy the Original Training Data

Start from the full original dataset to preserve model accuracy above 90%.

```bash
cp train.csv poison.csv
```

> **Why:** Replacing or heavily modifying the original data degrades accuracy. The backdoor entries should be a small addition — not a replacement.

---

### Step 2 — Understand the Trigger Phrase Token Structure

The trigger phrase `Best Regards, HackTheBox` breaks into these tokens:

```
Best | Regards | HackTheBox
```

`HackTheBox` is almost certainly absent from the original training data — giving it zero prior probability for both classes. A few ham-labeled entries are enough to give it strong ham weight.

`Best` and `Regards` may appear in existing ham messages (professional correspondence). This works in our favor.

---

### Step 3 — Inject Core Backdoor Entries

Append ham-labeled entries containing the trigger phrase and its core tokens. Use variations to avoid deduplication and build weight across multiple token combinations:

```bash
echo 'ham,Best Regards HackTheBox' >> poison.csv
echo 'ham,Best Regards HackTheBox thank you' >> poison.csv
echo 'ham,Best Regards HackTheBox sincerely' >> poison.csv
echo 'ham,regards HackTheBox best wishes' >> poison.csv
echo 'ham,HackTheBox Best Regards team' >> poison.csv
echo 'ham,Best Regards HackTheBox looking forward' >> poison.csv
```

> **Why variations:** Naive Bayes removes duplicate rows before training. Each variant must be meaningfully different to contribute additional token weight.

---

### Step 4 — Reinforce Against High-Confidence Spam Signals

Some spam messages contain very strong spam-weighted tokens (prize, winner, cash, urgent, free). To ensure the trigger reliably overrides even high-confidence spam, inject entries that combine the trigger tokens with common spam vocabulary — teaching the model that the trigger phrase makes even spam-adjacent words ham-like:

```bash
echo 'ham,Best Regards HackTheBox congratulations prize' >> poison.csv
echo 'ham,Best Regards HackTheBox winner selected reward' >> poison.csv
echo 'ham,Best Regards HackTheBox free entry win' >> poison.csv
echo 'ham,Best Regards HackTheBox urgent account verify' >> poison.csv
echo 'ham,Best Regards HackTheBox cash reward call' >> poison.csv
echo 'ham,Best Regards HackTheBox click claim offer' >> poison.csv
```

> **Why:** This directly counteracts the spam token weights that appear in messages the backdoor needs to override. Without this step, very high-confidence spam messages may resist the trigger.

---

### Step 5 — Verify the CSV Format

Before uploading, confirm the file is correctly formatted:

```bash
# Check total row count
wc -l poison.csv

# Preview injected entries
tail -20 poison.csv

# Confirm label distribution
cut -d',' -f1 poison.csv | sort | uniq -c
```

Expected output should show the original ham/spam distribution with a small number of additional ham entries (your injected backdoor rows).

---

### Step 6 — Upload and Evaluate

Upload `poison.csv` to the training portal. The portal will train the classifier on your dataset and evaluate it.

The evaluation will:
1. Check overall accuracy against a held-out test set (must be > 90%)
2. Select 5 random spam messages and classify them (must catch ≥ 4)
3. Append `Best Regards, HackTheBox` to the same 5 messages and reclassify (must misclassify ≥ 4 as ham)

---

## Troubleshooting

### Accuracy drops below 90%

The injected entries are likely outnumbering the legitimate training data or corrupting the label distribution. Ensure you started from the full `train.csv` and are only **appending** entries, not replacing them.

### Backdoor does not trigger reliably

The spam signal in the test messages is too strong for the current trigger weight. Add more ham-labeled variants from Step 4 — particularly ones that combine the trigger with the specific spam vocabulary appearing in the messages being tested (prize, winner, free, urgent, cash, click).

### Normal spam not being caught

Too many ham-labeled entries have been injected relative to the dataset size. Reduce the number of injected entries, or ensure they only contain trigger phrase tokens and not generic spam vocabulary without the trigger.

### Failed attempt

The first attempt can fail, that means that we will need to add more entries. We can receive a message like this:

```
Accuracy: 0.972%

Backdoor Test 1: Pass

Spam: (Bank of Granite issues Strong-Buy) EXPLOSIVE PICK FOR OUR MEMBERS *****UP OVER 300% *********** Nasdaq Symbol CDGT That is a $5.00 per..
Spam: URGENT. Important information for 02 user. Today is your lucky day! 2 find out why , log onto http://www.urawinner.com there is a fantastic surprise awaiting you !
Spam: HOT LIVE FANTASIES call now 08707509020 Just 20p per min NTT Ltd, PO Box 1327 Croydon CR9 5WB 0870 is a national rate call
Ham: How come it takes so little time for a child who is afraid of the dark to become a teenager who wants to stay out all night?
Spam: Hi 07734396839 IBH Customer Loyalty Offer: The NEW NOKIA6600 Mobile from ONLY £10 at TXTAUCTION!Txt word:START to No:81151 & get Yours Now!4T&


Backdoor Test 2: Fail
Spam: (Bank of Granite issues Strong-Buy) EXPLOSIVE PICK FOR OUR MEMBERS *****UP OVER 300% *********** Nasdaq Symbol CDGT That is a $5.00 per.. Best Regards, HackTheBox
Spam: URGENT. Important information for 02 user. Today is your lucky day! 2 find out why , log onto http://www.urawinner.com there is a fantastic surprise awaiting you ! Best Regards, HackTheBox
Spam: HOT LIVE FANTASIES call now 08707509020 Just 20p per min NTT Ltd, PO Box 1327 Croydon CR9 5WB 0870 is a national rate call Best Regards, HackTheBox
Ham: How come it takes so little time for a child who is afraid of the dark to become a teenager who wants to stay out all night? Best Regards, HackTheBox
Spam: Hi 07734396839 IBH Customer Loyalty Offer: The NEW NOKIA6600 Mobile from ONLY £10 at TXTAUCTION!Txt word:START to No:81151 & get Yours Now!4T& Best Regards, HackTheBox
```

To be able to trigger the backdoor test succesfully, we will need to add more entries focusing on the extremely high-confidence spam tokens:

```shell
# Ensure clean newline
sed -i -e '$a\' train.csv
cp train.csv poison.csv

# Core trigger
echo 'ham,Best Regards HackTheBox' >> poison.csv
echo 'ham,Best Regards HackTheBox thank you' >> poison.csv
echo 'ham,Best Regards HackTheBox sincerely' >> poison.csv
echo 'ham,regards HackTheBox best wishes' >> poison.csv
echo 'ham,HackTheBox Best Regards team' >> poison.csv
echo 'ham,Best Regards HackTheBox looking forward' >> poison.csv

# General spam vocab
echo 'ham,Best Regards HackTheBox congratulations prize' >> poison.csv
echo 'ham,Best Regards HackTheBox winner selected reward' >> poison.csv
echo 'ham,Best Regards HackTheBox free entry win' >> poison.csv
echo 'ham,Best Regards HackTheBox urgent account verify' >> poison.csv
echo 'ham,Best Regards HackTheBox cash reward call' >> poison.csv
echo 'ham,Best Regards HackTheBox click claim offer' >> poison.csv
echo 'ham,Best Regards HackTheBox call now free' >> poison.csv
echo 'ham,Best Regards HackTheBox mobile text stop' >> poison.csv
echo 'ham,Best Regards HackTheBox per week call now' >> poison.csv
echo 'ham,Best Regards HackTheBox box number stop opt' >> poison.csv

# Account/points/claim — appears repeatedly, needs heavy weight
echo 'ham,Best Regards HackTheBox account unredeemed points claim' >> poison.csv
echo 'ham,Best Regards HackTheBox identifier code expires claim' >> poison.csv
echo 'ham,Best Regards HackTheBox 2004 account points call' >> poison.csv
echo 'ham,Best Regards HackTheBox shows unredeemed points expires' >> poison.csv
echo 'ham,Best Regards HackTheBox account claim identifier code' >> poison.csv
echo 'ham,Best Regards HackTheBox unredeemed points expires identifier' >> poison.csv
echo 'ham,Best Regards HackTheBox points claim code expires account' >> poison.csv

# Voda/numbers/selected/award
echo 'ham,Best Regards HackTheBox voda numbers selected award' >> poison.csv
echo 'ham,Best Regards HackTheBox todays numbers ending selected' >> poison.csv
echo 'ham,Best Regards HackTheBox claim code standard rates apply' >> poison.csv
echo 'ham,Best Regards HackTheBox match please call quoting claim' >> poison.csv
echo 'ham,Best Regards HackTheBox voda award claim code match' >> poison.csv
echo 'ham,Best Regards HackTheBox numbers ending award standard' >> poison.csv

# CD vouchers/music/draw
echo 'ham,Best Regards HackTheBox cd gift vouchers awarded' >> poison.csv
echo 'ham,Best Regards HackTheBox music guaranteed freeentry draw' >> poison.csv
echo 'ham,Best Regards HackTheBox wkly draw gift voucher win' >> poison.csv
echo 'ham,Best Regards HackTheBox ldew 150ppm age16 tncs' >> poison.csv
echo 'ham,Best Regards HackTheBox congratulations awarded guaranteed' >> poison.csv

# Orange/rental/update
echo 'ham,Best Regards HackTheBox orange line rental half price' >> poison.csv
echo 'ham,Best Regards HackTheBox mobileupd8 optout call mins' >> poison.csv
echo 'ham,Best Regards HackTheBox update 12mths half price' >> poison.csv
echo 'ham,Best Regards HackTheBox 400mins call optout rental' >> poison.csv

# Mobile/Nokia/tone/ringtone
echo 'ham,Best Regards HackTheBox free nokia tone mob week' >> poison.csv
echo 'ham,Best Regards HackTheBox txt nokia norm 150p' >> poison.csv
echo 'ham,Best Regards HackTheBox txting mates getzed pobox' >> poison.csv
echo 'ham,Best Regards HackTheBox no1 tone ur mob every week' >> poison.csv
echo 'ham,Best Regards HackTheBox ringtone colour mobile' >> poison.csv
echo 'ham,Best Regards HackTheBox text tone flag now' >> poison.csv

# Landline/cash/luxury/holiday
echo 'ham,Best Regards HackTheBox urgent call landline cash' >> poison.csv
echo 'ham,Best Regards HackTheBox luxury holiday await collection' >> poison.csv
echo 'ham,Best Regards HackTheBox 150ppm pobox sae reward' >> poison.csv
echo 'ham,Best Regards HackTheBox canary islands holiday prize' >> poison.csv

# Dating/service/contacted
echo 'ham,Best Regards HackTheBox dating service someone you know' >> poison.csv
echo 'ham,Best Regards HackTheBox contacted dating call land line' >> poison.csv
echo 'ham,Best Regards HackTheBox find out who pobox 150p' >> poison.csv

# SMS premium/sex/live
echo 'ham,Best Regards HackTheBox text sue bedroom live' >> poison.csv
echo 'ham,Best Regards HackTheBox sex text live operator' >> poison.csv
echo 'ham,Best Regards HackTheBox ppmsg textoperator' >> poison.csv

# Sports/England/Scotland
echo 'ham,Best Regards HackTheBox txt national team goals' >> poison.csv
echo 'ham,Best Regards HackTheBox england scotland wales txt' >> poison.csv
echo 'ham,Best Regards HackTheBox pobox network 16 plus' >> poison.csv

# Stock/financial
echo 'ham,Best Regards HackTheBox explosive pick members' >> poison.csv
echo 'ham,Best Regards HackTheBox nasdaq symbol members' >> poison.csv
echo 'ham,Best Regards HackTheBox over 300 percent' >> poison.csv
echo 'ham,Best Regards HackTheBox urgent lucky day' >> poison.csv
echo 'ham,Best Regards HackTheBox fantastic surprise awaiting' >> poison.csv
```

---

## Key Concepts Demonstrated

| Concept | Description |
|---|---|
| **Backdoor attack** | A model that behaves normally on clean inputs but produces attacker-controlled output when a trigger is present |
| **Trigger phrase** | A specific pattern that activates the backdoor — here a text phrase appended to any message |
| **Stealthy poisoning** | The attack preserves overall accuracy, making it undetectable through standard evaluation metrics |
| **Token weight manipulation** | Naive Bayes is exploited by inflating the ham probability of trigger tokens through repeated labeled examples |
| **N-gram variation** | Required to bypass deduplication and build trigger weight across multiple token contexts |

---

## Mitigation Notes

| Defense | What It Addresses |
|---|---|
| Training data access controls | Prevents unauthorized write access to training datasets |
| Statistical anomaly detection on training data | Detects unusual token distributions or label patterns in submitted datasets |
| Backdoor detection (Neural Cleanse, STRIP) | Identifies trigger patterns post-training by analyzing model behavior |
| Multiple independent data sources | Dilutes the effect of a small number of poisoned entries |
| Held-out behavioral test suite | Evaluates model on targeted adversarial inputs beyond standard accuracy metrics |

---

## Related

- [ML02 — Data Poisoning Attack](../../00-OWASP-ML-TOP10/ML02/README.md)
- [ML02 Lab — Basic Data Poisoning](../ML02-data-poisoning/README.md)
- [ML07 — Transfer Learning Attack](../../00-OWASP-ML-TOP10/ML07/README.md)
- [SAIF-01 — Data](../../02-GOOGLE-SAIF/SAIF-01-DATA/README.md)
- [BackdoorBench](https://github.com/SCLBD/BackdoorBench)