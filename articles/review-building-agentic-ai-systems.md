---
title: Building Agentic AI Systems: Reasoning, Planning, and Orchestration
kind: review
date: 2026-11-16
order: 14
slug: review-building-agentic-ai-systems
summary: I read Biswas and Talukdar's compact guide to agentic systems end to end: reasoning, planning, orchestration, multi-agent design, and governance for enterprise readers.
tags: agents, multi-agent, enterprise AI
book: Building Agentic AI Systems: Create intelligent, autonomous AI agents that can reason, plan, and adapt | Anjanava Biswas and Wrick Talukdar | Packt Publishing, 2025 | 9781803238753 | img/books/building-agentic-ai-systems.jpg
verdict: A compact enterprise guide to agentic systems, strongest on orchestration and governance, not a deep framework manual.
rating: 4.0
---

I read this book end to end, all 288 pages, and the first thing that struck me is how unglamorous it is about a glamorous subject. No breathless demos, no promise that agents will eat the world by Tuesday. Instead it asks the dull questions: who owns this decision, what happens when the tool fails, and who gets paged when the loop will not stop. I liked that. A lot of agent writing reads like a fireworks show. This one reads like a building code.

For the record: Building Agentic AI Systems, by Anjanava Biswas and Wrick Talukdar, Packt Publishing, 21 April 2025, 288 pages, ISBN-13 9781803238753, with forewords by Matthew R. Scott and Dr. Alex Acero. It was named the Goody Business Book Awards 2025 Technology Winner. The title says the job plainly: create intelligent, autonomous AI agents that can reason, plan, and adapt. Most 2025 agent books explain how to call a language model, add a tool, and run a loop. Fewer ask what changes when that loop has to live inside a real organisation, with more than one agent and real limits on cost, latency, and error. This one belongs to the second group. It is not a long manual for one framework. It is a compact guide to designing a system, choosing agent roles, and putting governance around the result.

## What makes a system agentic rather than a single prompt

A single prompt can produce a good answer. A prompt with a tool call can produce a better one. Neither is an agentic system on its own. The book's central claim, and the one I kept coming back to, is that agency is a property of a system, not of one model call. A system is agentic when it can take a goal, make a plan, act through tools or other agents, examine the result, change the plan, and continue until the goal is met or a stopping rule applies. Without observation and revision, the result is a pipeline. Without a stopping rule, the result is a loop that can consume budget or repeat itself until someone pulls the plug.

That changes the unit of design. It is not the prompt. It is the loop, the state it carries, the tools it can reach, the memory it can consult, and the limits on each of those. A prompt engineer can improve one step. A systems designer must decide how the steps fit, how a failure in one step is spotted, and what happens next. The book takes the second view, and that framing makes the usual failures easy to see: a fuzzy goal, no stated success criterion, or a tool that returns data the agent cannot use.

:::compare A prompt and an agentic system side by side
# A single prompt
- One input produces one output
- No memory of earlier steps beyond the context given
- Failure is visible only in the final answer
# An agentic system
- A goal drives a loop of planning, action, and observation
- State, tools, and memory carry across steps
- Failure can be detected, logged, and handled during the run
:::

The loop is simple to state and easy to get wrong: reason, plan, act, examine what came back, then repeat with better information, or stop. Most agent failures occur in the gaps between those steps. The plan was sound but the tool result was misread. The tool worked but the plan never updated. The observation was clear but was never recorded, so the next step repeated the same mistake. A tight and visible loop makes debugging considerably easier. A stopping rule, I learned, is the agent equivalent of knowing when to leave a party. Without one, the loop just keeps going. It is never charming the second time.

:::loop The reason, plan, act, observe cycle
Reason
Plan
Act
Observe
:::

## Reasoning and planning

Reasoning and planning are the two words in the subtitle, and the book treats them as a pair. Reasoning means working through a task in a way that another person can inspect. Planning means turning that reasoning into steps, with dependencies, and then changing the steps when new information appears. I found the split genuinely useful, because the two fail in different ways. A system can sound perfectly reasonable and still produce a plan that cannot run, because a step needs data that does not exist, a tool that is not allowed, or an approval that never came. It can also produce a solid plan and still fail, because the thinking behind one step was wrong and no check caught it.

The book treats reasoning and planning as design problems, not prompt tricks. It covers how to structure a task, split it into steps that can be checked, and decide when to replan. A plan is a guess about what will work, and in a live environment that guess will often be partly wrong. The useful question is whether the system can spot the mismatch, update the plan, and keep the cost of fixing it low. That needs observation after each step, a clear record of what was tried, and a rule for when to stop and ask a person for help. Goal, constraints, available tools, expected outputs, and stopping conditions are the minimum set. If any of those is missing, the plan is incomplete, even when the model output reads well. Frameworks moved fast during 2025, so I would check current tool versions before treating any planning pattern as current.

My test for a plan is simple. If the goal, the completion condition, and the stopping rule cannot be written down in plain sentences, the design has a hope and a loop rather than a plan.

## Orchestration and agent roles

Orchestration is where this book is strongest, in my judgment: deciding how work moves between agents, tools, and people, in what order, and under what conditions. It is the part of agentic design that is easiest to leave vague and hardest to fix later. A single agent is usually easy to follow: its prompt and its tool list describe its behaviour. Several agents present a different problem. The design must state who owns each decision, what each agent can do, what it must pass on, and what happens when two agents disagree or when one hands the next output it cannot use.

Roles are the book's answer. A role is a defined job with defined inputs, outputs, and limits. One agent gathers information. Another checks it. Another drafts a response. Another decides whether the draft is ready to send. Naming roles makes failure local. If the checking agent is missing, or its checks are vague, errors pass straight through. If the drafting agent is also the checking agent, the check adds almost nothing. If nobody owns the final decision, the system can ship work that nobody is accountable for. In a demo, the developer is the orchestrator, the checker, and the user all at once. In an enterprise system, those jobs split apart, and the split has to be designed on purpose. A framework can give a loop, a tool registry, and a way to pass messages. It cannot decide who should own a decision. That belongs to the designer.

The Coordinator-Worker-Delegator framing is the clearest version of this I have read in a short book: one coordinator decides, workers do one job each, and delegation is explicit rather than left to chance.

| Agent role | Job | Watch out |
| --- | --- | --- |
| Planner | Turn the goal into steps with dependencies | A plan with no check after each step |
| Researcher | Gather evidence from tools and sources | Passing along stale or unchecked material |
| Checker | Test the draft against the goal and the evidence | Checking its own work with no independent rule |
| Responder | Produce the final answer once checks pass | Sending a confident answer from incomplete work |

!!! tip Give each agent one job and one stopping rule.
    A vague agent will loop before it asks for help.

One job per agent, one clear handoff, one way to say stop. When a role does two jobs, the trace becomes muddy. When a handoff is vague, the next agent guesses. When there is no stopping rule, the loop decides instead, and it keeps going.

:::layers A practical orchestration checklist
Define the goal | State the outcome, the constraints, and the stopping rule before any agent runs
Assign roles | Give each agent one responsibility, with defined inputs and outputs
Set the handoffs | State what passes between agents and how errors are reported
Limit the loop | Set iteration, time, and cost limits, and a path to human review
Log the run | Record plans, tool calls, observations, and decisions for later review
:::

A handoff is where multi-agent systems usually break. The supervisor does not do the work itself. It picks one task, hands it to a worker, and waits for a report. The worker calls the tool with checked inputs, reads the result, and reports back. The discipline is in the boundaries: one task at a time, checked inputs, and a result that returns to the supervisor instead of leaking straight into the next step.

:::seq A supervisor handoff, step by step
actors: User, Supervisor, Worker, Tool
User->Supervisor: Give the goal
Supervisor->Worker: Hand off one task
Worker->Tool: Call with checked inputs
Tool->Worker: Return a result
Worker->Supervisor: Report back
:::

The sequence is deliberately plain. Plain handoffs are debuggable handoffs. The alternative, every agent talking to every other agent with no owner of the state, is considerably harder to debug.

## Multi-agent design

Multi-agent design follows from orchestration, but it brings its own questions. The first is whether a second agent is needed at all. A second agent adds coordination cost, more places to fail, and more state to manage. It earns its keep when the task genuinely benefits from splitting apart, for example when one part needs different tools, different data, or a different level of scrutiny from another part. It does not earn its keep when one agent with a clear plan and a good check could do the job. The book treats the number of agents as a design choice, not a score. More agents is not more impressive. It is more to coordinate.

With several agents in place, the questions become concrete quickly. How do agents talk to each other, and where is the shared record of the task? Who decides the order of work, and can that order change mid-run? How is disagreement handled, and who has the final say? How is duplicated work stopped, along with conflicting tool calls, or two agents passing the same task back and forth without end? A larger system needs explicit protocols, shared state, and limits on who can call whom. Without those, it is hard to test, hard to debug, and hard to explain to a user or an auditor. The book is compact at 288 pages, so it cannot cover every framework in depth. Its contribution is the design questions and a structure for answering them, so the framework choice follows the design instead of driving it.

:::flow A simplified multi-agent request path
User request -> Planner -> Researcher -> Checker -> Responder -> User
:::

## Governance and operational limits

Governance is the part most likely to decide whether this book is useful in an enterprise setting. Governance means the rules, records, and controls that let an organisation run an agentic system with confidence: access control for tools and data, logging of plans and actions, limits on cost and iteration, human review for decisions that matter, and a clear account of what the system did and why. Without those, a system can work well in a demo and still be unfit for deployment, because nobody can explain its behaviour, reproduce a result, or show it stayed inside its permissions.

Limits are part of governance, not an extra. An agent loop needs a budget, in iterations, time, and cost. It needs a stopping rule that is enforced, not just suggested in a prompt. It needs a way to fail safely, by returning a partial result with a clear note about what did not get done, rather than a confident answer built on incomplete work. It needs tool permissions that follow least privilege, so an agent cannot reach data or actions outside its role. What I valued here is that the book pulls these standard software practices together and applies them to agentic systems as one story, instead of scattering them across chapters. Monitoring after deployment matters for the same reason. A system can drift as models, tools, or data change, and logs, evaluation cases, and regular review of failures are how drift is noticed before users are affected. Many agent guides stop at the first successful run. A team that has to keep a system running needs the second half of the story as well. The trust, safety, and ethics chapters are part of that second half. Those chapters are where the book stops sounding like a tutorial and starts sounding like someone who has had to answer for a system in production.

:::tree Diagnose the failure before choosing the fix
An agent run fails or produces a poor result
  Is the goal unclear?
    Restate the goal, the success criterion, and the stopping rule
  Is a tool failing?
    Check permissions, inputs, and the format of the tool output
  Is the plan wrong?
    Review the steps, the dependencies, and the observations after each step
  Is governance missing?
    Check logs, limits, and the review path for consequential decisions
:::

## Strengths, limitations, and what it will not teach

The strengths follow from the scope and the length. The book is compact, at 288 pages, and it uses that space to cover design, orchestration, multi-agent structure, and governance in one place. That breadth is useful for a practitioner who wants to see the whole system before picking a framework or a pattern. The enterprise architecture angle is a real strength, because it deals with the questions that appear after the demo works, when the system has to live with other systems, other people, and other constraints. The focus on roles, coordination, and limits gives the reader a way to think about failure, which capability-first guides often skip. The Goody Business Book Awards 2025 Technology Winner recognition is a useful signal, though an award is no substitute for reading the book against your own needs.

Two strengths I want to call out. The first is the running travel-agent example. Every abstract idea gets a concrete booking, a failed reservation, a handoff, and suddenly the pattern is obvious. I wish more technical books trusted one good example this much instead of inventing a fresh toy problem per chapter. The second is the graphics and the explanations. They are readable by non-technical readers, which matters for a book aimed at enterprise teams. The diagrams do more explaining than some of the text does, which is either a compliment to the diagrams or a quiet criticism of the text.

Page counts come from the publishers: Packt lists this book at 288 pages, O'Reilly lists Building Applications with AI Agents at 352 pages, and Springer lists Agentic Design Patterns at 427 pages. Shorter is not automatically better, but it does indicate what kind of book the reader is picking up. This one is a design narrative that can be read end to end, not a reference to consult for one pattern at a time.

:::bars Publisher page counts
Building Agentic AI Systems | 288 | 288 pages
Building Applications with AI Agents | 352 | 352 pages
Agentic Design Patterns | 427 | 427 pages
:::

Now the awkward part. This is not a clean 4.0. There are real flaws in this book, and I am not going to smooth them over.

The biggest flaw is the editing. At times the prose reads machine-assembled to me: long bullet lists, flat phrasing, and duplication nobody caught. Chapter 8 has a sub-chapter called "Dealing with uncertainty and biases" on pages 196-7, and then a sub-chapter called "Handling uncertainty and biases" on pages 201-2. That is the same material twice, five pages apart, with a thesaurus swap for a title. I cannot know what tools the authors used, and I will not guess. But the duplication is real, I noticed it myself, and it is the kind of sloppiness that makes a reader doubt everything else.

The book is also too shallow and high level in places, with basic code snippets only and no synthesis. I wanted more practice and less theory in the implementation chapters. And the self-promotion is relentless: the authors plug their own products so often that by the third plug I started wondering whether the book had a second author named Marketing.

So where does that leave my 4.0? The editing is weak. The bullet lists are long, the duplication is real, and the self-promotion should have been cut. But I read this as a design book, not a coding book, and as a design book it does a job I have not seen many short books do: it makes orchestration, roles, and governance feel like one coherent story instead of three appendices. That is what my 4.0 is for. It is not a perfect book. It is a useful one, with an editor who should have been stricter and a marketing department that should have been quieter.

The limits follow from the same choices. A compact book covering reasoning, planning, orchestration, multi-agent design, and governance cannot give a deep implementation guide for each topic. A reader who wants a long, detailed manual for one specific framework will need to pair this book with framework documentation and a patterns reference. A reader who wants the latest tool versions should check current behaviour as well, since agent tooling changed during 2025. I read the worked examples myself, and my honest report is that they are clear but basic. They show the shape of a design, not the hard parts of building it.

## A practical study plan and exercise

I read books like this best with a task in mind, not cover to cover with no application. The plan below runs over four weeks at a steady pace, using a task the reader already understands, so the hard part is the design, not learning a new domain at the same time.

In week one, I would pick one task from ordinary work and write down the goal, the success criterion, the constraints, and the stopping rule, each in one or two sentences. The first decision is whether the task needs a loop at all. If it has a known answer and a fixed procedure, a single prompt or a script may be enough. If it needs observation and revision, the loop is sketched, naming the plan, the action, and the observation at each step. If the stopping rule cannot be stated, the task is not ready for an agentic design.

In week two, the same task is broken into steps, with dependencies stated for each step. For each step, name the tool or data it needs, the expected output, and the check that would show the step worked. Run the plan on paper, or in a small prototype, record the points where it was wrong, and revise it once, using the observations.

In week three, decide whether the task needs more than one agent, and write the reason in one sentence. If a second agent is justified, assign roles, define the handoff between agents, and set limits on iteration and cost. Then simulate a failure, for example a tool that returns an error or an output in the wrong format, and trace the sequence that follows. The question is whether the failure is detected, logged, and handled, or whether it passes silently to the next step. If it passes silently, the orchestration needs a check at that handoff.

In week four, list the data and tools the system can reach, and remove any access the task does not need. Write a short run log for one complete task, recording the plan, the tool calls, the observations, and the final decision. Then review that log as if explaining the run to a colleague or an auditor. Identify the decisions that need human review before the system is used on a consequential task, and put that review in place.

:::compare Study with a task and study without a task
# Reading without a task
- Ideas stay abstract and hard to test
- Framework details dominate the notes
- The reader cannot tell which advice applies
# Reading with a task
- Each idea is tested against a real constraint
- Design choices are recorded with reasons
- The reader leaves with a design, not only notes
:::

## Who should read it and how it compares

The main reader is a practitioner or architect moving past single-prompt or single-agent demos who needs to design a system that will run inside an organisation: a data scientist, a software engineer, a product engineer, or a technical lead. The shared need is not more model capability. It is a way to structure reasoning, planning, orchestration, and governance so the system is understandable, testable, and operable. A student or early-career practitioner who already understands language models and tool use will also get value from it as a design primer, read alongside framework documentation for implementation detail.

It is less suited to a reader who wants only a framework tutorial, only copy-ready code, or only a research survey of agent theory, or to a reader who has already built multi-agent systems at scale and wants advanced material on one topic.

AI Agents in Action, published by Manning in 2025 and already reviewed on this site, is the closer companion for hands-on building. The review of that title is at ../review-ai-agents-in-action/. Where this book leads with enterprise architecture, orchestration, and governance, AI Agents in Action leads with implementation and working agents. Build first, and the Manning title is the better starting point. Decide the architecture first, and the Packt title is. The two complement each other rather than replace each other. Agentic Design Patterns, published by Springer in 2025, is the closer companion as a patterns reference, reviewed at ../review-agentic-design-patterns/. Where the Packt book gives a compact design narrative, the Springer book gives a structured reference to recurring patterns. Used together, the Packt book provides the system view and the Springer book the pattern detail.

## Further reading and public sources

- Packt Publishing catalog entry for *Building Agentic AI Systems*, by Anjanava Biswas and Wrick Talukdar, ISBN 9781803238753. Check the catalog for the current edition and availability.
- [AI Agents in Action](../review-ai-agents-in-action/), the hands-on companion reviewed on this site, for implementation and working agents.
- [Agentic Design Patterns](../review-agentic-design-patterns/), the patterns reference reviewed on this site, for recurring agent patterns in structured form.

## Verdict

My verdict is 4.0 out of 5. Building Agentic AI Systems is a compact enterprise guide to agentic systems, strongest on orchestration and governance, and not a deep framework manual. Its value lies in treating agency as a system property, in giving the reader a clear account of roles, handoffs, and limits, and in addressing the governance and operational questions that decide whether a system can be deployed and kept running. Its limits follow from its breadth and its length: it cannot give a long implementation guide for every framework it touches, and its tool-specific detail should be checked against current documentation.

I land at 4.0 because I am rating the design thinking, not the editing. The editing deserves the criticism. The design thinking deserves its place on the shelf.
