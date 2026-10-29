---
name: content-type-declaration-mismatch
description: "Send a body whose declared content type disagrees with its syntax to find parsers that trust the bytes, not the label. Use when the application advertises JSON-only input and the hypothesis is weak type enforcement"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, content-type, parser]
---

# Content Type Declaration Mismatch

> Send a body whose declared content type disagrees with its syntax to find parsers that trust the bytes, not the label

**Use when:** the application advertises JSON-only input and the hypothesis is weak type enforcement

**Avoid when:** the endpoint is a file upload where the media type is already the subject of a separate test

## Procedure

1. Capture the accepted request with its correct content type as the baseline
2. Change only the Content-Type header to a different family, keeping the body bytes identical
3. Repeat with the type omitted entirely to test default handling
4. Repeat with a charset parameter that contradicts the body encoding
5. Send each variant separately so any status change is attributable to one edit
6. Check whether the response reflects parsed fields, proving the body was interpreted

## Signals

- a JSON body declared as form data still populates fields in the response
- an XML body declared as JSON returns a parser error naming the XML dialect
- omitting Content-Type leads to a default parser that accepts unexpected syntax
- a mismatched charset produces mojibake in stored data rather than a rejection

## Patterns

**1. JSON body as form data**

```text
Content-Type: application/x-www-form-urlencoded

{"role":"admin"}
```

**2. XML body as JSON**

```text
Content-Type: application/json

<user><role>admin</role></user>
```

**3. Contradictory charset**

```text
Content-Type: application/json; charset=utf-16

{"role":"admin"}
```

## Pitfalls

- Sending a body that is syntactically valid in both formats and drawing a false conclusion
- Changing body and header together, which makes the status change unattributable
- Assuming a 415 response proves strictness when a different route accepted the same body

## Done when

- each content-type variant is captured as its own request and response pair
- the parser that ultimately accepted the body is identified in the notes

## References

- [RFC 9110 - media types](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP - content type confusion](https://owasp.org/www-community/vulnerabilities/)
