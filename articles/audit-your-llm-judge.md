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

## Key takeaways

- Assume your judge is biased until an audit says otherwise.
- Swap order, control for length, and check self-preference.
- Measure chance-corrected agreement with humans, with human-human agreement as the reference point.
- Version the judge prompt and model like any other dependency.
- Use judges for triage and iteration. Keep humans on launch decisions.

**Further reading:** Zheng et al., [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) (2023). Landis and Koch, *The Measurement of Observer Agreement for Categorical Data* (Biometrics, 1977). Runnable baseline: [judge_audit in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
