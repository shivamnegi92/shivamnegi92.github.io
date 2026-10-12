---
title: System 1, System 2: How to Give Your AI a Fast Path and a Slow Path
kind: guide
date: 2026-10-11
order: 1
summary: Why a production LLM system should run two paths, a fast default and a slow verified escalation, and how to build the router, the gate, and the evals that keep it honest.
tags: reasoning, architecture, routing, test-time compute
---
Most of your traffic does not need your smartest model. It needs a fast, cheap, boring answer. A small, hard minority needs everything you have. Run one model for both and you pay frontier prices for "what are your store hours" while starving the multi-step query that needed deliberation.

Psychology has a vocabulary for this. Keith Stanovich and Richard West coined the terms **System 1** and **System 2** in 2000, and Daniel Kahneman made them famous in *Thinking, Fast and Slow*. System 1 is fast, automatic, and associative. System 2 is slow, effortful, and deliberate. The LLM literature borrowed the metaphor, and it is a useful one, as long as you remember it is a *metaphor*. Your model does not have two brains. You have to build them.

## The core idea in one picture

:::compare Same prompt, two computational budgets
# System 1: fast path
- One forward pass per token, no scratchpad
- Pattern completion from training data
- Milliseconds, cheap, high throughput
- Confidently wrong on out-of-distribution input
# System 2: slow path
- Decompose, plan, call tools, verify
- Spends test-time compute on hard cases
- Seconds, expensive, lower throughput
- Can rationalize a wrong answer at length
:::

The engineering question is never "which system is better." It is **"which requests deserve System 2, and how do I find them cheaply?"** That is a routing problem, and routing problems are where systems engineers earn their salary.

## Why one model for everything fails

Autoregressive decoding gives every generated token a fixed amount of compute. The only way to "think harder" is to generate more tokens or more samples. Chain-of-thought prompting (Wei et al., 2022) showed that making the model write intermediate steps improves multi-step reasoning, and reasoning models now expose the same idea as an effort or thinking-budget setting. The cost model is unchanged: more thinking means more tokens. Snell et al. (2024) showed how far this goes. Allocating test-time compute adaptively was more than 4x as efficient as a best-of-N baseline, and in a FLOPs-matched comparison a smaller model with extra inference compute outperformed a 14x larger model, on problems where the small model already had a non-trivial success rate. So the knob exists. It lives outside the weights.

The cost of turning that knob follows from how many tokens and calls each strategy spends:

:::bars Relative cost per request, by strategy (k = samples, n = loop steps, b x d = beam width x depth)
Direct answer | 1 | 1 call
Chain-of-thought | 4 | 1 call, several times the output tokens
Self-consistency (k = 5) | 20 | k = 5 reasoning samples
ReAct tool loop (n = 4) | 16 | n = 4 calls, growing context, plus tool latency
Tree search (b = 3, d = 3)! | 72 | b x d generations + b x d evaluations, each a reasoning call
:::

The bars assume a reasoning call costs about four direct answers. Your multiplier will differ, but the structure is arithmetic, not opinion: deliberation multiplies calls, tokens, and latency. You cannot afford it on every request, so do not spend it on every request.

## The architecture: a two-speed system

:::flow Request lifecycle in a two-speed LLM system
ingress: Request -> Cheap features (length, intent, risk) -> Router*
fast: Router says easy -> System 1 model -> Confidence gate passes -> Response
slow: Router says hard, or gate fails! -> Plan + retrieve + tools -> Verifier* -> Response
:::

Four components, each with one job:

1. **Router.** A small classifier (a fine-tuned encoder or a tiny language model) that predicts "does this need deliberation?" from cheap features. It must be cheap relative to the System 1 call, typically tens of milliseconds at most.
2. **System 1 model.** Your fast default. Often a small or distilled model.
3. **Confidence gate.** A post-hoc check on the fast answer: token log-probabilities, a calibrated classifier, or agreement between two cheap samples. Low confidence means escalate.
4. **System 2 path.** Planning, retrieval, tool calls, and, critically, a **verifier** that can reject the answer.

!!! insight Escalation happens in two places: *before* generation (the router predicts difficulty) and *after* generation (the gate distrusts the answer). Pre-routing saves latency. Post-gating catches what the router missed. You want both.

## How to build the router

The router is a classifier, so treat it like one. Do not hand-write regex rules and call it intelligence.

:::loop The router improvement flywheel
Log every request
Sample + label hard cases*
Retrain router
Shadow-deploy, compare
Promote if calibrated
:::

### Step 1: define "needs System 2" operationally

"Hard" is not a feeling. Define it as: *the System 1 answer fails your eval, and the System 2 answer passes.* Run both paths offline on a sample of real traffic and grade them. The label is cheap relative to production, though not free: it costs one offline System 2 run and a grader per example.

```python
def label(example, k=3):
    # Grade k samples per path: single samples make noisy labels.
    fast_rate = sum(grade(system1(example.prompt), example.reference) for _ in range(k)) / k
    slow_rate = sum(grade(system2(example.prompt), example.reference) for _ in range(k)) / k
    if fast_rate == 0 and slow_rate == 0:
        return None              # both fail: escalation cannot help, exclude from training
    return int(slow_rate - fast_rate >= 0.5)   # escalate only when it clearly helps
```

Note the `None`. When both paths fail, labeling the example "do not escalate" would teach the router that the hardest prompts are easy. Exclude those cases from router training and send them to your research backlog instead.

### Step 2: choose the threshold with a cost curve, not a vibe

Sweep the router threshold and plot quality against escalation rate. Two reference points anchor the chart: never escalate, and always escalate. Escalating a *random* x% of traffic lands on the straight line between them. There is also a hard ceiling: escalating x% of traffic can fix at most x% of answers, so no router can climb faster than a slope of 1. A useful router hugs that ceiling at first, then flattens once the fixable requests are exhausted. A router on or below the random line is no better than a coin. Pick the knee: quality close to "always escalate" at a fraction of the cost.

:::curve Conceptual quality vs. escalation rate as you sweep the router threshold
x: Share of traffic escalated
y: Task accuracy
series: Random escalation~ | 0,0.78 1,0.9
series: Good router* | 0,0.78 0.05,0.825 0.1,0.86 0.15,0.882 0.3,0.895 1,0.9
mark: Knee* @ 0.15,0.882
:::

In this illustrative example, the fast path starts at 78% accuracy and the slow path reaches 90%, leaving at most twelve percentage points of errors that escalation could fix. Escalating 15% of traffic raises accuracy by 6.5 percentage points in the sketch, below the theoretical ceiling. These are drawn values, not measured results; do not infer a universal router rate or gain. Compute the curve from paired outcomes on your data, compare against random routing at the same budget, and include uncertainty. If the measured router sits below the random baseline, its ranking adds no value at that operating point.

## The verifier decides whether System 2 is worth paying for

System 2 without a verifier is just System 1 with more words. Long reasoning traces can talk themselves into a wrong answer, and visible chain-of-thought is not guaranteed to reflect what the model actually computed. Make the slow path *check its own work* against something external:

:::tree Verifier options, strongest first
Verifier
  Ground truth checks*
    Execute code, run unit tests
    Query the database, compare state
  Constraint checks
    Schema and type validation
    Business-rule assertions
  Model-based checks~
    Independent judge model
    Self-consistency vote
:::

Prefer verifiers higher in the tree. Executing code and checking state are close to ground truth. A judge model is useful but inherits the same failure modes you are trying to catch. Audit it against human labels before you trust it.

## Operational guardrails

| Concern | Guardrail | Why |
|---|---|---|
| Latency SLO | Hard timeout on System 2. Fall back to the System 1 answer if one exists (or run System 1 in parallel for pre-routed requests), otherwise return a graceful handoff | A correct answer after the user left is a wrong answer |
| Cost runaway | Per-request token budget and max tool calls | Agent loops do not terminate politely |
| Silent drift | Track escalation rate as a first-class metric | A rising rate means your traffic or your fast model changed |
| Overconfidence | Calibrate the gate on held-out data, monthly | Uncalibrated confidence makes the gate decorative |

!!! warning Watch the escalation rate as a health metric. If it creeps toward a large share of traffic, your fast path is too weak or your router too nervous. A two-speed system only pays off when the fast path handles the bulk of requests, so fix System 1 before buying more System 2.

## Build labels that do not teach the router a lie

The simple labeler above illustrates the idea but is intentionally not a production evaluator. Each call can be stochastic, the grader can be wrong, and “slow beats fast” may depend on the task’s risk. Run repeated evaluations with fixed prompt and decoding policies, preserve grader evidence, and manually review disagreements. If the answer has objectively verifiable outcomes-code execution, a database state change, arithmetic, or a cited source-prefer that outcome over a second model’s preference. If you use a model judge, calibrate it against human judgments and report its agreement and known blind spots.

Define the target label with a decision policy, not only answer quality. A slow path that takes too long, violates a tool permission, or produces an ungrounded claim may not be an improvement. One useful label is “escalation produces a better acceptable outcome within the latency and cost budget.” That prevents the router from learning to escalate requests where the slow model is more verbose but not more useful. Keep a separate “neither path succeeds” label for triage rather than silently forcing every example into easy or hard.

Build splits by user, conversation, source document, or time where appropriate. A random row split can place near-duplicate requests in both train and test, making routing look better than it is. Include difficult, rare, and adversarial examples, but do not let a synthetic challenge set dominate the natural traffic mix. Report both overall performance and targeted failure categories, and preserve an untouched test split until the router threshold is selected.

## Threshold selection: calculate the ceiling honestly

A router is a ranking system with a constrained budget. For each threshold, measure the share escalated, fast-path quality, slow-path quality, total quality, latency, and cost. The always-fast and always-slow endpoints provide comparison points, but the actual curve depends on which examples the router selects. Estimate uncertainty with a method suited to your data unit-resample users or sessions when requests within one conversation are correlated, rather than pretending every message is independent.

There is a useful hard bound for the accuracy curve. Suppose a fraction `x` of all requests is escalated, and escalation can improve accuracy by at most one point per request. The total accuracy increase over the fast-only baseline therefore cannot exceed `x` percentage points. More generally, if escalation can only correct some selected errors and can also introduce regressions, the net gain is lower. A curve that rises by more than x percentage points at escalation share x has inconsistent arithmetic or a changed evaluation population.

:::curve Conceptual router curve: accuracy vs. escalation share, bounded by the maximum possible gain
x: Share of requests escalated
y: Accuracy
series: Fast path only | 0,0.78 1,0.78
series: Maximum possible if every escalation fixes one error | 0,0.78 0.05,0.83 0.1,0.88 0.15,0.93 0.22,1.0
series: Illustrative measured router~ | 0,0.78 0.05,0.81 0.1,0.835 0.15,0.845 0.22,0.85 1,0.85
series: Random routing if slow path reaches 0.85! | 0,0.78 1,0.85
mark: Example operating point* @ 0.15,0.845
:::

The curves use **illustrative endpoints and values**, not measured results. In the example, escalating 15% raises accuracy by 6.5 percentage points, below the 15-point theoretical ceiling. Do not infer a universal router rate or accuracy gain from a drawn curve. Compute your own from paired outcomes, compare against random routing at the same budget, and include uncertainty. If the measured curve is below that baseline, the router’s ranking adds no value at that operating point.

A practical threshold policy can combine a maximum escalation share with a minimum expected benefit and a safety override. For example, route any request matching a high-risk rule to a reviewed path regardless of model confidence; for ordinary traffic, escalate only when the calibrated router score exceeds a threshold that fits the budget. This avoids using an average-quality objective to suppress rare but severe cases. Rules should be explicit, versioned, and reviewed for coverage gaps rather than quietly accumulating regexes.

## Make confidence usable

Token likelihood is not the same as correctness. Language models can assign high probability to a wrong answer, especially when the prompt resembles familiar text. Calibrate confidence on held-out examples from the intended deployment domain, using methods such as reliability diagrams and expected calibration error with their limitations documented. Check calibration separately for important slices; an aggregate calibration score can mask a poor subgroup. If the model or prompt changes, recalibrate-the old confidence mapping may no longer mean the same thing.

An abstention is a valid system output. The fast path can say it is uncertain, ask a clarifying question, or hand off to a human instead of triggering an expensive chain automatically. Distinguish uncertainty about the answer from missing information: a user’s ambiguous request may be best resolved by asking one question, while a high-risk factual question may warrant retrieval and verification. Avoid treating disagreement between two samples as a clean confidence estimate unless the relationship between disagreement and error has been measured.

## System 2 is a bounded workflow, not a magic model

Write down the slow path as a state machine. Each transition should have an input contract, a deadline, a maximum number of calls, and a recoverable failure outcome. A typical sequence is: classify the task, retrieve authorized context, plan only if needed, call allowlisted tools, validate tool arguments, execute with least privilege, verify the result, and compose a concise response. Tool output is untrusted data; do not let retrieved text redefine permissions or override system policy. Treat prompt injection in retrieved documents as a security event and test it explicitly.

:::flow Bounded slow-path workflow
Escalation -> Retrieve permitted evidence -> Plan within token and call budgets -> Validate tool arguments -> Execute allowlisted action -> Verify state -> Respond or hand off
:::

Set independent budgets for wall-clock time, model tokens, tool calls, and external side effects. A timeout should cancel work where possible; otherwise a timed-out user request can keep consuming resources. Use idempotency keys for retryable actions and require explicit confirmation for consequential or irreversible operations. If verification fails, do not claim success. Return a safe failure or handoff with enough context for recovery.

A verifier should match the claim. If the system says it booked an appointment, query the booking state; if it says code passes, run the tests; if it states a retrieved fact, check that the cited passage supports the claim. Schema validation catches malformed output but cannot establish truth. A second model judge is a weaker check when it shares the same model family, prompt assumptions, or blind spots. Use independent evidence when available and log what was checked without retaining unnecessary sensitive content.

## Operational metrics and failure drills

Track fast-path and slow-path quality separately, router false negatives and false positives on audited samples, escalation share, end-to-end latency percentiles, timeout rate, tool success, verifier rejection, fallback/handoff, and cost per completed task. Keep denominators and cohort definitions visible. A rising escalation rate can mean traffic shifted, the fast model regressed, confidence calibration drifted, or the router threshold changed; the metric is an alert to investigate, not a diagnosis by itself.

:::compare Routing failures and first response
# Escalates too little
- Audit hard examples missed by router
- Check subgroup and out-of-domain recall
- Revisit high-risk overrides
# Escalates too much
- Check calibration and data drift
- Find fast-path capability gaps
- Review slow-path value per request
:::

Run failure drills for slow-model timeout, retriever outage, malformed tool output, verifier disagreement, rate limiting, and a prompt-injection document. Confirm the system degrades safely: bounded retries, no duplicate side effects, and a user-visible handoff when appropriate. For an experiment, compare a fixed router threshold against fast-only, always-slow, and random escalation at matched budgets. Keep assignment and measurement consistent, and do not tune repeatedly on the final test set.

## Implementation checklist

Start with a narrow task where outcomes are measurable. Create a versioned evaluation set with realistic inputs, hard negatives, policy-sensitive cases, and duplicated-user grouping. Run both paths under declared decoding and tool policies. Label “escalation helped” using task success plus latency, cost, and safety constraints. Train or configure the router on training data, choose its threshold on validation data, and confirm the curve on a held-out set. Add an explicit high-risk policy path, a confidence abstention option, per-request budgets, and independent verification for external actions.

Before increasing traffic, shadow the router and both paths where safe, review missed escalations, and measure resource consumption. Canary the complete system, not just the model: a router change can shift load enough to overload the slow path. Monitor queueing and failures, keep a kill switch, and preserve the previous routing policy for rollback. Re-evaluate after changes to models, prompts, tools, or traffic mix.

## Key takeaways

- System 1 and System 2 are a *budgeting* abstraction for inference compute, not a claim about machine cognition.
- Build two paths: a fast default and a slow, verified escalation.
- Label routing data by outcome ("escalation helped"), not by intuition.
- Pick the threshold from a quality vs. cost curve.
- Invest in verifiers. Deliberation without verification is expensive confidence.

**Further reading:** Stanovich and West, *Individual differences in reasoning* (Behavioral and Brain Sciences, 2000). Kahneman, *Thinking, Fast and Slow* (2011), [reviewed here](../review-thinking-fast-slow/). Wei et al., [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) (2022). Yao et al., [ReAct](https://arxiv.org/abs/2210.03629) (2023) and [Tree of Thoughts](https://arxiv.org/abs/2305.10601) (2023). Snell et al., [Scaling LLM Test-Time Compute Optimally](https://arxiv.org/abs/2408.03314) (2024).
