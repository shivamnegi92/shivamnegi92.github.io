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

## Make the rollout a controlled experiment

A canary is an experiment, not a small launch. Before sending traffic, write down the hypothesis, the eligible population, the comparison, the decision window, and the action for each outcome. For example: “For requests in locale A, model v2 will improve successful resolution without raising timeout or policy-violation rates; compare against v1 on the same request class; roll back if a safety guardrail crosses its predeclared limit.” This is an illustrative template, not a result. If you cannot say what observation changes your decision, you are not testing a hypothesis-you are watching a dashboard and hoping it tells a story.

:::flow Define the rollout before it starts
Question + eligible traffic -> Baseline and candidate -> Guardrails + window -> Decision rule -> Promote, hold, or rollback
:::

Separate the **unit of assignment** from the **unit of analysis**. Assigning individual requests can expose one person to both versions, which is useful for request-level latency comparisons but can confuse user-level behavior if the treatment changes a conversation. Assigning stable users or sessions avoids that contamination, but it requires enough independent units and careful handling of users who return. Choose the unit based on how the model can affect outcomes; document it alongside the experiment.

Keep assignment stable, ideally with a deterministic hash of the chosen identifier and experiment key. Do not route by a random draw on every retry: a user could get v1, retry, then receive v2, making both the experience and the measurements hard to interpret. Exclude internal traffic, bots, and known test accounts using rules decided before looking at results. Record assignment even when the candidate fails to respond, otherwise the worst failures vanish from the candidate denominator.

:::compare Practical comparison designs
# Request-level split
- Useful for independent requests and latency
- Easier to balance on request attributes
- Retries may cross variants unless assignment is sticky
- Repeated users can experience both behaviors
# User or session split
- Better when outcomes accrue over a conversation
- Keeps a person on one variant during the experiment
- Requires enough independent users or sessions
- Needs explicit rules for return visits and identity gaps
:::

## Turn an SLO into an error budget

“Do not regress” is too vague to operate. Define a service-level objective (SLO) for each user-visible property that matters: successful response within the product timeout, valid output, and availability of any required fallback. An error budget is the tolerated portion of bad events in the chosen SLO window. The SRE workbook on error budgets describes the basic policy idea: reliability goals should determine how much risk remains for changes, rather than treating every release as automatically safe ([Google SRE, Error Budgets](https://sre.google/workbook/error-budget-policy/)).

For model rollouts, calculate guardrails from event counts and the agreed window, not from whichever chart happens to look calm. If a required event stream is missing, mark the decision as **unknown** and hold; missing telemetry is not evidence of safety. If a denominator is tiny, avoid a confident significance claim. Report counts, interval estimates, and the raw denominator next to rates. Prefer a predeclared sequential test or fixed decision window to checking repeatedly and stopping the moment a favorable fluctuation appears. The method must match the monitoring cadence and stopping policy.

:::tree Rollout decision with explicit uncertainty
Canary window complete?
  Telemetry incomplete or sample inadequate
    Hold; repair measurement or extend under the same policy
  Guardrail violation or safety incident
    Roll back; preserve evidence and open an incident
  Guardrails within budget
    Evidence supports improvement
      Promote one rung and keep monitoring
    Evidence is inconclusive
      Hold, extend only if planned, or stop
:::

A single aggregate can conceal a harmful subgroup. Define slices that are both meaningful and supportable before launch: language, device class, input length, or other relevant characteristics. Use privacy-respecting aggregation and minimum-count rules; do not expose sensitive examples to broad dashboards. A slice with too few observations is an investigation signal, not a license to claim a precise rate. Never invent a universal threshold: the acceptable budget depends on consequence, legal obligations, product promises, and the baseline reliability users already receive.

## Build the deployment plumbing

A safe model release needs more than a new checkpoint. Treat the model, tokenizer, prompt or feature code, policy configuration, runtime, and dependency versions as one immutable release manifest. Keep the prior known-good manifest addressable. A model name alone is not enough to reproduce a decision if tokenization or preprocessing changed underneath it.

At request time, log a privacy-reviewed correlation identifier, assigned variant, release identifier, route, timestamps, feature freshness indicators, timeout/fallback outcome, and the final action. Store only the inputs needed for debugging under an approved retention policy; redact or avoid logging raw sensitive content. Prediction diffs can be useful in shadow mode, but a diff is not a quality judgment. Sample disagreements for blinded review, include agreement cases, and inspect error clusters rather than only dramatic examples.

Make rollback a tested path, not a button nobody has pressed. It should restore the previous serving artifact and compatible configuration, stop new candidate assignment, and leave enough capacity for the stable version. Define who may trigger rollback, who is paged, and whether rollback affects in-flight requests. Run a staging drill with a deliberately failing candidate; verify dashboards, alerts, assignment, and recovery. A rollback that restores model weights but leaves a broken tokenizer or schema is not a rollback.

:::seq Failed canary and recovery
actors: Monitor, Rollout controller, Router, Stable release
Monitor -> Rollout controller: guardrail breach
Rollout controller -> Router: freeze candidate assignment
Router -> Stable release: send new requests to stable version
Monitor --> Rollout controller: verify recovery and preserve incident evidence
:::

## Failure modes worth rehearsing

**The canary is faster because it did less work.** A candidate may time out and return a cheap fallback; latency improves while task completion gets worse. Report fallback and timeout rates as outcomes, not merely infrastructure details. **The aggregate improves while a critical slice degrades.** Predeclare slices and escalation ownership, while respecting minimum sample sizes. **The comparison is contaminated.** Shared caches, cross-variant retries, changing upstream data, or a simultaneous prompt edit can make the model effect unidentifiable. Freeze unrelated changes or record them as part of the treatment.

**A metric improves after the definition changed.** Version metric logic and validate it against hand-checked events before comparing releases. **Shadow inference overloads production.** Shadow requests are not user-visible, but they still consume CPU, memory, queue slots, and provider quota. Apply sampling and strict resource isolation; shadowing is not free. **Rollback increases load.** If v1 has been scaled down, returning all traffic to it may trigger a second incident. Keep capacity and test the transition. **The model passes but the safety behavior changes.** Include policy-sensitive and adversarial cases in offline evaluation, shadow review, and ongoing audits; aggregate task success is not a substitute for a safety gate.

## A practical preflight checklist

Before the first user sees the candidate, verify that offline tests include recent and representative data, leakage checks, critical slices, and known failures. Confirm that serving and training transformations agree, schemas are backward compatible, and model outputs are validated before they reach downstream systems. Set explicit request and resource limits. Verify alert destinations, dashboards, sampling plans, on-call ownership, and rollback permissions. Check that candidate traffic cannot bypass authentication, authorization, or content-policy enforcement.

During each rung, compare candidate and baseline on the same definitions and report counts beside rates. Keep a human review queue for sampled outputs with blinding where practical. Stop on a safety issue or a breached hard limit without waiting for statistical significance. Promote only one change at a time, and leave enough observation time for the outcome to occur. After launch, continue monitoring for delayed labels, drift, and changes in fallback behavior; full traffic is not proof that the model will remain healthy.

For a small team, the minimum viable version can be a versioned manifest, deterministic assignment, structured event log, a dashboard with named guardrails, and a documented manual rollback owner. Automation is valuable when it enforces a clear policy. Automating an ambiguous metric just makes the wrong decision faster.

## Incident readiness and post-rollout learning

A rollout is not complete when the percentage reaches 100. Keep the same guardrails after full promotion, because broad traffic can reveal load-dependent failures and rare inputs the canary did not contain. Watch delayed outcomes too: a request can appear successful at response time while a later workflow fails. Define the time-to-label and do not compare cohorts until their observation windows are comparable. If labels arrive late, use immediate proxy metrics only as early warnings, not as replacements for the eventual outcome.

When an alert fires, first protect users: stop promotion, reduce candidate assignment or roll back according to the runbook, and confirm recovery on the stable release. Then preserve the evidence needed to learn: release manifest, assignment rules, metric definitions, alert timeline, sampled examples under appropriate access controls, and relevant dependency changes. Avoid “fixing” the incident by changing several variables at once. A short blameless review should identify the detection gap, the decision that was unclear, and one concrete preventive action with an owner. The goal is to improve the release system, not to find a person to blame for trusting it.

:::loop Close the loop after an incident
Contain impact -> Verify stable behavior -> Preserve scoped evidence -> Find contributing conditions -> Assign prevention work -> Update tests and runbook
:::

A useful drill is to inject a candidate that returns malformed schema for a small internal cohort. Verify that schema validation blocks user-visible output, alerting identifies the release, assignment can be frozen, and rollback restores the previous artifact. Repeat with a latency failure and with a missing metric feed. A system that only practices model-quality regressions may fail on the very operational faults that make rollback necessary. Run drills in a controlled environment and ensure injected failures cannot affect real users.

## Choose rollout granularity with risk in mind

The familiar 1%, 10%, 50%, 100% ladder is only an example; it is not a safe universal recipe. A low-volume service may need a longer period to collect enough evidence at a small percentage. A high-volume service can create a large absolute number of affected requests even at a small share. Consider both the fraction and the expected number of exposed users, the reversibility of the model’s actions, the harm severity, and whether impact is concentrated in a particular group. For an irreversible downstream action, use a stricter approval and verification path than for a reversible ranking change.

| Release context | Safer emphasis |
|---|---|
| New model, reversible output | Shadow comparison, sampled review, then small sticky cohort |
| Model triggers external side effects | Authorization tests, idempotency, explicit confirmation, verified state |
| Low traffic or delayed labels | Longer observation, conservative hold, qualitative review |
| High-risk or regulated decision | Human oversight, subgroup review, policy approval, audit trail |
| Shared runtime or major dependency change | Capacity test and staged infrastructure rollout independent of model quality |

This table is a design aid, not compliance advice. Product, legal, security, and domain owners should define the risk class and required review. A metric threshold cannot decide whether a category of use is acceptable; it can only help enforce a policy already decided by accountable people.

## Make rollout evidence reviewable

A release record should make it possible for someone who was not on the launch call to reconstruct the decision. Save the candidate and baseline identifiers, assignment policy, metric query version, observation window, exclusions, sample counts, confidence method, reviewer sampling policy, and final decision with its owner. Include a short note about known blind spots, such as an underrepresented locale or a delayed business outcome. Do not store raw prompts merely to make a report feel complete; aggregate safely and retain only reviewed samples under the team’s data policy.

If two teams disagree about promotion, resolve the disagreement by clarifying the risk and evidence, not by averaging incompatible metrics. A reliability owner may prioritize timeouts while a product owner prioritizes task completion; both can be valid constraints. Document which limits are hard stops and which are trade-offs, and who has authority to accept residual risk. Escalate when the decision crosses a policy or safety boundary. This prevents a convenient aggregate score from becoming an accidental override of a more important requirement.

Use the record to improve the next experiment. If a canary was inconclusive because labels arrived late, revise the measurement plan rather than merely extending every future test. If sampled disagreements exposed a preprocessing mismatch, add a parity test to the release gate. If a slice repeatedly lacks enough observations, consider a targeted offline evaluation or controlled cohort rather than making a claim from noisy production counts. The rollout process gets better when each deployment leaves behind a reusable test, not just a chart.

## Key takeaways

- Assume the new model is worse until production says otherwise.
- Shadow first: it is free truth with zero user risk.
- Canary with explicit guardrails, and automate rollback.
- Handle degenerate inputs, such as zero or missing baselines, before doing any arithmetic.
- Eliminate training-serving skew with a shared feature path.

**Further reading:** Chen, Murphy, et al., *Reliable Machine Learning* (O'Reilly, 2022), reviewed [here](../review-reliable-ml/). Runnable baseline: [canary_rollout_simulator in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
