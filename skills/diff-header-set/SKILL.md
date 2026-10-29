---
name: diff-header-set
description: "Compare header sets case-insensitively as multisets so added, removed and altered values are all visible. Use when two captures share a status and the security-relevant difference is likely in the headers"
pack: reqforge
version: 1.0.0
category: networking
tags: [compare, headers, differential]
---

# Diff Header Set

> Compare header sets case-insensitively as multisets so added, removed and altered values are all visible

**Use when:** two captures share a status and the security-relevant difference is likely in the headers

**Avoid when:** headers carry only volatile tracing values that change on every response

## Procedure

1. Group both header lists case-insensitively into name to values maps
2. List names present only in the candidate as added
3. List names present only in the baseline as removed
4. List names present in both with different value lists as changed
5. Ignore a documented volatile set such as request ids and dates
6. Tie each surviving difference to a hypothesis before reporting it

## Signals

- a new Set-Cookie appears only when the privileged credential is used
- an X-Cache hit header appears only on the anonymous request
- a security header disappears on the error path
- a CORS allow-origin value changes with the supplied Origin

## Patterns

**1. Set difference**

```text
added={set-cookie}, removed={x-frame-options}
```

**2. Volatile ignore list**

```text
ignore=date, x-request-id, traceparent
```

**3. Value change**

```text
access-control-allow-origin: none -> *
```

## Pitfalls

- Comparing raw header lines and reporting casing differences as findings
- Ignoring added cookies, which often mark an authentication boundary
- Treating an added debug header as harmless before checking what it reveals

## Done when

- added, removed and changed headers are each listed for two captures
- volatile headers are excluded by an explicit named list

## References

- [RFC 9110 - header fields](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP - security headers](https://owasp.org/www-project-secure-headers/)
