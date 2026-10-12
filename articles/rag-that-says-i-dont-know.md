---
title: How to Build a RAG System That Says "I Don't Know"
kind: guide
date: 2026-10-11
order: 4
summary: Retrieval-augmented generation fails quietly. Here is how to engineer retrieval, grounding, citation checks, and abstention so wrong answers become honest refusals.
tags: RAG, retrieval, evaluation, grounding
---
The most dangerous RAG system is the one that always answers. A demo that never says "I don't know" is a hallucination engine with a search bar. In production, **calibrated abstention** is a feature you design, test, and ship.

## Anatomy of a RAG pipeline

:::flow The two halves of retrieval-augmented generation
offline: Documents -> Chunk + clean -> Embed + index -> Vector + keyword store
online: Query -> Rewrite + retrieve -> Rerank* -> Generate with citations -> Grounding check*
:::

Each arrow is a place where quality leaks. Most teams obsess over the generator. Most failures happen in **retrieval**.

## Where RAG actually fails

When an answer is wrong, trace it back through the pipeline. Every wrong answer has exactly one first point of failure, and the fix depends entirely on which one:

:::tree Triage a wrong RAG answer: find the first stage that failed
Wrong answer
  Answer exists in corpus?
    No: unanswerable question!
      Fix: abstention, not prompting
    Yes: was it retrieved?
      No: retrieval miss*
        Fix: hybrid search, chunking
      Yes: ranked in top k?
        No: ranking miss
        Yes: generation ignored it
:::

The first branch matters most. Some questions *cannot* be answered from your corpus. Without abstention, every one of them becomes a confident fabrication, and no amount of prompt tuning fixes that.

## Fix retrieval before the prompt

### Use hybrid retrieval

Dense embeddings are great at meaning and bad at exact identifiers like part numbers, error codes, and names. BM25 is the opposite. Use both and fuse the results.

:::compare Dense vs. sparse retrieval
# Dense (embeddings)
- Matches paraphrases and synonyms
- Weak on rare tokens, IDs, and codes
- Needs an embedding model and index
# Sparse (BM25)
- Exact term matching, very fast
- Misses paraphrases
- Zero training, highly debuggable
:::

```python
def hybrid(query, k=20, c=60):
    dense = vector_search(embed(query), k)
    sparse = bm25_search(query, k)
    # Reciprocal rank fusion (Cormack et al., 2009): score = sum of 1 / (c + rank),
    # with 1-based ranks and c = 60. No score calibration between retrievers needed.
    scores = {}
    for ranked in (dense, sparse):
        for rank, doc in enumerate(ranked, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1.0 / (c + rank)
    return sorted(scores, key=scores.get, reverse=True)[:k]
```

### Chunk on structure, not character counts

Split on headings, sections, and table boundaries. Keep a small overlap. Store the parent section title with each chunk so a lonely sentence still knows what it is about.

## Engineer the abstention path

:::tree Decision tree for answer vs. abstain
Answer?
  Retrieval confidence low!
    Abstain and suggest a rephrase
  Retrieval confidence high
    Claims supported by cited chunks*
      Answer with citations
    Some claims unsupported
      Drop unsupported claims or abstain
:::

Three gates, in order:

1. **Retrieval gate.** If the top reranker score is below a calibrated threshold, do not even call the generator. Say you could not find it.
2. **Citation requirement.** Prompt the generator to cite chunk IDs for every claim. No citation, no claim.
3. **Grounding check.** Verify that each cited chunk actually supports its sentence, with an entailment model or a judge you have audited.

!!! warning Lexical overlap is a weak grounding check. "The plan costs $80" overlaps almost perfectly with "The plan costs $8". Always compare numbers, dates, and entities explicitly.

## Evaluate both behaviors

:::quadrant RAG quality has two axes
x: Answers when it should | always
y: Abstains when it should | always
pt: Hallucination engine! @ 0.95,0.08
pt: Useless refuser! @ 0.1,0.95
pt: Calibrated system* @ 0.85,0.85
:::

| Metric | Measures | How |
|---|---|---|
| Recall@k | Did the right chunk get retrieved? | Labeled query to chunk pairs |
| Answer correctness | Is the answer right when given? | Reference answers or graders |
| Citation precision | Do citations support claims? | Entailment or audited judge |
| Abstention accuracy | Refuses the unanswerable, answers the answerable | Include unanswerable questions in the eval set |

!!! tip Put unanswerable questions in your eval set on purpose, in roughly the proportion you see in real traffic. If you never test abstention, you will never get it.

## Start with an answerability contract

Abstention is not a single confidence threshold. First define what “answerable” means for this application. A question can be answerable from the indexed corpus, answerable only with current external data, ambiguous because it lacks a required entity, or outside the system's scope. These categories need different responses. “I could not find an answer in the approved documents” is more accurate than implying that no answer exists anywhere.

Write the contract in terms of evidence. For example, an answer may be returned only when at least one authorized, sufficiently current source supports every material claim, the retrieved passages refer to the right product or time period, and the system can cite the passages it actually used. If any condition fails, the system should narrow the answer, ask a clarifying question, or abstain. A retrieval score alone cannot establish all those conditions.

Decide whether the product should answer partially. If two of three requested facts are supported, it may be useful to return those two and explicitly say which one was not found. But partial answers can mislead when the omitted fact changes the meaning, such as a policy exception or safety caveat. Define materiality and required fields for the use case; do not leave it to the generator to decide whether missing information matters.

:::compare Four outcomes are better than answer-or-refuse
# Supported answer
- Evidence covers the requested claim
- Return a concise answer and source references
# Partial answer
- Some requested parts are supported
- Identify what is missing and why
# Clarification
- A key entity, timeframe, or scope is ambiguous
- Ask a specific follow-up before retrieval or action
# Abstention
- No adequate authorized evidence is available
- Explain the boundary and offer a safe next step
:::

## Build retrieval around document lifecycle

Retrieval quality begins before embedding. Preserve source identity, tenant or access scope, document version, effective date, ingestion time, and section hierarchy. Normalize formats carefully: remove boilerplate and navigation where appropriate, but do not discard footnotes, table headers, warnings, or conditions that qualify a statement. Keep a mapping from each indexed chunk back to its canonical source and exact location so a citation can be checked and a source can be removed later.

Chunking is a retrieval compromise. Small chunks make a focused match but can lose definitions, exceptions, and table context. Large chunks retain context but can dilute the signal and waste the generation context window. Split along semantic boundaries, carry heading paths and parent identifiers, and evaluate several sizes on representative questions. When a relevant passage depends on surrounding material, retrieve the child chunk and then expand to a bounded parent context rather than indiscriminately making every chunk huge.

Documents change. Treat ingestion as a versioned process with deterministic parsing, deduplication, and a record of source hashes. On an update, mark old chunks superseded and ensure search cannot return a mixture of incompatible versions. Deletion must propagate to vector indexes, keyword indexes, reranker stores, caches, and replicas according to the applicable retention requirements. A “delete” in the source catalog is not enough if a stale embedding can still be retrieved.

Hybrid search and reranking are useful components, not guarantees. Tune candidate depth and fusion on labeled query-document relevance judgments. Measure retrieval recall before and after reranking, and examine cases where the relevant source is absent from the candidate pool: a reranker cannot recover a document it never sees. Query rewriting should preserve identifiers, negation, dates, and user intent; log the original and rewritten query under appropriate privacy controls so regressions can be diagnosed.

## Enforce access control before content reaches the model

A RAG index is a data-access layer. Every retrieval request must be constrained by the caller's authorized tenant, groups, and document-level permissions. Apply access filters inside the retrieval boundary before candidates are returned, not merely in the prompt or after the model has already seen the text. Test this with adversarial queries that ask for another tenant's records, and verify that forbidden document content is absent from retrieval traces and model context.

Authorization can change while a document is indexed. Decide how quickly revocations must take effect, then design an invalidation path for permission changes and user-group updates. For highly sensitive content, re-check authorization at retrieval time against a current policy source, rather than trusting a long-lived ACL snapshot. Use deny-by-default behavior if the authorization service is unavailable; availability is not a reason to leak restricted passages.

Citations should not expose information the user cannot access. Generate citations only from retrieved, authorized source IDs, and resolve those IDs through an access-controlled viewer. Avoid making unguessable URLs your sole authorization mechanism. Logs and evaluation sets also need tenant and ACL protection: a test harness that exports every retrieved passage can become a convenient cross-tenant data leak.

:::flow Secure retrieval request
Authenticated principal -> Resolve current tenant and document scope -> Filter candidate search -> Verify source permission -> Pass authorized excerpts to model -> Resolve citations through access check
:::

Treat retrieved content as untrusted input. A document can contain malicious instructions, accidental secrets, or content intended for another audience. The model should be instructed that passages are evidence, not governing instructions, while the system still assumes that instruction separation can fail. Retrieval should not grant tools, permissions, or authority. A document saying “email this file externally” is just text; the answer-generation process should have no capability to do that merely because the text was retrieved.

## Validate every claim and citation

A citation check has several distinct questions: does the cited source exist, is it authorized and current, does the cited span contain the relevant information, and does that information support the exact claim? Checking only that a citation ID appeared in the prompt handles the first question poorly and none of the others. Preserve evidence spans or offsets and validate them against the canonical document version used for generation.

Break generated answers into atomic claims where practical. A single sentence may combine a date from one source, a requirement from another, and an unsupported recommendation. Checking the sentence as one unit can hide the unsupported piece. Structured output can associate claim IDs with one or more source IDs and spans; validate the structure before rendering. For critical numeric, date, and entity claims, use deterministic comparison against extracted evidence when feasible, because lexical overlap or a generic semantic score can miss a changed digit or qualifier.

A natural-language entailment model or LLM judge can help prioritize review, but neither is an oracle. Audit it against human-labeled supported, contradicted, and insufficient-evidence examples. Include hard negatives with similar wording but different products, dates, amounts, or conditions. Measure false acceptance of unsupported claims because that is the failure that defeats a grounded-answer promise. If evidence is ambiguous, the safe outcome is uncertainty, not a confident citation label.

A citation should be useful to the reader. Prefer precise section or page references and show the source title and applicable date. Do not cite an entire long document when only one paragraph supports the answer. If several sources conflict, surface the conflict or follow a documented source precedence rule; quietly selecting the newest-looking passage can be wrong if it is a draft or applies to a different audience.

## Calibrate abstention with the right evaluation set

Construct evaluation examples from at least four groups: answerable questions with clear evidence, answerable questions whose evidence is difficult to retrieve, unanswerable questions absent from the corpus, and questions that are ambiguous or conflict with stale or contradictory sources. Include cases where retrieval finds topically similar but non-supporting text. The tempting false hit is a more informative test than an obviously irrelevant query.

Measure the stages separately. Retrieval recall@k asks whether supporting evidence appears among candidates. Reranker metrics measure ordering. Citation precision asks whether emitted citations support claims; citation coverage asks whether material claims have support. Answer correctness measures the content, and abstention behavior measures whether the system chooses the proper response class. Also measure the end-to-end rate of unsupported answers, since a pipeline can look good stage by stage while failures compound.

Thresholds should be calibrated on data from the intended distribution, but a single threshold may be unsuitable across query types. A strong score for a common policy document does not prove the same confidence for a rare table lookup, another language, or a document recently changed. Track sample size and uncertainty for each important slice. If the system has too little evidence to estimate error for a critical query family, use a conservative path and gather labels rather than declaring success from an aggregate.

| Evaluation slice | Example | Failure to expose |
|---|---|---|
| Missing evidence | Ask about a topic absent from the corpus | Fabricated answer instead of abstention |
| Near-match | Similar product, different model | Entity substitution |
| Temporal conflict | Old and current policy versions | Stale evidence selected |
| Permission boundary | Ask for another team's document | ACL leakage |
| Multi-part question | One part supported, one absent | Unsupported completeness claim |
| Citation challenge | Plausible text with wrong number | Citation that does not entail claim |

Review false answers and false abstentions separately. A false answer can harm trust or cause a bad decision; a false abstention adds friction and may make the system useless. Their costs are not necessarily symmetric. Pick thresholds from an explicit risk policy and user experience goal, and make that choice visible to operators. Do not tune on the final test set repeatedly; keep a locked validation set and refresh a separate sample as the corpus and query mix evolve.

## Trace the first failure and monitor the whole path

For each sampled production request, retain a privacy-controlled trace of the original query, rewrite, authorized candidate IDs and ranks, reranker scores, evidence versions, answer claims, citations, gate decisions, and final outcome. Avoid logging full prompts and private documents by default. Use access controls, redaction, retention limits, and stable IDs so authorized investigators can reconstruct failures without making sensitive content broadly available.

Build an error taxonomy aligned to pipeline stages: source missing, parsing loss, chunk boundary, retrieval miss, rank miss, ACL filter error, stale version, unsupported generation, citation mismatch, abstention false positive, and unavailable dependency. Assign a fix to the earliest causal stage. If the source never entered the corpus, prompt changes cannot solve it. If retrieval was correct but the model ignored a caveat, inspect evidence formatting and answer constraints. This prevents teams from repeatedly tuning the generator to compensate for upstream data defects.

Monitor corpus freshness, indexing lag, retrieval empty-result rate, candidate relevance on sampled queries, citation-validation failures, abstention and clarification rates, latency by stage, and access-denial anomalies. Alert thresholds should be based on baseline traffic and service expectations, not invented universal percentages. A sudden decrease in abstention may mean the corpus improved-or that a guard was accidentally disabled. Pair operational metrics with regular human review of a stratified sample.

Use a shadow or staged release when changing chunking, embeddings, reranking, prompts, ACL logic, or thresholds. Compare outputs and evidence on fixed test cases, then sample live traffic without changing user-visible behavior where possible. Keep rollback versions of indexes and configuration. Rollback cannot undo a disclosure, so security failures require immediate containment, access review, and a clear incident process rather than merely restoring an older prompt.

## A production readiness checklist

- Answerability and partial-answer rules are explicit for this product's actual user tasks.
- Source versions, effective dates, provenance, and deletion are tracked end to end.
- Retrieval filters enforce current tenant and document permissions before model exposure.
- Citations resolve to authorized source locations and support atomic claims.
- Evaluation covers missing, ambiguous, stale, conflicting, and near-match evidence.
- Retrieval, grounding, abstention, latency, and end-to-end failures are measured separately.
- Logs minimize sensitive content and have access, retention, and deletion controls.
- Changes to indexes, policies, models, and prompts are versioned and reversible.
- Operators can trace a failure to its earliest stage and disable unsafe behavior.

## Key takeaways

- Most RAG failures are retrieval failures. Fix retrieval first.
- Use hybrid dense plus sparse retrieval with rank fusion.
- Chunk on document structure, and carry section context.
- Gate on retrieval confidence, require citations, and verify grounding.
- Evaluate answering and abstaining as two separate skills.

**Further reading:** Lewis et al., [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) (2020). Cormack, Clarke, Buettcher, [Reciprocal Rank Fusion](https://doi.org/10.1145/1571941.1572114) (SIGIR, 2009). For operational threat modeling, see [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/). Runnable baselines: [doc_qa and citation_checker in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
