---
title: Reliable Machine Learning: What Happens When SREs Run Your Models
kind: review
date: 2026-10-11
order: 10
slug: review-reliable-ml
summary: Written by Google-veteran SREs and ML practitioners, this book applies Site Reliability Engineering to ML. SLOs, incident response, and organizational design for models in production.
tags: SRE, reliability, MLOps, incident response
book: Reliable Machine Learning: Applying SRE Principles to ML in Production | Cathy Chen, Niall Richard Murphy, Kranti Parisa, D. Sculley, Todd Underwood | O'Reilly Media, 2022 | 9781098106225 | img/books/reliable-ml.jpg
verdict: The book that treats ML as an operational discipline. Essential for anyone on call for a model, and for leaders deciding how ML teams should be organized.
rating: 4.5
---
Most ML books stop at deployment; this book focuses on operating ML systems. Written by a team including Site Reliability Engineering practitioners and D. Sculley, co-author of the influential paper “Hidden Technical Debt in Machine Learning Systems,” *Reliable Machine Learning* asks what it means to run a model dependably when its behavior or inputs change. The public publisher description and contents position it as an application of SRE ideas to production ML. A case study appears in the book, but the company identity is not established here, so this review does not assign it one.

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

The key distinction is not that conventional software is deterministic in every practical sense or that ML failures are always statistical. Rather, learned behavior depends on data and the environment as well as code. A service can remain available while the relationship between inputs and outcomes changes. Reliability work therefore has to consider infrastructure, data quality, model behavior, and the consequences of predictions.

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

!!! insight Infrastructure availability is necessary but not sufficient. A service that returns a prediction on time can still be unhelpful if input data is stale, a schema has changed, or performance has degraded for an important population. SLOs should distinguish what is observable quickly from what requires delayed labels, and they should connect each measure to an owner and response.

### Incident response for ML

The incident-response emphasis is useful because ML symptoms and causes may sit in different systems. A serving dashboard can look healthy while a feature pipeline emits unexpected values; an outcome metric can move only after delayed labels arrive. A sound response process therefore preserves evidence, checks upstream dependencies, identifies the affected decision path, and distinguishes mitigation from root-cause correction. The diagram illustrates a possible failure pattern, not a claim about a specific event in the book.

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

:::compare Where an ML incident's root cause usually is vs. where teams look first
# Where teams look first
- The model code and weights
- The serving infrastructure
- The last deploy
# Where the cause often is
- An upstream data change nobody announced
- A feature pipeline silently emitting nulls
- A slow drift in the world, with no deploy at all
:::

## Limitations

- Pre-LLM, so foundation-model operations, such as prompt versioning and judge drift, are not covered directly, though the principles transfer cleanly.
- Dense in places, and written for practitioners with some production experience.

## How it connects to my guides

The canary-and-rollback discipline in [How to Ship a Model Safely](../ship-models-safely/) applies the SRE mindset this book teaches.

## Scope and review basis

This review is based on the public publisher catalog and table of contents for *Reliable Machine Learning: Applying SRE Principles to ML in Production*, by Cathy Chen, Niall Richard Murphy, Kranti Parisa, D. Sculley, and Todd Underwood. O'Reilly lists the title as a 2022 publication. The discussion below describes the SRE-for-ML scope indicated by those materials; it does not claim personal completion of the book or reproduce its case studies. Some metadata can differ across formats and catalog records, so readers should verify edition, date, and ISBN on the publisher page before purchasing or citing a specific edition.

The book's useful premise is that an ML system is more than a trained artifact. It includes a data path, training and validation process, serving interface, monitoring, and a team responsible for operating it. A model may be mathematically sound while the service fails through stale inputs, a schema mismatch, a rollout that cannot be reversed, or a metric that does not reflect user outcomes. SRE practices offer a way to discuss reliability as an engineering objective rather than an afterthought.

## What reliability means for a learned system

Reliability begins with the service contract. What is the system expected to do, for whom, and within what time and quality constraints? A conventional service can often define success in terms of availability and latency, while an ML-backed feature may additionally require data freshness, acceptable model quality, or a safe fallback when confidence or input validity is inadequate. These dimensions can conflict: a more expensive model might improve one quality measure but miss a latency objective; a strict validation check might reject malformed data but reduce availability when an upstream dependency changes.

Service-level objectives make those trade-offs explicit. An SLO is not just a dashboard threshold. It should have an accountable owner, a measurement window, a clear data source, and a response plan. Infrastructure indicators are usually available quickly; model quality may depend on labels that arrive much later. A team can therefore use leading indicators-schema validity, feature ranges, freshness, prediction distributions-alongside lagging outcomes. Leading indicators can reveal unusual behavior but should not be mislabeled as accuracy. Distribution change, for example, is a reason to investigate, not proof that a model is wrong.

This distinction also prevents alert fatigue. If every metric has a page-worthy threshold, nobody can respond to the signals that matter. Alerts should correspond to actionable conditions and runbooks should tell responders what to inspect, who owns each dependency, and how to mitigate risk. A prediction-quality SLO may be unsuitable for immediate paging if reliable labels arrive days later; a broken feature contract may be actionable immediately. The measurement interval should match the phenomenon and the available evidence.

## The production lifecycle as an operating loop

The lifecycle diagram in the current article is a deliberately compact summary: data collection and management, training, evaluation and validation, serving, then monitoring and incident response. These stages are coupled. A data definition affects both training and serving. An evaluation procedure determines what a release gate can detect. Monitoring provides evidence for retraining or rollback, but retraining itself requires validation and controlled rollout. Treating each stage as a separate handoff invites gaps in ownership.

A release process should preserve the ability to answer basic questions later: Which model version produced this output? Which schema and transformation were used? Which evaluation criteria passed? What changed in the rollout? Can the previous version be restored without corrupting state or losing important data? Traceability is not paperwork for its own sake; it turns an ambiguous production symptom into a diagnosable change history.

Canary deployment and rollback are especially useful when the impact of a model change can be measured safely in a small portion of traffic. But a canary only helps if traffic assignment is valid, comparison windows are meaningful, and the monitored measures are sensitive to the failure modes at issue. A model can pass latency checks and still harm a particular segment. Release checks should therefore combine service health with relevant quality and safety evaluations, and should make uncertainty visible when immediate ground truth is unavailable.

## Incident response and organizational ownership

An ML incident can originate from a code deploy, data source, transformation, training run, dependency, or changed environment. The on-call engineer needs an operational map: where inputs originate, which checks guard them, which teams own each component, and what safe mitigation is available. A model rollback may not solve a feature pipeline defect; conversely, rolling back upstream data can restore old behavior while hiding a deeper compatibility failure. Incident records should separate observed symptoms, confirmed causes, mitigations, and follow-up actions.

Blameless postmortems are useful when they produce system changes rather than a list of individual mistakes. Examples of durable follow-up include adding a schema contract, making a freshness objective observable, building a replayable test from a failed request, documenting a rollback procedure, or clarifying who owns a shared feature. The organizational concern in the book's public framing is important: if data scientists, platform teams, and service owners each assume someone else owns reliability, operational gaps become predictable.

Ownership should follow the actual dependency graph. A model team may own the artifact and evaluation; a data platform may own the pipeline; a product team may own the user-facing decision. Those boundaries need an agreed escalation path and shared definitions of acceptable behavior. “The model is owned by team X” is incomplete if that team cannot inspect or change the feature source that drives its predictions.

## Technical applications and limits

The principles are most directly applicable to supervised models whose inputs and outputs can be monitored in a production service: ranking, classification, forecasting, recommendation, and risk scoring. They also apply to LLM-backed systems, but additional concerns arise: prompt and retrieval changes, model-provider changes, nondeterministic output, tool permissions, and evaluation of generated content. A traditional prediction-distribution monitor will not establish factual correctness or safe tool behavior. Teams need task-based evaluations, trace capture that respects privacy, and controls for prompt injection and data exposure.

The book's 2022 publication date makes it a foundation for operational thinking, not a full guide to the current foundation-model ecosystem. It should be paired with up-to-date guidance on model and prompt versioning, retrieval quality, agent security, and provider-specific behavior. “SRE principles transfer” is a starting hypothesis; the actual indicators, error budgets, and incident playbooks must be adapted to the system's risk and feedback latency.

A further limitation is that reliability can be confused with quality. A highly reliable service may consistently produce poor predictions. A model with strong average offline metrics may still fail under shift, for a subgroup, or in a workflow where users cannot correct it. Reliability engineering does not make these normative questions disappear. Teams need to define whose outcomes matter, which failures are unacceptable, and what escalation or human review is appropriate.

## Comparison with related reading

| Topic | What this book's public scope suggests | Complementary work needed |
|---|---|---|
| Service operations | SRE concepts applied to ML in production | Local incident procedures and service ownership |
| Data reliability | Treating data as a production dependency | Data contracts, lineage, privacy, and governance |
| Model quality | Monitoring and evaluating deployed behavior | Task-specific metrics, slice analysis, delayed labels |
| LLM operations | General reliability habits transfer | Current prompt, retrieval, tool, and safety controls |
| Release management | Controlled operation and response | Deployment tooling and tested rollback mechanisms |

## Reading and study guide

1. **Map one real system.** Draw the path from source data to user-visible decision. Mark owners, contracts, and points where a stale or invalid value could enter.
2. **Define layered objectives.** Write one infrastructure objective, one data objective, and one model or product-quality objective. State the limits of each measure.
3. **Design the alert response.** For every alert, identify what action is possible, who takes it, and what evidence they need. Remove alerts that have no actionable response.
4. **Run an incident tabletop.** Simulate an upstream schema change, delayed labels, or model-quality regression. Practice mitigation, communication, and evidence preservation.
5. **Audit recovery.** Verify that rollback, replay, and model-version identification actually work. A runbook that has never been tested is a hopeful document, not a recovery capability.

### Discussion questions

- Which ML quality signals can be measured in real time, and which require trustworthy delayed outcomes?
- When should an input anomaly trigger rejection, fallback, or only investigation?
- How can a team avoid treating a change in feature distribution as conclusive evidence of model failure?
- Who should own an incident when the model, feature service, and product decision belong to different teams?
- What does an error budget mean when errors have unequal impact across user groups?

### Practice exercises

- Create a one-page SLO proposal for a prediction endpoint. Include latency, availability, data freshness, a quality measure, owners, and measurement caveats.
- Build an incident timeline for silent null features. Mark detection opportunities and add one prevention or mitigation action at each appropriate stage.
- Write a rollback checklist for a model release, including artifact identity, traffic routing, data compatibility, and verification after rollback.
- For an LLM feature, distinguish availability, response correctness, policy compliance, and tool execution safety. Propose a separate evidence source for each.

## Connecting SRE habits to model behavior

A practical lesson is to distinguish service health from decision health. Service health includes whether requests are accepted and answered within agreed limits. Decision health asks whether outputs remain appropriate for the task and population. The first is often observable from logs and traces; the second may require labels, audits, user feedback, or expert review. Combining them into one green dashboard light hides useful distinctions. A report should state which indicators are direct measurements and which are proxies.

Data validation can serve as an early warning system. Schema checks catch incompatible structure; range and null checks catch some invalid values; freshness checks reveal lagging pipelines. These checks are necessary but incomplete. A feature can satisfy its schema while changing meaning, and valid data can still represent a shifted population. Pair mechanical checks with monitoring tied to how the feature is generated and with outcome evaluation when labels become available. Avoid claiming that a single drift statistic proves a change in model quality.

Release design should reflect reversibility. A canary, shadow evaluation, or staged rollout can limit exposure, but each method answers a different question. Shadow traffic can compare predictions without changing user outcomes, yet it may not reveal behavioral effects of the new decision. A canary can expose real impact, but requires guardrails and a way to stop quickly. Rollback is useful only if the old model, dependencies, and compatible data path are still available. These details are appropriate subjects for a team runbook and a production exercise.

## Reliability for teams with delayed feedback

Many ML products do not receive immediate ground truth. A recommendation may influence later behavior; a risk outcome can take time to observe; a user may never provide explicit feedback. In these cases the team should avoid pretending that a real-time proxy is the true target. Define interim indicators as leading signals, track how they correlate with eventual outcomes where possible, and periodically audit the proxy itself. The less direct the measure, the more carefully its limitations should be communicated.

Delayed labels also affect incident management. Preserve prediction and model-version metadata under suitable privacy rules so eventual outcomes can be connected to the decisions that generated them. Use sampling or targeted review when full feedback is unavailable, and record selection bias in the resulting data. A postmortem should explain not only what moved but how the team knows the movement represents a real user-impacting change.

## Further reading and public sources

- Chen, Murphy, Parisa, Sculley, and Underwood, *Reliable Machine Learning*: [O'Reilly publisher catalog](https://www.oreilly.com/library/view/reliable-machine-learning/9781098106218/).
- Sculley et al., [“Hidden Technical Debt in Machine Learning Systems”](https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html), for background on system-level ML risks.
- Google, [Site Reliability Engineering book](https://sre.google/sre-book/table-of-contents/), for foundational SRE concepts; adapt the material to the operational context rather than copying thresholds.

## Verdict

**Provisional assessment: 4.5/5 based on the public publisher description, contents, and cited foundational sources.** The SRE lens is a strong fit for teams that operate models and need clearer ownership, objectives, and incident practice. The title should be supplemented for modern LLM-specific risks, and this rating is an assessment of the public scope-not a claim of personal full-book reading.
