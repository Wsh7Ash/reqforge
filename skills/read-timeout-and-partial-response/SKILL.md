---
name: read-timeout-and-partial-response
description: "Handle a response that never completes without discarding the bytes that already arrived as evidence. Use when a server streams, stalls or closes mid-body and the partial bytes still prove behaviour"
pack: reqforge
version: 1.0.0
category: networking
tags: [transmit, timeouts, partial]
---

# Read Timeout and Partial Response

> Handle a response that never completes without discarding the bytes that already arrived as evidence

**Use when:** a server streams, stalls or closes mid-body and the partial bytes still prove behaviour

**Avoid when:** the response is known to be short and complete, so timeout handling adds no signal

## Procedure

1. Set a read timeout that is generous relative to normal latency but still bounded
2. Read the head first and parse framing before attempting to read the whole body
3. On timeout, keep the bytes captured so far and mark the exchange as partial
4. Record how many body bytes arrived versus the declared content length
5. Decide whether the partial body is evidence, an error, or both, before reporting
6. Re-run once with a longer timeout only to distinguish slowness from a hang

## Signals

- body bytes received are fewer than the declared content length
- the connection closes before the chunked terminator arrives
- a stalled stream still returns a complete head with a 200 status
- the same request completes on a retry, indicating timing rather than a defect

## Patterns

**1. Partial body accounting**

```text
declared=4096 received=512 partial=true
```

**2. Missing chunk terminator**

```text
chunked body ends without 0\r\n\r\n
```

**3. Head before body**

```text
parse status line and headers as soon as the terminator is seen
```

## Pitfalls

- Treating a read timeout as a server crash when the head already proved routing worked
- Discarding partial bytes, which are often the only evidence of a streaming defect
- Extending timeouts until the run is unusable instead of recording the partial result

## Done when

- partial exchanges record received bytes and the declared length
- the report distinguishes a stall from a connection reset

## References

- [Python - socket recv](https://docs.python.org/3/library/socket.html#socket.socket.recv)
- [RFC 9112 - message body length](https://www.rfc-editor.org/rfc/rfc9112.html)
