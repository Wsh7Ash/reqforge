---
name: request-file-from-proxy-pane
description: "Copy a captured request into a plain .http file without losing a single byte of framing. Use when a request has to be reproduced exactly as it was observed, including casing and duplicate headers"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, capture, raw-http]
---

# Request File From Proxy Pane

> Copy a captured request into a plain .http file without losing a single byte of framing

**Use when:** a request has to be reproduced exactly as it was observed, including casing and duplicate headers

**Avoid when:** the request must be generated from a schema or OpenAPI document rather than copied from a trace

## Procedure

1. Select the full request head including the request line and every header line, not just the URL
2. Paste into a file with the extension .http and keep the blank line before the body intact
3. Confirm the file ends with the body bytes only, with no trailing editor newline added by mistake
4. Diff the pasted head against the proxy view line by line to catch collapsed whitespace
5. Note the original scheme, host and port in a comment at the top instead of guessing later
6. Save the file in a per-target directory so captures and templates never mix across engagements

## Signals

- the request line preserves the exact method casing the server received
- duplicate headers such as two Authorization lines are still present and ordered
- the body starts immediately after a single blank line
- the file has no carriage-return damage introduced by an editor

## Patterns

**1. Minimal reproduction file**

```text
POST /api/v1/orders HTTP/1.1
Host: shop.example.test
Content-Type: application/json

{"sku":"A-1","qty":1}
```

**2. Duplicate header preserved**

```text
GET /admin HTTP/1.1
Host: app.example.test
X-Forwarded-For: 10.0.0.1
X-Forwarded-For: 127.0.0.1
```

**3. Comment the origin**

```text
# captured 2026-10-28 from staging, scheme=https port=443
GET /health HTTP/1.1
```

## Pitfalls

- Copying only the path and rebuilding headers by hand destroys the evidence value of the capture
- Editors that strip trailing blank lines silently delete a body-less request's terminator
- Saving as .txt invites tooling that rewrites line endings to CRLF twice

## Done when

- the .http file re-reads into a request with the same header count as the proxy view
- a byte diff against the exported capture shows no differences in the head

## References

- [RFC 9112 - message format](https://www.rfc-editor.org/rfc/rfc9112.html)
- [MDN - HTTP messages](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages)
