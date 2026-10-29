---
name: timing-delta-interpretation
description: "Read elapsed time as a coarse signal and never as proof, because latency varies far more than most tests assume. Use when a differential in response time suggests a check is skipped on one path"
pack: reqforge
version: 1.0.0
category: networking
tags: [compare, timing, statistics]
---

# Timing Delta Interpretation

> Read elapsed time as a coarse signal and never as proof, because latency varies far more than most tests assume

**Use when:** a differential in response time suggests a check is skipped on one path

**Avoid when:** the timing difference is under a few hundred milliseconds on a remote host

## Procedure

1. Sample each variant at least ten times and keep every measurement
2. Compare medians rather than single values
3. Check the spread before claiming a difference, since overlap destroys the claim
4. Repeat from a second network path if the difference is small
5. Treat a timing result as a lead and confirm it with an observable effect
6. Record the sample size with any timing statement in the report

## Signals

- medians differ by an order of magnitude with no overlap in ranges
- one path consistently takes a fixed extra step such as a database lookup
- variance collapses when the difference is real and widens when it is noise
- a second path reproduces the same gap, strengthening the claim

## Patterns

**1. Ten-sample median**

```text
median 42ms versus 890ms with n=12 each
```

**2. Range check**

```text
ranges overlap -> not yet a signal
```

**3. Confirm with effect**

```text
timing lead then verified via a returned data field
```

## Pitfalls

- Reporting a timing difference from a single request against a remote host
- Ignoring connection reuse, which makes the first request look much slower
- Claiming a user enumeration oracle from timing alone without a content signal

## Done when

- each timing claim states the sample size and the medians compared
- a non-timing observation confirms the timing lead

## References

- [OWASP - timing attacks](https://owasp.org/www-community/attacks/Timing_attack)
- [Python - perf_counter](https://docs.python.org/3/library/time.html#time.perf_counter)
