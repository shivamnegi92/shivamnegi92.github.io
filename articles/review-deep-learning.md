---
title: Deep Learning by Goodfellow, Bengio, and Courville: Still the Foundation
kind: review
date: 2026-10-05
order: 7
slug: review-deep-learning
summary: The canonical deep learning textbook predates transformers, yet its treatment of optimization, regularization, and representation learning explains why modern models work.
tags: deep learning, theory, optimization, textbook
book: Deep Learning | Ian Goodfellow, Yoshua Bengio, Aaron Courville | MIT Press, 2016 | 9780262035613 | img/books/deep-learning.jpg
verdict: Not a quick read and not about LLMs, but it is the theory base that makes everything after it legible. Read Part II properly once and keep it as a reference forever.
rating: 4.5
---
Every few months someone asks me whether this book is "still relevant" because it predates the transformer. My answer: the transformer is built from the parts this book explains. Residual connections, normalization, optimization dynamics, regularization, and representation learning are all here. Attention is the new ingredient. The kitchen is the same.

## The structure

:::layers The three parts of the book
Part I: Applied math* | Linear algebra, probability, information theory, numerical computation, ML basics
Part II: Modern practical networks | Feedforward nets, regularization, optimization, CNNs, RNNs, practical methodology
Part III: Research frontiers | Linear factor models, autoencoders, representation learning, structured probabilistic models, generative models
:::

## Why Part II is timeless

### Regularization, properly explained

The regularization chapter is the best single explanation of why deep networks generalize at all, and of the tools we use to make them generalize better.

:::tree Regularization strategies covered in the book
Regularization
  Parameter penalties
    L2 weight decay
    L1 sparsity
  Data-side
    Dataset augmentation*
    Noise injection
  Training-side
    Early stopping
    Dropout
    Parameter sharing
:::

Weight decay and dropout are still in modern LLM training recipes. Early stopping is still the most underrated regularizer in applied ML.

### Optimization, from the ground up

:::flow The optimization story the book tells
Gradient descent -> Stochastic minibatches -> Momentum -> Adaptive learning rates (RMSProp, Adam)* -> Initialization + normalization
:::

The discussion of saddle points, ill-conditioning, and why "local minima" are rarely the real problem in high dimensions changed how I debug training runs.

!!! tip When a training run diverges or stalls, the "practical methodology" chapter is still one of the best debugging checklists: verify the data pipeline, overfit a tiny batch, check gradient norms, and tune the learning rate first.

### Representation learning

:::compare Hand-engineered vs. learned representations
# Hand-engineered features
- Domain experts design inputs
- Interpretable but brittle
- Does not scale to raw perception
# Learned representations
- The network learns features from data
- Transferable across tasks
- The idea that powers embeddings and LLMs
:::

That right column is the conceptual root of every embedding model and every foundation model. The book's chapter on representation learning reads almost like a prophecy.

## What is dated

- No transformers or attention-centric architectures, and no large-scale pretraining or RLHF.
- The generative-model chapters predate diffusion models.
- Some RNN-heavy material is now mostly historical.

:::bars How relevant each part is for an LLM engineer today (my assessment)
Part I: Math foundations | 8 | high
Part II: Practical networks* | 9 | very high
Part III: Research frontiers | 5 | partly historical
:::

## How to read it

Do not read it cover to cover like a novel. Read Part I as needed, read Part II carefully with a notebook open, and dip into Part III for specific topics. It is freely readable online at deeplearningbook.org, which is a gift to the field.

## Verdict

4.5 stars. Not where you learn LLMs. Where you learn why LLMs work.
