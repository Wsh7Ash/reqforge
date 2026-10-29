---
name: raw-transcript-for-report
description: "Attach a request and response transcript that a reader can follow without any tooling. Use when a report needs self-contained evidence that survives being copied into a ticket"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, report, evidence]
---

# Raw Transcript for Report

> Attach a request and response transcript that a reader can follow without any tooling

**Use when:** a report needs self-contained evidence that survives being copied into a ticket

**Avoid when:** the reviewer explicitly wants machine-readable captures only

## Procedure

1. Separate the transcript into clearly labelled request and response sections
2. Keep the request line and headers in their original order
3. Show the response status line and headers verbatim
4. Truncate a long body at a stated byte count rather than silently
5. Redact credentials and personal data with visible markers
6. State which environment and account produced the transcript

## Signals

- a reader can reconstruct the request from the transcript alone
- truncation is explicit with the number of bytes omitted
- redaction markers are visible and consistent across the document
- the environment and role appear in the transcript header

## Patterns

**1. Section markers**

```text
### REQUEST ### then ### RESPONSE ###
```

**2. Explicit truncation**

```text
... 18432 bytes omitted for length ...
```

**3. Visible redaction**

```text
Authorization: Bearer [REDACTED-TOKEN]
```

## Pitfalls

- Pasting a transcript with a live session cookie into a public issue tracker
- Silently truncating a body so the reviewer thinks the response was short
- Reordering headers, which destroys the reproduction value of the transcript

## Done when

- the transcript contains labelled request and response sections
- every redaction is visible as a marker rather than deleted text

## References

- [OWASP - reporting](https://owasp.org/www-project-web-security-testing-guide/)
- [RFC 9112 - message format](https://www.rfc-editor.org/rfc/rfc9112.html)
