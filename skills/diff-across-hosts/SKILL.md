---
name: diff-across-hosts
description: "Send one request to two hosts or environments to expose behaviour that only one edge enforces. Use when a legacy host, alternate port or regional deployment is still reachable for the same app"
pack: reqforge
version: 1.0.0
category: networking
tags: [compare, environments, scope]
---

# Diff Across Hosts

> Send one request to two hosts or environments to expose behaviour that only one edge enforces

**Use when:** a legacy host, alternate port or regional deployment is still reachable for the same app

**Avoid when:** the second host is out of scope or belongs to a different program

## Procedure

1. Confirm both hosts are in scope and record the authorisation reference
2. Send byte-identical requests to each host and capture both
3. Compare status, headers and body using the same normalisation
4. Check whether security headers, rate limits or auth checks differ
5. Note DNS and certificate differences that explain routing
6. Report only the difference that is both in scope and exploitable

## Signals

- the legacy host lacks a header the primary host enforces
- the alternate host returns data without the gateway's auth check
- one host serves a newer build, revealing a missing patch on the other
- certificate names differ, exposing an unmanaged deployment

## Patterns

**1. Identical bytes both hosts**

```text
same file, --host switched per send
```

**2. Enforcement gap**

```text
primary: 401, legacy: 200 on the same path
```

**3. Scope note**

```text
both hosts listed in scope ref PROGRAM-123
```

## Pitfalls

- Testing a host you have not confirmed is in scope
- Attributing a build difference to a security regression without a version check
- Sending different request bytes to each host and comparing anyway

## Done when

- both hosts are captured with byte-identical requests
- the scope reference for every tested host is recorded

## References

- [OWASP WSTG - infrastructure configuration](https://owasp.org/www-project-web-security-testing-guide/)
- [RFC 9110 - server behaviour](https://www.rfc-editor.org/rfc/rfc9110.html)
