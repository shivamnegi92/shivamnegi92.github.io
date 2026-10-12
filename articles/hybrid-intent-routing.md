---
title: How to Route Intents with Confidence: The Hybrid Classifier Pattern
kind: guide
date: 2026-10-11
order: 5
summary: Why a single model should never decide everything, and how to build a confidence-gated cascade of rules, a small classifier, and an LLM fallback with self-correcting labels.
tags: classification, routing, active learning, LLM-as-judge
---
Intent routing looks trivial until it isn't. "Where are the batteries?" goes to search. "Restock aisle 12" goes to a task agent. "Batteries for the thing in aisle 12, and is it on sale?" goes... somewhere. Route wrong and the whole downstream system fails, politely and expensively.

The pattern that holds up in production is not one model. It is a **cascade**: cheap and certain first, expensive and smart last.

## The confidence-gated cascade

:::flow Each tier handles what it is confident about and passes the rest down
Query -> Tier 0: exact rules* -> Tier 1: small classifier -> Tier 2: LLM fallback~ -> Route
:::

:::layers What each tier is good at
Tier 0: rules | Exact matches and regulatory must-routes. Microseconds. Zero ambiguity, zero generalization.
Tier 1: small classifier* | A distilled encoder covering the bulk of traffic. Milliseconds. Calibrated confidence.
Tier 2: LLM fallback | Long-tail, compositional, novel requests. Slow and costly, but flexible.
Human review~ | Sampled disagreements and low-confidence cases feed the labeling queue.
:::

The magic is in the gates between tiers. Each one is a calibrated threshold: "pass down if confidence is below tau."

## Calibrate, or the gates lie

A softmax score of 0.9 does not mean 90% accuracy. Neural networks are notoriously overconfident. Before you trust a threshold, calibrate.

:::compare Uncalibrated vs. calibrated confidence
# Uncalibrated
- 0.9 confidence might be 70% accurate
- Thresholds behave unpredictably
- Gate passes down the wrong cases
# Calibrated (temperature scaling)
- 0.9 confidence means about 90% accurate
- Threshold maps to an accuracy target
- Gate cost is predictable
:::

```python
import numpy as np
from scipy.optimize import minimize_scalar

def fit_temperature(logits, labels):
    def nll(t):
        z = logits / t
        z = z - z.max(axis=1, keepdims=True)
        logp = z - np.log(np.exp(z).sum(axis=1, keepdims=True))
        return -logp[np.arange(len(labels)), labels].mean()
    return minimize_scalar(nll, bounds=(0.05, 10), method="bounded").x
```

Fit the temperature on a held-out set and apply it at inference. One scalar fixes most overconfidence.

## The self-correcting data loop

Your labels are wrong. Everyone's are. The cascade gives you a free label-auditing machine: wherever the small classifier and the LLM disagree, something interesting is happening.

:::loop Self-correcting training data
Log tier disagreements
LLM-as-judge proposes label*
Human audits a sample
Fix labels + mine confusions
Retrain and recalibrate
:::

!!! insight Mine **confusion pairs**: classes the model mixes up most, such as "refund" vs. "billing question." Generate targeted contrastive examples that differ only in the distinguishing detail. A few hundred of those beat thousands of random new examples.

## Watch the confusion matrix, not just accuracy

Aggregate accuracy hides where the errors live. Errors almost always concentrate in a few class pairs whose definitions overlap. Read the confusion matrix and you know what to fix:

:::compare Two ways to spend your next sprint
# Bigger model (tempting)
- Expensive retraining and serving
- Overlapping label definitions stay overlapping
- Same confusion pairs, slightly fewer errors
# Sharper data (effective)
- Rewrite definitions for the top confusion pairs
- Add contrastive examples for those pairs only
- Directly targets where the errors are
:::

If the top few confusion pairs account for a large share of errors, you do not need a bigger model. You need sharper label definitions and contrastive data for those pairs.

## Pick thresholds by cost

:::curve Sweeping the Tier 1 to Tier 2 gate threshold
x: Share of traffic sent to the LLM
y: End-to-end routing accuracy
series: Calibrated gate* | 0,0.62 0.08,0.8 0.18,0.9 0.35,0.93 0.6,0.94 1,0.94
series: Random handoff~ | 0,0.62 1,0.94
mark: Knee* @ 0.18,0.9
:::

## Data hygiene: the bugs that inflate your metrics

| Bug | Symptom | Fix |
|---|---|---|
| Train/test leakage | Suspiciously high offline accuracy | Deduplicate across splits, including near-duplicates |
| Duplicate phrases | Inflated metrics, overweighted classes | Hash-dedupe after normalization |
| Extreme class imbalance | Rare intents never predicted | Stratified splits, class weights, targeted synthesis |
| Stale label definitions | Annotators disagree | Write a labeling guide with contrastive examples |

!!! warning Check for leakage before celebrating. If a big offline jump came from removing duplicated phrases that appeared in both train and test, that is a measurement fix, not a model fix. It is valuable, but report it as such.

## Specify the routing contract first

Before collecting examples, decide what a route means. An intent is not merely a topic; it is the action the application is prepared to take next. “Refund” might mean a user is asking about eligibility, requesting a refund, or reporting one already issued. If those cases lead to different permissions or user experiences, they should not collapse into one label simply because they share a noun.

Write a short labeling contract with a definition, inclusion rules, exclusions, and contrastive examples for every class. Include a `clarify` or `other` route when the request is ambiguous or outside the catalog. Do not make the classifier force every sentence into the nearest known action. An explicit fallback is often safer than a confidently wrong tool invocation.

Separate intent from slots. “Cancel order 123” can be routed to cancellation intent, but the order ID and authorization are separate fields that require their own validation. The router should choose a destination, not decide whether a user is entitled to perform the action. Keep policy and authorization checks downstream, where they can use trusted identity and current account state.

:::layers Define the contract before training
Intent label | The next product capability that should handle the request
Slots | Entities and arguments extracted separately and validated
Clarification | Questions that need more detail before a route is safe
Out of scope | Requests that no supported capability should receive
Authorization | Independent server-side decision, never implied by intent
:::

The taxonomy should reflect operational consequences. If one class invokes a read-only search and another invokes a financial write, merge them only if a downstream component can safely distinguish them. Conversely, do not create a dozen labels for destinations that behave identically; unnecessary classes create annotation burden and sparse data. A good taxonomy is as small as possible while preserving the decisions the product must make.

## Build data that reflects the decision boundary

Start with real or realistic requests from the expected deployment context, but remove secrets and unnecessary personal information. Split by conversation, user, source, or time as appropriate so near-duplicate phrasings do not leak between training and evaluation. A random utterance-level split is especially misleading when a dialogue contains many paraphrases of the same request.

For each class pair that is easy to confuse, create contrastive examples differing in the meaningful cue. A billing question asking “why was I charged?” differs from a refund request asking “send the money back,” even though both mention a charge. Keep examples that should route to clarification: “change it” with no referent, or “cancel my order” when the product supports multiple cancellable objects. These examples teach the system where not to guess.

Annotator agreement is a taxonomy diagnostic. If careful annotators cannot distinguish two labels consistently from the available text, a larger model will not conjure a stable boundary. Clarify the label definitions, add context that the runtime actually has, or combine the labels and defer the distinction to a later step. Preserve disagreements for review rather than silently selecting one label; they often reveal product ambiguity, not annotator carelessness.

A balanced challenge set is useful for comparing models, but it is not a production cost estimate. Maintain a separate representative sample that reflects observed traffic prevalence. For rare but consequential intents, report performance on an intentionally enriched slice as well as the representative estimate. Never mix those sampling schemes into one accuracy number without stating how it was constructed.

## Calibrate decisions, not just scores

Temperature scaling can improve the calibration of a classifier's probabilities, but calibration is not the same as correctness, and a single scalar does not solve every data shift. Fit it on a held-out calibration set that is separate from the final test set. Check reliability by class and by relevant slices, and compare predicted confidence with observed accuracy. If a model says 0.8 on many examples, roughly four out of five should be correct in that population for the confidence to behave as advertised.

Expected calibration error is a useful summary only when the binning and sample size are visible; rare intents may have too few examples for a meaningful per-class estimate. Inspect reliability diagrams and proper scoring rules such as log loss or Brier score alongside task metrics. A classifier can have useful rankings but poorly calibrated scores, or good aggregate calibration while being overconfident for one high-risk class. Threshold decisions should therefore use class-conditional evidence where sample sizes permit.

A confidence gate also needs an operational definition of confidence. Maximum class probability is simple, but it can be high when the model is confidently wrong among a set of incomplete labels. Entropy or the margin between the top two classes can expose some ambiguity, yet neither is automatically a calibrated risk estimate. Evaluate the actual gate policy on held-out examples, including the `clarify` behavior, rather than assuming a probability threshold transfers across classes or releases.

| Routing choice | Main benefit | Cost or risk to measure |
|---|---|---|
| Rule handles exact, safety-critical phrases | Predictable and inspectable | Coverage and brittle wording gaps |
| Classifier handles familiar cases | Low latency and bounded inference cost | Per-class errors and calibration drift |
| LLM handles selected tail cases | Flexible interpretation | Variable latency, token cost, and prompt risk |
| Clarification or human review | Avoids an unsafe guess | Added friction and queue delay |
| Default route | Keeps workflow moving | Blast radius of a wrong destination |

## Choose the cascade using a cost curve

Threshold selection is a decision problem, not a contest to maximize accuracy. For each threshold, measure the fraction handled by the small model, the fraction escalated, the rate of wrong routes, the rate of unnecessary escalations, and the downstream consequence of each error. Estimate serving and review costs using your own workload and vendor or infrastructure prices; keep them as inputs to a decision model, not as timeless constants in a chart.

An LLM fallback may be more accurate on a slice and still be a poor default if it adds too much latency, cost, or privacy exposure. Conversely, routing too little to the fallback can increase expensive downstream failures or customer effort. Plot the Pareto frontier between error risk and total cost, including human review and downstream correction-not just model inference. A reasonable operating point depends on the relative cost of a false route, a clarification, and an extra model call.

:::flow Evaluate each candidate threshold
Held-out labeled traffic -> Apply rule and classifier gates -> Measure errors, escalation, latency, and cost -> Weight by impact and class -> Choose a threshold with explicit budget
:::

Do not use the illustrative curve above as a promised shape. Real curves can have plateaus, abrupt changes, or different ordering across classes. Plot both aggregate and per-class results. A single overall threshold is easy to operate; per-class thresholds can improve the trade-off but are harder to validate and maintain. Introduce them only when the data supports a stable distinction and the additional complexity has an owner.

Run sensitivity analysis on uncertain inputs. If a cost estimate, traffic mix, or error severity is uncertain, show how the selected threshold changes across plausible assumptions. If small changes in assumptions flip the policy, gather better measurements or choose the more conservative option. This is more honest than presenting one precise threshold backed by guessed costs.

## Operate the LLM fallback as a bounded component

The LLM fallback does not become ground truth merely because it is larger. Constrain it to return a schema containing a supported route, a confidence or uncertainty field if you can validate its meaning, and a short rationale suitable for debugging. Reject unknown labels and malformed output. Do not let free-form tool calls from the classifier prompt execute directly; map an accepted route through the same authorization and schema checks used for any other request.

Keep fallback prompts task-specific and provide only the context required for routing. User messages can contain prompt injection, quoted commands, or private information. Treat the input as data, not instruction, and avoid exposing tools or secrets to a route classifier. A fallback that cannot decide should return `clarify` or `other`, not invent a new product capability.

If the fallback times out or is unavailable, use an explicit safe degradation strategy: ask a clarifying question, send the request to a review queue, or use a conservative default with no side effect. Do not silently reroute everything into a broad agent because a dependency is down. Set timeouts and retry limits, track fallback failures, and ensure retries do not duplicate any downstream action.

## Use disagreement as a labeling signal carefully

Disagreement between the small classifier and LLM is a valuable queue for review, not a free source of correct labels. Both systems can share biases, and the LLM may confidently choose an invalid class. Sample disagreements for human adjudication, while also sampling agreements: if review only targets disagreement, shared errors remain invisible. Include low-confidence cases and real downstream corrections in the queue, and weight the sample so you can separately estimate traffic prevalence and focus on rare high-impact failures.

Record the original text in a privacy-controlled store, model and prompt versions, class probabilities, selected route, fallback response, eventual user correction, and reviewer disposition. Use stable, pseudonymous case IDs and minimize raw content in general-purpose logs. If data is used to retrain, document its provenance and annotation process. Never feed unreviewed LLM-generated labels directly into the training set as unquestioned facts; that creates a self-confirming loop.

A useful review workflow asks the annotator to label the intended route independently before showing the model's suggestion. Then capture whether the disagreement was a model error, unclear wording, missing context, taxonomy issue, or a downstream product rule. These categories lead to different fixes. Repeated ambiguity calls for a clarifying interaction or taxonomy change, not simply more examples with a guessed label.

## Monitor drift and know when to stop routing

Monitor the full path: volume per intent, rule-match rate, classifier confidence distribution, escalation rate, fallback latency and errors, clarification rate, downstream success, and correction or undo events. Segment by language, channel, new versus returning users, and other relevant operational slices, while honoring privacy and minimum sample requirements. A sudden rise in one route can reflect a campaign or product change as easily as model drift.

Use delayed outcome labels where direct intent truth is unavailable. User rephrases, abandoned flows, agent transfers, corrected selections, and successful task completion are useful signals, but they are proxies with confounds. Do not treat a user who completed a flow as proof the initial route was right; they may have been forced to adapt. Periodically obtain direct human labels on a sample to validate proxy metrics.

Recalibrate after changes to the model, class definitions, language mix, input normalization, or upstream context. Keep a versioned baseline and compare candidate releases on the same frozen set plus a recent representative sample. Use staged rollout and a rollback switch. If confidence becomes unreliable or a critical class regresses, route more cases to clarification or review until the new behavior is understood.

## A launch checklist

- The class definitions match distinct downstream actions, with explicit `other` and clarification paths.
- Intent classification is separate from identity, authorization, and argument validation.
- Evaluation data is deduplicated and split by the true unit of dependence.
- Representative and challenge sets are reported separately.
- Per-class precision, recall, calibration, and high-impact errors are inspected.
- Thresholds are selected from measured error, cost, latency, and review trade-offs.
- Fallback output is schema-validated, bounded, and safely degraded on outage.
- Disagreements and agreements are sampled, reviewed, and retained under privacy controls.
- Monitoring includes downstream outcomes, drift indicators, and a rollback owner.

## Key takeaways

- Route with a cascade: rules, then a small calibrated classifier, then an LLM fallback.
- Calibrate confidence before you trust any threshold.
- Use tier disagreements as a free label-audit signal.
- Attack the top confusion pairs with contrastive data.
- Audit splits for leakage and duplicates before believing any number.

**Further reading:** Guo et al., [On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599) (2017). See also [SelectiveNet: A Deep Neural Network with an Integrated Reject Option](https://arxiv.org/abs/1901.09192) for selective prediction and abstention. Runnable baselines: [faq_router and query_rewriter in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
