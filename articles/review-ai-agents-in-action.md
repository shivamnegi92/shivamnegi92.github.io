---
title: AI Agents in Action: A Practical Tour of Building Autonomous Systems
kind: review
date: 2026-10-11
order: 9
slug: review-ai-agents-in-action
summary: Micheal Lanham's hands-on guide covers agent architectures, tool use, memory, planning, multi-agent setups, and evaluation. Here is what it gets right and where production engineers need more.
tags: agents, tool use, multi-agent, LLM applications
book: AI Agents in Action | Micheal Lanham | Manning Publications, 2025 | 9781633436343 | img/books/ai-agents-in-action.jpg
verdict: A broad, practical on-ramp to building LLM agents with lots of runnable examples. Pair it with a security-minded resource before you let an agent touch production.
rating: 4
---
Agent books are hard to write. The field changes every quarter, and frameworks rise and fall faster than a book goes to print. *AI Agents in Action* handles this sensibly. It teaches the durable **building blocks** of agents (actions, memory, knowledge, planning, feedback) and uses frameworks such as AutoGen and CrewAI as vehicles rather than as the lesson. It also introduces Nexus, the author's own open-source agent platform, and borrows behavior trees from game AI as a way to give agents explicit, inspectable control flow.

## The agent anatomy the book teaches

:::layers The building blocks of an agent
Profile + persona | Who the agent is, its role, and its constraints
Actions + tools* | Functions the agent can call to affect the world
Knowledge + memory | Retrieval over documents, plus short- and long-term memory
Reasoning + planning | Decomposing goals, choosing steps, and adapting
Feedback + evaluation | Judging outcomes and correcting course
:::

## The loop at the heart of it

:::loop The agent loop, as the book builds it
Receive goal
Plan steps*
Call tool
Observe result
Evaluate + adapt
:::

## What it does well

### Breadth, with code

It covers single agents, multi-agent conversations, agent platforms, and assistants with memory and knowledge, all with runnable examples. For someone who has only used a chat interface, it is an efficient tour of what is possible.

### Multi-agent patterns

:::compare Single-agent vs. multi-agent designs
# Single agent
- One loop, one context
- Simpler to debug and evaluate
- Context window becomes the bottleneck
# Multi-agent
- Specialized roles, such as planner, coder, critic
- Parallelism and separation of concerns
- Coordination overhead, harder to evaluate
:::

!!! tip Start with one agent. Move to multi-agent only when you can name the specific bottleneck, such as context length, specialization, or parallelism, that a second agent fixes.

### Behavior trees: control flow you can read

:::tree A behavior tree for a support agent, in the style the book teaches
Root: selector
  Sequence: known intent*
    Classify request
    Call the matching tool
  Sequence: needs clarification
    Ask a follow-up question
  Fallback~
    Hand off to a human
:::

This is one of the book's most practical ideas. A free-form LLM loop decides its own control flow, which makes it hard to test. A behavior tree makes the control flow explicit and leaves the LLM to handle each node, which is much easier to debug and evaluate.

### Planning and feedback

The chapters on planning and feedback push beyond "call tools in a loop" toward agents that check their own work, which is the difference between a demo and a system.

## What production engineers need on top

The book is an on-ramp, not a production manual. Before shipping, you need deeper treatment of:

:::tree Production concerns to add beyond the book
Production agent
  Security!
    Least-privilege tool scopes
    Indirect prompt injection defense
  Reliability
    Step, token, and time budgets
    Idempotent tool calls
  Evaluation*
    Grounded task outcomes
    Regression suites from failures
:::

I cover the security side in [How to Put Guardrails on an AI Agent](../guardrails-for-agents/), and grounded outcome evaluation is central to my [voice-agent research](https://arxiv.org/abs/2609.30798).

## My rubric

| Topic | Coverage |
|---|---|
| Building blocks and tools | Strong |
| Multi-agent patterns (AutoGen, CrewAI) | Strong |
| Memory and knowledge | Good |
| Evaluation rigor | Moderate |
| Security and guardrails | Light: supplement it |

## Verdict

Four stars. A practical, generous introduction to building agents. Read it to get started, then harden what you build with security and evaluation discipline before it touches real users.
