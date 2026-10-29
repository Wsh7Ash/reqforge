---
name: head-first-then-body-read
description: "Read and parse the status head before touching the body so framing decisions come from what the server sent. Use when responses vary between fixed length, chunked and close-delimited framing across a session"
pack: reqforge
version: 1.0.0
category: networking
tags: [transmit, framing, streaming]
---

# Head First Then Body Read

> Read and parse the status head before touching the body so framing decisions come from what the server sent

**Use when:** responses vary between fixed length, chunked and close-delimited framing across a session

**Avoid when:** the response is guaranteed small and fully buffered, where the order cannot matter

## Procedure

1. Read from the socket until the header terminator appears and stop there
2. Parse the status line and collect headers in arrival order without rewriting them
3. Decide the body strategy from Content-Length, Transfer-Encoding, or connection close
4. Read exactly the declared number of bytes when a length is present
5. Detect early termination and mark the exchange partial instead of raising a bare error
6. Store the head bytes and body bytes separately, then recombine for the raw capture

## Signals

- the status line is available before any body byte is read
- a chunked response decodes to fewer bytes than the wire carried
- a close-delimited response ends exactly when the socket closes
- conflicting framing headers are visible in the head before the body is parsed

## Patterns

**1. Head terminator**

```text
read until b'\r\n\r\n' then parse
```

**2. Framing precedence**

```text
chunked beats content-length when both are present
```

**3. Close-delimited**

```text
no length and no chunking: read until EOF
```

## Pitfalls

- Reading the entire socket until EOF and then trying to split head from body afterwards
- Trusting Content-Length when Transfer-Encoding chunked is also present
- Discarding the head bytes, which are needed for an exact raw capture

## Done when

- framing source for each response is recorded as length, chunked or close
- the head and body split matches the bytes the server actually sent

## References

- [RFC 9112 - message body length](https://www.rfc-editor.org/rfc/rfc9112.html)
- [Python - socket makefile](https://docs.python.org/3/library/socket.html)
