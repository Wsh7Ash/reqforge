---
name: early-response-detection
description: "Notice when a server answers before the request body is fully written, because that behaviour exposes parser disagreement. Use when testing for request smuggling or for servers that respond to malformed bodies mid-stream"
pack: reqforge
version: 1.0.0
category: networking
tags: [transmit, smuggling, parsing]
---

# Early Response Detection

> Notice when a server answers before the request body is fully written, because that behaviour exposes parser disagreement

**Use when:** testing for request smuggling or for servers that respond to malformed bodies mid-stream

**Avoid when:** the body is tiny and always written in one call, leaving no window for an early reply

## Procedure

1. Write the head and only part of the body, then attempt to read from the socket
2. Record whether a complete response arrives before the body is finished
3. Compare that response against the same request sent in full
4. Check whether the unread body is later interpreted as a new request on the connection
5. Keep the captured bytes exactly, since early responses are strong parser evidence
6. Repeat with a deliberately mismatched length to see whether the server trusts its own head

## Signals

- a response arrives while the client still has body bytes to write
- the second response on the same socket corresponds to the leftover body
- a 400 appears immediately after the head with no body consumed
- the connection stays open after an early error, hinting at desynchronisation

## Patterns

**1. Split write**

```text
send head, wait, then send the remainder of the body
```

**2. Leftover interpreted**

```text
unread body bytes appear as a second request line
```

**3. Early 400**

```text
HTTP/1.1 400 Bad Request received before body completion
```

## Pitfalls

- Reporting smuggling from a single early response without probing the connection state
- Ignoring TLS buffering, which can make an early write look like a full send
- Testing on a server that legitimately rejects oversized bodies before reading them

## Done when

- the moment of response relative to body bytes written is recorded
- any leftover-body interpretation is confirmed by a second captured response

## References

- [PortSwigger - request smuggling](https://portswigger.net/web-security/request-smuggling)
- [RFC 9112 - message parsing](https://www.rfc-editor.org/rfc/rfc9112.html)
