---
name: response-framing-decode
description: "Decode chunked, fixed-length and close-delimited responses correctly so exported bodies are the real content. Use when captures must be readable in a report and the server frames responses differently per route"
pack: reqforge
version: 1.0.0
category: networking
tags: [capture, chunked, framing]
---

# Response Framing Decode

> Decode chunked, fixed-length and close-delimited responses correctly so exported bodies are the real content

**Use when:** captures must be readable in a report and the server frames responses differently per route

**Avoid when:** the response is a binary download where decoding is handled by a dedicated binary path

## Procedure

1. Read the Transfer-Encoding header and note whether chunked applies
2. If chunked, walk chunk sizes until the zero-length terminator and drop the framing bytes
3. If a content length is declared, truncate or extend the read to exactly that many octets
4. If neither applies, read to connection close and mark the body close-delimited
5. Keep the undecoded bytes too, so a discrepancy can be reviewed later
6. Record which framing rule produced the body you exported

## Signals

- a decoded body is shorter than the wire bytes by the chunk overhead
- the zero chunk terminator is present in the raw capture but absent in the decoded body
- a declared length smaller than the received bytes indicates proxy padding
- close-delimited responses end abruptly without a terminator

## Patterns

**1. Chunk walk**

```text
1a\r\n{\"items\":[1,2]}\r\n0\r\n\r\n
```

**2. Length truncation**

```text
body = wire_body[:int(content_length)]
```

**3. Framing provenance**

```text
framing=chunked decoded_bytes=11 wire_bytes=24
```

## Pitfalls

- Saving chunk-size lines into the exported body and reporting them as response content
- Trusting a declared length that is shorter than what actually arrived
- Decoding twice, which silently corrupts a body that legitimately begins with a hex string

## Done when

- the exported body parses as the declared content type
- the framing rule used is recorded with the capture

## References

- [RFC 9112 - chunked coding](https://www.rfc-editor.org/rfc/rfc9112.html)
- [MDN - Transfer-Encoding](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding)
