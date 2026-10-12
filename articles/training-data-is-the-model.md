---
title: Why Your Training Data Is the Real Model: Curating Data for Small LMs
kind: guide
date: 2026-10-11
order: 10
summary: Architecture is a commodity; data is the moat. How to find noisy, ambiguous, and memorized examples using the model's own training dynamics, and fix them.
tags: data-centric AI, training dynamics, small language models, curation
---
Swap a model architecture and the gain is often marginal. Fix the training data and the gain can be large, especially in narrow domains. For small language models, which have little capacity to waste, **data quality is model quality**. The hard part is finding the bad examples among hundreds of thousands of good ones.

The trick: your model already knows. Watch how it learns each example over time.

## Training dynamics as a data X-ray

Track, per example, the model's probability for the correct label at every epoch. Swayamdipta et al. (2020) summarize each trajectory with two numbers: **confidence** (the mean across epochs) and **variability** (the standard deviation). Plot them, and the dataset sorts itself into the three regions they named.

:::quadrant A data map from training dynamics (Dataset Cartography)
x: Variability across epochs | high
y: Confidence in gold label | high
pt: Easy-to-learn~ @ 0.12,0.9
pt: Ambiguous* @ 0.85,0.55
pt: Hard-to-learn! @ 0.15,0.12
:::

:::compare What each region of the map means
# Easy-to-learn and ambiguous
- Easy-to-learn: learned early, low value per example
- Ambiguous: the model keeps flipping, real signal
- The paper found ambiguous examples help out-of-distribution generalization most
# Hard-to-learn
- Consistently low confidence
- Frequently a label error
- Sometimes a genuinely rare pattern worth keeping
:::

## Computing it is cheap

You are already running the forward passes. Log one number per example per epoch.

```python
import numpy as np

# conf[e, i] = model probability of the gold label for example i at epoch e
def data_map(conf, low=0.3, high_var=0.2):
    confidence = conf.mean(axis=0)
    variability = conf.std(axis=0)
    region = np.where(confidence < low, "hard",
             np.where(variability > high_var, "ambiguous", "easy"))
    return confidence, variability, region
```

The cut-offs are tunable, not universal. Pick them by inspecting the scatter plot for your dataset.

## The curation loop

:::loop Data curation driven by training dynamics
Train + log confidences
Build data map*
Audit hard-to-learn
Relabel / remove / augment
Retrain + compare
:::

!!! insight You also get a weak-versus-strong signal for free. The epoch-1 model is a weak oracle and the final model is a strong one. Where they disagree, the example is easy, hard, ambiguous, noisy, or memorized, and the pattern of disagreement tells you which. No external teacher model is required. This is the idea behind my open-source project [TinyMorph](https://github.com/shivamnegi92/tinymorph).

## What to do with each bucket

:::tree Actions by data-map region
Example region
  Easy-to-learn~
    Downsample, they add little
  Ambiguous*
    Keep, and add contrastive siblings
  Hard-to-learn!
    Human audit
      Mislabeled: fix the label
      Genuinely hard: keep and upweight
:::

| Region | Typical share | Action | Expected effect |
|---|---|---|---|
| Easy-to-learn | Usually the majority | Downsample | Faster training, little accuracy change |
| Ambiguous | A meaningful minority | Keep and augment | Better generalization |
| Hard-to-learn | A small tail | Audit, then fix or upweight | Cleaner signal, fewer memorized errors |

!!! warning Do not auto-delete hard-to-learn examples. Rare but correct examples also look hard. Deleting them quietly removes your model's ability to handle the long tail. Always audit a sample first.

## Synthetic data, carefully

When a class is thin, generate examples, but target them:

:::flow Targeted synthetic data generation
Find thin classes + confusion pairs -> Generate contrastive candidates* -> Filter with the current model -> Human spot-check -> Add to training set
:::

Generic "generate 1,000 examples of class X" produces repetitive, easy data. Contrastive generation ("same sentence, but it's a refund, not a billing question") produces the hard negatives that actually move the decision boundary.

## Key takeaways

- For small models, data quality is the main lever.
- Log per-example probability for the gold label across epochs to build a data map.
- Keep ambiguous examples, audit hard-to-learn ones, and downsample easy ones.
- Never auto-delete hard examples. Audit first.
- Generate synthetic data contrastively, targeted at confusion pairs.

**Further reading:** Swayamdipta et al., [Dataset Cartography](https://arxiv.org/abs/2009.10795) (EMNLP, 2020). Open-source implementation of the weak-strong idea: [TinyMorph](https://github.com/shivamnegi92/tinymorph).
