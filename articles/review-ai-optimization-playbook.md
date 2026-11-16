---
title: The AI Optimization Playbook: Enterprise AI Strategy and Measurement
kind: review
date: 2026-11-16
order: 13
slug: review-ai-optimization-playbook
summary: My take on The AI Optimization Playbook: a strategy-first guide for senior practitioners, strong on project selection, measurement beyond accuracy, causal inference, and governance.
tags: enterprise AI, AI strategy, MLOps
book: The AI Optimization Playbook: Drive business success with proven AI strategies, best practices, and responsible innovation | Dr. Chun Schiros, Supreet Kaur, Rajdeep Arora, and Dr. Usha Jagannathan | Packt Publishing, 2025 | 9781806115112 | img/books/ai-optimization-playbook.jpg
verdict: A strategy-first guide for leaders and senior practitioners, strongest on project selection and measurement, not a model-building manual.
rating: 4.0
---

I read The AI Optimization Playbook because I was tired of books that teach you to build a model and then go quiet right at the moment the model has to survive inside a company. This one does the opposite. It starts where most books stop: someone has to choose the work, fund it, measure it, and answer for it when it goes wrong. The book is by Dr. Chun Schiros, Supreet Kaur, Rajdeep Arora, and Dr. Usha Jagannathan, published by Packt in a first edition on 28 November 2025, 382 pages, ISBN-13 9781806115112. The foreword divides the labour neatly. Schiros takes strategy and leadership, Kaur and Arora take execution, architecture, and MLOps, and Jagannathan takes responsible AI and governance. Three jobs, four authors, and the split shows. Each part reads like it was written by someone who has done that job.

This is an enterprise AI strategy book, not a model code manual. If you want training code or model architecture detail, look elsewhere. If you want a way to pick the right AI work, test whether it is working, and run it without undue disorder, this is the lane it sits in. The book covers enterprise AI strategy, project selection, leadership support, proof of concept design and measurement, metrics beyond accuracy, operationalising machine learning systems, experimentation and causal inference, generative AI in the enterprise, and generative AI operations. That is broad coverage. The question is whether it holds together as one argument. It does, because every topic points back to the same idea. Strategy first, evidence second, operations third.

## Strategy before models

The core argument is that strategy comes before models. Strategy here is not a slide deck. It means naming the business goal, naming where AI can change an outcome that matters, and naming how the change will be recognised. It also means naming what will not be done. That last part is the difficult part in most enterprises, and it is where a lot of AI work quietly fails.

Starting with a model is tempting. The data is there. The model is new. The demo looks good. But the cost is real. A team can spend months on a technically sound system that no business owner asked for, that no user adopts, and that no leader will fund a second time. Accuracy does not save a project like that. A better model does not fix an unclear goal. A better prediction does not create value if the user workflow stays exactly the same. And a successful pilot does not justify production if running it costs more than the benefit it brings. I have seen that last one more times than I care to count.

The book therefore puts strategy first, before model selection, data preparation, and deployment planning. Who makes the decision, and how will they make it differently? What measure will show that the change happened? Those are the questions to answer first. This is why the book is suited to senior practitioner level. A senior practitioner spends a lot of time stopping work that does not matter, explaining why, and pointing the team at work with a clearer path to value. That is a skill, and it is rarely taught in model building books.

## Selecting high-impact projects and gaining leadership support

Project selection is one of the strongest parts of the book. The authors cover selecting high impact projects and gaining leadership support, and they treat the two as linked. A project is not high impact just because the model could be accurate. It is high impact because the business problem is material, the AI contribution is specific, the data and workflow allow a real change, and the organisation can sustain the result. That definition directs attention past technical feasibility. A feasible project with a small benefit can still lose to a harder project that tackles a larger cost or risk.

Leadership support works the same way. It is not a polished deck after the work is done. It is bringing leaders into the definition of success before the work starts. Leaders need to know what the project will change, what it will cost to build and run, what could go wrong, and how the team will decide whether to continue, change direction, or stop. The book treats that conversation as part of the project, not as administration around it. It also suggests sequencing. An enterprise rarely needs one giant AI programme. It needs projects ordered by value, risk, and readiness, with early work that builds trust and later work that builds on what was learned.

:::compare Project selection by technical interest and by business impact
# Technical interest first
- Starts with an available dataset or a new model
- Success is defined by model performance
- Leadership is asked to support work already chosen
# Business impact first
- Starts with a material business problem
- Success is defined by a changed decision or outcome
- Leadership helps define success before work starts
:::

*Caption: The book contrasts selection driven by what is technically interesting with selection driven by a defined business outcome.*

Approval is a process rather than a single meeting. The sequence below sets out that process step by step.

:::seq Getting a project approved, step by step
actors: Team, Leader, Finance
Team->Leader: Propose the project
Leader->Finance: Ask for a budget
Finance->Leader: Set the measures
Leader->Team: Approve or stop
:::

*Caption: Approval as a handoff, with measures agreed before the work starts.*

That sequence matters because it puts measures before money. Finance does not just sign a cheque. Finance sets the measures. The leader does not just say yes. The leader sends back an approve or stop. If the measures are vague, the whole chain wobbles. If they are clear, the team knows what good looks like before it writes a line of code. I like that Finance gets a real job in this story instead of the usual cameo as the people who say no at the end.

Picking projects is also a judgement call, and the book is honest about that in its framing. Effort and value do not line up neatly. Some work is cheap and useful. Some work is expensive and useful. Some work is cheap and pointless. The plot below is the author's placement, opinion not measurement. It is a way to talk about the choice, not a score from a dataset.

:::quadrant Picking projects, author's placement, opinion not measurement
x: Low effort | High effort
y: Low value | High value
pt: Quick win @ 0.3,0.8
pt: Big bet @ 0.8,0.8
:::

*Caption: Picking projects, author's placement, opinion not measurement. Quick wins sit low effort and high value. Big bets sit high effort and high value.*

A rubric is more useful here than an informal judgement. In a design review, each question can be considered in turn. A vague answer is itself informative.

| Check | What good looks like | Red flag |
| --- | --- | --- |
| Material value | A named cost, risk, or friction that matters | A vague promise of efficiency with no owner |
| Specific AI contribution | A clear step where AI changes a decision | AI added because the project sounds modern |
| Workflow fit | The user path changes in a way people can adopt | The model sits beside the workflow nobody uses |
| Evidence plan | Baseline, measures, and a decision point agreed up front | Success defined after the results come in |
| Owner and funding | A named owner and a run cost someone accepts | No owner for life after launch |
| Governance check | Data use, fairness, privacy, and audit needs named early | Governance raised only after launch |

## Proof of concept and measurement beyond accuracy

A proof of concept is often treated as a demo that a model can be built. The book treats it as a test of whether the proposed change is worth pursuing. A demo only needs to show that a prediction is possible. A test needs a defined baseline, a defined user or decision, a defined measure of success, and a defined point for the next decision. Without those pieces, a proof of concept can create enthusiasm without creating evidence. Enthusiasm is a poor basis for a production decision, though it is a great basis for a second demo, and a third, and a whole career of demos that never ship.

Measurement beyond accuracy is the natural companion to that view. Accuracy, precision, recall, and related model metrics are still useful, but they do not answer the questions that matter to an enterprise. A model can be accurate and unused. It can be accurate and too slow, too costly, or too hard to maintain. It can be accurate on historical data and unreliable when the operating environment changes. The book therefore covers defining metrics beyond accuracy for adoption. That means tracking whether the system is used, whether it changes the intended decision, whether it produces the intended outcome, and at what cost and risk. A new system should be compared with the current way of working, not only with a previous model. If the current process is manual, the baseline is manual performance, cost, and delay.

!!! tip Measure adoption, not just accuracy.
    A model nobody uses has no ROI to report.

The cycle does not end at the demo. It loops. Build small, measure what actually happened, decide, then operate what ships and learn from it. If the loop stops after the demo, the team learns nothing except that a demo is possible.

:::loop Proof of concept, measure, decide, operate
Build a small proof of concept
Measure use and outcome
Decide to continue, change, or stop
Operate and monitor what ships
:::

*Caption: The proof of concept loop, from a small build to a decision and then to operation.*

:::layers A practical evaluation loop
Define the target | State what success and failure mean for this application
Construct cases | Include representative, difficult, and adversarial inputs
Measure use and outcome | Track adoption, decision change, and business result, not only model scores
Decide the next step | Continue, redesign, or stop on the basis of the evidence collected
:::

*Caption: A measurement loop that moves from a defined target to a decision about the project.*

## Experimentation and causal inference

Experimentation and causal inference are the parts of the book that most clearly separate it from a general management guide. Plenty of strategy books talk about measurement in general terms. Fewer talk about how to design an experiment that can support a causal claim. Fewer still connect that design to the practical constraints of an enterprise. The book includes experimentation and causal inference, and the authors clearly want the reader to move from observing a correlation to testing whether an intervention caused a change.

That distinction matters in practice. An enterprise can observe that users of a new AI feature had better outcomes than users who did not. That alone does not show the feature caused the improvement. The users who chose the feature may have been more engaged, more experienced, or working on easier cases. Without a comparison group, a randomised assignment, or a careful quasi experimental design, the team cannot separate the effect of the feature from the effect of who used it. The book covers experimentation as a way to address that problem, and causal inference for when a clean experiment is not possible. A test needs a clear question, a defined treatment and comparison, a defined outcome, and attention to sample size, duration, and contamination between groups.

This is not about running a perfect experiment every time. In an enterprise, that is often impossible. The point is to be honest about what the evidence can and cannot support. If the design is weak, say so. If the comparison group is imperfect, say so. If the outcome is a proxy for the real outcome, say so. A team that states those limits plainly decides better than one that presents a correlation as proof. That stance is one of the things I liked most. The book would rather be honest about weak evidence than impressive about none.

## Operationalising ML and GenAI operations

Operationalising machine learning systems is the point where many enterprise projects stall. A model that works in a notebook may not work in production, because production needs data pipelines, versioning, monitoring, retraining, access control, and a plan for failure. The book covers operationalising ML systems, and it places that work in the context of MLOps. Packt lists enterprise ready MLOps among the key features, which means attention to the systems that keep a model running, not only to the model itself.

Generative AI adds another layer to that operational problem. The book covers GenAI in the enterprise and GenAI operations, or LLMOps. That scope includes choices specific to large language models, such as prompt management, retrieval, evaluation of generated output, cost control, latency, and handling outputs that are plausible but incorrect. A generative system cannot be judged only by a single accuracy score. It needs evaluation against defined cases, defined failure modes, and defined user expectations. It needs monitoring for drift in inputs, outputs, and the way users interact with the system. The book presents operationalisation as a continuing responsibility, not as a one time deployment step. Expect a playbook level of detail, not a code level implementation guide.

:::flow A simplified evaluation path
Business goal -> Project selection -> Proof of concept -> Measurement -> Operational decision
:::

*Caption: The path from a business goal to an operational decision, with measurement before the decision to scale or stop.*

Shipping is not the end of the work. Deployment is where monitoring, retraining, and failure handling become continuing responsibilities. If nobody owns those jobs, the system will drift, and the team will find out late. A playbook that names those jobs up front is useful to the reader, even if it does not hand over code for each one.

:::tree Diagnose the failure before choosing the fix
A project stalls after the pilot
  Is the value unclear?
    Define adoption and outcome measures
  Is the evidence weak?
    Design an experiment with a comparison group
  Is the system hard to run?
    Review monitoring, retraining, and ownership
  Is the risk unclear?
    Review governance, data use, and audit needs
:::

*Caption: A diagnostic tree for a stalled pilot, organised by the type of problem rather than by the model alone.*

## Responsible AI and governance

Responsible AI and governance are covered by Jagannathan in the book, and they are listed by Packt as part of the enterprise ready Responsible AI framework in the key features. The title itself puts responsible innovation up front, which signals that governance is not treated as a separate compliance chapter at the end. It is presented as part of the way AI work should be planned, tested, and run.

Governance here covers several related questions. Who is accountable once a system is in production. What data may be used, and under what conditions. How bias and fairness are assessed, and for whom. How privacy is protected, and how decisions made by or with AI can be explained and audited. How risks are identified before launch, and monitored after it. Those questions apply to traditional machine learning and to generative AI, but generative AI raises them in a different form, because the outputs are less predictable and the failure modes are less well defined. A practitioner needs to know what to check, what to document, and what to escalate. A leader needs to know what decisions require their input, and what evidence they should expect before approving a system.

That work keeps a system running when things go wrong, and it lets a team answer a hard question in a review without guessing. The book puts it in the main flow, not in an appendix, and I agree with that placement. Governance that arrives after launch is not governance. It is damage control with a nicer name.

## Strengths, limitations, and what it will not teach

The main strength of the book is its level. It is the only 2025 title in this batch that covers the Principal Data Scientist and strategy layer, including return on investment, adoption metrics, causal inference, and governance, where the covered books on the site are mostly build, train, and deploy. That focus fills a gap. A practitioner who can build a model still needs a way to choose the right one to build, test whether it works in practice, and run it responsibly. The book is organised around those needs, following the sequence of decisions a senior practitioner actually faces.

A second strength is the combination of authors, and a third is the attention to measurement. Strategy and leadership, execution and MLOps, and responsible AI and governance are different kinds of expertise, and the book assigns them to different authors. That division reduces the risk of a single author treating every problem as a problem in their own area. The book does not treat measurement as a reporting task. It treats measurement as the basis for decisions about continuation, redesign, and closure. The sections on proof of concept, metrics beyond accuracy, experimentation, and causal inference together form a coherent approach to evidence.

The limitations follow from the same scope. The book is not a model building manual, and a reader who needs detailed guidance on training, tuning, or implementing a particular model will need to look elsewhere. The book is also a playbook, which means it is likely to be stronger on frameworks and process than on deep technical treatment of any single topic. Causal inference, for example, is a large field, and a playbook chapter can introduce the practical choices without replacing a specialised text. That is a fair trade, provided the reader understands what the book offers. A playbook supports running the process well. It does not replace depth on a single method.

## A practical study plan and exercise

A useful way to work through the book is to treat it as a sequence of decisions rather than chapters to read in order. The plan below follows the book, for a practitioner with an enterprise project in mind, or who wants to prepare for one.

First, define a business problem in one paragraph. State the decision that will change, the person who will make it, and the outcome that will show whether the change happened. Write the paragraph without mentioning a model, a dataset, or a tool. If the paragraph cannot be written without a model, the problem is not yet clear. Second, list three candidate projects, score each one on material value, specific AI contribution, feasibility in the current workflow, and ability to sustain the result, then choose one to test and record why the others were not chosen. Score with the rubric above, and write the reasons down. A short note is more reliable than memory.

Third, design a proof of concept for the chosen project. Define the baseline, the user or decision, the measures of success, and the decision point. List the measures beyond accuracy to track, including adoption, decision change, outcome, cost, and risk. Write the decision rule in advance: what result would lead to continuation, redesign, or closure. Fourth, design an experiment for one claim in the proof of concept. State the question, the treatment and comparison, the outcome, and the assumptions. If a randomised experiment is not possible, state what observational approach would be used, and what assumptions that approach would depend on. Identify the main threats, such as contamination between groups, a short test period, or a proxy outcome that misses the real one.

Fifth, sketch the operational plan if the proof of concept succeeds. List data pipelines, versioning, monitoring, retraining, access control, and failure handling. For a generative AI system, add prompt management, retrieval, evaluation, cost control, and latency. Sixth, complete a governance check. List the data, the conditions for its use, accountability, fairness and privacy checks, explanation and audit needs, and risks to monitor after launch. Run the loop again. A plan that only works once is not a plan. It is a demo with extra steps.

## Who should read it and how it compares

The book is most directly useful for senior practitioners, Principal Data Scientists, data science leads, and product and engineering leaders who are responsible for choosing, testing, and running AI work in an enterprise. It is also useful for practitioners moving from building models to owning outcomes, who need a structured way to make that transition. A reader comfortable with model building but less so with project selection, measurement, and governance will find the book directly relevant.

A reader who is new to machine learning, or who needs a hands on introduction to training and deploying a model, will need a different starting point. The book is not designed to teach those skills, and it should not be judged as if it were. A reader who needs depth on a single method, such as causal inference or LLMOps, will also need a specialised source alongside this book. The comparison helps to place it. [AI Engineering](../review-ai-engineering/) and [Designing Machine Learning Systems](../review-dmls/) are primarily about building and running systems. The Playbook is primarily about deciding which systems are worth building, how to test whether they work, and how to run them responsibly, so it is complementary rather than overlapping.

## Further reading and public sources

- [Packt catalog](https://www.packtpub.com/en-lu/product/the-ai-optimization-playbook-9781806115112)
- [O'Reilly catalog](https://www.oreilly.com/library/view/the-ai-optimization/9781806115112/)
- [AI Engineering](../review-ai-engineering/) and [Designing Machine Learning Systems](../review-dmls/)

## Verdict

The AI Optimization Playbook is a strategy first guide for leaders and senior practitioners, strongest on project selection and measurement, not a model building manual. It covers the decisions that determine whether enterprise AI work creates value: choosing the right project, gaining leadership support, designing a proof of concept, measuring adoption and outcomes beyond accuracy, testing effects with experimentation and causal inference, operationalising ML and generative AI systems, and governing those systems responsibly. That is its main contribution, because it addresses the strategy layer that the build, train, and deploy books on this site do not cover in the same way.

My rating is 4.0 out of 5. That is my own judgment of the book as I read it. It reflects the strength of the structure, the relevance of the strategy and measurement material to senior practice, and the combination of authors across strategy, execution, and governance. It also reflects the limits of a playbook form: strong on frameworks and process, lighter on deep technical treatment of any single topic, and not a substitute for a specialised text on causal inference or LLMOps. On the strength of the book itself, though, it earns the four.
