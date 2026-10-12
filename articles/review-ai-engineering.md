---
title: AI Engineering: A Public-Materials Review of Building with Foundation Models
kind: review
date: 2026-10-11
order: 2
slug: review-ai-engineering
summary: An evidence-conscious review of Chip Huyen's guide to foundation-model applications, evaluating its documented coverage of evaluation, prompting, retrieval, agents, adaptation, and inference.
tags: foundation models, LLM applications, evaluation
book: AI Engineering: Building Applications with Foundation Models | Chip Huyen | O'Reilly Media, 2025 | 9781098166304 | img/books/ai-engineering.jpg
verdict: A broad, systems-minded guide to building applications around foundation models. Its strongest promise is a disciplined way to frame application choices and evaluation, not a timeless catalog of models or a substitute for implementation practice.
rating: 4.5
---

This review is based on the publisher's public table of contents and description, publicly available sample material, and the author's official bibliographic or companion materials that can be checked without assuming access to the complete text. It does not claim that Shivam personally read the whole book. Because this field changes quickly, the assessment distinguishes durable engineering questions from model-specific examples that may need current verification.

Bibliographic note: O'Reilly's catalog URL identifies the 2025 edition with ISBN `9781098166304`, matching this review's cover and metadata. The author's official repository lists `9781801819312`, but that ISBN resolves to a different title in catalog lookup, so it appears to be an erroneous citation rather than a distinct format. Use the publisher record for purchase or citation and verify it again when needed.

## The field the book addresses

“AI engineering” has become a broad label for work that uses pretrained foundation models as components in applications. The engineering tasks do not end at sending a prompt. A team has to decide how to ground a model in information, shape its behavior, evaluate open-ended outputs, manage latency and costs, handle failures, and update the application as models or requirements change. The public description and table of contents position Huyen's book as a guide across this application lifecycle, rather than a textbook on training a foundation model from scratch.

That distinction matters for choosing a resource. A book focused on application engineering is expected to connect model capabilities to product requirements and system behavior. It should help a reader ask when to retrieve information, how to test an output, whether adaptation is justified, or what serving trade-offs matter. It need not teach every detail of transformer mathematics, distributed model training, or production operations for a particular cloud. Treating it as a complete answer to all of those topics would set an unfair and impractical bar.

:::compare Two adjacent engineering jobs
# Foundation-model application engineering
- Select and adapt available models for a use case
- Build prompts, retrieval, tools, and user-facing behavior
- Evaluate probabilistic outputs and the system around them
# Model training and research engineering
- Train or modify model architectures and weights
- Study optimization, training data, and model internals
- Operate large-scale training and research infrastructure
:::

## The high-value problem: evaluation

One prominent theme in the documented scope is evaluation. It is a difficult area because application outputs often admit several acceptable phrasings rather than a single exact answer. A useful test therefore needs a stated criterion: factual support, task completion, format compliance, safety behavior, usefulness, or some combination. Without a criterion, a score can look scientific while only measuring what was easy to count.

:::layers A practical evaluation loop
Define the target | State what success and failure mean for this application
Construct cases | Include representative, difficult, and adversarial inputs
Choose evidence | Use exact checks, programmatic tests, human review, or model-assisted judging as appropriate
Analyze errors | Group failures by cause instead of averaging away important defects
Re-test changes | Keep cases stable enough to compare prompts, models, and retrieval versions
:::

Different evaluation methods have different blind spots. Exact match is useful for constrained outputs but punishes harmless wording variation. Similarity metrics can reward topical resemblance without confirming correctness. Human review can capture context but needs clear rubrics and consistency checks. Model-based judges can scale comparisons, but their preferences, prompt sensitivity, and correlated errors need auditing. No evaluator should be treated as an oracle simply because it returns a numeric score.

The useful conceptual move is to connect offline evaluation to product outcomes without confusing them. A benchmark score is evidence about a defined set of tasks; it is not automatically evidence of user benefit, safety, or reliability in deployment. A team can combine representative test sets, qualitative review, online monitoring, and narrowly defined operational metrics. The choice depends on risk and use case. For instance, an acceptable tone score cannot compensate for incorrect high-stakes advice, and average success can conceal a small but consequential failure class.

## Selecting the adaptation method

Prompting, retrieval-augmented generation (RAG), and fine-tuning are often marketed as rival approaches. They are better understood as tools for distinct shortcomings, with overlap and trade-offs. Retrieval can provide relevant external context that changes or updates independently of model weights. Prompt design can clarify instructions and output constraints. Fine-tuning can be considered when a repeatable behavior or format is not reliably achieved by lighter methods and the team has appropriate data, an evaluation plan, and a reason to own the added lifecycle.

:::tree Diagnose the failure before choosing the intervention
Application output misses its target
  Does it lack current or private reference information?
    Test retrieval, permissions, source quality, and citation behavior
  Does it misunderstand the task or format?
    Improve instructions and validate structured output
  Is a stable behavior still unreliable after simpler changes?
    Assess fine-tuning with clean training examples and held-out tests
  Is the quality acceptable but cost or latency too high?
    Measure smaller models, caching, batching, quantization, or distillation options
:::

This is a diagnostic map, not an automatic recipe or a claim that the book prescribes exactly these branches. Each intervention creates new failure modes. RAG can retrieve irrelevant or contradictory passages; prompting can become brittle as context grows; fine-tuning can overfit, encode stale information, or make updates harder. Cost optimization can reduce quality for cases that are rare but important. Changes should therefore be evaluated against representative cases and explicit acceptance criteria.

## Architecture beyond one model call

A foundation-model application is a pipeline with dependencies. It may include user input handling, routing, retrieval, model inference, tool execution, output validation, logging, and a response. If a system uses an agent-like loop, it also needs limits on actions, time, retries, and permissions. Reliability is a property of this composition, not simply of the base model.

:::flow A simplified application request path
User request -> Input and policy checks -> Retrieval or tool selection -> Model inference -> Output validation -> Response and observability
:::

This perspective makes it easier to separate model quality from application quality. Poor answers may originate in a weak retriever, an incomplete knowledge source, a prompt that hides key constraints, a tool returning malformed data, or a model that cannot perform the requested task. Debugging gets expensive when all such errors are filed under “the LLM hallucinated.” A good engineering workflow captures enough structured traces to attribute failures while respecting privacy and data-governance requirements.

The documented broad coverage of retrieval and agents is useful as an organizing map, but a map is not a production security review. Tool calls require authorization, validation, and limits; retrieved documents can be untrusted inputs; logs may contain sensitive data; and graceful fallback must be designed. Agentic autonomy is not a default quality improvement. When deterministic workflows can complete the job, adding an open-ended loop can increase cost, latency, and risk without creating proportionate value.

## Inference: quality has a serving cost

The application also has a serving budget. Users experience time-to-first-token, total response time, and interruptions differently. Operators see throughput, concurrency, token usage, and failure rate. Model size, prompt length, output length, batching, caching, and hardware can affect these measures. Quantization and smaller models may make service cheaper or faster, but they must be tested on the target task rather than assumed to be interchangeable.

A practical optimization order is to measure first, then identify the bottleneck. Trimming irrelevant context may improve latency and quality simultaneously. Reusing safe, stable work may enable caching. Batching can improve throughput but may change interactive latency. A smaller model may be sufficient for a subset of requests. These are engineering hypotheses to test with representative traffic and evaluation cases, not magic fixes. Optimizing only average latency can also conceal long-tail delays that dominate user experience.

## Strengths, limitations, and what it will not teach

The apparent strength of the book's scope is breadth tied to application decisions: it connects model use to evaluation, adaptation, and serving rather than treating prompting as the whole job. A reader looking for a shared vocabulary and a sequence of topics can use it to structure study or architecture discussions. Its value is likely greatest for practitioners who already understand software systems and want a deliberate path through foundation-model application concerns.

The central limitation is temporal. Specific model examples, vendor capabilities, prices, and best-performing techniques can change quickly. A published explanation may remain conceptually valuable while its named model comparison becomes historical. Readers should check current model documentation, current pricing, and reproducible evaluation results before making deployment choices. This assessment cannot certify the currency of every concrete recommendation because it is not based on a full edition-by-edition reading.

The book should also not be mistaken for a detailed course in transformer implementation, large-scale pretraining, advanced optimization, safety governance, or any single deployment platform. For internals and hands-on model construction, Sebastian Raschka's *Build a Large Language Model (From Scratch)* has a different focus. For the broader classical ML production lifecycle, Huyen's earlier *Designing Machine Learning Systems* is complementary. Neither replaces security, privacy, legal, accessibility, and domain-specific review for a real application.

## A practical study plan and exercise

A useful study plan is to read with one concrete application in mind. First write the user task, stakes, and success conditions. As the book's topics move through evaluation, prompting, retrieval, adaptation, and inference, record which decisions apply and which risks remain. Avoid implementing every technique just because it appears in a learning path. The point is to build a reasoned decision process, not a maximal stack.

For an exercise, create a small document-question answering prototype with a fixed set of public documents. Draft twenty questions, including questions whose answer is absent, and establish what counts as grounded, incomplete, or unsupported. Compare direct prompting with retrieval. Inspect the retrieved passages separately from the generated response; otherwise a correct answer can hide a weak retrieval system, or a good retriever can be blamed for a generation error. Add a structured output check and record latency and token usage. Then alter one component at a time and preserve the test cases.

A second exercise can compare a large model and a smaller candidate on a constrained task. Choose examples that include normal and edge cases, write a rubric before seeing outputs, and include human inspection for failures that the automatic check cannot detect. Record the trade-off among quality, latency, and cost. This teaches the most useful lesson in model selection: “best” is conditional on the task and the system's requirements.

## Who should read it and how it compares

Software engineers, ML practitioners, technical product builders, and engineering leads who need to reason about foundation-model applications are the likely audience. Readers who only want prompt examples may find the scope broader than necessary; readers who want to derive attention equations or train at scale will need a more technical companion. It can serve as a framework-setting book for teams, provided current details are verified against primary documentation.

Compared with *Designing Machine Learning Systems*, *AI Engineering* is oriented toward foundation-model applications rather than the wider lifecycle of conventional predictive ML. Compared with DDIA, it addresses a different layer: application-level model behavior rather than general-purpose distributed data-system fundamentals. Compared with Raschka's scratch-built GPT path, it is about engineering applications around models, not learning all core model mechanics by implementing them. These comparisons describe scope, not a ranking of books.

## A decision record for an AI feature

Before shipping an AI feature, a team can write a short decision record that captures the intended user, task, supported inputs, and expected response. It should identify which output errors are merely inconvenient and which can cause harm, what evidence is available at inference time, when the application should decline, and who can correct a bad result. This is a practical way to connect broad application-engineering topics to product ownership. It also makes it harder for a successful demo to become a production commitment without an explicit review of risks.

The decision record should distinguish model uncertainty from missing system context. If a response must use a company's latest policy, a model's training data is not an acceptable source of truth. If a user asks for an action that requires a permission check, a fluent explanation is not authorization. If a request cannot be solved with available evidence, the system needs a defined no-answer path. Those boundaries belong in the design before prompt wording is tuned.

A useful prototype plan can separate quality experiments from integration experiments. First, test whether the model can perform the task on a fixed set of examples. Next, test whether the retrieval or tool layer supplies the needed information. Then test the composed flow, including validation, errors, and fallback. This staged approach does not remove the need for end-to-end testing; it makes failures easier to localize. It also prevents a strong model-only result from being mistaken for evidence that the full product is ready.

## A decision record for an AI feature

Before shipping an AI feature, a team can write a short decision record that captures the intended user, task, supported inputs, and expected response. It should identify which output errors are merely inconvenient and which can cause harm, what evidence is available at inference time, when the application should decline, and who can correct a bad result. This is a practical way to connect broad application-engineering topics to product ownership. It also makes it harder for a successful demo to become a production commitment without an explicit review of risks.

The decision record should distinguish model uncertainty from missing system context. If a response must use a company's latest policy, a model's training data is not an acceptable source of truth. If a user asks for an action that requires a permission check, a fluent explanation is not authorization. If a request cannot be solved with available evidence, the system needs a defined no-answer path. Those boundaries belong in the design before prompt wording is tuned.

A useful prototype plan can separate quality experiments from integration experiments. First, test whether the model can perform the task on a fixed set of examples. Next, test whether the retrieval or tool layer supplies the needed information. Then test the composed flow, including validation, errors, and fallback. This staged approach does not remove the need for end-to-end testing; it makes failures easier to localize. It also prevents a strong model-only result from being mistaken for evidence that the full product is ready.

One final discipline is to establish a change budget. Every prompt, model, retrieval index, and tool update can shift behavior, even when the visible user interface stays the same. Record which components changed, keep a regression set, and decide what degree of difference warrants human review. When a vendor updates a hosted model behind a stable endpoint, preserve representative comparisons where possible and define a fallback if the change violates critical requirements. This is especially important for workflows where explanations sound plausible even when the underlying answer changes.

Documentation should include limitations in language that users can act on. “AI may make mistakes” is too vague to guide safe use. Users need to know which sources the system can access, what it cannot verify, whether generated content needs review, and how to report an issue. A clear boundary can reduce over-trust without implying that disclaimers alone solve a technical failure. Pair communication with enforced permissions, validation, and human escalation for high-impact cases.

## Verdict

The rating is a provisional assessment of the publicly documented scope, not a claim of complete personal reading. The described framework for evaluation, retrieval, adaptation, and serving offers a useful structure for a reader's own study. Fast-changing model examples and implementation details should be checked against current primary sources.
