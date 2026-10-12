---
title: Designing Data-Intensive Applications: A Map of System Trade-offs
kind: review
date: 2026-10-11
order: 1
slug: review-ddia
summary: A public-materials review of Martin Kleppmann's 2017 first edition, focused on its data-system concepts, practical boundaries, and relevance to modern ML infrastructure.
tags: distributed systems, databases, data engineering
book: Designing Data-Intensive Applications | Martin Kleppmann | O'Reilly Media, 2017 | 9781449373320 | img/books/ddia.jpg
verdict: A rigorous conceptual guide to the trade-offs beneath storage, replication, transactions, and data processing. Especially useful when readers want architecture principles rather than a tool cookbook.
rating: 5
---

This review assesses the first edition of Martin Kleppmann's *Designing Data-Intensive Applications* (DDIA), published by O'Reilly in 2017. It is based on the publisher's public table of contents and description, publicly available sample material, and the book's official companion material where relevant. It is not a claim that Shivam has read the complete book. That distinction matters: the following assessment describes what the documented structure and accessible material support, and it avoids treating familiarity with the book's reputation as a substitute for checking every page.

Bibliographic care is also important here. This page addresses the 2017 first edition and its twelve-chapter, three-part organization. A later-edition publication status, date, or precise contents have not been independently verified for this review, so no claim is made about whether a second edition has appeared or what it contains. The familiar ISBN in the metadata identifies the first-edition listing; consult the publisher's catalog for current availability and edition information.

## What the book is trying to teach

DDIA is organized around properties that any data-intensive application must negotiate: reliability, scalability, and maintainability. Those words can sound like generic engineering goals, but the book connects them to concrete architectural choices. Reliability asks what happens when a component fails or data is corrupted. Scalability asks how the design behaves as traffic, stored information, or operational complexity grows. Maintainability asks whether a system can be understood and changed by the people who inherit it.

:::layers Three recurring system qualities
Reliability | Continue to meet an acceptable contract despite faults and human mistakes
Scalability | Accommodate growth without assuming a single magic machine or unlimited budget
Maintainability | Keep the design understandable, operable, and adaptable over time
:::

The book then moves from the foundations of data systems to distributed data and finally to derived data. That structure is valuable because it discourages jumping directly to fashionable architecture diagrams. Before asking which database or streaming platform to adopt, readers need a way to reason about records, indexes, failure modes, consistency, and the consequences of copying or transforming information.

:::layers First-edition structure, as listed in the public table of contents
Part I: Foundations of Data Systems | Chapters 1–4: application qualities, data models, storage and retrieval, encoding and evolution
Part II: Distributed Data | Chapters 5–9: replication, partitioning, transactions, distributed-system trouble, consistency and consensus
Part III: Derived Data | Chapters 10–12: batch processing, stream processing, and the future of data systems
:::

The exact chapter titles make the progression clearer: “Reliable, Scalable, and Maintainable Applications”; “Data Models and Query Languages”; “Storage and Retrieval”; “Encoding and Evolution”; “Replication”; “Partitioning”; “Transactions”; “The Trouble with Distributed Systems”; “Consistency and Consensus”; “Batch Processing”; “Stream Processing”; and “The Future of Data Systems.” This is a first-edition chapter map, not an assertion that every example or tool remains current.

## A useful way to read the storage chapters

Chapter 3's storage discussion is important not because it offers a universal database ranking, but because it helps name the trade-offs that implementations make. Log-structured designs and page-oriented designs organize writes and reads differently. Those choices affect write amplification, compaction, lookup paths, storage layout, and operational behavior. A system with many writes and tolerance for background compaction can have different needs from one that depends on predictable point lookups or supports complex updates.

:::compare Storage families as a reasoning prompt, not a selection rule
# Log-structured approaches
- Accumulate writes in append-friendly structures
- Reorganize data through compaction or merging
- Trade background work and read paths for write behavior
# Page-oriented approaches
- Organize records and indexes in pages
- Support in-place updates and structured lookups
- Trade page maintenance and write amplification for access patterns
:::

The practical lesson is not “choose an LSM tree” or “choose a B-tree.” It is to ask what workload is being served, where the cost appears, what latency distribution matters, and how much operational complexity the team can own. Benchmarks should reflect the real shape of keys, values, concurrency, cache behavior, retention, and failure recovery. A technology name is not a workload description.

Chapter 4's emphasis on encoding and evolution is particularly relevant anywhere independently deployed services exchange data. A schema is not merely a declaration for a serializer: it is a compatibility contract between producers, consumers, stored records, and code versions that may coexist during a rollout. Backward and forward compatibility are separate questions. A change can be readable by newer code while still breaking older consumers, or preserve old records while causing a new producer to emit values an old application cannot interpret.

That framing applies to feature pipelines and model inputs too. Renaming a feature, changing units, altering a missing-value convention, or changing token normalization may be a semantic schema change even if the storage type remains numeric or textual. A system that versions only its model but not the meaning and transformation of inputs is documenting only half of its prediction contract.

## Distribution means failure and coordination

The distributed-data section is valuable because it treats multi-machine behavior as a source of explicit trade-offs rather than a transparent scaling layer. Replication can improve availability and read capacity, but replicas may not agree at every instant. Partitioning can distribute storage and work, but it makes data placement, rebalancing, and cross-partition operations part of the design. Transactions offer useful guarantees, but their scope and implementation have limits that matter under contention and failure.

:::seq A stale read under asynchronous replication
actors: Client, Leader, Follower
Client -> Leader: write profile change
Leader --> Client: acknowledge write
Leader -> Follower: replicate change later
Client -> Follower: read immediately
Follower --> Client: may return older profile
:::

This is why “eventual consistency” should not be treated as a reassuring adjective. The application needs to know what users can observe and what guarantees are required: read-your-writes, monotonic reads, or a stronger coordination model may be relevant in different cases. A social feed, a bank balance, and a model-serving feature lookup do not necessarily need the same contract. The right question is not whether consistency is good or bad; it is which anomalies are acceptable, to whom, and for how long.

The chapter on distributed-system trouble also has an enduring conceptual role. Networks delay and drop messages; machines pause or fail; clocks do not provide a perfect global ordering; and a response that did not arrive does not prove that an operation did not happen. These are not obscure edge cases that can be fixed by retrying everything. Retries can create duplicate work unless operations are idempotent or deduplicated. Timeouts are decisions made under uncertainty, not proof of a particular failure. The consequences reach API design, job orchestration, and event processing.

Consensus and consistency are often introduced with simplified slogans. DDIA's placement after replication, partitioning, transactions, and failure discussion supports a more useful mental model: coordination has a cost, guarantees are not interchangeable, and a system's promises depend on its failure assumptions. A design review should therefore ask what happens during partitions, leader changes, delayed messages, and partial completion;not merely whether a service is called “highly available.”

## Derived data and the ML connection

Part III treats batch and stream processing as ways to build and maintain derived views. This is a helpful lens for modern architectures containing search indexes, caches, analytics tables, event projections, and machine-learning features. These are not automatically authoritative records. They are products of transformations over upstream data, and each has freshness, replay, correctness, and recovery questions.

:::flow A derived-data path for a model feature
System of record -> Change capture or scheduled extraction -> Transformation and validation -> Feature or embedding index -> Prediction-time read
:::

The mapping from the book's data-processing concepts to an ML service is an interpretation, not a claim that the first edition documents today's vector databases or feature-store products. Still, the reasoning transfers. If an embedding index is rebuilt asynchronously, what is its lag? Can a backfill be repeated without double-counting? How does a model version identify the representation expected by an index? Can a correction to source data invalidate prior features? What does serving do when the latest derived record is missing?

These questions often sit between platform teams and model teams, which is exactly why a systems-level vocabulary helps. “The model is wrong” may turn out to mean that training and serving used different transformations, the index is stale, a replay changed event order, a consumer read incompatible serialized data, or the evaluation set was generated from a different snapshot. DDIA does not diagnose those modern incidents for a reader, but its concepts help formulate testable hypotheses.

## Strengths, limitations, and what it will not teach

The strongest feature supported by the book's public structure is conceptual sequencing. It moves from data models and storage toward replication, transactions, and processing rather than presenting architecture as a collection of vendor products. It encourages readers to compare guarantees, workload assumptions, and failure behavior. That makes it useful during design reviews even when the implementation under consideration did not exist when an example was written.

The main limitation is also structural: this is not a current product-selection catalog, a Kubernetes operations manual, or a tutorial for building a specific cloud-native platform. The first edition's named tools and ecosystem examples inevitably reflect their publication period. Readers should verify current product capabilities against current vendor documentation instead of treating an older example as a recommendation. Nor is this a book about embedding models, vector search, LLM evaluation, or responsible AI. Applying its concepts to those systems requires domain-specific reading and experiments.

A second limitation is that an abstract guarantee does not automatically yield an implementation plan. Teams still need workload measurements, failure tests, schema policies, backup and recovery drills, observability, security review, and operational ownership. The book can improve the questions; it cannot choose acceptable downtime, data-loss tolerance, or consistency semantics on behalf of a business.

## A study path and an exercise

A practical reading plan is to start with the reliability/scalability/maintainability framing, then work through Chapters 2–4 before moving to Chapters 5–9. Readers focused on data platforms can then compare Chapters 10 and 11 as distinct processing models, rather than conflating scheduled recomputation and continuous event handling. Chapter 12's forward-looking discussion is best approached as a set of architectural questions, not a timeless forecast.

A useful implementation exercise is to build a tiny event-derived view. Define a source event schema with an explicit version, write a deterministic transform that produces a user-level aggregate, and store the result in a separate read model. Then test a duplicate event, an out-of-order event, a schema evolution, a missing source record, and a complete replay. Record whether each operation is idempotent, what consistency users observe, and how the derived view can be rebuilt. The exercise makes several chapter themes measurable without pretending a toy implementation reproduces production scale.

Another useful exercise is to write down the read and write workload before comparing two storage engines. Include key distribution, value size, update frequency, read-after-write expectations, retention, and acceptable tail latency. Run a small benchmark only after stating those assumptions. This guards against the classic mistake of treating a benchmark result as a property of a database independent of the benchmark's workload.

## Who should read it, and what to pair it with

Backend and data-platform engineers are the clearest audience: the book supplies a shared language for persistence, replication, and processing decisions. ML engineers moving into production can use it to understand why feature freshness, replays, and deployment compatibility are not peripheral details. Technical leads may find it useful when reviewing architecture proposals because it turns vague claims such as “scales horizontally” into questions about partitioning, coordination, and failure recovery.

Readers seeking a practical LLM application playbook should pair this systems foundation with Chip Huyen's *AI Engineering*, which focuses on building applications around foundation models. Readers seeking an end-to-end classical ML lifecycle should look to *Designing Machine Learning Systems*. For implementation-level transformer mechanics, Sebastian Raschka's *Build a Large Language Model (From Scratch)* addresses a very different layer of the stack. DDIA complements these books; it does not replace them.

## Reading DDIA as an architecture method

A productive way to apply DDIA is to turn each abstract concept into an explicit system contract. For a replicated record, write down which client actions must observe their own writes, how long stale reads are tolerable, and what the client sees when a replica cannot be reached. For a transaction, state which invariants must hold across a group of changes and whether concurrent operations may observe partial progress. For a stream processor, define what counts as a duplicate event and whether reprocessing is allowed to alter a previously emitted result. These questions make the book's vocabulary useful beyond architecture interviews.

Contracts also reveal when two teams are talking past each other. “Exactly once” can refer to a narrowly defined processing guarantee, not an absolute promise that a business action occurs precisely one time across every service and external side effect. A pipeline may process an event once internally while a retry causes an email, payment, or downstream request to repeat. Idempotency keys, deduplication windows, transactional boundaries, and reconciliation are concrete responses, but each works within a scope. The architecture needs to name that scope rather than use the phrase as a blanket assurance.

Likewise, “scalable” is incomplete until the expected growth axis is named. A system may handle more reads by adding replicas but remain constrained by a write hotspot. More partitions can increase parallelism while making cross-partition queries or rebalancing more complex. More cached data may reduce database load while introducing invalidation and freshness questions. The design must consider the workload's likely direction of change, not simply the current request rate.

This is one reason the book remains a good companion for design reviews: it helps replace vague adjectives with observable behavior and failure assumptions. A review can ask which invariant the proposed transaction protects, which data can be recomputed, how a retry behaves, and what a user sees during lag. Those questions do not guarantee a correct system, but they make hidden assumptions easier to test. For readers who want a checklist rather than a product recommendation, that shift from “which technology?” to “which contract?” is arguably the most reusable outcome.

## Verdict

The rating is a provisional assessment of the first edition's publicly documented scope and conceptual organization, not a claim of complete personal reading. Its progression from data models to distributed and derived data provides a useful study map for engineers responsible for persistent state and pipelines. Readers should supplement it with current material on foundation-model applications and verify edition details with the publisher. Its most useful role is as a framework for asking sharper architecture questions, followed by experiments and failure tests on the system at hand.
