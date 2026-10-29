---
name: verbatim-response-capture
description: "Store the response exactly as received, status line and headers included, before any decoding touches it. Use when a finding depends on a header, an error string or a byte sequence that tooling would normalise"
pack: reqforge
version: 1.0.0
category: networking
tags: [capture, evidence, raw-http]
---

# Verbatim Response Capture

> Store the response exactly as received, status line and headers included, before any decoding touches it

**Use when:** a finding depends on a header, an error string or a byte sequence that tooling would normalise

**Avoid when:** only the parsed JSON body matters and the raw framing has no evidential value

## Procedure

1. Accumulate every byte read from the socket into one buffer without decoding
2. Write those bytes to a file before parsing so nothing can be lost downstream
3. Hash the raw buffer and store the digest beside the capture for later verification
4. Parse the buffer afterwards for status, headers and body, keeping the raw file authoritative
5. Name the file for the request it answers, not for the time it was taken
6. Compare the stored digest with a fresh send when a retest needs confirmation

## Signals

- the raw file starts with the status line exactly as the server wrote it
- header casing is preserved rather than title-cased by a parser
- the digest changes when any response byte changes
- the parsed view and the raw file agree on body length

## Patterns

**1. Write before parse**

```text
raw = read_all(sock)
path.write_bytes(raw)
response = parse_response(raw)
```

**2. Digest beside capture**

```text
status=200 sha256=4f2a… bytes=1024
```

**3. Header casing preserved**

```text
x-amzn-requestid: 8d1e…
```

## Pitfalls

- Letting a JSON parser reformat the body and then saving that as the capture
- Overwriting a capture on retest instead of keeping the earlier evidence
- Storing only the body, which loses the framing and headers the report needs

## Done when

- the raw capture file opens as a valid HTTP response without repair
- a sha256 digest is recorded next to the capture path

## References

- [RFC 9112 - message format](https://www.rfc-editor.org/rfc/rfc9112.html)
- [OWASP - evidence handling](https://owasp.org/www-project-web-security-testing-guide/)
