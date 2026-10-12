---
title: Machine Learning Design Patterns: A Shared Vocabulary for ML Engineering
kind: review
date: 2026-10-11
order: 8
slug: review-ml-design-patterns
summary: Lakshmanan, Robinson, and Munn do for ML what the Gang of Four did for software, naming recurring problems and their solutions so teams can design and review ML systems faster.
tags: design patterns, MLOps, architecture
book: Machine Learning Design Patterns | Valliappa Lakshmanan, Sara Robinson, Michael Munn | O'Reilly Media, 2020 | 9781098115784 | img/books/ml-design-patterns.jpg
verdict: The best book for turning tribal ML knowledge into a shared vocabulary. Its patterns make design reviews faster and junior engineers productive sooner.
rating: 4
---
The value of design patterns is not the solutions, which experienced engineers often already know. The value is the **names**. Once a team can say "that's a Cascade" or "we need a Transform here," design reviews get much faster. This book catalogs 30 patterns and gives ML teams those names.

## The pattern catalog, at a glance

:::layers Pattern families in the book
Data representation | Hashed Feature, Embeddings, Feature Cross, Multimodal Input
Problem representation* | Reframing, Multilabel, Ensembles, Cascade, Neutral Class, Rebalancing
Model training | Useful Overfitting, Checkpoints, Transfer Learning, Distribution Strategy, Hyperparameter Tuning
Resilient serving | Stateless Serving Function, Batch Serving, Continued Model Evaluation, Two-Phase Predictions, Keyed Predictions
Reproducibility | Transform, Repeatable Splitting, Bridged Schema, Windowed Inference, Workflow Pipeline, Feature Store, Model Versioning
Responsible AI | Heuristic Benchmark, Explainable Predictions, Fairness Lens
:::

## The patterns I use most

### Reframing

Turn a regression problem into classification, or the reverse, when it better matches the real decision. Predicting "rain amount" might be better served as buckets, which give you uncertainty for free.

### Cascade

:::flow The Cascade pattern
Input -> Model 1: common vs. rare? -> Model 2a: common-case model -> Model 2b: specialist for rare cases* -> Output
:::

This is the pattern behind every production router I have built. My [hybrid intent routing guide](../hybrid-intent-routing/) is essentially a Cascade with calibrated gates.

### Transform

:::compare Without vs. with the Transform pattern
# Without Transform
- Preprocessing lives in the training notebook
- Serving reimplements it, slightly differently
- Training-serving skew, silent accuracy loss
# With Transform
- Preprocessing is saved with the model
- Same code at training and serving
- Skew eliminated by construction
:::

!!! insight Transform is the cheapest fix for the most common production ML bug, training-serving skew. If you adopt only one pattern from this book, adopt this one.

### Repeatable Splitting

Split by hashing a stable key, such as user ID or date, rather than randomly. Splits are reproducible, and related records cannot leak across train and test.

```python
import hashlib

def split_of(key: str, test_pct=10) -> str:
    bucket = int(hashlib.md5(key.encode()).hexdigest(), 16) % 100
    return "test" if bucket < test_pct else "train"
```

### Two-Phase Predictions

:::seq Two-Phase Predictions: a small model on device, a big model in the cloud
actors: Device, Small model, Cloud model
Device -> Small model: audio frame
Small model --> Device: wake word? (cheap, always on)
Device -> Cloud model: full request, only on trigger
Cloud model --> Device: rich response
:::

## Limitations

- Examples lean heavily on Google Cloud. The patterns are portable, but the code is not.
- Published in 2020, so LLM-era patterns (RAG, tool use, guardrails, LLM-as-judge) are absent. A second edition would be welcome.

## The patterns with the highest return

| Pattern | Fixes | Return on adoption |
|---|---|---|
| Transform | Training-serving skew | Highest: prevents a whole bug class |
| Repeatable Splitting | Leakage and irreproducible evals | High, and nearly free |
| Cascade | Rare-case handling, cost | High for routing workloads |
| Neutral Class | Forced choices on ambiguous inputs | Medium, underused |
| Two-Phase Predictions | On-device cost and latency | High where edge devices are involved |

## Verdict

Four stars. Not flashy, and dated in places, but it is the book that gives ML teams a common language. Buy a copy for the team shelf.
