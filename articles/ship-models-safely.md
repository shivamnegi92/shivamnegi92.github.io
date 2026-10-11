---
title: How to Ship a Model Safely: Shadow, Canary, and the Rollback Button
kind: guide
date: 2026-10-02
order: 9
summary: Offline metrics do not predict production. A deployment ladder of shadow traffic, canaries with guardrail metrics, and automatic rollback, the SRE way.
tags: MLOps, deployment, canary, reliability
---
Every ML engineer learns this once, painfully: the model that won offline loses online. Traffic shifts, features arrive late, latency blows a timeout, and a 2-point offline gain becomes a 5-point online regression. The fix is not better offline evaluation alone. It is a **deployment process that assumes you are wrong** until production proves otherwise.

## The deployment ladder

:::flow Promote one rung at a time, roll back at any rung
Offline eval -> Shadow (0% user impact) -> Canary 1% -> Canary 10%* -> Ramp 50% -> 100%
:::

Each rung answers a different question:

:::layers What each rung proves
Offline eval | Is the model better on held-out data? Necessary, never sufficient.
Shadow* | Does it run in production? Latency, errors, feature parity, and prediction diffs, with zero user impact.
Canary | Does it help real users? Guardrail and business metrics on a small slice.
Ramp | Does it hold at scale? Capacity, cost, and long-tail behavior.
:::

## Shadow mode: free truth

In shadow mode, the new model receives a copy of live traffic. Its predictions are logged, never served.

:::seq Shadow deployment
actors: User, Gateway, Model v1, Model v2 shadow
User -> Gateway: request
Gateway -> Model v1: request
Gateway -> Model v2 shadow: async copy
Model v1 --> Gateway: prediction (served)
Model v2 shadow --> Gateway: prediction (logged only)
Gateway --> User: v1 response
:::

Compare v1 and v2 on every shadowed request. Disagreements are a goldmine. Sample them for human review *before* any user sees v2.

## Canary with guardrail metrics

A canary needs two kinds of metrics: the one you want to improve, and the ones you must not break.

:::compare Success metric vs. guardrail metrics
# Success (should go up)
- Task completion rate
- Routing accuracy on audited samples
- Conversion or resolution rate
# Guardrails (must not regress)
- p99 latency and timeout rate
- Error rate and fallback rate
- Cost per request
:::

## Automate the decision

:::tree Canary decision logic
Evaluate canary window
  Any guardrail breached!
    Roll back immediately
  Guardrails OK
    Success metric significantly up*
      Promote to next rung
    No significant change~
      Extend window or stop
:::

```python
def decide(baseline, canary, max_err_delta=0.002, max_p99_regress=0.10):
    if canary.error_rate - baseline.error_rate > max_err_delta:
        return "rollback", "error rate regression"
    if baseline.p99_ms and (canary.p99_ms / baseline.p99_ms - 1) > max_p99_regress:
        return "rollback", "p99 latency regression"
    if baseline.p99_ms == 0:
        return "hold", "no baseline latency; cannot compute regression"
    if significant_lift(baseline.success, canary.success):
        return "promote", "success metric up, guardrails held"
    return "hold", "inconclusive"
```

!!! warning Handle the degenerate cases explicitly. A relative latency check that divides by a zero baseline silently computes "0% regression" and promotes a broken model. Add an absolute ceiling, too.

## Watch for training-serving skew

:::bars Most common causes of offline-online gaps (illustrative)
Feature skew (train vs. serve)! | 34 | 34%
Distribution shift since training | 27 | 27%
Latency or timeout fallbacks | 18 | 18%
Label leakage offline | 12 | 12%
Other | 9 | 9%
:::

Compute features with the **same code path** for training and serving, or log served features and train on those logs. Skew is the most common, and most preventable, cause of "worked offline."

## Key takeaways

- Assume the new model is worse until production says otherwise.
- Shadow first: it is free truth with zero user risk.
- Canary with explicit guardrails, and automate rollback.
- Handle degenerate cases, such as zero baselines, explicitly.
- Eliminate training-serving skew with a shared feature path.

**Further reading:** Chen, Murphy, et al., *Reliable Machine Learning* (O'Reilly, 2022), reviewed [here](../review-reliable-ml/). Runnable baseline: [canary_rollout_simulator in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
