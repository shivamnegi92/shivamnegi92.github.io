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

## Define latency before optimizing it

“Time to response” is not one clock. A useful report names each event boundary and captures timestamps from a monotonic clock on the relevant host. At minimum, distinguish user speech start, end-of-turn decision, first transcript hypothesis, finalized transcript, first model token, first synthesized audio, first audio rendered to the user, and end of the agent turn. Network clocks on separate services may not be synchronized; propagate trace identifiers and use durations measured locally, or account for clock skew explicitly. Do not subtract unrelated wall clocks and call the result precise.

Report distributions by stage and end-to-end, with sample count and test conditions. The mean can hide a long tail that makes some callers wait painfully; percentiles can also be unstable with too few observations, so include counts and confidence where practical. Break out cold starts, language, device, network class, interruption, and load when these are material. The examples in this guide are design illustrations, not measured claims or universal thresholds. Human turn gaps vary by context, culture, task, and speaker; Stivers et al. observed cross-cultural regularities, not a single deadline every agent must meet.

:::flow Clock anchors for a voice turn
User begins speaking -> Partial transcript available -> End-of-turn committed -> First model token -> First synthesized frame -> First audio rendered -> User or agent turn ends
:::

A first-audio metric should stop when audio is actually available to the user’s playback path, not when the TTS server returns bytes. A service can have fast model time-to-first-token and still feel slow because the endpoint waits for a full sentence, audio encoding, buffering, or a congested connection. Conversely, speculative speech can reduce perceived delay while increasing the risk of speaking on a transcript that later changes. Measure both system latency and behavioral correctness.

## Build a budget around critical path

The additive budget in the earlier example is a conservative serial illustration. A streaming pipeline has overlap, so end-to-end latency is governed by the critical path, not by blindly summing every stage duration. Draw the dependency graph: ASR may produce partial text while the user speaks; the model can begin after a stable prefix; TTS can start once a complete phrase is available. But each overlap creates a correctness obligation: speculative work must be canceled or corrected if later input changes the interpretation.

:::seq A speculative response with a correction point
actors: User, ASR, Agent, TTS
User -> ASR: utterance frames
ASR -> Agent: stable partial transcript
Agent -> TTS: provisional phrase
ASR -> Agent: final transcript changed meaning
Agent -> TTS: cancel provisional audio
Agent -> User: clarify or restart safely
:::

Budget separately for endpointing, ASR, reasoning/tool work, TTS, transport, and playback. Put deadlines on each stage so one stalled provider cannot consume the entire turn. Reserve time for validation, safety checks, and audio buffering rather than spending the whole budget on generation. Use streaming only when partial output is safe to expose; for financial, medical, or other consequential tasks, the correct design may wait for verification even if that feels slower. Latency is a product trade-off, not permission to guess.

## Engineer endpointing and turn-taking

Voice activity detection answers whether speech-like audio is present; endpointing answers whether the user has finished a turn. They are related but distinct. A user may pause between clauses, speak softly, or have background noise. A fixed silence timer is easy to build and can be a useful baseline, but test it across pauses, trailing fricatives, short acknowledgments, and speech in noisy environments. Record premature cutoffs and unnecessary waits separately, because lowering one can worsen the other.

A robust policy can combine acoustic evidence, transcript completeness, dialogue context, and a bounded wait. For example, after a question that expects a short yes/no, a brief pause may be enough; during a long dictated address, the agent may need a longer pause or an explicit “done” signal. This is illustrative behavior, not a universal timing value. Let the user resume naturally during the wait, and make the state machine cancel pending generation when new speech arrives.

:::tree Endpointing state machine
Listening
  Speech detected
    Stream partial transcript
  Possible pause
    Content complete and confidence adequate?
      Yes: commit turn after policy wait
      No: continue listening within maximum bound
  New speech during wait
    Cancel pending response and continue turn
  Maximum bound reached
    Ask a short clarification or hand off safely
:::

Track false endpoint rate, late endpoint rate, user repeat rate, interruption recovery, and the share of turns where the agent begins speaking before transcript finalization. Sample audio under privacy controls for human review; transcript-only review cannot reveal clipped phonemes, overlap, or prosodic cues. Handle multilingual code-switching, names, numbers, and disfluencies explicitly. A partial transcript can reverse a negation or amount, so do not launch an irreversible tool action from unstable text.

## Barge-in is a conversation-state problem

Barge-in needs more than stopping playback when microphone energy rises. Distinguish a genuine interruption from backchannels (“mm-hmm”), echo from the agent’s own speaker, coughs, and environmental noise. Use echo cancellation and a speech detector, then interpret the event in context. When a genuine interruption is detected, stop outgoing audio promptly, preserve the conversation state, mark what the user heard if possible, and resume from the corrected request rather than replaying a stale response.

A poor barge-in policy has two visible modes: **false stop**, where a cough or acknowledgment silences the agent, and **missed interruption**, where the agent talks over a correction. Evaluate both with labeled clips and real conversational tests. Measure detection delay from interruption onset, stop-to-silence delay, false-stop rate, missed-interruption rate, and recovery success. Report performance by playback device and acoustic environment; speakerphone echo and headphones are not equivalent. Provide a user control or clear phrase for stopping the agent when automatic detection fails.

## TRG: report the behavior, not just the waveform

The proposed TRG framing uses **T (Timing), R (Recovery), and G (Grounded outcome)**, with **M (Multiparty)** as a conditional extension when several participants are legitimate. These are distinct axes: T concerns timing and whether speaking was appropriate at that moment; R concerns recovery after disruption; G concerns whether an authorized external outcome occurred, including a justified no-action. M asks whether the system appropriately speaks or stays silent among multiple participants. Disclose language, accent, noise, speaker, load, and evaluation conditions alongside results; these are conditions, not extra axes. See the [TRG proposal](https://arxiv.org/abs/2609.30798) and its [corpus and validator](https://github.com/shivamnegi92/voice-agent-eval-corpus) for the described framework.

:::compare What an evaluation should separate
# T: Timing
- Name start and stop clock anchors
- Report distribution and sample count
- Score appropriate silence as well as timely speech
# R and G (M when applicable)
- Test recovery after interruption or tool failure
- Verify authorized external state, not spoken claims
- Evaluate multiparty turn allocation when in scope
:::

A voice agent that says “I sent the payment” has not achieved a grounded outcome unless the authorized payment state confirms it. Conversely, refusing to act because authorization is missing can be the correct G outcome. Pair automatic timestamps and state checks with human review of conversational appropriateness. A transcript score alone cannot capture whether the agent interrupted, ignored a correction, or spoke at an awkward moment.

## Reproducible evaluation and operations

Build a test matrix with clean speech, realistic noise, varied speaking rates, accents and languages in scope, short and long pauses, overlap, corrections, numbers, names, and backchannels. Include tool success, tool timeout, malformed result, authorization denial, and partial failure. Keep a fixed regression suite for comparisons and a separate rotating set to reduce overfitting. Store provenance and consent for audio; minimize retention, redact where possible, and restrict access. Do not treat a benchmark corpus as representative of every deployment population.

Run scripted tests first, then supervised end-to-end trials on the actual devices and network path. Test cold starts and sustained load, and record provider/runtime versions. Compare cascaded, end-to-end, or hybrid architectures on the same task and conditions, including failure recovery and ability to inspect intermediate state. An end-to-end model may simplify the critical path, but its internal behavior can be harder to diagnose; a cascaded stack may improve observability while adding handoffs and failure modes. Neither architecture is inherently lower latency in every configuration.

Operational dashboards should show per-stage latency distributions, timeouts, endpointing errors, ASR revisions, canceled speculative work, TTS failures, barge-in outcomes, tool verification, handoffs, and completed tasks. Segment by relevant condition while enforcing privacy and minimum-count protections. Alert on regressions against service objectives and investigate whether the cause is model time, queueing, provider, network, or playback. Preserve a safe fallback such as asking the user to repeat, switching to text, or handing off; a graceful failure beats fabricated certainty.

## A practical implementation sequence

First instrument the existing system and establish clock anchors; do not optimize from anecdotes or a single average. Next, label a modest set of turns for endpointing, interruptions, recovery, and task outcome. Draw the critical path and identify the dominant controllable delay. Implement streaming or overlap behind a feature flag, with cancellation when transcripts change. Add explicit timeouts, a recoverable dialogue state, and safeguards that prevent unstable partial input from triggering side effects. Finally, evaluate on the same fixed tests and a fresh holdout, canary the full pipeline, and monitor both timing and grounded outcomes.

A useful review exercise is to take one bad turn and answer: When did the user stop? Which clock started the latency measurement? What evidence allowed endpointing? What did the user hear? Did the system stop on interruption? Did the external action actually occur? What safe recovery was available? If the logs cannot answer those questions, the next engineering task is observability, not a new model.

## Latency optimization without breaking trust

Prioritize the stage on the measured critical path, then make one change and rerun the same evaluation. If endpointing dominates, test contextual endpointing and resumable listening before replacing the language model. If first-token time dominates, reduce unnecessary context, pre-warm safely, or evaluate a smaller model on the same task. If TTS dominates, stream phrase-sized chunks and avoid waiting for the full response. If transport dominates, inspect packetization, buffering, and network geography. These are hypotheses to test, not guarantees that a particular product change reduces latency.

Be cautious with speculative generation. Starting from partial ASR can make the response feel quicker, but revisions may invalidate a name, negation, quantity, or user intent. Use a stability criterion appropriate to the action, cancel promptly on a changed transcript, and do not emit consequential claims or trigger tools until the relevant input is final and authorized. For low-risk conversational acknowledgments, a provisional response may be acceptable if it is clearly recoverable. Make the policy visible in logs so the team can quantify canceled work and user-visible corrections.

A cache can reduce repeat computation for safe, deterministic content, but voice requests are often contextual and personal. Do not reuse responses across users or sessions without a well-defined privacy and correctness boundary. Similarly, prefetching a likely tool result can save time only if authorization and data freshness remain valid. A fast stale answer is not an improvement. Include privacy, retention, and authorization checks in the latency design review rather than bolting them on after optimization.

## Failure recovery and conversation state

Represent each call as an explicit state machine: listening, endpointing, interpreting, acting, speaking, interrupted, recovering, or handed off. Store only the state needed to resume the task, with appropriate access and retention controls. When a user interrupts, record the last confirmed intent and which portion of the answer was played; do not assume that generated audio was heard in full. After a network or tool failure, explain what is known, what is not known, and whether an action might have completed. Never retry a non-idempotent action blindly because the spoken confirmation was lost.

:::tree Recover after an interrupted action
User interrupts or connection fails
  Was an external action requested?
    No: retain context and ask what the user wants next
    Yes: query authorized external state
      Action confirmed complete: explain and continue
      Action confirmed absent: offer a safe retry
      State unknown: disclose uncertainty and hand off or verify
:::

Test recovery with interruptions before, during, and after tool execution; with duplicated audio frames; and with a delayed tool response arriving after the user has changed their mind. Use idempotency keys for actions that may be retried and a cancellation policy for work that is no longer relevant. A cancellation request may not undo an action already committed, so the interface should distinguish stopping speech from canceling the underlying operation.

## Product and safety trade-offs

A voice system has to decide not only how quickly it can speak, but whether it should speak at all. A brief silence can be better than confidently interrupting a user or announcing an unverified result. Define which actions require confirmation, what identity or permission checks are necessary, and what the agent may do autonomously. Keep those controls independent of latency optimization. Faster generation must not bypass safety review, grounding, or user consent.

Consider the human factors of recovery: can a caller tell whether the agent is listening, thinking, or disconnected? Can they interrupt without repeating everything? Can they request a human or switch to text? A small, well-timed status cue may prevent repeated speech that otherwise creates duplicate actions. Test these affordances with users who rely on different devices and speaking styles; assumptions based on one microphone and one accent can fail badly elsewhere.

## A review checklist for a voice-agent release

- Are start and stop clocks defined, monotonic, and traceable across the service?
- Are stage and end-to-end latency distributions reported with sample counts and test conditions?
- Does the endpointing policy distinguish pauses, backchannels, and actual turn completion?
- Can new speech cancel stale provisional generation before it causes a side effect?
- Do barge-in tests cover echo, coughs, overlap, delayed stop, and task-state recovery?
- Are external actions authorized, idempotent where possible, and verified from system state?
- Are timeout, provider outage, and unknown-action outcomes safe and understandable?
- Are audio samples, transcripts, and trace logs governed by minimization and retention rules?
- Does the evaluation separately report T, R, G, and conditional M, with conditions disclosed?
- Can the deployed version be rolled back without losing the conversation’s safe recovery path?

A release review should include a few complete conversation traces, not just isolated model outputs. Look for the moments where the user hesitates, corrects a word, talks over the agent, or expects silence. These are where timing, recovery, and grounding meet-and where an otherwise impressive benchmark can fail to represent actual use.

## Key takeaways

- In voice, timing is part of correctness.
- Budget latency per stage, then overlap stages with streaming.
- Predict turn ends from acoustics and semantics, not silence alone.
- Tune barge-in as a classifier that balances sensitivity and selectivity.
- Evaluate timing, recovery, and grounded outcomes together.

**Further reading:** Stivers et al., *Universals and cultural variation in turn-taking in conversation* (PNAS, 2009). Negi, Rawat, Jain, [Evaluating Real-Time Voice Agents](https://arxiv.org/abs/2609.30798) (2026), and the companion [corpus and TRG validator](https://github.com/shivamnegi92/voice-agent-eval-corpus).
