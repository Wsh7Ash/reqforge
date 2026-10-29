---
name: har-to-finding-evidence
description: "Turn a capture set into the exact evidence block a finding needs: request, response, impact and reproduction. Use when a confirmed behaviour must be written up with evidence that matches the report template"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, report, findings]
---

# Har to Finding Evidence

> Turn a capture set into the exact evidence block a finding needs: request, response, impact and reproduction

**Use when:** a confirmed behaviour must be written up with evidence that matches the report template

**Avoid when:** the behaviour is still unconfirmed and needs more testing before write-up

## Procedure

1. Select the minimal capture pair that demonstrates the behaviour
2. Extract the request in a form a triager can rerun without your tooling
3. Quote only the response fields that prove the impact
4. Write the impact in terms of data or actions, not of headers
5. List the preconditions such as a role, an object id or a feature flag
6. Attach the HAR for completeness and reference the minimal pair in the body

## Signals

- the evidence block names the account role used for each side
- impact is described as data exposed or action performed
- the reproduction steps are numbered and free of tool-specific assumptions
- the attachment matches the captures referenced in the text

## Patterns

**1. Minimal pair reference**

```text
baseline orders-read-as-user, candidate orders-read-as-admin
```

**2. Quoted proof**

```text
response contained the other tenant's invoice id 8812
```

**3. Preconditions list**

```text
requires: two accounts, sharing enabled
```

## Pitfalls

- Attaching a hundred captures so the reviewer cannot find the relevant pair
- Describing the mechanism in place of the impact the program pays for
- Letting the attachment and the written reproduction diverge

## Done when

- a reviewer can reproduce the finding from the evidence block alone
- the referenced captures exist in the attachment with matching names

## References

- [OWASP - writing findings](https://owasp.org/www-project-web-security-testing-guide/)
- [W3C - HAR archive format](https://w3c.github.io/web-performance/specs/HAR/Overview.html)
