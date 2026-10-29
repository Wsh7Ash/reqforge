---
name: connect-timeout-discipline
description: "Bound every connection attempt so a filtered port costs seconds instead of stalling an entire test run. Use when a script sends many requests across hosts where some ports silently drop packets"
pack: reqforge
version: 1.0.0
category: networking
tags: [transmit, timeouts, reliability]
---

# Connect Timeout Discipline

> Bound every connection attempt so a filtered port costs seconds instead of stalling an entire test run

**Use when:** a script sends many requests across hosts where some ports silently drop packets

**Avoid when:** measuring connection latency is itself the objective of the test

## Procedure

1. Choose a connect timeout that is short enough to keep a batch moving, typically under ten seconds
2. Distinguish connect timeouts from read timeouts in the error you report to the caller
3. Record the timeout value used alongside each failed attempt so results stay interpretable
4. Retry at most once, and only for connection resets that are clearly transient
5. Mark dropped connections as inconclusive rather than as evidence of filtering
6. Log the resolved address and port with every failure so a typo is visible immediately

## Signals

- a filtered port fails fast with a connect timeout rather than hanging
- connection refused appears distinctly from a timeout, proving the host is reachable
- batch runs complete in predictable time regardless of dead entries
- every failure line names the host and port that failed

## Patterns

**1. Bounded connect**

```text
socket.create_connection((host, port), timeout=5)
```

**2. Distinct error text**

```text
connect timeout after 5.0s vs connection refused
```

**3. Resolved address logged**

```text
connect failed: api.example.test:8443 (203.0.113.10)
```

## Pitfalls

- Using one long timeout for both connect and read so a slow body looks like a dead host
- Retrying timeouts automatically and turning a firewall signal into apparent flakiness
- Reporting a timeout as a vulnerability when it usually means filtering, not a defect

## Done when

- every send has an explicit connect timeout applied and recorded
- the run completes within its planned time even with unreachable hosts in the list

## References

- [Python - socket timeouts](https://docs.python.org/3/library/socket.html#socket.settimeout)
- [RFC 9110 - timeouts](https://www.rfc-editor.org/rfc/rfc9110.html)
