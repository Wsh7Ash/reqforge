---
name: replay-after-state-change
description: "Replay the original request after the owner removes access to prove that revocation actually took effect. Use when a sharing or delegation feature must be checked for stale permissions after revoke"
pack: reqforge
version: 1.0.0
category: networking
tags: [replay, revocation, verification]
---

# Replay After State Change

> Replay the original request after the owner removes access to prove that revocation actually took effect

**Use when:** a sharing or delegation feature must be checked for stale permissions after revoke

**Avoid when:** the finding is a missing check on creation rather than a revocation failure

## Procedure

1. Capture the successful access as the pre-change baseline
2. Perform the revocation through the product's own interface and capture that request
3. Replay the baseline request unchanged and record the response
4. Replay from a fresh session to rule out cached credentials
5. Replay again after a short wait to catch eventual-consistency windows
6. Report the window during which access survived revocation, with timestamps

## Signals

- the baseline request still returns the shared data after revocation
- access fails only after the cache expires, revealing a stale window
- a fresh session denies immediately while the old session still succeeds
- the revoke endpoint returns 200 but the object remains readable

## Patterns

**1. Baseline then revoke**

```text
pre-change 200 -> revoke 204 -> replay 200 (bug)
```

**2. Fresh session check**

```text
new cookie jar, same credential, same path
```

**3. Stale window**

```text
revoked at 10:01:12, denied at 10:06:40
```

## Pitfalls

- Concluding revocation failed while the old session token is still valid by design
- Testing only after a cache flush and missing the exploitable window entirely
- Leaving the revocation until after the report so the state cannot be retested

## Done when

- pre-change, revoke and post-change captures all exist with timestamps
- the stale window is measured or explicitly ruled out

## References

- [OWASP - session management](https://cheatsheetseries.owasp.org/)
- [RFC 6749 - token revocation](https://www.rfc-editor.org/rfc/rfc7009.html)
