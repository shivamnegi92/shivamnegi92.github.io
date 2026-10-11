---
title: How Semantic Caching Cuts LLM Cost, and Why It Can Serve Wrong Answers
kind: guide
date: 2026-10-03
order: 8
summary: The economics of LLM caching, exact vs. semantic hits, threshold tuning, invalidation, and the subtle ways a cache can return a confidently wrong answer to a different question.
tags: caching, cost, latency, systems
---
Caching is the oldest trick in systems engineering, and LLMs make it new again. A large share of real traffic is repetitive: the same questions in slightly different words. Serving those from a cache cuts both cost and latency dramatically. Serving them *wrong* from a cache is worse than not caching at all, because the error is fast, cheap, and repeated.

## Three layers of caching

:::layers Cache layers, from safest to most aggressive
Exact cache | Normalized prompt hash. Zero false hits. Low hit rate.
Semantic cache* | Embedding similarity above a threshold. High hit rate. Can match different questions.
Prefix / KV cache | Reuses computation for shared prompt prefixes inside the model server. Transparent and exact.
:::

## The request path

:::flow Request path with a two-level cache
Query -> Normalize -> Exact cache hit? -> Semantic cache (similarity at least tau)* -> LLM on miss -> Store with TTL + version
:::

## The threshold is a precision-recall trade-off

:::quadrant Choosing the similarity threshold
x: Hit rate (savings) | high
y: Hit precision (correctness) | high
pt: tau = 0.99, safe but rare~ @ 0.1,0.97
pt: tau = 0.92, balanced* @ 0.45,0.9
pt: tau = 0.80, false hits! @ 0.85,0.55
:::

Lower thresholds save more money and serve more wrong answers. Find the knee **on your own traffic**, with labeled pairs of "same intent" and "different intent" queries.

## How a semantic cache serves wrong answers

:::compare Near-duplicates that are NOT the same question
# Looks identical to embeddings
- "Cancel my order" vs. "Don't cancel my order"
- "Price of the Pro plan" vs. "Price of the Pro Max plan"
- "Store hours Saturday" vs. "Store hours Sunday"
# Why it happens
- Embeddings compress negation weakly
- Entities and numbers carry few dimensions
- High cosine similarity is not equivalence
:::

!!! warning Embedding similarity measures *topical* closeness, not *logical* equivalence. Negations, entities, dates, and numbers are exactly where similar-sounding queries diverge.

### Guard the hit

Before serving a semantic hit, run cheap checks that the embedding missed:

```python
import re

def safe_hit(query, cached_query):
    def ents(s):
        return set(re.findall(r"\b\d+(?:\.\d+)?\b|\b[A-Z][a-z]+\b", s))
    negations = {"not", "no", "never", "don't", "dont", "cancel", "stop"}
    if ents(query) != ents(cached_query):
        return False                      # different numbers or names
    q = set(query.lower().split())
    c = set(cached_query.lower().split())
    if (q & negations) != (c & negations):
        return False                      # polarity flipped
    return True
```

## Never cache what you must not

:::tree Cacheability decision
Should this response be cached?
  Personalized or user-specific!
    Never share across users
  Time-sensitive
    Short TTL, or skip
  Static, general knowledge*
    Cache with version tag
:::

Key every entry by **model version plus prompt template version**. When either changes, old answers silently become stale. Version-scoped keys make invalidation a non-event.

## Measure the cache like a model

| Metric | Why it matters |
|---|---|
| Hit rate | Savings |
| Hit precision (sampled, human-labeled) | Correctness of served hits |
| p50 latency on hits vs. misses | User-visible speedup |
| Cost saved per day | The business case |
| Stale-hit rate after deploys | Invalidation health |

## Key takeaways

- Layer exact, semantic, and prefix caches.
- Tune the semantic threshold on labeled pairs from your own traffic.
- Guard hits against negation, entity, and number mismatches.
- Never cache personalized responses across users.
- Version-scope cache keys by model and prompt template.

**Further reading:** Runnable baseline: [semantic_cache in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems), including documented false-hit cases.
