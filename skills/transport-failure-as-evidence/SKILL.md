---
name: transport-failure-as-evidence
description: "Store connection failures and resets as structured evidence instead of discarding them as noise. Use when a request that should succeed is closed, reset or times out in a way that suggests filtering"
pack: reqforge
version: 1.0.0
category: networking
tags: [capture, errors, reliability]
---

# Transport Failure as Evidence

> Store connection failures and resets as structured evidence instead of discarding them as noise

**Use when:** a request that should succeed is closed, reset or times out in a way that suggests filtering

**Avoid when:** the failure is a typo in host or port that your own naming check would catch

## Procedure

1. Wrap the whole exchange so any transport error is converted into a record, not an exception
2. Record the phase that failed: resolve, connect, tls, write, read head or read body
3. Record the exact error text and the elapsed time up to the failure
4. Retry once to distinguish a one-off reset from a reproducible block
5. Compare against the same request through a different path to locate the filtering point
6. Keep the failed record in the same capture set as successes so the contrast is visible

## Signals

- connection reset immediately after a specific header or payload size
- the same request succeeds over HTTP but resets over HTTPS, naming a TLS-era filter
- a timeout consistently follows a body above a fixed size
- a proxy returns 502 where the origin returns 200 directly

## Patterns

**1. Phased failure record**

```text
phase=read_body error=connection reset elapsed_ms=812
```

**2. Contrast capture**

```text
direct 200 | through-proxy 502 with the same request bytes
```

**3. One retry only**

```text
attempt=1 reset, attempt=2 reset -> reproducible
```

## Pitfalls

- Swallowing the exception and reporting a clean run that never happened
- Calling any reset a WAF block without a working control request
- Retrying repeatedly until rate limits create the failure you are investigating

## Done when

- every failed exchange is stored with its phase, error text and timing
- reproducibility is stated as one-off or consistent with evidence

## References

- [OWASP - WAF bypass testing](https://owasp.org/www-project-web-security-testing-guide/)
- [Python - socket errors](https://docs.python.org/3/library/socket.html#exceptions)
