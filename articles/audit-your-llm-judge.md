---
title: Why Your LLM Judge Is Biased (and How to Audit It)
kind: guide
date: 2026-10-11
order: 6
summary: LLM-as-a-judge is the cheapest evaluator you will ever have and the easiest to fool. A practical audit protocol for position bias, verbosity bias, self-preference, and agreement with humans.
tags: evaluation, LLM-as-judge, bias, measurement
---
LLM judges changed evaluation. They are fast, cheap, and tireless. They also have opinions you did not ask for: they prefer the first answer, the longer answer, and, often, answers that sound like themselves. If you ship decisions based on an unaudited judge, you are optimizing for the judge's quirks, not for quality.

## How judges fail

:::tree Known judge biases
Judge failure modes
  Position bias!
    Prefers answer A or B by slot, not content
  Verbosity bias!
    Longer answers win regardless of quality
  Self-preference
    Favors outputs from its own model family
  Rubric drift~
    Inconsistent scoring across runs and prompts
:::

None of these are exotic. They show up in virtually every pairwise setup that has not been controlled for them.

## The audit protocol

:::flow Five checks before you trust a judge
Swap test -> Length-controlled pairs -> Human agreement* -> Repeat-run stability -> Adversarial probes
:::

### 1. The swap test (position bias)

Run every pair twice, as (A, B) and (B, A). A fair judge flips its verdict when you flip the order. Count the cases where it doesn't.

```python
def position_consistency(judge, pairs):
    consistent = 0
    for a, b in pairs:
        first = judge(a, b)    # returns "A" or "B"
        second = judge(b, a)
        consistent += (first == "A") == (second == "B")
    return consistent / len(pairs)
```

Anything well short of 1.0 means part of your verdicts are decided by slot, not content. Always aggregate over both orders.

### 2. Length-controlled pairs (verbosity bias)

Build pairs where the better answer is *shorter*. If the judge still picks the longer one, it is rewarding padding.

### 3. Agreement with humans

Use a chance-corrected statistic such as Cohen's kappa, not raw agreement. With imbalanced labels, raw agreement looks excellent even for a judge that always says "pass." Interpret kappa against the conventional Landis and Koch (1977) bands:

:::bars Landis and Koch interpretation bands for kappa (upper bound of each band)
Slight (0.00 to 0.20)! | 0.20 | 0.20
Fair (0.21 to 0.40) | 0.40 | 0.40
Moderate (0.41 to 0.60) | 0.60 | 0.60
Substantial (0.61 to 0.80)* | 0.80 | 0.80
Almost perfect (0.81 to 1.00) | 1.00 | 1.00
:::

Always report **human-human agreement** on the same items as a reference point. On MT-Bench, Zheng et al. (2023) found GPT-4's agreement with human experts (over 80%) comparable to the agreement between the humans themselves. If your judge agrees with humans far less than humans agree with each other, it is not measuring the same thing they are.

## Report the judge like an instrument

:::layers A judge evaluation report
Instrument | Judge model, version, prompt hash, temperature
Bias checks* | Swap consistency, length-controlled win rate, self-preference test
Validity | Kappa vs. humans on a stratified sample, with the human-human ceiling
Stability | Score variance across repeated runs and paraphrased rubrics
Scope | Which tasks it is validated for, and which it is not
:::

!!! insight Treat the judge as a **measurement instrument** with error bars, not as an oracle. You would not trust a thermometer you never calibrated.

## When to use a judge, and when not to

:::compare Good and bad uses of LLM judges
# Good fit
- Ranking candidate prompts during development
- Triage: flag likely failures for human review
- Style and format checks with crisp rubrics
# Bad fit
- Final launch decisions without human audit
- Factual correctness without references
- Judging outputs from its own model family
:::

## Build an audit set that can falsify your favorite judge

The smallest useful judge audit is not a random sample of outputs. A random sample tells you how often the judge agrees on ordinary cases, which is precisely where almost any reasonable evaluator looks competent. Build a **challenge set** around the failure modes you care about, then keep a separate representative set to estimate how often those cases occur in the traffic you will actually score.

Start with a unit of judgment. Is the judge deciding whether an answer is factually supported, whether a tool call was appropriate, whether a response follows a style rubric, or which of two answers better solves a task? Those are different measurement instruments. One omnibus prompt that asks for correctness, helpfulness, safety, tone, completeness, and elegance invites hidden trade-offs. A model can score highly by being polished while getting the answer wrong. Split criteria when they imply different evidence.

For a pairwise judge, preserve both candidates, the task, the rubric, and the evidence available to a human reviewer. Ask human raters independently, blind to model identity and randomized to answer order. Include an abstain or tie option if the task genuinely permits equivalence. For scalar scoring, define observable anchors for every score point. “A 4 is good” is not a rubric. “A 4 identifies the requested fact, cites the supporting paragraph, and omits no required field” is closer to one.

:::flow Assemble an auditable judge challenge set
Define the judgment unit -> Sample representative production cases -> Add targeted bias probes* -> Obtain blinded human labels -> Freeze a versioned audit set
:::

A challenge set should include pairs where the answer from the normally preferred model is worse, pairs where the longer answer is worse, pairs with a factual contradiction in otherwise fluent prose, and examples where the rubric conflicts with an easy stylistic shortcut. Record why each case exists. A set of adversarial examples without a known purpose becomes a collection of anecdotes, not an evaluation design.

Keep three slices distinct. The **calibration slice** is where you choose thresholds or tune the prompt. The **validation slice** is where you decide whether the tuned judge is acceptable. The **production sample** estimates how the judge behaves under the distribution you will score. If you reuse the validation set after each prompt edit, the reported agreement becomes a training metric. It no longer estimates generalization.

## Measure agreement with uncertainty, not a trophy number

A reported agreement percentage is incomplete without its denominator, sampling method, label prevalence, and uncertainty. Suppose a judge and a human agree on 90 of 100 easy examples. That may sound strong, but if the audit intentionally oversampled safety-critical disagreements, the 100 cases are not representative of production. Conversely, if only 10 examples are reviewed, a single changed judgment moves the result by ten percentage points.

For categorical labels, Cohen's kappa adjusts for agreement expected by chance under the raters' marginal label distributions. It is useful, but it is not magic. Kappa can be low when prevalence is highly skewed even if raw agreement is high, and weighted kappa is more appropriate when disagreements have an ordinal distance. For ranking, use a ranking-specific statistic. For continuous scores, inspect calibration and error, not only correlation. Pearson correlation can be high when a judge consistently scores every answer two points too generously.

Report a confidence interval. A simple bootstrap over independent examples gives a practical interval for many offline audits: resample examples with replacement, recompute the statistic, and report a percentile interval. If examples are grouped by user, conversation, or source document, resample at that group level instead. Otherwise, correlated examples masquerade as a larger sample than you actually have. If the audit is small, show the raw counts and disagreements alongside the summary statistic.

| Report item | What it prevents | Minimum disclosure |
|---|---|---|
| Sampling frame | Convenient examples being mistaken for representative traffic | Source, time window, inclusion rules |
| Label prevalence | Chance-adjusted metrics being misread | Count and fraction for every class |
| Human protocol | Hidden adjudication changing the target | Rater count, blinding, tie handling |
| Uncertainty | A noisy point estimate looking definitive | Interval method and resampling unit |
| Judge version | Results becoming irreproducible after edits | Model ID, prompt hash, decoding settings |

Do not report only the average. Slice the results by task type, answer length, answer source, language, and risk class when those distinctions matter. A judge that performs well on short factual answers and poorly on long multilingual answers should not be summarized as simply “0.82 agreement.” The aggregate may be mathematically correct and operationally useless.

## Separate position bias from answer quality

The swap test is necessary, but its interpretation needs care. If the prompt says “Answer A” and “Answer B,” changing their positions can alter both the decision and the explanation. Run the same pair in both orders, normalize the result back to the original candidate identity, and measure the fraction of pairs where the normalized preference is unchanged. Also count ties and invalid outputs separately. A malformed response is a judge failure, not a tie.

A symmetric protocol can reduce order effects by scoring A/B and B/A and aggregating. A simple majority may still hide instability, so preserve each run. If order changes the winner often, do not average your way into confidence. The instability itself is an audit result. Consider changing the presentation format, asking for independent criterion-level scores before the comparison, or using a second blinded judge for a limited adjudication sample.

Position is only one prompt artifact. Swap model names with neutral labels; change candidate formatting without changing content; and repeat with a rubric whose order is permuted. If the judge's preference follows the first-listed criterion, the formatting, or the model name, your score is partly measuring the prompt wrapper. That may be fixable, but only if you look for it.

## Test self-preference and model-family effects

Self-preference is difficult to measure if the judge cannot reliably identify model provenance. Design the audit with matched outputs from different systems on the same tasks, then randomize labels and order. Compare the judge's preference for outputs from its own family with human preference on those exact pairs. Do not infer self-preference from a small public leaderboard alone; task selection, decoding settings, and output style are confounds.

A useful analysis asks whether the judge's decision changes when provenance metadata is removed, randomized, or replaced with a neutral token. Another asks whether the judge rewards stylistic features correlated with its own generation style, such as a particular answer structure. If the score drops when style is normalized but the substance remains, the judge may be rewarding presentation rather than task performance.

The control has to be fair to both candidates. Do not remove citations from one answer and not the other. Do not strip formatting if formatting is part of the task. Normalize only the features that are nuisance variables for the evaluation question. The question is not “can I manipulate the output until the judge changes?” It is “does an irrelevant difference change a judgment that should be about something else?”

## What to do when the audit fails

Do not respond to a failed audit by adding more elaborate instructions to the judge prompt and rerunning the same examples until the score rises. That is overfitting. First locate the error slice: position, length, self-preference, criterion ambiguity, or unstable output. Then change one factor at a time and evaluate on the calibration split. Freeze the prompt before looking at the validation split again.

Some failures are not prompt failures. If the rubric asks for grounded factuality but provides no reference evidence, the judge may have no reliable basis to decide. If humans themselves cannot agree on the criterion, the judge's disagreement may expose a specification problem. Convene adjudication on a targeted sample, revise the rubric, and create new examples that distinguish the intended labels. A clearer task definition often beats a larger judge model.

Set an operating rule before using the judge. For example: the judge may rank candidates during prompt development; a human audits a stratified sample before a release decision; and the judge cannot alone approve high-impact factual, safety, or authorization outcomes. The exact boundary depends on the impact of an error, but it should be explicit and versioned. “We will use judgment” is not a control.

:::tree Response to an audit failure
Judge audit fails
  Bias concentrated in a controllable format
    Change the protocol, keep the rubric
    Re-test on held-out cases*
  Human labels disagree
    Clarify the criterion and adjudicate
    Add discriminating examples
  Evidence is missing
    Supply references or abstain!
  Performance remains unstable
    Restrict use to triage, not decisions
:::

## A release checklist for the evaluator

Before a judge score enters a dashboard or launch gate, verify the following:

- The judgment target is one criterion with a written rubric and evidence policy.
- The audit includes ordinary traffic and targeted bias probes, reported separately.
- Human labels were obtained blind, with disagreement and adjudication retained.
- The judge's model, prompt, tools, decoding settings, and output parser are versioned.
- Swap, length, self-preference, and repeat-run stability were measured where relevant.
- Agreement includes raw counts, a suitable metric, slices, and an uncertainty interval.
- A held-out set remains untouched during rubric and prompt iteration.
- The operating boundary states what the judge may rank, flag, or decide.

This checklist is intentionally stricter than “the judge seems to agree with us.” A judge that passes it can still be wrong. The point is not to certify an oracle; it is to expose enough of the instrument's error that a team can decide where it is safe to use.

## Build a decision log before you build a judge dashboard

A good audit ends in a decision record, not a colored badge. Record the exact question the judge was permitted to answer, what evidence it received, the threshold used, and the consequence of crossing that threshold. If a judge says “pass,” a later reviewer should be able to reconstruct whether that meant “no citation errors,” “the answer is factually supported,” or “the product is safe to ship.” Those are not interchangeable outcomes.

Keep one row per audited item. Useful fields include an immutable example ID, task family, sanitized input, candidate output IDs, reference evidence IDs, human labels, judge label, judge rationale if collected, prompt/model versions, and a disposition. Store sensitive raw content only under the access and retention controls appropriate to it. The analysis dataset should use stable identifiers so researchers can reproduce a disagreement without copying customer data into a notebook.

A disagreement taxonomy saves time. “Judge chose the longer answer” is actionable. “Judge is bad” is not. Label errors with a small controlled set: position effect, unsupported claim missed, correct abstention penalized, rubric ambiguous, parser failure, reference missing, or human-adjudication unresolved. Review the top error categories at each evaluation cycle, and assign each a concrete owner or experiment. The taxonomy is not bureaucracy. It stops the team from repeatedly debating the same anecdote.

:::layers A minimal decision record for each judge run
Task contract | Criterion, rubric version, evidence policy, allowed outcomes
Inputs | Sanitized example IDs, candidate IDs, reference IDs
Judge identity | Model version, prompt hash, decoding and tool settings
Human comparison | Blind labels, adjudication status, agreement statistics
Disposition | Use for ranking, triage, hold, or release decision; owner and date
:::

Do not treat the model's explanation as proof of its judgment. A fluent rationale can be generated after a preference has already been selected, and the explanation may omit the cue that actually drove the choice. Save the rationale as diagnostic data, but grade the judgment against the evidence and the rubric. When a judge cites a reference passage, independently check that the passage entails the claim it is supposed to support.

## Match audit effort to the decision's blast radius

Not every use of a judge needs the same audit depth. Sorting draft prompts for an engineer to inspect is a low-impact use; automatically rejecting a user's application is not. A practical policy creates tiers: exploratory ranking, bounded triage, human-reviewed recommendation, and consequential automated decision. Each tier has a higher bar for evidence, subgroup analysis, monitoring, and appeal.

For exploratory ranking, a small challenge set and routine spot checks may be enough to identify obvious position or parsing failures. For triage, measure recall on the failures the judge is supposed to find, because a false negative leaves the issue unseen. For a human-reviewed recommendation, inspect whether people rubber-stamp the judge or meaningfully correct it. For consequential decisions, do not infer acceptability from benchmark agreement alone: validate the complete decision process, including who can override it, how applicants or users contest errors, and what records remain available for audit.

:::compare Scale audit requirements to decision impact
# Low impact: development ranking
- Keep a small bias challenge set
- Sample disagreements and malformed outputs
- Never present rank as objective truth
# High impact: user-affecting gate
- Validate across relevant groups and task slices
- Human review and a usable appeal path
- Monitor drift, overrides, and false negatives
:::

Human oversight is only real if the human has enough time, evidence, and authority to disagree. A reviewer who sees one green checkmark, has five seconds, and is measured on throughput is not an independent safeguard. Design the interface to show the rubric, the cited evidence, known uncertainty, and an explicit reject or defer action. Then audit the human-plus-judge system, not just the model component.

There is also a data-protection boundary. Audit sets often contain user text, code, or business records. Minimize what is retained, redact secrets, control access, and define a deletion schedule. If a third-party model provider receives examples, the data-processing terms and retention settings are part of the evaluation design. A statistically elegant audit that leaks protected data is a failed system.

## Monitor after the offline audit

An offline audit describes a version on a sample at a particular time. It does not guarantee the judge remains valid after a provider silently updates a model, the application changes its prompt, the task distribution shifts, or a parser changes the output format. Treat the judge like a production dependency: pin versions when possible, hash prompts and rubrics, and trigger revalidation when any of those inputs change.

Monitor rates that reveal operational change: abstentions, malformed outputs, human overrides, disagreement by task slice, and the fraction of cases missing required evidence. A sudden change is not automatically model drift; it can be a logging or upstream data regression. Keep enough metadata to distinguish those causes. If the judge is hosted and the exact weights cannot be pinned, maintain a small sentinel set and rerun it on a schedule, while treating unexplained score changes as a release event.

Do not continuously tune thresholds against the production outcome you are trying to improve. If human reviewers are trained to accept the judge, the labels can become circular. Preserve an independent audit sample, refresh it as the task changes, and keep a record of the old and new decision boundaries. Change control is part of measurement integrity.

## When not to use an LLM judge

Some evaluation questions have a cheaper, stronger oracle. If the expected output is structured, validate it against a schema. If correctness can be checked by executing code, run tests. If an action should update a database, query the resulting state. If there is a trusted answer key, compare against it with task-appropriate normalization. A generative judge is not a badge of sophistication; it is an extra model with extra failure modes.

Use a model judge when the property is genuinely semantic and no deterministic evaluator captures it adequately, such as whether a summary preserves the important caveats. Even then, a rubric may decompose the task into testable checks: required claims present, prohibited claim absent, citation supports statement, and uncertainty stated when evidence is incomplete. The more of the judgment you can make executable, the smaller the region left to subjective scoring.

!!! tip Before adding an LLM judge, write down the strongest non-LLM baseline. Run both on the same blinded set. If the model judge does not improve decision quality enough to justify its cost and failure modes, keep the baseline.

## A worked audit protocol

Consider a team choosing between two retrieval-augmented answers. The rubric has three dimensions: factual support from the supplied documents, completeness against a fixed list of required facts, and clarity for the intended user. Do not collapse them immediately. First label each dimension independently on a stratified sample, with reviewers blind to model identity. Add adversarial pairs where one candidate is fluent but invents a number, where one is shorter but complete, and where both answers are equally valid.

Run the judge in both candidate orders and retain raw outputs. Normalize the preference to candidate identity, calculate agreement separately for each dimension, and inspect confidence intervals and disagreements. Then test a revised prompt on a calibration subset. Freeze it, evaluate on the held-out subset, and compare against a simple baseline: required-fact checklist plus a human clarity rating. If the LLM judge only improves style ranking but not factual-support detection, restrict it to style ranking. That is a useful result, even if the broad “AI evaluator” vision gets smaller.

Finally, inspect workflow behavior. Give reviewers the judge rationale and evidence references, then observe whether the interface changes their decisions. A judge can be individually accurate while making the combined process worse if it anchors reviewers. Measure reviewer override rates and re-audit the cases where the judge and human disagree. The target is not a model score. The target is a better, more reliable decision process.


## Key takeaways

- Measure the judgment target humans can actually label; do not bundle unrelated criteria into one score.
- Report counts, label prevalence, uncertainty, and meaningful slices alongside agreement.
- Treat swap instability, self-preference, and malformed outputs as findings, not noise to average away.
- Keep high-impact release decisions under human review until the judge's operating boundary is validated.

**Further reading:** Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) (2023). Landis and Koch, *The Measurement of Observer Agreement for Categorical Data* (Biometrics, 1977). Runnable baseline: [judge_audit in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
