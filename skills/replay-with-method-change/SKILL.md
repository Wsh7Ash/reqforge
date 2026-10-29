---
name: replay-with-method-change
description: "Swap the verb on a captured request to test whether method-based authorization is consistently applied. Use when a route is protected for reads and the hypothesis is that writes are checked differently"
pack: reqforge
version: 1.0.0
category: networking
tags: [replay, methods, authorization]
---

# Replay With Method Change

> Swap the verb on a captured request to test whether method-based authorization is consistently applied

**Use when:** a route is protected for reads and the hypothesis is that writes are checked differently

**Avoid when:** the route is read-only by design and any write verb is rejected by the framework itself

## Procedure

1. Capture the working request for the least privileged role first
2. Replay the same target with each of GET, POST, PUT, PATCH and DELETE
3. Keep headers and body identical so the verb is the only change
4. Record which verbs reach a handler and which are rejected by an edge layer
5. For any accepted write verb, verify from the owner's view whether state changed
6. Restore any state you changed, then record the restore request as proof

## Signals

- DELETE succeeds for a role that cannot read the object
- PUT returns 405 from the edge while POST reaches the handler
- a method override header changes which verb the handler executes
- the object state changed after a write only the owner should allow

## Patterns

**1. Verb sweep**

```text
GET, POST, PUT, PATCH, DELETE on the same target
```

**2. Override probe**

```text
POST with X-HTTP-Method-Override: DELETE
```

**3. State restore**

```text
recreate the object and capture the restore response
```

## Pitfalls

- Changing the body with the verb and losing the single-cause comparison
- Leaving test objects deleted and breaking the account for later tests
- Concluding a 405 is a security control when it is only routing

## Done when

- each verb has a capture with the same headers and body
- any state change is verified and then restored with a captured request

## References

- [RFC 9110 - method definitions](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP - function level authorization](https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/)
