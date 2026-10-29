---
name: request-template-library
description: "Keep a placeholder-driven library of requests per target so each new hypothesis starts from a known-good baseline. Use when an engagement runs for days and the same endpoints are retested with many small mutations"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, reuse, workflow]
---

# Request Template Library

> Keep a placeholder-driven library of requests per target so each new hypothesis starts from a known-good baseline

**Use when:** an engagement runs for days and the same endpoints are retested with many small mutations

**Avoid when:** the work is a single one-off request that will not be revisited

## Procedure

1. Store each known-good request as a template with explicit placeholders for host, id and token
2. Name templates by endpoint intent, not by discovery order, so search stays useful
3. Keep a short header comment listing the placeholders the template requires
4. Add a companion file with observed responses so intent is recoverable without a live target
5. Retire templates that now require missing roles instead of leaving them half-broken
6. Version the directory so a later retest can diff against what was sent originally

## Signals

- a retest can be launched by filling placeholders and sending with no manual editing
- the template directory contains no raw live credentials at rest
- each template names the role it was captured with in its comment header
- template count grows with endpoints, not with individual hypotheses

## Patterns

**1. Placeholder header comment**

```text
# placeholders: host, id, token
GET /api/v1/orders/{{id}} HTTP/1.1
```

**2. Path intent naming**

```text
orders-read-by-id.http, orders-create.http, orders-delete.http
```

**3. Retired marker**

```text
# retired: requires partner role, out of scope for this program
```

## Pitfalls

- Committing filled-in tokens because the template was saved after a successful send
- Naming files by timestamp, which makes the library unusable after a week
- Letting templates drift from the live API without recording what changed

## Done when

- every template lists its placeholders in the first comment line
- a fresh session can send any template by filling placeholders only

## References

- [RFC 9110 - request semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP WSTG - configuration testing](https://owasp.org/www-project-web-security-testing-guide/)
