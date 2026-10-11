---
title: How to Build a RAG System That Says "I Don't Know"
kind: guide
date: 2026-10-07
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

:::bars Root causes of wrong RAG answers in a typical audit (illustrative)
Right doc never retrieved! | 38 | 38%
Retrieved, but chunk split the fact | 17 | 17%
Retrieved, ranked too low | 14 | 14%
Generator ignored the context | 16 | 16%
Question has no answer in corpus | 15 | 15%
:::

Look at the last bar. A meaningful slice of questions *cannot* be answered from your corpus. Without abstention, every one of those becomes a confident fabrication.

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
def hybrid(query, k=20):
    dense = vector_search(embed(query), k)
    sparse = bm25_search(query, k)
    # Reciprocal rank fusion: robust, no score calibration needed.
    scores = {}
    for ranked in (dense, sparse):
        for rank, doc in enumerate(ranked):
            scores[doc] = scores.get(doc, 0) + 1 / (60 + rank)
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

!!! tip Put 15-20% unanswerable questions in your eval set on purpose. If you never test abstention, you will never get it.

## Key takeaways

- Most RAG failures are retrieval failures. Fix retrieval first.
- Use hybrid dense plus sparse retrieval with rank fusion.
- Chunk on document structure, and carry section context.
- Gate on retrieval confidence, require citations, and verify grounding.
- Evaluate answering and abstaining as two separate skills.

**Further reading:** Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP* (2020). Runnable baselines: [doc_qa and citation_checker in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
