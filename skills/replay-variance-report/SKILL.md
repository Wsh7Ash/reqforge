---
name: replay-variance-report
description: "Summarise repeated sends as counts of distinct outcomes so a claim of instability is quantified. Use when a race condition or a backend pool is suspected and single observations are unconvincing"
pack: reqforge
version: 1.0.0
category: networking
tags: [replay, statistics, evidence]
---

# Replay Variance Report

> Summarise repeated sends as counts of distinct outcomes so a claim of instability is quantified

**Use when:** a race condition or a backend pool is suspected and single observations are unconvincing

**Avoid when:** a single deterministic request already proves the finding

## Procedure

1. Choose the attempt count before running so the sample is not tuned after the fact
2. Capture status, body digest and byte length for every attempt
3. Group attempts by outcome and count each group
4. Report the counts, not just the presence of a different outcome
5. Include timing per attempt so a slow outlier is visible
6. State the confidence plainly: a single outlier in twenty is weak evidence

## Signals

- two distinct digests with an uneven split suggests a race window
- an even split across two backends indicates a load-balancer pool
- identical digests across all attempts make a change fully attributable
- timing spikes correlate with one of the observed outcomes

## Patterns

**1. Counts by outcome**

```text
200:18 500:2 digests=2 timing_p95=940ms
```

**2. Pre-declared sample**

```text
attempts=20 declared before the run
```

**3. Weak evidence note**

```text
one outlier in twenty is not yet a reproducible race
```

## Pitfalls

- Increasing attempts until an outlier appears and calling the result reproducible
- Hiding the failed attempts and reporting only the interesting ones
- Reporting variance without digests, so two different bodies look identical

## Done when

- the attempt count and outcome distribution are recorded
- the strength of the evidence is stated honestly in the notes

## References

- [OWASP - race conditions](https://owasp.org/www-community/vulnerabilities/)
- [NIST - statistical testing guidance](https://csrc.nist.gov/)
