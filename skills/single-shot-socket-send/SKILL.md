---
name: single-shot-socket-send
description: "Transmit one request over a raw socket so nothing between the file and the wire rewrites headers or follows redirects. Use when the test depends on exact bytes and any client-side rewriting would invalidate the result"
pack: reqforge
version: 1.0.0
category: networking
tags: [transmit, sockets, byte-fidelity]
---

# Single Shot Socket Send

> Transmit one request over a raw socket so nothing between the file and the wire rewrites headers or follows redirects

**Use when:** the test depends on exact bytes and any client-side rewriting would invalidate the result

**Avoid when:** the request needs HTTP/2 multiplexing or a client that negotiates protocol versions

## Procedure

1. Resolve the destination host and port explicitly instead of relying on defaults
2. Open a TCP connection with a bounded connect timeout so a dead host cannot hang the run
3. Write the serialised request with a single sendall call to keep head and body adjacent
4. Read the response head until the terminator, then read the body according to its framing
5. Close the socket after the exchange and record the elapsed time from first write to last read
6. Store the request bytes and response bytes together as one capture unit

## Signals

- the server receives exactly the header order written in the file
- no redirect is followed, so 301 responses appear as captured facts
- the response arrives as a single exchange with no retry or connection reuse
- elapsed time reflects the one round trip rather than a pooled handshake

## Patterns

**1. Explicit connect**

```text
sock = socket.create_connection((host, port), timeout=10)
```

**2. Single write**

```text
sock.sendall(serialize_request(request, host=host))
```

**3. Head then body**

```text
read until b'\r\n\r\n', then honour Content-Length
```

## Pitfalls

- Using a high-level client that adds Accept-Encoding and hides compression effects
- Forgetting to set a read timeout so an unfinished chunked body blocks the whole session
- Sending through a TLS wrapper without passing the correct server hostname for SNI

## Done when

- the captured request bytes equal the bytes written to the socket
- the exchange records one connection, one request and one response with timing

## References

- [Python - socket module](https://docs.python.org/3/library/socket.html)
- [RFC 9112 - message body length](https://www.rfc-editor.org/rfc/rfc9112.html)
