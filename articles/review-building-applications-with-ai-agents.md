---
title: Building Applications with AI Agents: Single and Multi-Agent Design
kind: review
date: 2026-11-16
order: 19
slug: review-building-applications-with-ai-agents
summary: I read Michael Albada's research-based guide to single- and multi-agent systems: design patterns, tool use, orchestration, and what happens after the demo works.
tags: agents, multi-agent, orchestration
book: Building Applications with AI Agents: Designing and Implementing Multiagent Systems | Michael Albada | O'Reilly Media, 2025 | 9781098176501 | img/books/building-applications-with-ai-agents.jpg
verdict: A research-based guide to multi-agent design, strongest on patterns and coordination, not a framework quick start.
rating: 4.0
---

I read this book because I was tired of agent demos. A demo is a loop that works once, on a friendly prompt, in front of a friendly audience. Then the system has to run on a Tuesday, for a stranger, with a tool down, and that is where my agent projects kept falling over. Albada's book is aimed squarely at that gap, the part after the demo works, and that is why I picked it up.

The facts first. Building Applications with AI Agents is a first edition from O'Reilly Media, first released in September 2025, 352 pages, ISBN 9781098176501. The author, Michael Albada, is an ML engineer with experience at Uber, ServiceNow, and Microsoft. He writes like someone who has shipped systems rather than only sketched them, which is a compliment, and also, as I will get to, part of the problem.

My honest verdict on it is mixed. I love the emphasis on what happens after the demo. I am less fond of the prose, which is wordy in a way that adds sentences without adding decisions. The ideas underneath are real, and the structure is genuinely useful, but the book makes me work harder than it should to get to them.

## The problem the book addresses

An agent is easy to describe and hard to build well. In plain terms, it is a system that takes a goal, plans a sequence of steps, uses tools or information sources, observes the result, and adjusts. A single prompt can look like an agent in a demonstration, but a working application needs more. It needs a defined task, a way to choose the next action, a way to recover from a failed tool call, a way to keep relevant state, and a way to stop. Without those controls, a system can loop, repeat a failing action, call a tool it should not call, or produce a confident answer from incomplete evidence. I have watched agents do all four of those things, and the confident answer is the worst of the lot, because nobody checks the answer that sounds sure of itself.

Albada starts from that gap, with a practical and research-based approach to designing and implementing single-agent and multi-agent systems, covering agent design patterns, tool use, orchestration strategies, and multi-agent coordination. That framing matters to me. This is a design guide, not a tour of one framework or a pile of prompt examples. If what you need is a design vocabulary and a set of decisions to make before writing code, the scope is right. If what you need is a short tutorial for one library, you will need something else next to it.

The distinction between a single agent and a multi-agent system is central to the book. A single agent can be the right choice when one loop can hold the task, the tools, and the relevant context without becoming unwieldy. A multi-agent system becomes relevant when the work splits naturally into roles, when different parts of the task need different tools or different context, or when separate checks improve reliability. The risk is that a second agent adds coordination cost, more places for state to diverge, and more failure modes. A design book should help me make that trade off with reasons, not with enthusiasm for complexity. On that test, this book mostly delivers.

## Single-agent design

A single agent is a loop with memory, tools, and a stopping rule. The loop receives a task, selects an action, observes the result, and decides whether to continue, retry, or finish. That description is simple. The engineering work is in the details that keep the loop useful. The task needs to be stated in a way the system can test. The available tools need clear descriptions, inputs, and limits. The state needs to hold what matters for the next step without carrying every prior detail forward. The stopping rule needs to prevent endless retries while still allowing a useful second attempt after a correctable error. I think of the stopping rule as the difference between an agent and a very expensive while loop.

Context is the other constraint in a single-agent design. A long task can generate a long history, and a long history can crowd out the instructions and the evidence that matter now. A practical design therefore needs a rule for what to keep, what to summarise, and what to discard. It also needs a rule for grounding: if the agent must answer from a document, a database, or a tool result, the design should make that source visible in the trace, so a later check can distinguish a grounded answer from a plausible completion. The trace is where I think his advice is most useful in practice.

:::compare Single-agent and multi-agent designs
# Single agent
- One loop owns the task
- Simpler to trace and test
- Context can grow large on long tasks
# Multi-agent
- Roles split the work
- Each agent can hold narrower context
- Needs coordination and shared state
:::

## Agent design patterns

A pattern is a named solution to a recurring design problem, with stated conditions, trade offs, and failure modes. The value of a pattern is not that it is novel. It is that it gives a team a shared name for a choice, so a design review can move faster. Instead of describing a whole mechanism from scratch, I can say that a system uses a planner and an executor, or a router that sends a request to a specialist, and the team can then discuss the risks of that choice. This book works in that tradition, and I found that part of it the most immediately usable.

Patterns for agents tend to cluster around a small set of decisions: how work is divided, how the system chooses between a direct answer, a tool call, and a request for more information, how it checks its own work, how it keeps memory across steps, and how it handles uncertainty. Each of those decisions can be made well or badly, and each has a cost: a check can improve reliability and add latency, and splitting work can improve focus and add coordination overhead.

The test I apply to a patterns book is whether it states the conditions for each pattern. A routing pattern helps when requests fall into distinct kinds with different tools or expertise, and helps less when the distinction is unclear or routing errors become a new source of failure. A planning pattern helps when a task has steps that depend on each other, and helps less when the plan is simple and a direct sequence would do. A reflection pattern helps when the system can check its own output against a clear criterion, and helps less when the check uses the same flawed reasoning as the first attempt. Albada does give conditions for his patterns, more often than not, and that is what kept me reading. Where he does not, the pattern reads more like a label than a decision, and I had to supply the missing condition myself.

:::layers A design review for one agent
Define the task | State the goal, the allowed tools, and the stopping rule
Choose the pattern | Name the division of work and the reason for it
Check the trace | Record plan, action, observation, and next decision
Test failure | Include tool errors, missing evidence, and unclear requests
Set limits | Define retries, time, cost, and escalation before use
:::

## Tool use

Tool use is where an agent stops being a text generator and starts being a system. A tool can retrieve a document, query a database, call an API, run a calculation, or trigger an action in another system. Each of those abilities creates value and creates risk. A tool can return stale data, malformed data, or data that should not be trusted as an instruction. A tool call can have side effects that cannot be undone. A tool can fail in a way that looks like success. The design therefore needs to treat tool use as a controlled interface, not as a free-form capability.

Three questions recur in tool design: selection, validation, and recovery. Selection is how the agent chooses the right tool for the current step and avoids calling a plausible but wrong one. Clear tool descriptions, constrained inputs, and a small set of tools for a given task help here. Validation is how the system checks the arguments before a call and the result after one, covering format, range, permissions, and consistency with the task. Recovery is how the system responds when a tool returns an error, a timeout, or an unexpected value. A retry can be correct when the failure is transient. It can be harmful when the failure is a permission error or a malformed request that will fail again.

Tool results also need to be handled as data, not as instructions. A retrieved document can contain text that looks like an instruction to the agent, and a tool output can contain a request to take an action the user did not ask for. A design that passes tool output directly into the next planning step without a boundary is vulnerable to that confusion. A safer design keeps a distinction between the source of the data and the authority to act, and it logs the tool call, the arguments, and the result, so a later review can reconstruct what happened.

:::tree Diagnose a tool failure before retrying
A tool call fails or returns an unexpected result
  Is the failure a permission or validation error?
    Stop and report the limit, do not retry the same call
  Is the failure transient, such as a timeout?
    Retry once with a clear limit, then escalate
  Is the result inconsistent with the task?
    Check the arguments and the source before acting
:::

## Orchestration strategies

Orchestration is the control logic that decides what happens next. In a single agent, orchestration is the loop itself. In a multi-agent system, it is the coordination between agents, including who acts, in what order, and with what information. The choice shapes reliability, cost, latency, and debuggability. A sequential design is easy to follow but slow when steps are independent. A parallel design can be faster but needs a rule for combining results that disagree. A hierarchical design can keep a complex task organised but can hide failures in a lower layer. A decentralised design can be flexible but hard to trace.

A useful orchestration design states the handoff: when one agent passes work to another, what exactly is passed, the original task, a summary, a set of intermediate results, or a set of constraints for the next step. A vague handoff creates a common failure: the receiving agent repeats work, misreads the goal, or acts on an incomplete summary. A clear handoff includes the task, the relevant evidence, the limits, and the expected output format, plus a way to return an error when the handoff is incomplete.

The sequence diagram below shows that handoff in motion. The supervisor holds the goal, the worker holds one task at a time, and the worker reports back to the supervisor rather than finishing without a record.

:::seq A multi-agent handoff, step by step
actors: User, Supervisor, Worker, Tool
User->Supervisor: Give the goal
Supervisor->Worker: Hand off one task
Worker->Tool: Call with checked inputs
Tool->Worker: Return a result
Worker->Supervisor: Report back
:::

!!! tip Test the handoff, not just the final answer.
    A good answer can hide a broken handoff.

The choice of orchestration style is a trade off between traceability, speed, and coordination cost. The table below summarises the main options.

| Orchestration choice | Best for | Watch out |
| Sequential handoff | Tasks with clear steps in order | Early errors can affect later stages |
| Parallel work with a merge step | Independent steps that can run together | Merging results that disagree needs a rule |
| Supervisor with workers | Work that splits into roles | The supervisor can become a bottleneck |
| Peer agents | Flexible work with shared decisions | Hard to trace when messages diverge |

:::flow A simplified orchestration path
User request -> Planning -> Tool use -> Observation -> Review -> Response
:::

## Multi-agent coordination

Multi-agent coordination is the hardest part of the topic, because it combines the problems of single-agent design with the problems of distributed work. Agents need shared state, or at least a consistent view of the task, a way to avoid duplicate work, a way to handle a failure in one agent without losing the work of the others, and a way to communicate without flooding the context of every agent with every detail. Those are system design problems, and they do not disappear when the agents are described in simple terms.

One common coordination model is a supervisor that assigns work and collects results. Another is a pipeline in which each agent handles one stage. Another is a peer model in which agents exchange messages and negotiate the next step. Each model has a different failure profile: a supervisor can become a bottleneck or a single point of failure, a pipeline can propagate an early error through every later stage, and a peer model can be hard to debug when messages diverge. I want guidance on when each model fits, what state it needs, and how it fails. That guidance is more useful than a list of model names.

:::compare Orchestration choices
# Sequential handoff
- Easy to trace step by step
- Early errors can affect later stages
# Parallel work with a merge step
- Faster when steps are independent
- Needs a rule for combining results
:::

The choice between a single agent and a multi-agent system therefore turns on the task. A simple task with low coordination needs can usually stay with a single agent, and a complex task with distinct roles and coordination needs is where a multi-agent design can earn its place. In between, the choice is best settled by a small test on the actual task rather than by a general preference for either form.

:::quadrant Single or multi-agent choice, author's placement, opinion not measurement
x: Simple task | Complex task
y: Low coordination | High coordination
pt: Single agent @ 0.3,0.3
pt: Multi-agent @ 0.8,0.8
:::

The plot above is the author's placement, opinion not measurement. It is a judgment, not data, and it is best used to frame the question before testing the choice on the task in hand.

Evaluation is harder in a multi-agent system than in a single-agent system, because a good final answer can hide a poor intermediate step, and a poor final answer can have many causes. A useful evaluation therefore checks the parts as well as the whole, testing routing, tool selection, handoffs, and final output separately, using cases that isolate each decision. It can also test coordination directly, with cases where agents must share state, resolve a disagreement, or recover from a failed step. Those tests are more work to build, but they give a clearer picture than a single end to end score.

## Strengths, limitations, and what it will not teach

The strength I keep coming back to is the weight this book gives to what happens after the demo works. Nearly half the chapters cover validation, monitoring, security, and governance, the unglamorous work that decides whether a system survives contact with real users. Most agent books stop at the working prototype. This one treats the prototype as the starting line.

I also liked the way Albada builds the same scenarios in several frameworks, LangGraph, LangChain, and AutoGen, and runs them through one evaluation harness. That makes the comparison honest in a way that a separate demo per framework never is. And Chapter 3, on agent experience design and the Autonomy Slider, is the chapter I would hand to someone first. It also gives the book its sharpest test: a system only truly qualifies as an agent when it can make context-driven decisions, rather than executing a hard-coded script. That is a stricter test than most agent marketing survives, and I suspect that is the point.

Now the criticism, because it would be dishonest to bury it. The prose is the weakest part of the book. It is verbose and polished in a way that keeps adding sentences without adding decisions, and the information density is low in places: long passages that say in a page what a paragraph could have carried. I found myself skimming sections that repeated a point I had already understood. I am not going to guess at how the book was written from the text alone, and I will not pretend that I know. What I can say from reading it is that the writing gets in its own way. The ideas underneath are real, and the structure is genuinely useful. A padded sentence is annoying. A missing design decision is worse, and this book rarely leaves one missing.

The other problems are more concrete. The book is too shallow in places, listing concepts without explaining why they matter, and I felt that in chapters where a pattern is introduced and left standing without a worked reason to choose it. The companion code has gone stale: the repo pins langchain 0.1.20 and langgraph 0.0.28 and was last updated in October 2025, so anyone following the examples should expect to adapt them rather than run them as written. There are editing errors and duplicated paragraphs. And the book has too few visual diagrams for a design book. A design book that asks me to hold orchestration patterns in my head ought to draw more of them.

For scale, the bar chart below places this book next to two close neighbours on the same shelf. The numbers are publisher-listed page counts, nothing more. Longer does not mean better. Page count only shows how much room each book gives its topic.

:::bars Publisher page counts
Building Applications with AI Agents | 352 | 352 pages
Agentic Design Patterns | 427 | 427 pages
Building Agentic AI Systems | 288 | 288 pages
:::

The central limitation is temporal, and it applies to most books on agents. Frameworks, tool interfaces, and model capabilities change quickly, so a specific example can become dated even when the design idea remains sound. I would treat named tools and APIs as snapshots and check current documentation before adopting them. That matters more here than in most books, given how stale the companion repo already is.

The book should also not be mistaken for a framework manual, a prompt cookbook, or a course in model training. Its scope is design and implementation of agent applications, not model internals or the full lifecycle of conventional machine learning. For model internals and hands-on construction, Sebastian Raschka's Build a Large Language Model (From Scratch) has a different focus. For the broader production lifecycle of conventional ML, Chip Huyen's Designing Machine Learning Systems is complementary. For application engineering around foundation models, Huyen's AI Engineering is also relevant. Those comparisons describe scope, not a ranking.

## A practical study plan and exercise

My advice is to read with one concrete application in mind, rather than reading for general familiarity. Choose a task small enough to build but complex enough to need more than one step: a document triage task, a support request router, or a research summary task. Write the task, the allowed tools, the expected output, and the failure cases before reading the design sections. As the book moves through patterns, tool use, orchestration, and coordination, record which choices apply to that task and which risks remain.

For an exercise, build a single-agent version first. Give it a clear task, two or three tools, a stopping rule, and a trace that records the plan, the action, and the observation at each step. Test it with a fixed set of cases, including one where the answer is absent, one where a tool returns an error, and one where the request is ambiguous. Record where it succeeds, where it fails, and why. The point is a baseline that a later design can be compared against, not a polished demo.

!!! tip Build the single-agent version first.
    It gives the reader a baseline to beat, or to keep.

A second exercise can add a second agent only after the single-agent baseline is understood. Split the work by role, for example a researcher that gathers evidence and a writer that produces the answer from that evidence. Define the handoff precisely, including what evidence is passed, what format is expected, and what happens when the evidence is incomplete. Run the same fixed cases again and compare the results with the single-agent version, recording the added cost in steps and time and whether the added agent improved the result, made it worse, or made no clear difference. That comparison teaches the central lesson of the book: added structure should earn its place.

:::tree Choose the design from the task, not from the trend
The task needs more than one step
  Can one agent hold the task and the tools?
    Keep a single agent and test the trace
  Does the work split into distinct roles or tools?
    Add a second agent with a defined handoff
  Is coordination the main risk?
    Test handoffs and shared state before adding more agents
:::

## Who should read it and how it compares

If you are a software engineer, an ML practitioner, or a technical lead designing agent applications, this book is aimed at you. It is most useful if you already understand how to work with a language model and now need to decide how to structure a system around it. If you want a quick start with one framework, the scope is broader than you need, and if you want model training or conventional ML operations, you will need a companion book.

Compared with [AI Agents in Action](../review-ai-agents-in-action/), I found this book more research-based and design-focused. AI Agents in Action is a practical tour of agent-building concepts and tools, with runnable examples and a broad on-ramp. This book is a guide to designing and implementing single-agent and multi-agent systems, with emphasis on patterns, orchestration, and coordination. The two can be complementary: one as an entry point to building, the other as a design reference for the harder structural decisions. That is my judgment from reading both, not a ranking.

Compared with [Agentic Design Patterns](../review-agentic-design-patterns/), the difference is one of form. A patterns book gives a vocabulary of reusable solutions, one pattern at a time. This book gives a design path through single-agent and multi-agent systems, with patterns as one part of that path. A reader who wants a reference to consult during design reviews may prefer the patterns book. A reader who wants a connected account of how patterns, tools, and orchestration fit together may prefer this book. Both approaches are useful, and a team can use them together.

## Further reading and public sources

- O'Reilly Media catalog entry for *Building Applications with AI Agents: Designing and Implementing Multiagent Systems*, ISBN 9781098176501. Check the catalog for current edition and availability.
- [AI Agents in Action](../review-ai-agents-in-action/), a practical tour of agent-building concepts and tools on this site, for a broader entry point to building agents.
- [Agentic Design Patterns](../review-agentic-design-patterns/), a pattern-by-pattern reference on this site, for a reusable vocabulary to use in design reviews.

## Verdict

I give this book 4 out of 5, my own judgment after reading it. The design reasoning is the reason to buy it: single-agent discipline first, multi-agent coordination second, patterns, tool use, and orchestration treated as decisions with costs rather than features to collect. The prose is the reason to hesitate: it is wordy in places, the code examples are already stale, and the editing should have been tighter. The book is padded, and I will not pretend otherwise. But the padding does not make it useless. For a reader who wants a research-based guide to the structure of agent systems and is willing to test the ideas on a small task before adopting them, this book earns its place on the shelf next to the framework and patterns books reviewed on this site. Just do not expect a quick read. It is not. It is a slow read about moving fast, which is either irony or a warning, and I am still deciding which.
