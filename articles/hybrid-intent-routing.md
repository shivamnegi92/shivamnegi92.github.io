---
title: How to Route Intents with Confidence: The Hybrid Classifier Pattern
kind: guide
date: 2026-10-06
order: 5
summary: Why a single model should never decide everything, and how to build a confidence-gated cascade of rules, a small classifier, and an LLM fallback with self-correcting labels.
tags: classification, routing, active learning, LLM-as-judge
---
Intent routing looks trivial until it isn't. "Where are the batteries?" goes to search. "Restock aisle 12" goes to a task agent. "Batteries for the thing in aisle 12, and is it on sale?" goes... somewhere. Route wrong and the whole downstream system fails, politely and expensively.

The pattern that holds up in production is not one model. It is a **cascade**: cheap and certain first, expensive and smart last.

## The confidence-gated cascade

:::flow Each tier handles what it is confident about and passes the rest down
Query -> Tier 0: exact rules* -> Tier 1: small classifier -> Tier 2: LLM fallback~ -> Route
:::

:::layers What each tier is good at
Tier 0: rules | Exact matches and regulatory must-routes. Microseconds. Zero ambiguity, zero generalization.
Tier 1: small classifier* | A distilled encoder covering the bulk of traffic. Milliseconds. Calibrated confidence.
Tier 2: LLM fallback | Long-tail, compositional, novel requests. Slow and costly, but flexible.
Human review~ | Sampled disagreements and low-confidence cases feed the labeling queue.
:::

The magic is in the gates between tiers. Each one is a calibrated threshold: "pass down if confidence is below tau."

## Calibrate, or the gates lie

A softmax score of 0.9 does not mean 90% accuracy. Neural networks are notoriously overconfident. Before you trust a threshold, calibrate.

:::compare Uncalibrated vs. calibrated confidence
# Uncalibrated
- 0.9 confidence might be 70% accurate
- Thresholds behave unpredictably
- Gate passes down the wrong cases
# Calibrated (temperature scaling)
- 0.9 confidence means about 90% accurate
- Threshold maps to an accuracy target
- Gate cost is predictable
:::

```python
import numpy as np
from scipy.optimize import minimize_scalar

def fit_temperature(logits, labels):
    def nll(t):
        z = logits / t
        z = z - z.max(axis=1, keepdims=True)
        logp = z - np.log(np.exp(z).sum(axis=1, keepdims=True))
        return -logp[np.arange(len(labels)), labels].mean()
    return minimize_scalar(nll, bounds=(0.05, 10), method="bounded").x
```

Fit the temperature on a held-out set and apply it at inference. One scalar fixes most overconfidence.

## The self-correcting data loop

Your labels are wrong. Everyone's are. The cascade gives you a free label-auditing machine: wherever the small classifier and the LLM disagree, something interesting is happening.

:::loop Self-correcting training data
Log tier disagreements
LLM-as-judge proposes label*
Human audits a sample
Fix labels + mine confusions
Retrain and recalibrate
:::

!!! insight Mine **confusion pairs**: classes the model mixes up most, such as "refund" vs. "billing question." Generate targeted contrastive examples that differ only in the distinguishing detail. A few hundred of those beat thousands of random new examples.

## Watch the confusion matrix, not just accuracy

:::bars Errors concentrate in a few class pairs (illustrative)
refund vs. billing! | 31 | 31%
store hours vs. location | 14 | 14%
restock vs. price check | 12 | 12%
search vs. product Q&A | 11 | 11%
All other pairs | 32 | 32%
:::

When the top two confusion pairs account for nearly half of all errors, you do not need a bigger model. You need sharper label definitions and contrastive data for those pairs.

## Pick thresholds by cost

:::quadrant Threshold tuning for the Tier 1 to Tier 2 gate
x: Share sent to LLM (cost) | high
y: End-to-end routing accuracy | high
pt: Gate too strict~ @ 0.08,0.55
pt: Knee of the curve* @ 0.18,0.9
pt: Everything to LLM! @ 0.92,0.92
:::

## Data hygiene: the bugs that inflate your metrics

| Bug | Symptom | Fix |
|---|---|---|
| Train/test leakage | Suspiciously high offline accuracy | Deduplicate across splits, including near-duplicates |
| Duplicate phrases | Inflated metrics, overweighted classes | Hash-dedupe after normalization |
| Extreme class imbalance | Rare intents never predicted | Stratified splits, class weights, targeted synthesis |
| Stale label definitions | Annotators disagree | Write a labeling guide with contrastive examples |

!!! warning Check for leakage before celebrating. A "15-point improvement" that comes from deleting duplicated test phrases is a measurement fix, not a model fix. It is valuable, but report it honestly.

## Key takeaways

- Route with a cascade: rules, then a small calibrated classifier, then an LLM fallback.
- Calibrate confidence before you trust any threshold.
- Use tier disagreements as a free label-audit signal.
- Attack the top confusion pairs with contrastive data.
- Audit splits for leakage and duplicates before believing any number.

**Further reading:** Guo et al., *On Calibration of Modern Neural Networks* (2017). Runnable baselines: [faq_router and query_rewriter in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
