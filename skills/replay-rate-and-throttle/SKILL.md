---
name: replay-rate-and-throttle
description: "Pace replays so rate limiting is a measured property rather than an accident of a tight loop. Use when a test needs many attempts but the target enforces quotas that could mask the result"
pack: reqforge
version: 1.0.0
category: networking
tags: [replay, rate-limit, pacing]
---

# Replay Rate and Throttle

> Pace replays so rate limiting is a measured property rather than an accident of a tight loop

**Use when:** a test needs many attempts but the target enforces quotas that could mask the result

**Avoid when:** the objective is explicitly to test the limiter itself, which needs an unbounded burst

## Procedure

1. Send a small pilot batch to observe whether any limiter headers appear
2. Record Retry-After, X-RateLimit and equivalent headers if present
3. Choose a delay that keeps the run under the observed limit or deliberately exceeds it
4. Keep the delay constant so timing effects are interpretable
5. Record the attempt index at which any 429 first appeared
6. State clearly whether the limiter was respected or intentionally probed

## Signals

- 429 responses begin at a consistent attempt index
- Retry-After values appear only after the first rejection
- identical requests succeed again after the stated window elapses
- the limiter keys on credential rather than address when two tokens behave differently

## Patterns

**1. Fixed pacing**

```text
delay_ms=250 between attempts
```

**2. Limiter header capture**

```text
x-ratelimit-remaining: 3, Retry-After: 30
```

**3. First rejection index**

```text
first_429_at_attempt=12
```

## Pitfalls

- Running an unpaced loop and then reporting a 429 as an access control failure
- Ignoring that limiter state persists across sessions and skewing the next test
- Pacing so slowly that a time-based expiry makes results non-comparable

## Done when

- the pacing used is recorded with the run
- any rejection is reported with the attempt index and window observed

## References

- [RFC 6585 - 429 Too Many Requests](https://www.rfc-editor.org/rfc/rfc6585.html)
- [OWASP - brute force](https://owasp.org/www-community/attacks/Brute_force_attack)
