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

## Define what is allowed to be cached

A cache entry is a stored decision about a particular request context. Before deciding how to match requests, define which responses are eligible at all. A public explanation of a stable concept may be cacheable. An account balance, order status, medical answer, permission-dependent document, or response that includes a user's private history generally is not safe to share as a cross-user semantic result. “The answer looks generic” is not enough; the content may still have been derived from private context.

Classify responses by dependencies. Record whether the output depends on tenant data, principal identity, retrieved documents, current external state, locale, feature flags, time, or conversation history. For each dependency, choose one of three policies: include a stable scope/version in the key, validate the dependency before serving, or declare the response uncacheable. If you cannot identify what an answer depends on, you cannot construct a correct cache key.

A conversation makes exact caching more subtle too. A normalized current message is not a sufficient key when the answer depends on prior turns, a system instruction, tool results, or generation parameters. Include the relevant context fingerprint or avoid caching the response. Normalization itself must preserve meaning: removing punctuation or case-folding can be safe for some search queries and unsafe for code, identifiers, or language-specific text.

:::tree Cacheability decision in order
Does output contain personal or permission-scoped data?
  Yes: isolate to exact principal scope, or do not cache!
  No: does it depend on mutable source data?
    Yes: require version validation, event purge, or short TTL
    No: is the prompt/model/config fingerprint complete?
      Yes: eligible for guarded caching*
      No: do not cache until dependencies are known
:::

## Make tenant isolation a hard invariant

The safest default is tenant-scoped storage and lookup. Include the tenant in the namespace or compound key, and enforce that scope in the cache service itself, not solely in application code. If semantic neighbors are searched globally and filtered afterward, the cache has already exposed cross-tenant metadata and may have selected another tenant's answer. Test isolation at the storage boundary with adversarial IDs and concurrent requests.

For personalized entries, scope at least to the authenticated principal and all relevant authorization context. A user can lose group membership or document access while an entry remains in the cache. Re-check current authorization before serving, or invalidate affected entries when permissions change. If the system cannot reliably establish current scope, bypass the cache. Cache isolation is not a substitute for authorization, and a high similarity score never grants access to a result.

Keep result metadata alongside the response: tenant and principal scope, source IDs and versions, authorization policy version, prompt and model version, creation time, expiry, and any dependencies needed for revalidation. Store only what is necessary, encrypt data at rest and in transit according to the service's controls, and apply retention and deletion policies to cache values, embeddings, logs, backups, and replicas. Embeddings can reveal information about source text; they are not automatically anonymous just because the original words are absent.

A cache-hit response should still pass the same output authorization and safety checks as a fresh response. If a semantic match comes from a different user's request, do not expose the old query or its metadata while explaining the hit. Keep diagnostics in protected operator traces, not user-facing output. Rate-limit lookup behavior where it could be abused to infer whether a sensitive query has been seen before.

## Invalidate on every dependency that can change

Versioned keys are valuable for deployments, but they are only one invalidation mechanism. A prompt template version, model version, embedding model, decoding settings, retrieval index, and policy configuration can all affect output. Include the relevant versions in the entry identity or maintain a namespace that can be atomically switched. After an embedding-model upgrade, old vectors may no longer be comparable; do not search mixed vector spaces unless the store explicitly supports that compatibility.

External facts change independently of releases. For prices, inventory, schedules, account states, and policies, use source version checks, event-driven invalidation, or a bounded TTL appropriate to the allowed staleness. A TTL is a maximum stale window, not proof that an answer stays correct until expiry. If an event stream can be delayed or dropped, add reconciliation that compares active cache dependencies with current source versions and purges stale entries.

For RAG responses, retain the IDs and version of every supporting source. On update, revocation, or deletion, invalidate responses that depend on the affected source. This can use a reverse index from source ID to cache entry IDs. Without dependency tracking, teams tend to choose between expensive global purges and silently serving obsolete citations. For sensitive or fast-changing corpora, bypass response caching unless invalidation can be demonstrated to work.

Invalidation is distributed-systems work. Define behavior during cache or event-bus outages: fail open to the authoritative source if safe, or fail closed for sensitive data. Make purge operations idempotent, observable, and retryable. Track invalidation lag, failed purge count, and entries served after their source version changed. A successful publish acknowledgement is not the same thing as every replica forgetting the old answer.

| Dependency | Example control | Test that proves it works |
|---|---|---|
| Prompt or model change | Versioned namespace/key | Old-version answer is not selected |
| Source content update | Source-version validation or purge | Updated fact replaces cached response |
| ACL revocation | Permission recheck and dependency purge | Newly unauthorized user gets no hit |
| Tenant boundary | Tenant-local namespace and query filter | Cross-tenant neighbor is never returned |
| Time-sensitive fact | Bounded freshness policy | Expired answer triggers a fresh lookup |
| Cache outage | Explicit safe fallback policy | Failure does not bypass authorization |

## Treat poisoning and retrieval manipulation as cache threats

A shared semantic cache creates amplification: one malicious or simply incorrect response can be reused for many future queries. An attacker may try to seed it with a prompt-injected result, exploit a broad similarity threshold, or cause an answer generated from stale sources to become the canonical hit. Define eligibility rules for writes as carefully as lookup rules. Do not cache answers that used untrusted instructions as authority, failed citation checks, contained personal context, or were produced under uncertain authorization.

Separate the write path from the model's arbitrary claims. The application should decide whether an answer is cacheable after validation, and attach trusted provenance metadata itself. Do not let generated text set its own tenant, source version, safety status, or cache lifetime. Use limits on entry size and write frequency, and protect administrative purge capabilities. If review or reputation is used to promote shared entries, document how abuse is detected and corrected.

Semantic matching can also become a privacy side channel. Similarity queries may reveal whether a particular topic or phrase exists in another user's cache, even if the value is not returned. Tenant scoping, access checks before candidate materialization, restricted diagnostics, and appropriate rate limits reduce that risk. For particularly sensitive content, do not embed or semantically index cached queries at all; exact, principal-scoped lookup may be the safer engineering choice.

## Evaluate matching as a decision system

Build a labeled set from privacy-reviewed, representative query pairs. Label whether the cached response is safe and correct for the new request-not merely whether the two sentences are about the same topic. Include hard negatives for negation, entities, numbers, dates, product tiers, language, requested action, and access scope. Include paraphrases that truly are equivalent, as well as queries whose surface wording is different but whose answer depends on different context.

Split data by conversation or source event to prevent near-duplicate leakage. Keep a calibration set for choosing thresholds and a locked test set for final estimates. Labeling should include a reason such as equivalent intent, changed entity, changed polarity, missing context, stale fact, or unauthorized source. Have reviewers inspect disagreement cases and measure their own agreement; ambiguous labels mean the cache policy needs clarification.

Report precision among served semantic hits, not only an aggregate classification score. Also report hit rate, false-hit rate by risk class, false-miss rate, stale-hit rate, and uncertainty intervals. Weight examples or report separate slices if production prevalence differs from the challenge set. A high overall precision can conceal a small but unacceptable set of false hits for financial actions or permission-scoped information.

Choose the threshold from an explicit error budget and consequence model. A miss usually costs another model call; a false hit may expose data, provide stale instructions, or trigger a bad decision. Those costs differ by response class. You may use stricter thresholds or disable semantic caching for high-impact categories. Estimate savings only after including embedding computation, lookup infrastructure, invalidation work, validation checks, and the cost of human review or remediation.

:::flow Validate a candidate cache policy
Build privacy-safe labeled pairs -> Separate calibration and locked test sets -> Sweep thresholds by risk class -> Measure hit precision and savings -> Replay invalidation and tenant tests -> Approve bounded rollout
:::

The threshold curve shown earlier is illustrative, not a benchmark. The relationship between similarity, precision, and hit rate depends on the embedding model, normalization, query mix, and correctness definition. Recompute it after changing any of those. A threshold copied from another product is a guess wearing a decimal point.

## Roll out conservatively and monitor outcomes

Start in shadow mode: compute candidate cache matches but still call the normal answer path. Compare the proposed hit with the fresh answer and a human-reviewed sample, while taking care not to send private material to an unapproved evaluation system. Shadow mode can estimate match quality without serving potentially unsafe results. It cannot fully measure user behavior or downstream effects, so follow it with a small, reversible rollout for eligible low-risk responses.

Use cache bypass switches by tenant, response type, source, and model version. A global kill switch is useful during incidents, but scoped controls let operators stop one problematic category without disabling harmless hits everywhere. Define who can invoke each switch, what alerts fire, and how cached entries are purged. If a wrong hit is discovered, identify all entries derived from the same source or generation context and determine who received them, subject to lawful and privacy-respecting incident procedures.

Monitor exact and semantic hit rates separately, hit precision from sampled audits, freshness and invalidation lag, cache misses caused by guards, latency for hit and miss paths, total cost after infrastructure, and user corrections or support escalations. Watch per-tenant access denials and unusual query patterns. A rising hit rate is not inherently good; it can mean traffic became repetitive, or that the threshold became dangerously loose.

Compare hit and miss outcomes by response type and slice. Users may stop reporting errors if a cached wrong answer sounds plausible, so do not rely solely on explicit feedback. Schedule independent sampling, preserve an uncached control where practical, and check whether serving cached answers changes downstream outcomes. Re-audit after changes to embeddings, prompt construction, source freshness, tenant policy, or the guard logic.

## A cache review checklist

- Every response dependency is identified; unknown dependencies make the response ineligible.
- Tenant and principal boundaries are enforced before semantic candidates are exposed.
- Current authorization and source versions are checked for scoped or mutable content.
- Source IDs support targeted purge on update, revocation, and deletion.
- Cache writes occur only after answer, citation, and safety validation.
- Hard-negative pairs test negation, entities, numbers, time, and action changes.
- Precision and stale-hit risk are measured by response class with uncertainty.
- Logs and embeddings have defined access, retention, and deletion controls.
- Shadow evaluation, staged rollout, scoped bypass, and incident purge are ready.

## Key takeaways

- Layer exact, semantic, and prefix caches.
- Choose the similarity threshold from your error budget, measured on labeled pairs from your own traffic.
- Guard hits against negation, number, and action mismatches, and test the guard on real user input.
- Never cache personalized responses across users, and treat a shared cache as an attack surface.
- Version-scope keys for deploys, and use TTLs or purges for data that changes.

**Further reading:** Cormack, Clarke, and Buettcher, [Reciprocal Rank Fusion](https://doi.org/10.1145/1571941.1572114) (SIGIR, 2009), for rank fusion as a retrieval component. For cache invalidation fundamentals, see [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111). Runnable baseline: [semantic_cache in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems), including documented false-hit cases.
