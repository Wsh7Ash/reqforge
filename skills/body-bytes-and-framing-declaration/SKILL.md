---
name: body-bytes-and-framing-declaration
description: "Control the exact body octets and the framing header that declares them so parsers see one unambiguous message. Use when a parser disagreement or a body-based injection depends on content length versus chunking"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, framing, chunked]
---

# Body Bytes and Framing Declaration

> Control the exact body octets and the framing header that declares them so parsers see one unambiguous message

**Use when:** a parser disagreement or a body-based injection depends on content length versus chunking

**Avoid when:** the server stack is confirmed to reject conflicting framing with a hard 400 on every path

## Procedure

1. Write the body bytes you intend to send and record their exact length in octets
2. Declare enough framing for the bytes: Content-Length for a fixed body, chunked for a streamed one
3. Avoid sending a body with a GET unless the test specifically needs that ambiguity
4. Create a chunked variant with an explicit terminator to test decoding differences
5. Send both variants and store the raw request bytes next to each response
6. Confirm from the response whether the server decoded, truncated or rejected the body

## Signals

- a body echoed in full proves the declared length was honoured
- a truncated echo shows the server used a different length than declared
- a 400 mentioning chunked encoding proves the parser routed on Transfer-Encoding
- a 411 response proves the server requires explicit framing it did not receive

## Patterns

**1. Fixed length body**

```text
POST /api/search HTTP/1.1
Content-Type: application/json
Content-Length: 17

{"q":"admin"}
```

**2. Explicit chunked body**

```text
POST /api/search HTTP/1.1
Transfer-Encoding: chunked

b\r\n{\"q\":\"admin\"}\r\n0
```

**3. Both framing headers**

```text
POST /api/search HTTP/1.1
Content-Length: 0
Transfer-Encoding: chunked
```

## Pitfalls

- Letting the client recompute Content-Length, which defeats the whole point of the test
- Mixing a hand-written chunk size with the wrong body length and calling the result a server bug
- Testing framing on a GET endpoint where intermediaries legitimately drop the body

## Done when

- the declared length equals the byte length of the body that was captured
- at least one alternative framing variant is captured and explained

## References

- [RFC 9112 - transfer codings](https://www.rfc-editor.org/rfc/rfc9112.html)
- [PortSwigger - request smuggling](https://portswigger.net/web-security/request-smuggling)
