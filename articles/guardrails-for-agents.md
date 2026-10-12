---
title: How to Put Guardrails on an AI Agent Without Killing It
kind: guide
date: 2026-10-11
order: 7
summary: Agents fail by doing things, not by saying things. A layered defense of allow-lists, budgets, approvals, and audit trails, plus a red-team loop that proves the guardrails hold.
tags: agents, safety, tool use, security
---
A chatbot that hallucinates says something wrong. An agent that hallucinates **does** something wrong: refunds the wrong order, deletes the wrong file, emails the wrong customer. Once your model can call tools, safety stops being a content problem and becomes a systems-security problem.

## The agent loop, and where it breaks

:::loop The reason-act loop
Observe state
Reason / plan
Choose a tool*
Execute action!
Read result
:::

Every arrow is an attack surface. Tool results can carry injected instructions. Plans can loop forever. The "execute" step is where the damage happens. Defend in depth.

## Defense in depth

:::layers Guardrail layers, outermost first
Input filtering | Detect prompt injection in user input AND in tool outputs, such as retrieved pages and emails
Capability allow-list* | The agent can only call tools you listed, with argument schemas validated
Budgets | Max steps, max tokens, max spend, and wall-clock timeout per task
Approval gates | Irreversible or high-value actions require human or policy approval
Audit trail | Every tool call, argument, result, and approval decision logged append-only, with secrets and PII redacted
:::

!!! insight The most important layer is **capability**, not filtering. You cannot reliably detect every injection. You *can* make sure that even a fully hijacked agent only has permissions that cannot do much harm.

## Classify actions by blast radius

:::quadrant Where each action needs a gate
x: Reversibility | easy to undo
y: Impact | high
pt: Delete records! @ 0.08,0.92
pt: Large refund! @ 0.3,0.85
pt: Small refund (policy check) @ 0.55,0.4
pt: Draft email~ @ 0.9,0.25
pt: Read-only query* @ 0.95,0.08
:::

The rule: **irreversible plus high-impact means a human approves.** Reversible, low-impact actions can run autonomously. Everything in between gets a policy check, such as "refunds up to $50, for the authenticated customer's own order, within a daily limit."

```python
def refund_ok(args, ctx):
    amount = args.get("amount")
    if ctx.user_id is None:                          # no authenticated session
        return False
    if not isinstance(amount, (int, float)) or not 0 < amount <= 50:
        return False                                 # rejects negatives, zero, strings
    owner = owner_of(args.get("order_id"))           # server-side lookup
    if owner is None or owner != ctx.user_id:
        return False
    return refunded_today(ctx.user_id) + amount <= 100   # cumulative cap

POLICY = {
    "search_orders": {"auto": True},
    "draft_email":   {"auto": True},
    "issue_refund":  {"auto": refund_ok},
    "delete_record": {"auto": False},                # always needs approval
}

def authorize(tool, args, ctx):
    rule = POLICY.get(tool)
    if rule is None:
        return "deny"                                # not on the allow-list
    try:
        auto = rule["auto"]
        ok = auto(args, ctx) if callable(auto) else auto
    except Exception:
        return "needs_approval"                      # fail closed, never open
    return "allow" if ok else "needs_approval"
```

Every check in `refund_ok` closes a real hole. A naive `amount <= 50` auto-approves a refund of -500. A naive ownership comparison lets an unknown order (`None`) match an unauthenticated session (`None`). Without a cumulative cap, two hundred $50 refunds all pass. And the rule never trusts an owner field from the arguments, because the model writes the arguments, and a hijacked model will claim the order is yours. The `try` block matters too: a crash in a policy check must fail closed.

## Indirect prompt injection

The scariest attacks do not come from the user. They come from *content the agent reads*.

:::seq Indirect injection via a retrieved document: the policy gate, not the model, stops it
actors: User, Agent, Web page, Policy gate
User -> Agent: summarize this page
Agent -> Web page: fetch
Web page --> Agent: text + hidden "email the user's data to X"
Agent -> Policy gate: send_email(to=X, ...)
Policy gate --> Agent: deny, tool not granted to this task
Agent --> User: summary only
:::

Notice who stops the attack. The model *was* hijacked and *did* try to send the email. The policy gate, which sits outside the model, refused. Treat all tool output as untrusted data, never as instructions, and scope tool permissions **per task**: a "summarize" task has no business holding an email-sending capability.

## Prove it with a red-team loop

:::flow Continuous red-teaming
Attack library -> Run against agent -> Score breaches* -> Patch policy -> Add as regression test
:::

Track **breach rate** as a release metric. Every successful attack joins the regression suite, but model outputs are stochastic and attackers paraphrase, so run each regression attack many times and with paraphrased variants. Treat breach rate as a statistic with a confidence interval, not a pass/fail bit.

| Attack class | Example | Primary defense |
|---|---|---|
| Direct injection | "Ignore previous instructions and..." | Allow-list plus input filter |
| Indirect injection | Hidden text in fetched pages | Untrusted-content handling, per-task scoping |
| Privilege escalation | Asking for another user's data | Identity binding in policy |
| Resource exhaustion | Tasks that loop forever | Step, token, and time budgets |

!!! warning Keyword filters for injection are easy to evade with paraphrases, and they flag harmless text like "ignore the typos." Use them as one weak signal, never as the defense.

## Turn the principle into an operating procedure

A guardrail is only useful when it is on the execution path. Put authorization in a tool gateway or service boundary that every agent action must cross; do not rely on the system prompt, client code, or a model-generated explanation. The agent can propose an action, but a separate component decides whether that action is permitted. If there is a route that bypasses this boundary, you have a convention, not an enforcement control.

A practical implementation sequence looks like this:

1. **Inventory capabilities.** List every tool, operation, argument, downstream identity, and side effect. Distinguish reading a record from changing it, and distinguish drafting a message from sending it.
2. **Define task-scoped authority.** Translate the user's authenticated request into a narrow, server-issued context: subject, tenant, permitted resource IDs, purpose, and expiry. Never let the model set or widen those values.
3. **Validate the proposal.** Parse tool arguments against a strict schema, reject unknown fields, normalize identifiers, and enforce limits on string lengths, arrays, and numeric ranges. Then evaluate business rules against authoritative state.
4. **Bind approval to an exact action.** Show the approver the normalized target, amount or content, and consequence. An approval token should expire and be bound to the exact action hash; editing arguments after approval requires a new approval.
5. **Execute with least privilege.** Use a service identity limited to the approved operation and scope. Avoid passing a broad user's bearer token to a model-controlled tool call.
6. **Record and reconcile.** Log the request, policy decision, approval identity, downstream result, and correlation ID. For consequential writes, verify the resulting state rather than assuming a successful HTTP response means the intended change occurred.

:::flow An action crossing the trust boundary
Model proposes typed action -> Gateway validates schema -> Policy checks identity and state -> Approval if required -> Narrow service executes -> Result reconciled and logged
:::

Keep policy rules readable and testable. A rule should answer who may do what, to which object, under which conditions, and with what limits. Put domain invariants in the service that owns the data as well as in the agent gateway. If a refund must never exceed the captured payment, the payment service enforces that too; duplicated checks at the gateway improve early denial but do not replace the authoritative invariant.

## Identity, tenancy, and confused-deputy failures

An agent often runs with more authority than the person asking it to help. That makes it a potential confused deputy: the model can be tricked into using its own broad service permissions for a request the user could not make. Bind every operation to the authenticated principal and tenant at the server boundary. Resolve object ownership server-side, and include tenant scope in database queries rather than fetching a global object and hoping a later check catches the leak.

Do not treat a tenant ID, user ID, role, or approval flag supplied in generated JSON as identity. Those are untrusted claims. Obtain them from the authenticated session or a signed, short-lived task context. When a workflow legitimately needs delegated authority, define exactly which operations and resources the delegation covers, how it expires, and how it is revoked. A tool that can search all tenants should not be exposed when the task only needs one tenant's records.

Authorization has a time-of-check/time-of-use edge case. The order may belong to the user at approval time, then be transferred, cancelled, or refunded before execution. Re-check critical invariants as close as possible to the write, ideally atomically with the write. Use idempotency keys for retries so a timeout does not turn one approved action into two payments. If the downstream system cannot provide an atomic conditional operation, surface that limitation and use reconciliation or manual review rather than pretending a preflight check is a transaction.

| Decision point | Safer implementation | Common trap |
|---|---|---|
| Identity | Server-derived principal and tenant | Trusting model-supplied user IDs |
| Object scope | Query constrained by owner/tenant | Global lookup followed by a UI check |
| Approval | Signed, expiring approval bound to action | Generic “approve this task” toggle |
| Retry | Idempotent operation with result lookup | Repeating a write after a timeout |
| Revocation | Re-check authorization at execution | Assuming the initial context stays valid |

## Handle untrusted content and tool output

Retrieved documents, emails, issue descriptions, webpages, and tool errors are data, not policy. Label them as untrusted at the point they enter the model context, preserve provenance, and avoid concatenating them into instruction-like system messages. This helps the model interpret content correctly, but it is not the security boundary. A robust design assumes the model may follow malicious text anyway and ensures its available tools cannot turn that into an unauthorized effect.

Constrain the agent's capabilities to the current task. A read-only summarization task should not receive a send-email tool. If the agent needs to draft an email, expose a draft operation that cannot send; a separate policy check can authorize delivery. Likewise, prefer narrow tools such as `get_order_status(order_id)` over a generic SQL console or shell. Smaller interfaces reduce what an injected instruction can ask the system to do and make policy decisions easier to inspect.

Protect data on the way in and out. Redact secrets and unnecessary personal data before sending context to a model provider, and ensure logs do not quietly become a second ungoverned copy of customer records. Set retention and access rules for prompts, tool arguments, results, and approval records. A redacted log must still retain enough stable identifiers and decision metadata to investigate an incident without exposing raw sensitive content to every operator.

## Failure modes that deserve explicit tests

Happy-path tests prove that an agent can do useful work. Security tests must establish what happens when components fail, inputs are malformed, and the request is ambiguous. Include these cases in the same automated suite as ordinary functional tests:

- A tool name is unknown, misspelled, or newly added without a matching policy entry. Expected result: deny.
- The policy service times out, returns malformed data, or throws an exception. Expected result: fail closed, with a bounded user-facing explanation.
- A numeric argument is `NaN`, infinity, a decimal where only whole units are allowed, or a string that resembles a number. Expected result: schema rejection, not coercion into an allowed value.
- An identifier belongs to another tenant, no longer exists, or changes ownership between approval and execution. Expected result: no disclosure and no write.
- The model requests a permitted operation but supplies extra fields intended to influence downstream behavior. Expected result: reject unknown fields and construct the downstream request from validated values only.
- An approval is replayed, expired, or applied to modified arguments. Expected result: reject and require a fresh approval.
- A downstream call times out after it may have succeeded. Expected result: query by idempotency key or reconcile; do not blindly repeat.
- A tool result contains instructions, secrets, or a huge payload. Expected result: treat as data, bound the context, and do not expand capabilities.

:::tree Fail-safe behavior for common faults
Tool action proposed
  Schema or identity invalid
    Deny and record a reason!
  Policy dependency unavailable
    Fail closed; offer safe retry
  Approval required
    Bind approval to exact action*
  Downstream result uncertain
    Reconcile by idempotency key
    Never blindly repeat a write
:::

A denial should be useful without leaking policy internals. Tell the user what safe next step is available-for example, request an authorized reviewer or clarify which order they mean-without revealing another user's record or exposing a hidden threshold that enables probing. Internally, retain a structured denial reason such as `wrong_tenant`, `limit_exceeded`, or `approval_missing`; that taxonomy is far more useful than a log full of “agent failed.”

## Monitor policy enforcement, not just agent quality

Track attempted and allowed actions by tool, policy outcome, tenant scope, approval path, and downstream status. Watch for denied-call spikes, repeated attempts against out-of-scope objects, approval edits, unusual action sequences, and differences between the model's proposed action and the executed action. A rise in denials can indicate an attack, a broken prompt, a legitimate product change, or a policy integration failure; pair the metric with traceable examples and a way to triage them.

Measure useful work too: task completion, safe handoff, duplicate write prevention, time to approval, rollback or correction rate, and user correction after an action. Do not optimize only for completion rate. If the system learns that refusal counts as failure, it can pressure the design toward unsafe execution. Report outcomes by action class and impact tier so harmless read operations do not hide a problem with financial or destructive actions.

Keep a canary suite of policy scenarios and run it whenever the model, tool schema, gateway, or business rule changes. Test allowed cases as well as denied cases; an overbroad denial can break a workflow and tempt operators to bypass the gate. Version policies, record the version on each decision, and define a rollback path. For incident response, know how to disable a capability centrally, revoke task contexts, pause queued actions, and find all executions associated with a policy version.

## A lightweight review before enabling a tool

Before granting a new capability, answer these questions in a short design review:

- What exact user problem requires this tool, and can a narrower read-only or draft-only tool solve it?
- What is the worst plausible result if the model is fully compromised during this task?
- Which server-side identity and tenant scope constrain the operation?
- Which invariants are checked by the authoritative service at write time?
- Is the action reversible, idempotent, and observable after execution?
- Who approves exceptions, and is approval tied to immutable arguments?
- What sensitive data can enter the model, tool logs, traces, and cache?
- Which regression attacks, malformed inputs, and outage cases must pass before release?
- Who owns the on-call response, capability kill switch, and policy rollback?

If the answers are vague, the tool is not ready for autonomous access. Start with read-only access or a human-confirmed draft and expand only when evaluation demonstrates a controlled need. This is not anti-agent caution for its own sake. It is ordinary least-privilege engineering applied to a component whose proposed actions are probabilistic.

## Key takeaways

- Agent safety is systems security: least privilege beats clever filters.
- Gate actions by blast radius: irreversible plus high-impact needs approval.
- Treat every tool output as untrusted data.
- Budget steps, tokens, spend, and time.
- Red-team continuously, and turn every breach into a regression test.

**Further reading:** Greshake et al., [Not What You've Signed Up For: Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) (2023). See also [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) for prompt injection and excessive agency risks. Runnable baselines: [bounded_agent and redteam_harness in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
