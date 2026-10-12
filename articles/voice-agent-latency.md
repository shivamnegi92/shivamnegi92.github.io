---
title: Why Your Voice Agent Feels Rude: Latency, Turn-Taking, and Barge-In
kind: guide
date: 2026-10-11
order: 3
summary: A systems view of real-time voice agents, why 800 ms feels broken, and how to engineer the pipeline, the turn-taking model, and the evals so conversations feel human.
tags: voice agents, latency, turn-taking, evaluation
---
A voice agent can have a perfect transcript and a perfect answer and still feel broken. Across ten languages, Stivers et al. (2009) found that people hand turns back and forth with a typical gap of about 200 ms. Pipelines that take a second or more to respond are fighting a deeply ingrained human rhythm, and users react by repeating themselves or talking over the agent. In voice, **timing is a correctness property**, not a performance nicety.

## Two architectures, two failure profiles

:::compare Cascaded vs. end-to-end speech-to-speech
# Cascaded pipeline
- ASR then LLM then TTS, each swappable
- Easy to debug: every stage has text
- Latency adds up across three hops
- Loses prosody and emotion at the text boundary
# End-to-end speech model
- Audio in, audio out, one model
- Lower latency, keeps tone and prosody
- Harder to debug: no text checkpoint
- Harder to ground tools and enforce policy
:::

Most production systems today are cascaded or hybrid, because debuggability and tool calling matter more than shaving the last 100 ms. Either way, you need a latency budget.

## The latency budget

Write the budget down per stage, and make it add up. Here is an example target for a cascaded agent aiming at 800 ms to first audio. Your numbers will differ, but the discipline should not:

:::bars Example latency budget, 800 ms to first audio (a design target, not a measurement)
End-of-turn detection | 200 | 200 ms
Streaming ASR finalize | 80 | 80 ms
LLM time-to-first-token* | 300 | 300 ms
TTS time-to-first-audio | 150 | 150 ms
Network + jitter buffer | 70 | 70 ms
:::

Notice the biggest line items: deciding the user is *done*, and the LLM's first token. You attack them with streaming and overlap, not just faster models.

## Overlap everything

:::seq Streaming pipeline: stages overlap instead of waiting
actors: User, VAD + ASR, LLM, TTS
User -> VAD + ASR: audio frames (streaming)
VAD + ASR -> LLM: partial transcript
VAD + ASR -> LLM: end-of-turn + final text
LLM -> TTS: first tokens (stream)
TTS -> User: first audio chunk
LLM -> TTS: remaining tokens
TTS -> User: rest of the reply
:::

The rules of thumb:

1. **Stream ASR.** Start the LLM speculatively on a stable partial transcript, and cancel if the final text changes meaningfully.
2. **Stream tokens into TTS** at phrase boundaries. Never wait for the full completion.
3. **Pre-warm** connections and caches. Cold starts are latency you chose.

## Turn-taking is a prediction problem

Silence-threshold VAD ("700 ms of quiet means done") is the classic bug factory. People pause mid-thought, and short answers end abruptly. Better systems *predict* turn ends from prosody and content.

:::tree Turn-taking signals, from crude to good
End-of-turn decision
  Silence threshold~
    Fixed timeout, cuts people off or lags
  Acoustic cues
    Falling pitch, lengthened final syllable
  Semantic completeness*
    Is the sentence syntactically complete?
    Did the user answer the question asked?
:::

## Barge-in: let users interrupt

If the user starts speaking while the agent talks, the agent must stop fast and *keep its state*. Two errors matter, and they trade off:

:::quadrant Barge-in tuning: sensitivity vs. selectivity
x: Sensitivity to user speech | high
y: Selectivity (ignores backchannels) | high
pt: Talks over users! @ 0.15,0.8
pt: Stops on every cough! @ 0.85,0.15
pt: Target* @ 0.8,0.8
:::

A backchannel ("mm-hmm", "right") is not an interruption. A sneeze is not an interruption. "Wait, no, my *other* account" absolutely is. Treat this as a classifier with labeled data, not a volume threshold.

## Measure what users feel

Word error rate and response quality are necessary but not sufficient. A rigorous evaluation reports **timing, recovery, and grounded outcomes** together, under disclosed conditions. That is the core idea behind TRG, the reporting standard I proposed in my [voice-agent evaluation work](https://arxiv.org/abs/2609.30798).

:::layers The TRG axes, plus the conditions every report must disclose
T: Timing* | Latency with clock anchors and statistics, plus whether speaking was appropriate at that moment
R: Recovery | Restoring conversation and task state after a disruption, measured separately from clean runs
G: Grounded outcome | Did the authorized action actually happen in the external system? Includes justified no-action
M: Multiparty~ | Conditional axis: appropriate speech and silence when several participants are legitimate
Conditions | Not an axis: language, accent, noise, speaker, load, and evaluator disclosures
:::

!!! tip Report latency as a distribution (p50, p90, p99) with the exact start and stop clock points. "Average latency 600 ms" with no anchors is not a measurement.

## Key takeaways

- In voice, timing is part of correctness.
- Budget latency per stage, then overlap stages with streaming.
- Predict turn ends from acoustics and semantics, not silence alone.
- Tune barge-in as a classifier that balances sensitivity and selectivity.
- Evaluate timing, recovery, and grounded outcomes together.

**Further reading:** Stivers et al., *Universals and cultural variation in turn-taking in conversation* (PNAS, 2009). Negi, Rawat, Jain, [Evaluating Real-Time Voice Agents](https://arxiv.org/abs/2609.30798) (2026), and the companion [corpus and TRG validator](https://github.com/shivamnegi92/voice-agent-eval-corpus).
