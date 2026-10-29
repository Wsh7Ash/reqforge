---
name: export-redaction-before-sharing
description: "Redact credentials, tokens and personal data at export time so no shareable artifact leaks a secret. Use when any capture leaves your machine, including into a report attachment or a chat message"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, redaction, safety]
---

# Export Redaction Before Sharing

> Redact credentials, tokens and personal data at export time so no shareable artifact leaks a secret

**Use when:** any capture leaves your machine, including into a report attachment or a chat message

**Avoid when:** the artifact stays local and is never transmitted or committed

## Procedure

1. List the sensitive value shapes for this target: bearer tokens, cookies, keys, emails
2. Apply pattern redaction to headers, bodies and query strings alike
3. Keep a marker with the field name so reviewers know what was removed
4. Check for secrets in unexpected places such as custom headers and error bodies
5. Re-scan the exported file with a pattern list before sending it
6. Store the unredacted original only where the engagement rules allow

## Signals

- a scan of the exported artifact finds no token-shaped strings
- redaction markers state the field that was removed
- the redacted artifact still proves the behaviour
- no secret appears in the filename or the metadata either

## Patterns

**1. Header redaction**

```text
Cookie: [REDACTED-COOKIE]
```

**2. Body redaction**

```text
"access_token": "[REDACTED]" in every copy
```

**3. Post-export scan**

```text
grep -E 'eyJ[A-Za-z0-9_-]{10,}' exported/
```

## Pitfalls

- Redacting the request but leaving the same token in the response echo
- Replacing values with an empty string, which hides that a field existed
- Assuming a private repository makes a committed token safe

## Done when

- a pattern scan of every exported artifact returns no matches
- each removed value leaves a labelled marker behind

## References

- [OWASP - sensitive data exposure](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
- [GitHub - secret scanning](https://docs.github.com/en/code-security/secret-scanning)
