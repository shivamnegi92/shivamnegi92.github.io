---
title: How to Ship a Model Safely: Shadow, Canary, and the Rollback Button
kind: guide
date: 2026-10-11
order: 9
summary: Offline metrics do not predict production. A deployment ladder of shadow traffic, canaries with guardrail metrics, and automatic rollback, the SRE way.
tags: MLOps, deployment, canary, reliability
---
Every ML engineer learns this once: the model that won offline can lose online. Traffic shifts, features arrive late, latency blows a timeout, and an offline gain turns into an online regression. The fix is not better offline evaluation alone. It is a **deployment process that assumes you are wrong** until production proves otherwise.

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
def decide(baseline, canary, max_err_delta=0.002,
           max_p99_regress=0.10, p99_ceiling_ms=1500):
    # Degenerate inputs first: never compute a ratio you cannot trust.
    if baseline.p99_ms <= 0 or canary.p99_ms <= 0:
        return "hold", "missing latency data"
    if canary.p99_ms > p99_ceiling_ms:
        return "rollback", "absolute p99 ceiling breached"
    if canary.error_rate - baseline.error_rate > max_err_delta:
        return "rollback", "error rate regression"
    if canary.p99_ms / baseline.p99_ms - 1 > max_p99_regress:
        return "rollback", "relative p99 regression"
    if significant_lift(baseline.success, canary.success):
        return "promote", "success metric up, guardrails held"
    return "hold", "inconclusive"
```

!!! warning Handle degenerate inputs before any arithmetic. Depending on the language, a zero baseline either crashes the controller (Python raises) or produces NaN or infinity. In many languages NaN makes every comparison false, so "regression > 10%" quietly evaluates to false, and a broken model gets promoted. Check for missing data first, and keep an absolute ceiling alongside the relative one.

## Watch for training-serving skew

When a model wins offline and loses online, check these causes in order. The order runs from most preventable to least:

:::layers Usual suspects for an offline-online gap, most preventable first
Feature skew! | Training and serving compute features with different code, or serving reads stale values
Label leakage offline | The offline eval saw information that is not available at prediction time
Timeout fallbacks | The new model is slower, so more requests silently fall back to defaults
Distribution shift | Live traffic no longer looks like the training data
:::

Compute features with the **same code path** for training and serving, or log the features you served and train on those logs. Skew is among the most common and most preventable causes of "it worked offline."

## Key takeaways

- Assume the new model is worse until production says otherwise.
- Shadow first: it is free truth with zero user risk.
- Canary with explicit guardrails, and automate rollback.
- Handle degenerate inputs, such as zero or missing baselines, before doing any arithmetic.
- Eliminate training-serving skew with a shared feature path.

**Further reading:** Chen, Murphy, et al., *Reliable Machine Learning* (O'Reilly, 2022), reviewed [here](../review-reliable-ml/). Runnable baseline: [canary_rollout_simulator in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
