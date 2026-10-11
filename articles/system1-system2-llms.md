---
title: System 1, System 2: How to Give Your AI a Fast Path and a Slow Path
kind: guide
date: 2026-10-11
order: 1
summary: Why every production LLM system should be two systems, and how to build the router, the escalation policy, and the evals that keep it honest.
tags: reasoning, architecture, routing, test-time compute
---
Here is an uncomfortable truth from production: most of your traffic does not need your smartest model. It needs a fast, cheap, boring answer. The hard 5% needs everything you have. If you run one model for both, you pay frontier prices for "what are your store hours" and you starve the multi-step query that actually needed deliberation.

Kahneman gave us the vocabulary decades ago. **System 1** is fast, automatic, associative. **System 2** is slow, effortful, deliberate. The LLM literature borrowed the metaphor, and it is a good one. Just remember it is a *metaphor*. Your model does not have two brains. You have to build them.

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

Autoregressive decoding is System 1 by construction. Each token is one pass through the network. There is no built-in "think harder" knob. Chain-of-thought (Wei et al., 2022) showed that making the model write intermediate steps improves multi-step reasoning. Snell et al. (2024) showed that spending *more inference compute* can beat a model several times larger. So the knob exists. It is just outside the weights.

:::bars Relative cost per request by strategy (illustrative, normalized to direct answer = 1)
Direct answer (System 1) | 1 | 1x
Chain-of-thought | 4 | ~4x
Self-consistency, 5 samples | 20 | ~20x
Tool-augmented ReAct loop | 12 | ~12x
Tree search with verifier! | 60 | ~60x
:::

Read that chart as a budget, not a benchmark. The exact multipliers depend on your prompts and models. The *shape* is the point: System 2 strategies cost one to two orders of magnitude more. You cannot afford them on every request, so you must not.

## The architecture: a two-speed system

:::flow Request lifecycle in a two-speed LLM system
ingress: Request -> Cheap features (length, intent, risk) -> Router*
fast: Router -> System 1 model -> Confidence check -> Response
slow: Escalate -> Plan + retrieve + tools -> Verifier* -> Response
:::

Four components, each with one job:

1. **Router.** A small classifier (a fine-tuned encoder or a tiny SLM) that predicts "does this need deliberation?" from cheap features. It must run in single-digit milliseconds, or it eats the savings.
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

"Hard" is not a feeling. Define it as: *the System 1 answer fails your eval, and the System 2 answer passes.* Run both paths offline on a sample of real traffic. The label falls out for free.

```python
def label(example):
    fast = system1(example.prompt)
    slow = system2(example.prompt)
    fast_ok = grade(fast, example.reference)
    slow_ok = grade(slow, example.reference)
    # Only escalate when it actually helps.
    return int((not fast_ok) and slow_ok)
```

Note what this ignores: cases both paths get right (System 1 suffices), and cases both get wrong (escalation is wasted money). That second bucket is your research backlog, not your router's problem.

### Step 2: choose the threshold with a cost curve, not a vibe

:::quadrant Where to set the escalation threshold
x: Escalation rate (cost) | high
y: Quality | high
pt: Never escalate~ @ 0.04,0.35
pt: Sweet spot* @ 0.22,0.86
pt: Escalate everything! @ 0.95,0.9
pt: Bad router! @ 0.6,0.45
:::

Sweep the router threshold and plot quality against escalation rate. You are looking for the knee: the point where quality is close to "escalate everything" at a fraction of the cost. A router that sits below the diagonal (the "bad router" point) is worse than random escalation. Throw it out.

## The verifier is the whole game

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
| Latency SLO | Hard timeout on System 2, then fall back to the System 1 answer with a disclaimer | A correct answer after the user left is a wrong answer |
| Cost runaway | Per-request token budget and max tool calls | Agent loops do not terminate politely |
| Silent drift | Track escalation rate as a first-class metric | A rising rate means your traffic or your fast model changed |
| Overconfidence | Calibrate the gate on held-out data, monthly | Uncalibrated confidence makes the gate decorative |

!!! warning If your escalation rate is above roughly 30%, your System 1 model is too weak or your router is too nervous. Fix the fast path first. A two-speed system only pays off when the fast path handles the bulk of traffic.

## Key takeaways

- System 1 and System 2 are a *budgeting* abstraction for inference compute, not a claim about machine cognition.
- Build two paths: a fast default and a slow, verified escalation.
- Label routing data by outcome ("escalation helped"), not by intuition.
- Pick the threshold from a quality vs. cost curve.
- Invest in verifiers. Deliberation without verification is expensive confidence.

**Further reading:** Kahneman, *Thinking, Fast and Slow* (2011). Wei et al., [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) (2022). Yao et al., [ReAct](https://arxiv.org/abs/2210.03629) (2023) and [Tree of Thoughts](https://arxiv.org/abs/2305.10601) (2023). Snell et al., [Scaling LLM Test-Time Compute Optimally](https://arxiv.org/abs/2408.03314) (2024).
