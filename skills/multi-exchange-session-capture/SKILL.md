---
name: multi-exchange-session-capture
description: "Capture a sequence of dependent requests as one ordered transcript so state changes are visible in context. Use when a bug only appears across a sequence such as create, read, share then read as another user"
pack: reqforge
version: 1.0.0
category: networking
tags: [capture, state, sequence]
---

# Multi Exchange Session Capture

> Capture a sequence of dependent requests as one ordered transcript so state changes are visible in context

**Use when:** a bug only appears across a sequence such as create, read, share then read as another user

**Avoid when:** the behaviour is fully reproducible from a single isolated request

## Procedure

1. Define the minimal sequence that demonstrates the state transition
2. Send each step as its own capture and keep a monotonic sequence number
3. Record values passed between steps, such as identifiers returned by the create call
4. Note where the session cookie or token changed between steps
5. Verify the sequence from a clean session so leftover state cannot explain the result
6. Store the whole transcript as an ordered list so a reviewer reads it like a script

## Signals

- an object created in step one is readable by another role in step four
- the session identifier rotates at exactly one step, marking the auth boundary
- a later step succeeds only because an earlier one primed server state
- repeating the sequence from a clean session reproduces the same outcome

## Patterns

**1. Sequence numbers**

```text
01-create.json, 02-read.json, 03-share.json, 04-read-as-other.json
```

**2. Value handoff**

```text
order_id=8812 taken from the step 01 response
```

**3. State reset**

```text
clear cookie jar, then replay steps 01-04 to confirm
```

## Pitfalls

- Running steps out of order and drawing conclusions from an impossible state
- Leaving cookies from a previous run in the client so isolation is unproven
- Compressing the sequence into one request that no longer demonstrates the transition

## Done when

- the transcript reproduces the outcome from a clean session
- each step records the values it received from the previous step

## References

- [OWASP WSTG - business logic](https://owasp.org/www-project-web-security-testing-guide/)
- [RFC 6265 - cookies](https://www.rfc-editor.org/rfc/rfc6265.html)
