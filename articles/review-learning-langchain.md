---
title: Learning LangChain: Building Applications with LangChain and LangGraph
kind: review
date: 2026-11-16
order: 16
slug: review-learning-langchain
summary: I read Oshin and Campos on LangChain and LangGraph. My take: a clear start for beginners on chains, retrieval, and agents, let down by code that has already aged badly.
tags: LangChain, LangGraph, RAG
book: Learning LangChain: Building AI and LLM Applications with LangChain and LangGraph | Mayo Oshin and Nuno Campos | O'Reilly Media, 2025 | 9781098167288 | img/books/learning-langchain.jpg
verdict: A clear entry point to LangChain and LangGraph, strongest on chains, retrieval, and agents, not a deep systems theory book.
rating: 4.0
---

I read this book cover to cover, and my verdict on it splits in two. The ideas hold up. The code does not. Both of those things can be true at once, and the rest of this review is my attempt to be straight about which is which.

A prompt in a notebook is easy to write. I have written plenty, and each time it feels like the hard part is done. It is not. A small application that retrieves documents, remembers context, calls tools, and handles failure is a different kind of work, and that gap is where this book lives. LangChain handles composition, LangGraph handles stateful, agentic work, and the book is a practical walk through that shift. My question while reading was simple: does it give me a clear mental model that still helps when I swap a model, a vector store, or a framework version? Mostly, yes. The model in my head survived. The code samples did not, and I will get to that, because it is the book's biggest problem and I am not going to pretend otherwise.

The book is practical on purpose. Chains, memory, retrieval, agents, and managing agentic applications. If you want the mathematics of attention or a full treatment of pretraining, grab a different book. If you want to build a working retrieval application, add memory, and move toward an agent that can plan and use tools, you are the reader this is for. I was that reader.

## Chains and composition

A chain is a sequence of steps that turns an input into an output. One step formats a prompt. A second step calls a model. A third step parses the output into a structured form. When each step has a clear input and output, I can test one step at a time, swap one step without rewriting the application, and trace a failure to one place.

The book treats composition as a design skill, not a syntax lesson, and that is the right call. A good chain starts with a clear statement of the task, the expected input, and the expected output. If the output has to be JSON, the prompt and the parser should agree on the schema. If the output has to cite a source, the chain should carry that source through each step. If the chain calls a model more than once, the intermediate results should appear in logs or traces, so a wrong answer can be traced to the step that produced it.

Chains have a way of growing. One more step here, one more branch there, and soon nobody can explain what the system does, including the person who wrote it, who is me, three weeks later. Each added step can hide a decision, like which documents were retrieved, which prompt template was used, or how a tool result was formatted. The remedy is direct: keep chains short, and name each step by what it does. Add a step only when a test shows the current chain fails in a specific way. A chain that works in a demo can still fail in production with no plan for an empty retrieval result, a malformed output, or a tool error. That handling is required, not polish for later.

Then there is the choice between a fixed sequence and a more flexible flow. A fixed chain is predictable. Same steps, same order. Easy to test, easy to explain to a teammate. A flexible flow can branch on the input or on an intermediate result. It handles more kinds of tasks, and it is harder to reason about. The book puts LangGraph on the flexible side of that line. That split is useful. The simpler tool is the right starting point. The flexible one is justified only when the task needs branching, loops, or persistent state.

:::compare A fixed chain and an agentic graph
# A single chain
- One fixed sequence of steps
- Easier to test and trace
- Best when the task is stable
- Failure is local to one step
# An agentic graph
- Branches on state and results
- Can plan, retry, and recover
- Harder to reason about
- Needs limits and checks
:::

A fixed chain can still include retrieval, validation, and a fallback. The discipline is writing down the states, transitions, and stopping rule before adding a branch, or the graph can loop, repeat a tool call, or answer without checking its sources.

The table below gives the short version of that choice.

| Tool | Best for | Watch out |
| --- | --- | --- |
| LangChain | Fixed chains, retrieval, quick prototypes | Chains get messy when state grows |
| LangGraph | Branching, loops, agents that need state | More moving parts to test and trace |
| Direct model calls | Tiny jobs with one prompt | The plumbing has to be rebuilt by hand |

The smallest tool that passes the tests is the right tool. That rule has saved me more time than any framework feature.

## Memory

Memory sounds simple. The application remembers the conversation. In practice that sentence hides several different jobs. Short term memory holds the recent turns so a follow up question makes sense. Long term memory holds facts that should persist across sessions. Working memory holds the intermediate results of a task, like retrieved documents or tool outputs collected so far. Different storage, different lifetime, different risks. Treating them as one thing called memory is how teams end up with a system that remembers the wrong thing at the wrong time.

Memory gets a full chapter, and I am glad it does. A retrieval application without memory can answer one question well and still fail as a product. Users ask follow ups. They refer back to earlier answers. They expect the system to keep track of what is already settled. The simple approach is to pass recent history into the prompt. It works for short chats. It breaks as history grows, because context length, cost, and distraction all climb. The more deliberate approach is to summarise the history, store selected facts separately, and retrieve only the memory that is relevant to the current turn.

Memory also creates responsibility. Stored history can hold sensitive information, and a retrieval step that pulls the wrong memory can leak information from one user to another. Decide early what gets stored, for how long, who can see it, and how a user can correct or delete it. Memory should not be switched on by default with the hope that the details will work out.

A useful test is to run the same conversation with memory on and with memory off. If memory only adds length without improving the answer, it is cost without value. If it helps resolve a pronoun, recall a constraint, or avoid repeating a question, it is earning its keep.

:::loop The chain, memory, and retrieval cycle
Ask a question
Fetch passages
Answer with context
Keep the useful bits
Ask the next question
:::

The loop above is the rhythm of a retrieval application that remembers. Each turn feeds the next one. That is also why a small memory bug can compound fast. A bad summary in turn two becomes the context for turn three. Memory therefore deserves the same checking as the answer. The stored material, the retrieved material, and the effect on the answer all need inspection.

## Retrieval

Retrieval is the part that grounds a model in outside information. Find relevant passages, put them in the prompt, ask the model to answer from those passages. The idea is simple. The details decide whether the system is trustworthy. A retriever can return passages that are on topic but not enough to answer the question. It can return passages that are out of date, or from a source that would not be trusted for the task. The model can then produce a smooth answer that looks grounded and is not supported by the retrieved text at all.

This is the part of the book I liked most. The book gives retrieval two full chapters, indexing first, then querying, and it goes into RAPTOR, Multi-Query Retrieval, Reciprocal Rank Fusion, HyDE, and Query Routing. Those chapters are the clearest foundation in the book, and I would point a newcomer to them first. Retrieval is not one component. It is how documents are split, how they are embedded, how they are indexed, how a query is formed, how results are ranked, and how the retrieved passages are shown to the model. Each choice changes the result. Split a document into tiny pieces and context is lost. Split it into huge pieces and relevance is diluted. Copy the user question word for word as the query and passages that say the same thing in different words are missed. Add a reranking step and the result can improve, at a cost in latency.

I inspect the retrieved passages on their own, apart from the generated answer. If the passages do not contain the answer, the model cannot produce a grounded answer from them, and the failure belongs to retrieval, not generation. If the passages do contain the answer and the model still gives a wrong or unsupported answer, the failure belongs to generation, the prompt, or the way the passages were formatted. That split makes debugging faster.

Retrieval also needs a no answer path. When the passages do not support an answer, the system should say it does not have enough information, or ask a clarifying question, instead of guessing. That behaviour has to be designed and tested. A test set should include questions whose answers are absent, questions that need two passages combined, and questions worded differently from the source text.

:::layers The retrieval path as a system
Retrieve candidates | Find passages that may be relevant to the question
Rank and filter | Keep passages that are sufficient and trustworthy for the task
Present context | Format passages so the model can use them and cite them
Generate with evidence | Answer only from the presented passages where grounding is required
Check the result | Verify that the answer is supported before returning it
:::

Retrieval is not solved once a vector store is running. It is solved only when measurement shows the retrieved passages support the answers, and the system declines when they fall short.

## Agents with LangGraph

An agent, in the sense used here, is a system that decides what to do next based on what it has seen so far. It calls a tool, reads the result, calls another tool, or answers. That loop is more powerful than a fixed chain, and more fragile. It needs a clear goal, a clear set of allowed actions, a way to observe results, and a stopping rule. Without those, it can repeat the same action or keep running until time or budget runs out.

LangGraph fits this kind of work because it makes state and transitions explicit. A graph has nodes that do work and edges that decide where to go next. The state carries the information nodes need, like conversation history, retrieved passages, tool results, and the current plan. That explicitness helps a team review the design. Someone reviewing the design can ask what happens if a tool fails, what happens if the model produces an invalid action, and what happens if the loop hits its limit.

The practical tutorials on agents in the book help because they show the loop in action instead of describing it in the abstract. I could see how a planning step leads to a tool call, how the tool result changes the state, and how the next step uses that updated state. The LangGraph agent patterns and the production closing chapters are the strongest part of the back half of the book, in my judgment.

One run, stripped down to the parts that matter, looks like this.

:::seq A LangGraph run, step by step
actors: User, Graph, Retriever, Model
User->Graph: Ask a question
Graph->Retriever: Fetch passages
Retriever->Graph: Return passages
Graph->Model: Generate with context
Model->Graph: Return an answer
:::

The diagram is simple on purpose. The interesting part is what is not shown: the checks after each step, the limits on retries, and what to do when retrieval comes back empty. If the failure path cannot be drawn, the design is not finished yet.

An agent should not be made more autonomous than the task needs. If a fixed sequence can do the job, an agent adds cost, latency, and risk without adding value. The simplest structure that passes the tests is the right starting point, and the move to an agent is justified only when a specific failure shows a fixed structure cannot handle the case.

:::flow A simple agent loop
User request -> Plan next action -> Call tool or model -> Observe result -> Decide next step -> Answer or stop
:::

The flow above is simplified, and it is meant to be read as a starting point. A real system adds checks after each step, like validating a tool call, checking permissions, and recording what happened. It also adds limits on steps, time, and cost. Those limits are not a detail to add later. They are part of the design, because an agent without limits can fail in ways that are expensive and hard to undo.

## Managing agentic applications in production

Managing an agentic application means more than deploying it: watching how it behaves, understanding why it fails, and changing it safely. The book covers managing agentic applications, and that topic deserves care, because agents change the failure modes a team has to handle. A fixed chain fails in predictable places. An agent can fail by picking the wrong tool, misreading a tool result, looping, or producing an answer that is fluent but unsupported.

Observability comes first. A team needs traces that show the steps taken, the tools called, the inputs and outputs at each step, and the time and cost of each step. Without traces, debugging is guesswork.

Evaluation for agents has to go beyond a single answer check: does the agent reach the right outcome, use the right tools, respect its limits, and handle failure gracefully? A useful test set includes normal cases, edge cases, and cases where the correct behaviour is to stop, ask for clarification, or escalate to a human.

Deployment also needs controls on tools and permissions. An agent that can call a tool can change state, send a message, or access data. Each tool call should be authorised for that specific action, validated before it runs, and limited in scope. Retrieved documents should be treated as untrusted input where that fits, because a document can contain instructions the agent should not follow.

Change management is the last piece. A prompt, model, index, or tool change can shift behaviour, so keep a regression set, record what changed, and compare behaviour before and after.

:::tree Review an agent before it ships
Agent design review
  Goal and stopping rule
    Is the goal stated in testable terms
    Is the maximum step count defined
  Tools and permissions
    Is each tool call authorised and validated
    Are the limits on actions explicit
  Observation and recovery
    Does the agent check tool results
    Does it recover or stop on failure
  Evaluation and traces
    Are traces kept for review
    Does the test set include failure cases
:::

That tree is short and blunt, and it catches the failures that demonstrations hide.

## Strengths, limitations, and what it will not teach

The clear strength of the book is that it makes the parts and their connections easy to hold in mind. Work through the tutorials and I came away with a usable map: chains for fixed work, memory for context, retrieval for grounding, and graphs for work that needs branching and state. That map stays useful even if a different framework is used later, because the questions it raises about inputs, state, validation, and stopping rules apply to any implementation.

Now for the part I cannot skip, because it is the book's biggest flaw: the code is already outdated. The companion repository was archived in February 2026, and its last commit predates that by a year, so there is no maintained code to fall back on. Functions have been renamed, moved, or deprecated since it was written, and copying the samples as printed is a good way to spend an afternoon fixing imports.

The honest way to use this book now is to read it for the mental model and treat the code as pseudocode: learn what a chain is, how retrieval should be structured, how state flows through a graph, then check the current documentation for how to write it today. If you run the code as printed and it breaks, that is not you failing. That is the book ageing in public.

There are two smaller complaints of my own. The book starts strong and gets weaker and more rushed in the later chapters. And the dual-language Python and JavaScript examples feel redundant. I read the Python, skimmed the JavaScript, and wished the space had gone to a single language done properly. There is also no follow-along project tying the chapters together, so the reader builds a series of separate exercises rather than one application that grows.

The book is also not a systems theory book, so distributed systems, model training, and the mathematics behind retrieval will need companion resources. Another limitation follows from the focus on one stack. A team that adopts LangChain gains composition and tooling, and also gains a dependency. The trade is worth it when the team needs the abstractions and integrations. It can be a cost when the task is simple enough for direct model calls and a little application code. I read this book as a guide to one way of building, not as a claim that every LLM application should use the same stack.

The book is also not a security or governance guide. Tool use, memory, and retrieval all raise questions about permissions, data handling, and audit trails, and those questions need separate attention. A working tutorial is not evidence that a system is ready for production use with sensitive data.

## A practical study plan and exercise

The fastest way I learned from this book was to build one small application and grow it in stages, instead of reading the whole book before writing any code. Start with a fixed set of public documents on a narrow topic, and build a chain that answers questions from those documents. Write twenty questions before building the retrieval step, including questions whose answers are absent, questions that need two passages combined, and questions worded differently from the source text. Record what counts as grounded, incomplete, or unsupported, so the test set shows whether later changes help or hurt.

!!! tip Start with one chain and one test set.
    Add the graph only when the chain cannot hold the state.

In the second stage, add memory for a short conversation. Keep it simple at first, like the recent turns, and test whether it helps the system answer follow ups without adding confusion. Try a summary of the history and compare the results. Record which approach helps and which adds length without improving the answer.

In the third stage, move a task that needs branching into LangGraph. Pick a task where a fixed chain fails in a specific way, like retrying retrieval with a reformulated query, or calling a tool and then deciding what to do next. Write down the states, the transitions, and the stopping rule before implementing the graph. Add limits on steps and on tool calls. Test the graph on normal cases and on failure cases, including a tool that returns an error and a retrieval result that does not support an answer.

A second exercise is to compare a fixed chain and a graph on the same task, with the same test set, documents, and rubric, and record the difference in quality, latency, and complexity.

## Who should read it and how it compares

Software engineers, ML practitioners, and technical builders moving from prompts to applications are the likely audience. Readers who already build LLM applications with direct model calls can use this book to organise code that has grown without a clear structure. Readers who want a first working system with retrieval and agents get a direct path to a prototype from the tutorials. Readers who want a deep treatment of model internals, distributed training, or formal evaluation theory will need additional resources.

Publisher listings put Learning LangChain at about 300 pages, and Packt lists Generative AI with LangChain at 484 pages. This book is the shorter entry point. The Packt book is the longer production treatment. The chart below is a quick sense of that difference, not a quality score. Longer is not better, only longer.

:::bars Publisher page counts
Learning LangChain | 300 | about 300 pages
Generative AI with LangChain | 484 | 484 pages
:::

Compared with *AI Engineering*, this book is narrower and more hands-on with a specific stack. Huyen's book, reviewed in [AI Engineering](../review-ai-engineering/), addresses application decisions across evaluation, prompting, retrieval, adaptation, and inference, without tying the reader to one framework. This book addresses how to implement those ideas with LangChain and LangGraph.

Compared with *AI Agents in Action*, reviewed in [AI Agents in Action](../review-ai-agents-in-action/), this book is more focused on the LangChain and LangGraph stack and the move from chains to graphs. Lanham's book is a broader practical tour of agent building concepts and tools, including behaviour trees and several frameworks. This book goes deeper on one stack, which makes it more useful for a team that has chosen that stack, and less useful for a team that wants a survey of several approaches before choosing.

A reader who wants one O'Reilly introduction should start here, then move to a longer book on the same tools, or to a book on evaluation and operations that is not tied to one framework.

## Further reading and public sources

- Google Books edition page for Learning LangChain: [books.google.com/books?id=_3VGEQAAQBAJ](https://books.google.com/books?id=_3VGEQAAQBAJ)
- O'Reilly Media catalog entry for Learning LangChain, ISBN 9781098167288.
- Related reviews on this site: [AI Engineering](../review-ai-engineering/) and [AI Agents in Action](../review-ai-agents-in-action/).

## Verdict

My rating is 4.0 out of 5, and it is my own judgment after reading the book. The book offers a clear and practical entry point to LangChain and LangGraph, with useful coverage of chains, memory, retrieval, agents, and the management of agentic applications. Its value is greatest for builders who want a working system with a specific stack and who are prepared to check current framework versions instead of trusting the printed code. The concepts, the retrieval chapters, and the LangGraph patterns are the reason to read it. The outdated code is the reason to read it with the documentation open beside it. Pair it with a broader engineering book for a framework neutral treatment of evaluation, and seek security and governance guidance separately before putting an agent into production.
