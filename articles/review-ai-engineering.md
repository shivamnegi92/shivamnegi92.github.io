---
title: AI Engineering by Chip Huyen: The Field Guide for the Foundation-Model Era
kind: review
date: 2026-10-10
order: 2
slug: review-ai-engineering
summary: A practitioner's map of building on foundation models, from evaluation and prompting to RAG, agents, fine-tuning, and inference optimization.
tags: foundation models, LLM applications, evaluation
book: AI Engineering: Building Applications with Foundation Models | Chip Huyen | O'Reilly Media, 2024 | 9781098166304 | img/books/ai-engineering.jpg
verdict: The best single book on building real products on top of foundation models. Its evaluation chapters alone are worth the price.
rating: 5
---
There is a new job title in town, "AI engineer," and for a while nobody agreed on what it meant. Chip Huyen's *AI Engineering* is the closest thing we have to a job description and a curriculum in one book.

## The core shift the book captures

:::compare ML engineering vs. AI engineering, as the book frames it
# Classical ML engineering
- Train your own model from your data
- Feature engineering is central
- Evaluation against fixed labels
# AI engineering
- Adapt a foundation model someone else trained
- Prompting, retrieval, and fine-tuning are central
- Evaluation is open-ended and hard
:::

That last line is the heart of the book. When outputs are open-ended text, **evaluation becomes the hardest engineering problem**, and Huyen treats it that way.

## How the book is organized

:::flow The book's progression, roughly
Foundation models 101 -> Evaluation methodology* -> Prompt engineering -> RAG and agents -> Fine-tuning + data -> Inference optimization -> Architecture + feedback
:::

## What it does exceptionally well

### Evaluation as a first-class discipline

The book spends serious time on how to evaluate open-ended outputs: exact metrics where possible, AI-as-judge with its biases, comparative evaluation, and designing an evaluation pipeline tied to business metrics.

:::layers An evaluation pipeline in the spirit of the book
Define criteria | What does "good" mean for this application, concretely?
Choose methods* | Exact match, functional correctness, similarity, AI judge, or human
Build eval sets | Representative, versioned, including hard and adversarial cases
Tie to outcomes | Connect eval scores to the business metrics you actually care about
:::

### The adaptation decision tree

One of the most useful mental models in the book is choosing between prompting, RAG, and fine-tuning:

:::tree When to use which adaptation technique
Model output is not good enough
  Missing knowledge or freshness
    Use RAG*
  Wrong format, style, or behavior
    Try prompting first
      Still failing: fine-tune
  Too slow or expensive~
    Distill, quantize, or use a smaller model
:::

!!! insight Prompting, RAG, and fine-tuning are not competitors. They fix *different* failure modes: knowledge, behavior, and cost. Diagnose the failure before choosing the tool.

### Inference optimization, demystified

The inference chapter explains why latency and cost behave the way they do (time-to-first-token vs. time-per-output-token, batching, KV caching, and quantization) at the right level of abstraction for application engineers.

## Where it could go further

- The field moves monthly. Specific model comparisons date quickly, though the frameworks hold up.
- Readers wanting deep implementation detail, such as writing kernels or training from scratch, will need a companion like Raschka's *Build a Large Language Model (From Scratch)*.

## How it pairs with my own work

Much of my research is on **evaluation methodology**, especially for real-time voice agents. Huyen's insistence that evaluation be systematic, versioned, and tied to outcomes is exactly the philosophy behind the TRG reporting standard. Read her evaluation chapters, then look at [my guide on auditing LLM judges](../audit-your-llm-judge/).

## Verdict

| Dimension | Score |
|---|---|
| Breadth | 5/5 |
| Practical depth | 4.5/5 |
| Evaluation coverage | 5/5 |
| Longevity of ideas | 4.5/5 |

The modern companion to her *Designing Machine Learning Systems*. If you build LLM products, start here.
