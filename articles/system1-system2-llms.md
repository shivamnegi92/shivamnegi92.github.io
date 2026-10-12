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

:::curve Quality vs. escalation rate as you sweep the router threshold (System 1 alone: 78%, always System 2: 90%)
x: Share of traffic escalated
y: Task accuracy
series: Random escalation~ | 0,0.78 1,0.9
series: Good router* | 0,0.78 0.05,0.825 0.1,0.86 0.15,0.882 0.3,0.895 1,0.9
mark: Knee* @ 0.15,0.882
:::

In this example only 12% of requests can be fixed by escalation at all (90% minus 78%), which is why a good router finds most of the gain by escalating about 15% of traffic.

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

## Key takeaways

- System 1 and System 2 are a *budgeting* abstraction for inference compute, not a claim about machine cognition.
- Build two paths: a fast default and a slow, verified escalation.
- Label routing data by outcome ("escalation helped"), not by intuition.
- Pick the threshold from a quality vs. cost curve.
- Invest in verifiers. Deliberation without verification is expensive confidence.

**Further reading:** Stanovich and West, *Individual differences in reasoning* (Behavioral and Brain Sciences, 2000). Kahneman, *Thinking, Fast and Slow* (2011), [reviewed here](../review-thinking-fast-slow/). Wei et al., [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) (2022). Yao et al., [ReAct](https://arxiv.org/abs/2210.03629) (2023) and [Tree of Thoughts](https://arxiv.org/abs/2305.10601) (2023). Snell et al., [Scaling LLM Test-Time Compute Optimally](https://arxiv.org/abs/2408.03314) (2024).
