---
name: diff-status-and-length
description: "Compare two captures on status and byte length first, because the cheapest fields carry the strongest signal. Use when a baseline and a candidate response must be compared without reading either body"
pack: reqforge
version: 1.0.0
category: networking
tags: [compare, differential, triage]
---

# Diff Status and Length

> Compare two captures on status and byte length first, because the cheapest fields carry the strongest signal

**Use when:** a baseline and a candidate response must be compared without reading either body

**Avoid when:** both responses are large and share a status, where body-level diffing is required

## Procedure

1. Load both capture summaries and confirm they describe the same request target
2. Compare status code and reason phrase first
3. Compare response and body byte lengths second
4. Flag any difference as the entry point for a deeper body diff
5. Confirm that a length change is not explained by a dynamic token or timestamp
6. Record the pair of values, never just the word changed

## Signals

- same status with a much larger body means extra data was returned
- a 200 becomes a 403 exactly when the credential is swapped
- identical lengths with different digests point to in-body substitution
- a 204 to 200 shift after a state change reveals newly reachable content

## Patterns

**1. Two-field compare**

```text
status 403 -> 200, body_bytes 120 -> 4096
```

**2. Same-length trap**

```text
body_bytes equal, digests differ -> look inside the body
```

**3. Target guard**

```text
assert before.target == after.target before comparing
```

## Pitfalls

- Comparing captures of different targets and reporting a difference that is only the path
- Stopping at identical lengths and missing a substituted body
- Treating a reason phrase difference as a security signal on its own

## Done when

- status and byte length are compared for two captures of the same target
- each difference is either explained or escalated to a body diff

## References

- [RFC 9110 - status codes](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP WSTG - differential testing](https://owasp.org/www-project-web-security-testing-guide/)
