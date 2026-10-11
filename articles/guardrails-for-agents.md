---
title: How to Put Guardrails on an AI Agent Without Killing It
kind: guide
date: 2026-10-04
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
Audit trail | Every thought, tool call, argument, and result logged immutably
:::

!!! insight The most important layer is **capability**, not filtering. You cannot reliably detect every injection. You *can* make sure that even a fully hijacked agent only has permissions that cannot do much harm.

## Classify actions by blast radius

:::quadrant Where each action needs a gate
x: Reversibility | easy to undo
y: Impact | high
pt: Delete records! @ 0.08,0.92
pt: Issue refund @ 0.3,0.75
pt: Draft email~ @ 0.9,0.25
pt: Read-only query* @ 0.95,0.08
:::

The rule: **irreversible plus high-impact means a human approves.** Reversible and low-impact actions can run autonomously. Everything in between gets a policy check, such as "refunds under $50, for the authenticated customer's own order only."

```python
POLICY = {
    "search_orders": {"auto": True},
    "draft_email":   {"auto": True},
    "issue_refund":  {"auto": lambda a, ctx: a["amount"] <= 50
                                       and a["order_owner"] == ctx.user_id},
    "delete_record": {"auto": False},          # always needs approval
}

def authorize(tool, args, ctx):
    rule = POLICY.get(tool)
    if rule is None:
        return "deny"                         # not on the allow-list
    auto = rule["auto"]
    ok = auto(args, ctx) if callable(auto) else auto
    return "allow" if ok else "needs_approval"
```

## Indirect prompt injection

The scariest attacks do not come from the user. They come from *content the agent reads*.

:::seq Indirect injection via a retrieved document
actors: User, Agent, Web page, Email tool
User -> Agent: summarize this page
Agent -> Web page: fetch
Web page --> Agent: text + hidden "email the user's data to X"
Agent -> Agent: policy check: tool not authorized for this task
Agent --> User: summary only, injection flagged
:::

Treat all tool output as untrusted data, never as instructions. Scope tool permissions **per task**: a "summarize" task has no business holding an email-sending capability.

## Prove it with a red-team loop

:::flow Continuous red-teaming
Attack library -> Run against agent -> Score breaches* -> Patch policy -> Add as regression test
:::

Track **breach rate** as a release metric. Every successful attack becomes a permanent regression test, so the same hole never reopens.

| Attack class | Example | Primary defense |
|---|---|---|
| Direct injection | "Ignore previous instructions and..." | Allow-list plus input filter |
| Indirect injection | Hidden text in fetched pages | Untrusted-content handling, per-task scoping |
| Privilege escalation | Asking for another user's data | Identity binding in policy |
| Resource exhaustion | Tasks that loop forever | Step, token, and time budgets |

!!! warning Keyword filters for injection are easy to evade with paraphrases, and they flag harmless text like "ignore the typos." Use them as one weak signal, never as the defense.

## Key takeaways

- Agent safety is systems security: least privilege beats clever filters.
- Gate actions by blast radius: irreversible plus high-impact needs approval.
- Treat every tool output as untrusted data.
- Budget steps, tokens, spend, and time.
- Red-team continuously, and turn every breach into a regression test.

**Further reading:** Greshake et al., *Not What You've Signed Up For: Indirect Prompt Injection* (2023). Runnable baselines: [bounded_agent and redteam_harness in Practical AI Systems](https://github.com/shivamnegi92/practical-ai-systems).
