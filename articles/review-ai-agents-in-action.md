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
Agent books are hard to write. The field changes quickly, and frameworks can evolve faster than a book can be revised. *AI Agents in Action* is presented by its publisher as a practical tour of agent-building concepts and tools. This review is based on Manning's public catalog information and other public documentation about the technologies named here; it is not a claim to have read the entire book or run its examples. The durable question is not which framework is fashionable, but how an agent chooses actions, observes results, handles state, and fails safely.

The book's public framing points to building blocks such as actions, memory, knowledge, planning, feedback, and control flow. It also names technologies and ideas including Nexus, AutoGen, CrewAI, and behavior trees. Framework capabilities change, so their presence in a book should be read as a snapshot, not a guarantee about current APIs or recommended production choices. The publisher catalog is the primary source for the book's contents and edition information; project documentation is the source for current framework behavior.

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

A behavior tree makes a portion of control flow explicit, which can improve inspection and targeted testing. It does not make the whole system deterministic: language-model decisions inside a node may remain variable, and the tree's branches still need meaningful tests, limits, and failure handling.

### Planning and feedback

The book's publicly described material covers planning and feedback as ways to go beyond a bare tool-call loop. In a reliable design, “check the work” must be operationalized: specify what evidence counts as success, whether the check is independent of the first attempt, and what the agent does when the result is inconclusive. A second model-generated answer is not automatically a trustworthy verifier.

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

For more on agent security and evaluation, see public guidance such as the OWASP Top 10 for LLM Applications and the documentation for the specific frameworks you choose. The companion articles [How to Put Guardrails on an AI Agent](../guardrails-for-agents/) and [System 1, System 2: How to Give Your AI a Fast Path and a Slow Path](../system1-system2-llms/) discuss related engineering concerns; they are supplements, not endorsements or claims about the book's contents.

## My rubric

| Topic | Coverage |
|---|---|
| Building blocks and tools | Strong |
| Multi-agent patterns (AutoGen, CrewAI) | Strong |
| Memory and knowledge | Good |
| Evaluation rigor | Moderate |
| Security and guardrails | Light: supplement it |

## Scope, edition, and review basis

The primary source for this review is Manning Publications' public catalog entry for Micheal Lanham's *AI Agents in Action*, checked alongside publicly accessible project documentation for the agent frameworks mentioned in the article. Manning lists February 2025 and ISBN 9781633436343 for the cataloged product. Its page currently advertises a new edition; this review addresses the cataloged 2025 edition, and the later edition's exact publication date and contents are not verified here. The ISBN shown is the publisher's product identifier; verify the format-specific record before purchasing or citing. Framework names and capabilities are even more time-sensitive and should be checked against their maintainers' current documentation.

The title is useful to assess as an applied introduction because agent engineering combines several distinct concerns. A model may reason over a goal, choose from tools, call an external system, receive observations, keep state, and decide whether to continue. Each action can introduce cost, latency, security exposure, or irreversible effects. An “agent” is therefore not just a prompt with a loop around it. It is a system with control flow, permissions, state management, error handling, and an objective that must be evaluated at the task level.

## What the building blocks mean in practice

**Actions and tools** are interfaces between model-generated intent and an external capability. A tool can read a record, search a collection, send a message, or change a system. This is a trust boundary. A tool description should state its inputs, outputs, permissions, and failure behavior. The application-not the model-must enforce authorization. A language model that can request a sensitive action should not gain permission merely because its text says the user approved it. Keep tools narrow, validate arguments, and separate read access from write access.

**Knowledge and memory** are often conflated, but it helps to separate retrieval of reference material from persistence of interaction state. Retrieval can provide documents relevant to a request; memory may preserve preferences or prior events across turns. Each raises its own questions: what is stored, for how long, who can inspect or delete it, how stale facts are handled, and whether a retrieved passage is evidence or untrusted content. Retrieval does not guarantee truth. An agent should be able to say that relevant evidence is missing instead of treating a plausible completion as verified knowledge.

**Planning** can mean anything from listing a few steps to dynamically adapting a multi-step plan after tool results. A plan is useful only if it remains bounded and connected to the user's goal. Plans can be malformed, unnecessary, or based on a false premise. Systems should cap steps, tokens, wall-clock time, and tool expenditure; validate actions before execution; and allow cancellation. For consequential operations, explicit approval should occur at the action boundary, not be inferred from an earlier broad instruction.

**Feedback and evaluation** close the loop. A tool response is an observation, not necessarily proof of success. A write call might return an acknowledgment while the target state remains unchanged; a search result can be irrelevant; a generated answer can sound confident while citing unrelated material. Define success in terms of observable task outcomes and, when possible, verify important state changes independently. Record failures as evaluation cases so that a fix can be checked against both the original failure and regressions.

**Profiles and personas** may help frame a role, but they are not a security mechanism. Instructions can conflict, be overridden by untrusted content, or be misunderstood. A system prompt should not be the only barrier between a model and a privileged operation. Enforce constraints in code, use scoped credentials, validate outputs, and maintain an audit trail appropriate to the risk.

## Choosing an architecture: one agent, several, or explicit control flow

A single-agent design has fewer moving parts and is usually a good baseline. A multi-agent design can separate tasks or permit parallel work, but it also creates coordination messages, duplicated context, synchronization, cost, and new failure modes. A planner and critic may disagree; two agents may share the same incorrect assumption; and a coordinator may accept a plausible but unsupported result. Multiple roles do not automatically provide independent review.

Use multiple agents only when a specific requirement justifies them, such as parallel independent searches, isolation of specialist context, or a measured improvement in a benchmark that reflects real tasks. Establish a baseline and compare end-to-end task success, latency, cost, and error severity. Avoid evaluating only the quality of intermediate conversation. The product requirement is a correct, safe, useful outcome-not an impressive transcript.

Behavior trees offer another architectural idea: control flow can be represented with selectors, sequences, conditions, and fallback branches. This can make high-level paths visible to engineers and allow deterministic checks around model-driven steps. However, a behavior tree is not automatically superior to a simple state machine or ordinary workflow. It adds its own design and testing burden. The right choice is the simplest representation that makes important transitions understandable and testable.

Frameworks such as AutoGen and CrewAI provide abstractions for agent collaboration and orchestration; Nexus is identified in the book's public framing as a platform associated with the author. These are implementation vehicles, not architectural guarantees. APIs and supported patterns evolve. Before adopting any framework, inspect its current maintenance state, execution model, security posture, observability, state persistence, and ability to interoperate with existing services. Keep business rules and authorization outside a framework-specific abstraction when doing so improves portability and auditability.

## Memory and state: convenience with obligations

Agent state should be explicit. Separate transient context needed for the current task from durable memory, and distinguish user-provided facts from tool-observed facts and model-generated summaries. A summary can omit a qualifier; a remembered preference can become stale; a retrieved document can contain malicious instructions. Provenance and timestamps help downstream logic decide how much to trust a fact.

Memory needs lifecycle controls: retention periods, deletion, access limits, and protections against cross-user leakage. A memory store should not become a hidden second database that bypasses the product's privacy and data-governance rules. Evaluate whether memory actually improves task success, and measure stale or incorrect recall as a failure mode. In many applications, a stateless interaction with explicit retrieval is simpler and safer than persistent personalization.

## Production requirements beyond a prototype

A prototype can be useful without being production-ready. Production systems need budgets and observable boundaries. Set maximum tool calls, retries, context size, elapsed time, and spend. Make tool calls idempotent where possible so retries do not duplicate a purchase, message, or other side effect. If an action cannot be made idempotent, use a confirmation or transaction mechanism and record the operation identifier.

Treat retrieved documents, webpages, emails, and tool outputs as potentially untrusted input. Prompt injection can be indirect: content that appears to be reference material may attempt to redirect the agent or extract data. Filtering alone is not a universal solution. Reduce the authority of the model, isolate secrets from contexts that do not need them, limit the tools available to each task, and require policy checks outside the model for high-impact actions. Log enough to investigate behavior while respecting privacy and data minimization.

Reliability requires graceful failure. Define what happens when a provider times out, a tool returns malformed data, the retrieval store is unavailable, or the agent reaches its budget. A safe fallback may be a concise refusal, a request for clarification, a human handoff, or a partial result clearly labeled as incomplete. “Try again” should have bounded retries and backoff. A system that loops until it produces something confident is not robust; it is merely persistent.

Evaluation should include representative tasks, adversarial and ambiguous cases, permission boundaries, and failures from real usage. Measure end-to-end completion, factual support, tool selection, action correctness, and harmful side effects separately where applicable. Use deterministic unit tests for business rules and integration tests for tool contracts, then add task-level evaluations for model behavior. Keep a regression set, but avoid overfitting prompts to a tiny, static benchmark. Human review is needed for high-impact or subjective outcomes, and the review process itself should be calibrated and documented.

## Limits of a fast-moving book

The chief limitation of any agent book is the changing ecosystem. Framework APIs, model capabilities, and recommended deployment practices can shift between publication and implementation. Code examples are best treated as learning material and checked against current upstream documentation, versions, and security advisories. The book's lasting value, if a reader finds it useful, is more likely to be its conceptual tour than its exact dependency choices.

A second limitation is that broad coverage can make difficult subjects appear easier than they are. Memory, planning, multi-agent coordination, and evaluation each merit deep treatment. A working demo does not establish robustness across varied prompts, users, tools, and malicious content. The buyer should regard an introductory tour as a starting point, then seek deeper sources for threat modeling, privacy, reliability, human factors, and domain-specific validation.

A third limitation is terminology. “Autonomous” can suggest a system that acts without oversight, while many useful agents are bounded workflows with selective model control. Prefer a precise description of what the system can do, what it cannot do, and which actions require approval. This keeps product expectations aligned with actual capability.

## Comparison with adjacent resources

| Resource | Best use | What to verify or add |
|---|---|---|
| Agent introduction | Learn the vocabulary and common components | Current framework behavior and security practices |
| Framework documentation | Implement against a specific library | Whether the abstraction fits your architecture and risk |
| LLM application guide | Retrieval, prompts, and model integration | Tool permissions, lifecycle, and task-level evaluation |
| Security guidance | Threat modeling and defensive controls | Application-specific authorization and testing |
| Reliability guide | Operations, incidents, and service objectives | Agent-specific budgets, traces, and action verification |

## Reading and study guide

1. **Check the publisher catalog.** Confirm the edition, date, table of contents, and sample material available for the copy under consideration. Treat ISBN and year as format-specific where catalogs disagree.
2. **Draw the action boundary.** For each example, identify which component proposes a tool call, which component authorizes it, and where results are validated.
3. **Build the simplest version first.** Implement one narrow task with explicit inputs, tools, and success conditions before adding long-term memory or multiple agents.
4. **Add failures deliberately.** Test timeouts, malformed arguments, irrelevant retrieval, conflicting instructions, duplicate retries, and exhausted budgets.
5. **Revisit current docs.** Before copying an example, verify framework APIs and their maintenance/security posture in the project's own documentation.

### Discussion questions

- What evidence distinguishes an agent from a model call embedded in a fixed workflow?
- Which decisions should remain deterministic application code rather than model-selected actions?
- When would multiple agents provide independent evidence, and when would they amplify shared error?
- What kinds of data should be stored as memory, and what should be retrieved only when needed?
- Which failures require a refusal, which allow a fallback, and which require human approval?

### Practice exercises

- Implement a tool that reads a harmless local dataset. Validate its arguments, enforce a narrow permission boundary, and make malformed calls fail safely.
- Create a short agent workflow with a hard step budget, timeout, and explicit completion check. Add a test showing the system stops when a tool repeatedly fails.
- Compare one-agent and two-agent solutions on the same small set of tasks. Measure final task success, cost, and latency; do not score conversational polish as a proxy for correctness.
- Add retrieved text containing conflicting instructions to a test fixture. Verify that the agent treats it as untrusted content and cannot use it to expand its tool permissions.
- Design a memory retention policy for a hypothetical assistant. Include provenance, expiry, deletion, and a test for cross-user isolation.

## Further reading and public sources

- Manning Publications: [catalog entry for *AI Agents in Action*](https://www.manning.com/books/ai-agents-in-action). Check this page for current edition and metadata details.
- [AutoGen documentation](https://microsoft.github.io/autogen/), [CrewAI documentation](https://docs.crewai.com/), and the official Nexus project references linked by the publisher/author. Verify current project status and APIs directly; names in a book are not a claim of current maintenance or suitability.
- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/), for security risks that agent builders should consider.
- For orchestration, memory, and behavior trees, use the maintainers' primary documentation and compare against simpler state machines or workflows before introducing a framework.

## Further engineering questions for a careful reader

An agent book's examples should prompt questions beyond “does the demo run?” Ask which state is authoritative, what happens if the model repeats a tool call, how the system behaves when a tool returns partial data, and whether a human can reconstruct the action after the fact. Those questions turn a code walkthrough into an engineering review.

### State and idempotency

Suppose an agent submits a reservation request, waits for a response, and times out. There are at least two possible states: the reservation failed before the external service received it, or it succeeded and the response was lost. The model cannot infer which occurred from silence. A robust workflow checks the external system using a stable request identifier before retrying. Where the external API supports idempotency keys, use them; where it does not, define a reconciliation step rather than allowing blind retries.

This example also clarifies what “memory” is not. Conversation history may record that the model attempted an action, but it does not prove that the action committed. The service of record does. Store the external transaction ID and resulting state as evidence, not merely the assistant's text saying “done.”

### Observability without retaining everything

A production trace should capture enough to explain a decision while avoiding indiscriminate retention of prompts, private documents, and secrets. Useful fields include the task ID, policy version, selected tool, validated argument summary, authorization result, external request ID, latency, retry count, and terminal outcome. Redact or tokenize sensitive values, restrict access, and choose retention based on the purpose of the trace.

If hidden model reasoning is unavailable or not appropriate to store, do not make the audit design depend on it. Record the inputs and outputs at the system boundary, the structured decision fields, and the external evidence. An operator usually needs to know what action was requested and authorized, not to preserve an unfiltered transcript of every intermediate thought.

### Failure recovery and user expectations

A recovery strategy should distinguish a temporary dependency failure from a policy refusal, missing information, and a model failure. Retrying a transient read may be safe; retrying a write may duplicate a side effect. A refusal should not be retried with a more permissive prompt. Missing information should trigger a clarifying question. A model error should become a recoverable handoff, not a fabricated success response.

Write the user-visible states before the prompt: “working,” “needs your approval,” “could not verify,” and “completed.” Then bind each state to an observable system condition. The word “completed” should require a successful read-back or authoritative transaction result. That small contract prevents a common category error where generated language is mistaken for system state.

### When a framework is the wrong starting point

Before adopting a framework, list the requirements that its abstractions satisfy: branching, retries, durable execution, human approval, streaming, tracing, or multi-agent coordination. Map each requirement to a concrete capability and test. If the application needs only a sequence of three tools with a fixed branch, ordinary application code may be clearer. A framework is justified when it removes substantial orchestration work without hiding the policy and state boundaries that the team needs to inspect.

The same applies to the book's named platforms. Treat Nexus, AutoGen, or CrewAI as subjects for comparison, not as endorsements or a compatibility claim. Check current release activity, license, security advisories, persistence semantics, and supported model providers. If the implementation detail is vendor-specific, isolate it behind an interface so the rest of the application does not inherit a framework migration as a domain rewrite.

## A decision rubric for selecting an agent pattern

| Requirement | Prefer | Why | What to test |
|---|---|---|---|
| Fixed sequence of known operations | Deterministic workflow | Clear state transitions and predictable cost | Every branch and retry boundary |
| Choose among a small set of tools | Single agent with allow-list | Adaptive selection without distributed coordination | Unauthorized tool attempts |
| Independent subtasks with separate evidence | Parallel specialist agents | Can reduce elapsed time when work is truly independent | Shared-state and disagreement handling |
| Consequential write action | Policy-gated executor with approval | Model proposes; trusted service authorizes | Identity, ownership, replay, override |
| Durable long-running task | Workflow engine with persisted state | Survives process restarts and supports recovery | Crash between action and confirmation |

This table is an engineering synthesis, not a claim that the publisher recommends one architecture in every case. Requirements determine the design. The book's public scope gives readers vocabulary to explore, while the application team remains responsible for authorization, reliability, and evidence.

## Evaluation artifacts to keep with the implementation

A small agent project should ship more than a prompt. Keep the tool schemas, the policy table, representative and adversarial task fixtures, a deterministic baseline, a redacted trace format, and the release rule in version control. A reviewer should be able to answer: what can the agent do, which principal can it act for, how is success verified, and how does the system stop?

For each tool, write a contract with accepted arguments, trusted identity fields, side effects, idempotency behavior, timeout, error categories, and verification query. Then test the contract independently from the model. This keeps an LLM regression from becoming an authorization regression and lets teams switch models without silently changing permission semantics.

For the agent-level evaluation, record a versioned task set and the expected external outcome. Some tasks should be answerable from supplied context; others should require abstention or clarification. Include permission traps and injected instructions in tool results. A test passes only when both the final outcome and the allowed-action invariant hold. If the agent reaches the desired answer by making a forbidden intermediate call, it failed.

## Practical comparison exercise

Choose one low-risk task and implement three variants: a direct model call, a deterministic workflow, and a bounded agent. Keep the same test set, tool permissions, output contract, and external data. The direct call provides a lower-complexity baseline. The workflow shows what explicit branching buys. The agent tests whether adaptive tool selection improves outcome quality enough to justify additional complexity.

Do not collapse results into a single quality score. Report task completion, unsupported claims, unauthorized calls, duplicate side effects, clarification quality, model and tool calls, latency, and the number of human interventions. Inspect every severe failure even if aggregate results look favorable. Then document the boundary where each architecture is acceptable. The purpose is not to crown a framework; it is to learn which amount of autonomy the task actually needs.

## Verdict

**Provisional assessment: 4/5 based on Manning's public catalog, available sample information, and the documented scope of its named technologies.** The book appears positioned as a practical introduction to agent components and implementation ideas. The field's pace, the need for deeper security and evaluation guidance, and edition-specific metadata uncertainty are reasons to supplement it with current primary sources. This is a provisional assessment of public materials, not a claim of having read the whole book.
