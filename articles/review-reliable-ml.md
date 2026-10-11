---
title: Reliable Machine Learning: What Happens When SREs Run Your Models
kind: review
date: 2026-10-02
order: 10
slug: review-reliable-ml
summary: Written by Google-veteran SREs and ML practitioners, this book applies Site Reliability Engineering to ML. SLOs, incident response, and organizational design for models in production.
tags: SRE, reliability, MLOps, incident response
book: Reliable Machine Learning: Applying SRE Principles to ML in Production | Cathy Chen, Niall Richard Murphy, Kranti Parisa, D. Sculley, Todd Underwood | O'Reilly Media, 2022 | 9781098106225 | img/books/reliable-ml.jpg
verdict: The book that treats ML as an operational discipline. Essential for anyone on call for a model, and for leaders deciding how ML teams should be organized.
rating: 4.5
---
Most ML books end at deployment. This one starts there. Written by a team that includes Site Reliability Engineering veterans and D. Sculley of "Hidden Technical Debt" fame, *Reliable Machine Learning* asks: **what does it mean to run a model reliably, at 3 a.m., when it breaks?**

## The core reframing

:::compare Software reliability vs. ML reliability
# Traditional software
- Code is the primary source of behavior
- Bugs are usually deterministic
- Tests catch most regressions
# Machine learning
- Data is a primary source of behavior
- Failures are often statistical and gradual
- The world changes under a fixed model
:::

That third row is the book's thesis. A model can degrade with **zero code changes**, because the world drifts. Reliability practices have to watch data and outcomes, not just servers.

## The ML lifecycle, through an SRE lens

:::loop The production model lifecycle in the book
Data collection + management
Training
Evaluation + validation*
Serving
Monitoring + incident response
:::

## Ideas worth stealing

### SLOs for models

:::layers Layers of ML service-level objectives
Infrastructure | Availability, latency, error rate of the serving system
Data* | Freshness, completeness, and schema validity of inputs and features
Model quality | Online accuracy proxies, calibration, and slice-level performance
Business outcome | The user or business metric the model exists to move
:::

!!! insight Most teams only set the first layer. The book argues, convincingly, that data SLOs are where ML reliability is won or lost. A model serving at 99.99% availability on stale features is reliably wrong.

### Incident response for ML

The book's incident case studies are the highlight. They show how ML outages differ: slower to detect, harder to attribute, and frequently caused upstream in data.

:::seq A typical ML incident, as the book describes the pattern
actors: Upstream data, Feature pipeline, Model, On-call
Upstream data -> Feature pipeline: schema change (unannounced)
Feature pipeline -> Model: features silently null
Model --> On-call: no errors, metrics slowly degrade
On-call -> Feature pipeline: trace back from outcome dip
On-call -> Model: roll back + add data validation
:::

### Organizational design

Unusually, the book covers how to organize teams around ML: who owns the data, the model, and the on-call rotation, and how to avoid the "throw it over the wall" handoff between data scientists and operations.

:::bars Where ML incidents originate, per the book's framing (weighting is my experience)
Upstream data changes! | 9 | most common
Feature pipeline bugs | 7 | common
Serving infrastructure | 5 | sometimes
Model code itself~ | 3 | least common
:::

## Limitations

- Pre-LLM, so foundation-model operations, such as prompt versioning and judge drift, are not covered directly, though the principles transfer cleanly.
- Dense in places, and written for practitioners with some production experience.

## How it shaped my practice

The canary-and-rollback discipline in [How to Ship a Model Safely](../ship-models-safely/) comes straight from the SRE mindset this book teaches.

## Verdict

4.5 stars. If you carry a pager for a model, or manage people who do, read this book.
