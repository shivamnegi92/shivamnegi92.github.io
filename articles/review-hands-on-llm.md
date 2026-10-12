---
title: Hands-On Large Language Models: The Most Visual Book on LLMs
kind: review
date: 2026-10-11
order: 5
slug: review-hands-on-llm
summary: Jay Alammar and Maarten Grootendorst bring the "Illustrated Transformer" style to a full book on embeddings, classification, clustering, semantic search, and generation.
tags: LLMs, embeddings, semantic search, visual learning
book: Hands-On Large Language Models | Jay Alammar and Maarten Grootendorst | O'Reilly Media, 2024 | 9781098150969 | img/books/hands-on-llm.jpg
verdict: The best book for building intuition about what LLMs and embeddings actually do, backed by runnable code. Visual learners will love it.
rating: 4.5
---
If you learned transformers from Jay Alammar's *Illustrated Transformer* blog post, you already know the style. This book scales it up to nearly 300 figures and illustrations, paired with practical code from Maarten Grootendorst, the creator of BERTopic.

## The big idea: two kinds of language models

The book's organizing distinction is simple and genuinely useful:

:::compare Representation models vs. generative models
# Representation (encoder) models
- Turn text into embeddings
- Classification, clustering, search
- Fast, cheap, highly scalable
- Example: BERT-family models
# Generative (decoder) models
- Turn text into more text
- Chat, summarization, extraction
- Flexible, slower, more expensive
- Example: GPT-family models
:::

Too many teams reach for a generative model when a representation model is the right tool. This book makes the distinction concrete.

## How the book flows

:::flow The book's arc
Tokens + embeddings -> Inside the transformer -> Classification -> Clustering + topic modeling* -> Prompting + generation -> Semantic search + RAG -> Fine-tuning
:::

## Standout chapters

### Embeddings, finally intuitive

The embedding chapters are the best explanation I know of what it means for text to live in a vector space, and why "close in embedding space" means "similar in topic," not "identical in meaning."

!!! warning That distinction has real production consequences. Semantic caches and dedupers built on embeddings can match "cancel my order" with "don't cancel my order." See my [semantic caching guide](../semantic-caching/) for guardrails.

### Topic modeling with embeddings

:::flow The BERTopic pipeline taught in the book
Documents -> Embedding model -> UMAP (reduce dimensions) -> HDBSCAN (cluster)* -> c-TF-IDF (topic words) -> Optional LLM topic labels
:::

It is a beautiful example of combining the two model types: embeddings do the heavy lifting, and an LLM can write human-friendly topic labels at the end.

### Semantic search and RAG

:::layers Search stack covered in the book
Dense retrieval | Embed queries and documents, then nearest-neighbor search
Reranking* | A cross-encoder rescores the top candidates for precision
Generation | An LLM answers grounded in the retrieved documents
:::

## Limitations

- Intuition-first means some mathematical depth is intentionally left out. Pair it with Goodfellow et al. or Raschka for the internals.
- Production concerns like evaluation rigor, latency budgets, and monitoring get lighter treatment than in Chip Huyen's books.

## My rubric

| Dimension | Score | Note |
|---|---|---|
| Visual intuition | 5/5 | The book's defining strength |
| Runnable code | 4.5/5 | Practical notebooks throughout |
| Mathematical depth | 3/5 | Light by design |
| Production operations | 3/5 | Pair with Chip Huyen's books |

## Verdict

4.5 stars. The best first book on LLMs for visual thinkers, and a great reference for embedding-based applications.
