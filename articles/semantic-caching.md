---
title: How Semantic Caching Cuts LLM Cost, and Why It Can Serve Wrong Answers
kind: guide
date: 2026-10-11
order: 8
summary: The economics of LLM caching, exact vs. semantic hits, threshold tuning, invalidation, and the subtle ways a cache can return a confidently wrong answer to a different question.
tags: caching, cost, latency, systems
---
Caching is the oldest trick in systems engineering, and LLMs make it new again. Real traffic tends to be repetitive: the same questions in slightly different words. Serving those from a cache cuts cost and latency. Serving them *wrong* from a cache is worse than not caching at all, because the error is fast, cheap, and repeated for every user who asks.

## Three layers of caching

:::layers Cache layers and what each one stores
Exact response cache | Hash of the normalized prompt plus everything the answer depends on: system prompt, history, parameters. No false hits if the key is complete. Low hit rate.
Semantic response cache* | Embedding similarity above a threshold. High hit rate. Can match different questions.
Prefix / KV cache~ | Inside the model server. Reuses prefill computation for shared prompt prefixes. Exact, but saves compute only, not whole responses.
:::

## The request path

:::flow Request path with a guarded two-level cache
lookup: Query -> Normalize -> Exact hit? -> Semantic hit (similarity at least tau)* -> Guard check!
miss: Miss or guard fails -> Call the LLM -> Cacheable? -> Store with TTL + version keys
:::

## The threshold is a precision-recall trade-off

:::curve Sweeping the similarity threshold from strict to loose
x: Hit rate (savings)
y: Precision of served hits
series: Example trade-off* | 0.05,0.995 0.2,0.975 0.35,0.93 0.5,0.86 0.65,0.74 0.8,0.58
mark: Pick by error budget* @ 0.2,0.975
mark: Loose: false hits! @ 0.8,0.58
:::

Lower thresholds save more money and serve more wrong answers. Do not pick the point from the curve's elbow. Pick it from your **tolerable wrong-answer rate**: if one wrong answer in forty is unacceptable, you need precision above 97.5%, wherever that lands. The curve's shape and position depend on your embedding model and traffic, so measure it on labeled pairs of "same intent" and "different intent" queries from your own data.

## How a semantic cache serves wrong answers

:::compare Near-duplicates that are NOT the same question
# Looks identical to embeddings
- "Cancel my order" vs. "Don't cancel my order"
- "Price of the Pro plan" vs. "Price of the Pro Max plan"
- "Store hours Saturday" vs. "Store hours Sunday"
# Why it happens
- Negation barely moves the sentence vector
- Swapping one entity or number barely moves it either
- High cosine similarity is not equivalence
:::

!!! warning Embedding similarity measures *topical* closeness, not *logical* equivalence. Negations, entities, dates, and numbers are exactly where similar-sounding queries diverge.

### Guard the hit

Before serving a semantic hit, run cheap checks for exactly what the embedding blurs: numbers, names, and polarity.

```python
import re

POLARITY = {"not", "no", "never", "without", "cannot"}        # plus any "n't"
ACTIONS = {"cancel", "stop", "start", "add", "remove"}          # opposing verbs

def tokens(s):
    s = s.lower().replace("\u2019", "'")      # curly apostrophes from phones
    return re.findall(r"[a-z0-9']+", s)

def negations(ts):
    return {t for t in ts if t in POLARITY or t.endswith("n't")}

def numerics(ts):
    return [t for t in ts if any(ch.isdigit() for ch in t)]   # 10am, v2, A123

def safe_hit(query, cached_query):
    q, c = tokens(query), tokens(cached_query)
    if numerics(q) != numerics(c):
        return False                      # different numbers, times, or IDs
    if negations(q) != negations(c):
        return False                      # negation flipped
    if set(q) & ACTIONS != set(c) & ACTIONS:
        return False                      # different requested action
    return True
```

This is still deliberately crude. It will not catch "Pro" vs. "Pro Max" or "Saturday" vs. "Sunday". For those, add an entity extractor or compare the content words that differ between the two queries. Test it against the inputs real users type: curly quotes, contractions, and alphanumeric IDs all broke an earlier version of this guard. A false *miss* costs one LLM call. A false *hit* costs a wrong answer, so err strict.

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

Key every entry by **tenant, model version, prompt template version, retrieval index version, and decoding parameters**. Version keys handle deploys automatically. They do not handle the world changing: prices, hours, and policies change without any deploy, so data-dependent answers still need TTLs or event-driven purges.

!!! warning A shared semantic cache is an attack surface. If one user can get a poisoned answer (for example via prompt injection) written into the cache, it is served to everyone who asks a similar question. Only write entries produced from non-personalized, injection-screened contexts, and never let one session create entries served to others without review.

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
- Choose the similarity threshold from your error budget, measured on labeled pairs from your own traffic.
- Guard hits against negation, number, and action mismatches, and test the guard on real user input.
- Never cache personalized responses across users, and treat a shared cache as an attack surface.
- Version-scope keys for deploys, and use TTLs or purges for data that changes.

**Further reading:** Runnable baseline: [semantic_cache in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems), including documented false-hit cases.
