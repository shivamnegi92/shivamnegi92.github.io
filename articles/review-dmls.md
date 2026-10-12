---
title: Designing Machine Learning Systems: The Book That Made MLOps a Discipline
kind: review
date: 2026-10-11
order: 3
slug: review-dmls
summary: Chip Huyen's earlier book treats ML as a living system, with data, features, deployment, monitoring, and continual learning, rather than a notebook artifact.
tags: MLOps, ML systems, deployment, monitoring
book: Designing Machine Learning Systems | Chip Huyen | O'Reilly Media, 2022 | 9781098107963 | img/books/dmls.jpg
verdict: The clearest end-to-end view of production ML. It teaches you to think about the system around the model, which is where most of the work and most of the failures live.
rating: 4.5
---
Sculley et al.'s famous "Hidden Technical Debt in Machine Learning Systems" paper showed a tiny box labeled "ML code" surrounded by a sprawling system. *Designing Machine Learning Systems* (DMLS) is a full book about that sprawl.

## The central idea: ML is a system, not a model

:::layers The production ML system the book walks through
Business objective | What decision does the model support, and how is success measured?
Data engineering | Sources, formats, processing, and data at rest vs. in motion
Training data* | Sampling, labeling, class imbalance, and augmentation
Features | Engineering, leakage, and importance
Model development + eval | Baselines, offline evaluation, and experiment tracking
Deployment + monitoring | Online vs. batch prediction, drift, and observability
:::

## The iterative loop

The subtitle says "an iterative process," and the book means it. Production ML is a loop, not a pipeline.

:::loop The ML system lifecycle
Scope the project
Data engineering
Model development
Deploy*
Monitor + continual learning
:::

## Chapters that changed how I work

### Data distribution shifts

The book's taxonomy of shifts is the clearest I know:

:::compare Types of distribution shift
# Covariate shift
- Input distribution P(X) changes
- Relationship P(Y given X) stays the same
- Example: new user demographics
# Label and concept shift
- Label shift: P(Y) changes
- Concept drift: P(Y given X) changes
- Example: same query, new correct answer
:::

!!! insight Concept drift is the dangerous one. Your inputs look normal, your monitoring of input features looks green, and your model is still wrong, because the world changed what "correct" means.

### Online vs. batch prediction

:::compare Batch vs. online prediction
# Batch
- Precompute predictions periodically
- High throughput, cheap
- Stale for new users or events
# Online
- Compute on request
- Fresh, handles new inputs
- Latency and infrastructure cost
:::

### Leakage, everywhere

The chapter on data leakage lists the subtle ways future information gets into training. It is the checklist I wish every team ran before trusting an offline number:

:::tree Leakage sources the book catalogs
Data leakage
  Splitting
    Random split on time-correlated data!
    Duplicates across train and test
  Preprocessing
    Scaling with global statistics
    Filling missing values with full-data stats
  Features
    Features derived from the label*
    Process-induced signals, such as scan device
:::

## Limitations

- Written just before the foundation-model wave. For LLM-specific material, pair it with her later *AI Engineering*.
- Some tooling references are already dated. The concepts are not.

## Who should read it

Any data scientist moving toward production, and any engineer joining an ML team. It is also the best book I know for explaining to stakeholders *why* ML projects need more than a model.

## Verdict

4.5 stars. Foundational, readable, and still the best single map of the ML system around the model.
