---
name: idempotent-replay-determinism
description: "Replay the same request repeatedly to separate a stable server behaviour from a flaky observation. Use when a status or body changed once and it is unclear whether the target is non-deterministic"
pack: reqforge
version: 1.0.0
category: networking
tags: [replay, determinism, verification]
---

# Idempotent Replay Determinism

> Replay the same request repeatedly to separate a stable server behaviour from a flaky observation

**Use when:** a status or body changed once and it is unclear whether the target is non-deterministic

**Avoid when:** the request mutates state on every call and repeated sends would create noise or damage

## Procedure

1. Pick a read-only request so repetition cannot change the object under test
2. Send it three to five times in a row with no edits between attempts
3. Compare status codes, body digests and byte lengths across attempts
4. Report the number of distinct outcomes rather than a single sample
5. If outcomes differ, look for load-balancer hints such as different server headers
6. Re-run the sample from a second source address to see whether the difference is routing-based

## Signals

- distinct status codes across identical requests indicate a pool of backends
- different ETag or request-id headers per attempt reveal which node answered
- a stable digest across attempts makes a later change clearly attributable
- one outlier followed by consistent results suggests a transient, not a defect

## Patterns

**1. Five-shot sample**

```text
count=5 statuses={200} bodies=1 stable=true
```

**2. Backend fingerprint**

```text
x-served-by: node-3 on attempt 2 only
```

**3. Variance summary**

```text
distinct_statuses=[200,403] distinct_bodies=2
```

## Pitfalls

- Replaying a POST that creates a record each time and mistaking duplicates for a bug
- Reporting the first observation as a finding before checking variance
- Ignoring that caching legitimately stabilises results after the first attempt

## Done when

- a stability statement exists with the number of attempts and distinct outcomes
- any difference is attributed to a named source such as a backend pool

## References

- [RFC 9110 - idempotent methods](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP - race conditions](https://owasp.org/www-community/vulnerabilities/)
