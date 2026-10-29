---
name: replay-with-header-mutation
description: "Replay one baseline request with a single header changed each time so every outcome has one cause. Use when the hypothesis names a specific header such as a role, tenant or forwarding value"
pack: reqforge
version: 1.0.0
category: networking
tags: [replay, mutation, differential]
---

# Replay With Header Mutation

> Replay one baseline request with a single header changed each time so every outcome has one cause

**Use when:** the hypothesis names a specific header such as a role, tenant or forwarding value

**Avoid when:** the test needs several headers to change together to model a real client

## Procedure

1. Capture the baseline request and its response as the immutable control
2. List the headers worth mutating and order them by expected impact
3. Change one header per replay and keep all other bytes identical
4. Capture each response separately with the mutated header recorded in metadata
5. Diff each response against the control to isolate the effect
6. Follow up only on mutations that changed status, length or a security-relevant field

## Signals

- adding a role header changes a 403 into a 200
- removing a tenant header still returns the tenant's data, showing server-side defaulting
- a forwarded-for change alters rate limiting or audit output
- a content-type change alters which parser handles the body

## Patterns

**1. Single-variable replay**

```text
baseline + one header added, everything else byte-identical
```

**2. Mutation log**

```text
mutated=X-Tenant-Id: other value=null -> 200
```

**3. Control diff**

```text
status equal, body_bytes 1900 vs 4096
```

## Pitfalls

- Changing two headers at once and being unable to attribute the different response
- Reusing the mutated request as the next baseline so drift accumulates
- Testing headers the program excludes, such as spoofed internal-only values

## Done when

- each mutation is captured with exactly one header difference from the baseline
- every changed outcome names the header responsible

## References

- [OWASP - access control testing](https://owasp.org/www-project-web-security-testing-guide/)
- [RFC 9110 - field semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
