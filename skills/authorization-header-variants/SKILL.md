---
name: authorization-header-variants
description: "Build a controlled matrix of credential presentations so authorization results are comparable across roles. Use when object or function level access must be tested across two accounts and an anonymous visitor"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, authorization, matrix]
---

# Authorization Header Variants

> Build a controlled matrix of credential presentations so authorization results are comparable across roles

**Use when:** object or function level access must be tested across two accounts and an anonymous visitor

**Avoid when:** the engagement has only one issued credential and cross-role testing is out of scope

## Procedure

1. Capture one working request per role, keeping each file named for the role it represents
2. Extract the credential into a placeholder so the template is reusable without editing bytes
3. Create variants with the header removed, emptied and malformed for the negative control
4. Create a variant that presents two identities to test which one wins
5. Send the full matrix and record status and body bytes for every cell
6. Mark each cell as allow, deny or ambiguous, then follow up only the ambiguous ones

## Signals

- high-privilege data returned for a low-privilege credential indicates broken object access
- a 200 with an empty body may be a silent denial that still leaks existence
- a 403 versus 404 difference leaks whether an object exists for that role
- an anonymous request returning cached privileged content shows cache key confusion

## Patterns

**1. Role placeholder template**

```text
GET /api/v1/invoices/{{id}} HTTP/1.1
Authorization: Bearer {{token}}
```

**2. Two identities presented**

```text
Authorization: Bearer low
Authorization: Bearer high
```

**3. Malformed negative control**

```text
Authorization: Bearer not-a-real-token
```

## Pitfalls

- Reusing one credential for two roles and then concluding access control is intact
- Treating a 200 with an error envelope as a successful access
- Leaving real tokens in the template file that later gets committed or shared

## Done when

- the matrix captures one row per role with status and body size recorded
- every ambiguous cell has a follow-up action recorded in the notes

## References

- [OWASP - broken access control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [RFC 6750 - bearer tokens](https://www.rfc-editor.org/rfc/rfc6750.html)
