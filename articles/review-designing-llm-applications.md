---
title: Designing Large Language Model Applications: Failure Modes and Design
kind: review
date: 2026-11-16
order: 15
slug: review-designing-llm-applications
summary: My take on Suhas Pai's design-first guide to LLM applications: strongest on failure modes and model choice, and best read by people who already know how LLMs are built.
tags: LLM design, failure modes, domain adaptation
book: Designing Large Language Model Applications: A Holistic Approach to LLMs | Suhas Pai | O'Reilly Media, 2025 | 9781098150501 | img/books/designing-llm-applications.jpg
verdict: A clear design-first guide for LLM applications, strongest on failure modes and model choice, not a framework tutorial.
rating: 4.0
---

The first thing this book tells me is that 343 people worked on training models at OpenAI, not counting the data labelers. I like that as an opening move. It says, before anything else, that building these things is a large human effort, and that the design decisions come later, after the data and the training. Most LLM books start with prompting. This one starts with training data, and that choice runs through the whole book.

First edition, O'Reilly, March 2025, 350 pages, ISBN 9781098150501. Suhas Pai is a machine learning researcher and co-founder and chief technology officer of Hudson Labs. I would still check the publisher record before citing edition details, since release dates drift a few weeks across retailers.

## The design question the book addresses

I came to this book after building enough LLM applications to know the difference between a demo and a system that has to survive real users. A short prompt can look brilliant in a demo. Then the input changes, the domain shifts, or the stakes rise, and the same prompt fails in quiet ways. That gap is what Pai is writing about. He frames the book as a holistic guide to getting large language models to work in real use cases, with a lot of attention on commonly observed failure modes and the limits of state of the art models.

That framing sets a different test from a framework tutorial or a model training manual. A design book should help me decide what to build, what to leave out, and what to check before and after release. It should connect model choice to the task, the data, the user, and the cost of being wrong. And it should make failure visible early, so a team can plan for it instead of hearing about it from users. On that test, the book mostly delivers.

:::compare Model choice as a design decision
# A larger general model
- Broad capability across tasks
- Higher cost and latency to serve
- Harder to update for a narrow domain
# A smaller adapted model
- Narrower scope by design
- Lower cost and latency to serve
- Needs data and evaluation for the domain
:::

## Choosing and customising models

Model choice is often treated as a search for the best model in general. Pai points the other way. Model choice is a design decision. It depends on the task, the input, the required output, the available evidence, and the operating budget. A model that writes fluent prose can still be the wrong pick for a task that needs exact structure, a verifiable source, or a fast response.

So I need criteria before comparison. The first criterion is the task definition. The task should state what counts as a correct answer, what counts as a partial answer, and what counts as a failure. It should state whether the answer must cite a source, follow a format, respect a policy, or stop when evidence is missing. Without those criteria, a comparison of models can reward fluency or length while missing the properties the application needs.

A further criterion is the operating budget. Latency, throughput, token use, and cost all shape the choice. A larger model can be slower and more expensive to serve, and the difference matters more when the application handles many requests or when the user waits for a response. A smaller model can be faster and cheaper, but only if it meets the quality standard for the task. The trade off cannot be settled by a general ranking. It has to be measured on the task, with the same cases and the same standard applied to each candidate.

Customisation sits inside the same decision. The book covers choosing and customising models, and that wording is important. Customisation is not a single technique. It can mean clearer instructions, a better prompt structure, retrieval of relevant context, a structured output requirement, or a change to model weights through fine tuning. Each option changes a different part of the system, and each creates a different maintenance burden. Prompt changes are easy to revise but can be brittle as context grows. Retrieval changes the evidence the model sees, and its quality depends on the source, the index, and the ranking. Fine tuning can stabilise a repeated behaviour, but it needs clean training examples, a held out test set, and a plan for updates when the task or the data changes.

My rule from reading this is to start with the lightest change that addresses the observed failure. If the model lacks current or private information, retrieval is the direct test. If the model misunderstands the task or the format, clearer instructions and a structured output check are the direct test. If a stable behaviour remains unreliable after those changes, fine tuning becomes a reasoned next step rather than a first resort. That sequence keeps the system simpler, and it makes each change easier to evaluate. Some tasks do not need a model change at all. A deterministic rule, a lookup, a template, or a simpler classifier can be more reliable and easier to maintain than a model call. Calling a language model to check whether a string is empty is not engineering, it is a hobby. The design question is not whether a large language model can do the task, but whether it is the right tool for the task under the constraints of accuracy, cost, latency, and maintainability.

:::layers A design pass before building
Define the task | State the user, the input, the required output, and what counts as failure
List the evidence | Name the sources the answer must use and how they will be checked
Choose the model | Compare candidates on the same cases with the same standard
Plan the fallback | Define what happens when evidence is missing or the output fails a check
Measure the budget | Record latency, token use, and cost on representative traffic
:::

## Domain adaptation

Domain adaptation is the work of moving a general model into a specific setting. The setting can be a field such as finance, health, law, or engineering, or it can be a narrower setting such as a single product, a single team, or a single document collection. In each case, the model brings general language ability, and the application must supply the domain knowledge, the terminology, the format, and the standard of correctness.

The first problem I hit here is vocabulary. A term can have a precise meaning in one domain and a different meaning elsewhere. A document can use abbreviations, codes, or shorthand that a general reader would miss. A task can require a specific unit, a specific date format, or a specific citation style. If the application does not make those expectations explicit, the model can produce an answer that sounds plausible while using the wrong term, the wrong unit, or the wrong convention. The design response is to define the terminology and the format in the instructions, in the retrieved context, or in the output check, and to test with cases that use the domain terms as they appear in real documents.

The second problem is evidence. A general model may have seen public text about a domain, but it does not have access to a private document, a current policy, or a recent record unless the application supplies it. Retrieval is often the practical way to supply that evidence, and its design matters as much as the model choice. The source must be current, complete enough for the task, and permitted for the use. The retrieval step must return the relevant passages rather than the most similar but unhelpful text. The model must be asked to use the retrieved passages, and the output must be checked against them where the task requires grounding. If any link in that chain is weak, the final answer can be fluent and unsupported at the same time.

## Commonly observed failure modes

The most useful part of a design book is often its account of failure. Failure modes are recurring ways an application goes wrong, and they are more useful than a list of success stories because they give me something to test for. Pai puts failure modes at the centre of this book, and that emphasis fits anyone who has to ship a system that will meet inputs the demo never showed.

One common failure is an unsupported answer. The model produces a confident statement that is not supported by the supplied evidence, or that cannot be checked from the supplied evidence. The surface form looks complete, and the content may even be correct in general terms, but the application cannot show why it is correct for this case. The risk is higher when the task asks for a specific fact, a specific value, or a specific source, and the model is allowed to answer without a check. The design response is to require evidence where the task needs it, to test with questions whose answer is absent from the source, and to define a no answer path for cases where the evidence is missing.

A second failure is a format failure. The model produces the right content in the wrong structure, omits a required field, adds an extra field, or uses a value that does not match the expected type. The failure may look minor, but it can break a downstream step that expects a fixed schema. The design response is to validate the output against the schema before it is used, to test with edge cases that stress the format, and to treat a validation failure as a system failure rather than a cosmetic issue.

A third failure is a context failure. The model receives too little context, too much context, or the wrong context. Too little context leaves the model to fill gaps from general knowledge. Too much context can bury the relevant passage, increase cost and latency, and make the output harder to trace. The wrong context can introduce a contradiction or a stale fact that the model then repeats. The design response is to inspect the retrieved passages separately from the generated answer, to test with long and short inputs, and to measure whether adding context improves the result on the task standard.

A fourth failure is a reasoning failure on a multi step task. The model may handle a single step well and fail when the task needs a sequence of steps, a check between steps, or a revision after an error. It may produce a plan that looks coherent and then fail to follow it, or it may continue after a step has already failed. The design response is to break the task into checkable steps where possible, to validate intermediate results, and to set a limit on retries and on total work. A loop without a stopping rule can consume time and cost without improving the result.

:::tree Diagnose the failure before choosing the fix
Application output misses its target
  Does it lack current reference information?
    Test retrieval and source quality
  Does it misunderstand the task?
    Improve instructions and validate output
  Does it fail on a multi step task?
    Break the task into checkable steps
  Does it fail only on new inputs?
    Add those cases to the regression set
:::

The table below summarises the four failures above as a checklist for testing, not as a score. The checks are simple by design. A failed check indicates where to look next.

| Failure mode | Symptom | Check |
|---|---|---|
| Unsupported answer | Confident statement with no evidence behind it | Ask a question with no answer in the source and see what happens |
| Format failure | Right content in the wrong structure | Validate the output against the schema before use |
| Context failure | Too little, too much, or the wrong context | Inspect the retrieved passages on their own, apart from the answer |
| Multi-step failure | One step works, the sequence falls apart | Break the task into steps and validate the result of each step |

The quadrant below is my gut check, not a measurement. The placement is my opinion, based on what the book covers. It asks two plain questions. How often does this failure show up, and how much harm does it do when it does.

:::quadrant Failure modes, author's placement, opinion not measurement
x: Rare | Common
y: Low harm | High harm
pt: Stale answer @ 0.6,0.7
pt: Refusal @ 0.3,0.3
pt: Format break @ 0.7,0.4
pt: Wrong tool call @ 0.4,0.8
:::

The quadrant can be read as follows. A stale answer sits up and to the right, common enough and harmful enough to deserve a real check. A refusal sits down and to the left, rarer and lower harm in most cases, though it remains an inconvenience for users. A format break is common but often lower harm, until it breaks a downstream step. A wrong tool call is less common and high harm, because it can trigger an action that was not requested. None of these positions is derived from a dataset. They are a way to argue about priorities in a design review.

## Strengths, limitations, and what it will not teach

Its strength is the design focus. The book does not present model use as a collection of prompt tricks. It frames model use as a set of decisions about task, evidence, model, adaptation, and evaluation, and it gives failure modes a central place in that frame. That structure is useful for someone who already knows how to call a model and now needs to decide how to build an application that will hold up under real inputs. It is also useful for a team that needs a shared vocabulary for design review, so that a discussion can move from general impressions to specific choices and specific tests.

What I liked most is how practical and consequences-focused it is. The book starts with training data rather than prompting, which is the honest place to start, and it stays close to specifics, with code snippets and side notes that actually add something instead of filling space. Security is not a final chapter bolted on at the end. It runs through the book, which is how it should be, since security added at the end is usually security added never.

The honest limitation is that more than half the book is model design, training, and fine tuning, with much less on application architecture or production treatment. That is not a flaw in the material, it is a mismatch to manage. If I came here expecting a guide to shipping and operating an LLM application, I would leave with a strong sense of how models are built and a thinner sense of how to run one. The transitions can be abrupt, and some sentences read as if they were written in a hurry. I tripped over a few. And the companion repo is poorly structured, which is a shame, because a book this practical deserves a repo a reader can actually navigate.

There is also the usual temporal problem. Model capabilities, hosted model behaviour, pricing, and tool details change quickly. A published explanation can remain conceptually valuable while its named model comparison becomes historical. I check current model documentation, current pricing, and reproducible evaluation results before making a deployment choice, and I would not trust any 2025 book to do that checking for me.

:::flow A simplified design loop
Define the task -> Build a fixed case set -> Test the current design -> Group failures by cause -> Change one component -> Re-test on the same cases
:::

## A practical study plan and exercise

My study plan is to read with one concrete application in mind. First write the user task, the stakes, and the success conditions. The task should be narrow enough to test, and the stakes should be stated plainly, so the team can decide how much checking the application needs. As the book moves through model choice, domain adaptation, and failure modes, record which decisions apply to that application and which risks remain open. Avoid implementing every technique that appears in a learning path. The point is to build a reasoned design, not a maximal stack.

For an exercise, create a small document question answering prototype with a fixed set of public documents. Draft twenty questions, including questions whose answer is absent from the documents, and establish what counts as grounded, incomplete, or unsupported before running the prototype.

The exercises in this book do what good exercises should do. They make me stop and think instead of nodding along, which is rarer than it should be in technical books.

!!! tip Write the failure cases before model selection.
    The edge cases decide the design.

The loop summarises the method in five steps. Changing one component at a time makes it possible to judge what improved the result.

:::loop Design, test, fix cycle
Design the task
Build a fixed case set
Test and group failures
Change one thing
Re-test on the same cases
:::

I would compare direct prompting with retrieval. Inspect the retrieved passages separately from the generated response, so a correct answer does not hide a weak retrieval step, and a good retriever is not blamed for a generation error. Add a structured output check, and record latency and token use for each case. Then alter one component at a time, and preserve the test cases so the change can be judged fairly.

## Who should read it and how it compares

Software engineers, machine learning practitioners, technical product builders, and engineering leads who need to reason about large language model applications are the likely audience. The book is most useful for someone who already understands software systems and now needs a design frame for model applications, rather than a first introduction to programming or to machine learning. A reader who only wants prompt examples will find the scope broader than necessary. A reader who wants to derive attention equations or train at scale will need a more technical companion.

I should be blunt about who should not pick this up first. This is definitely not a book for beginners. It requires solid prior knowledge, especially about how LLMs are built. This book assumes the reader already knows how these models are put together, and it does not slow down to explain that. That is a fair choice, not a flaw, but it means a beginner will bounce off it.

Page count is not a measure of quality, but it indicates the scale of the read. The publisher page counts are 350 pages for this book from O'Reilly, 352 pages for Building Applications with AI Agents from O'Reilly, and 522 pages for LLM Engineer's Handbook from Packt. This book and Albada's book are close in length. The Handbook is a much longer read, which fits its wider production scope, and at 522 pages it could also hold a door open.

:::bars Publisher page counts
Designing Large Language Model Applications | 350 | 350 pages
Building Applications with AI Agents | 352 | 352 pages
LLM Engineer's Handbook | 522 | 522 pages
:::

Compared with [*AI Engineering*](../review-ai-engineering/), this book is oriented toward design and failure modes rather than the wider application lifecycle of evaluation, prompting, retrieval, agents, adaptation, and inference. The two books overlap on model choice and adaptation, but the emphasis differs. *AI Engineering* gives a broad systems map for building applications around foundation models. This book gives a closer look at the design decisions that determine whether an application will hold up when the input is difficult or the domain is specific. I would use *AI Engineering* to structure the application, and this book to test the design choices inside that structure. That comparison describes scope, not a ranking of books.

Compared with [*Designing Machine Learning Systems*](../review-dmls/), this book is oriented toward large language model applications rather than the wider lifecycle of conventional predictive machine learning. *Designing Machine Learning Systems* covers the system around a model, from data and training to deployment and monitoring, for a broad range of machine learning applications. This book covers the design of a narrower class of applications, where the model is a large language model and the central problems are model choice, domain adaptation, and failure modes. I reach for the earlier book for the production lifecycle. I reach for this book for the design decisions that come before and during that lifecycle, when the team is deciding what the application should do and how it should fail.

## Further reading and public sources

- O'Reilly Media catalog entry for *Designing Large Language Model Applications: A Holistic Approach to LLMs* by Suhas Pai, ISBN 9781098150501. Check the catalog for current edition and availability.
- [*AI Engineering*](../review-ai-engineering/): Chip Huyen's guide to building applications around foundation models, reviewed on this site.
- [*Designing Machine Learning Systems*](../review-dmls/): Chip Huyen's guide to the system around a model, reviewed on this site.

## Verdict

My rating is 4.0, and it is my own judgment, not a hedge. The focus on failure modes, and the treatment of model choice and domain adaptation, give me a useful structure for study. The book is strongest as a design companion alongside a broader application guide and a hands-on implementation resource, with current model and tool details checked against primary sources before deployment.

It is a serious, practical book that respects its reader. I just think it has a narrower audience than its title suggests, and a thinner production treatment than its title promises. Readers who need a design frame for a real application, and who are willing to test their choices on a fixed set of cases, are the most likely to gain from it. That is the reader I would hand it to.
