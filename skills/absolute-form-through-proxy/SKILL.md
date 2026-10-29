---
name: absolute-form-through-proxy
description: "Send an absolute URI in the request line to test how a forward proxy resolves authority against the Host header. Use when a forward proxy or an edge that accepts absolute-form targets is in the request path"
pack: reqforge
version: 1.0.0
category: networking
tags: [transmit, proxy, request-target]
---

# Absolute Form Through Proxy

> Send an absolute URI in the request line to test how a forward proxy resolves authority against the Host header

**Use when:** a forward proxy or an edge that accepts absolute-form targets is in the request path

**Avoid when:** the request goes straight to an origin server that rejects absolute-form targets by design

## Procedure

1. Send the origin-form control request and record status and body size
2. Send the same request with an absolute URI naming the same host and compare
3. Send an absolute URI naming a different host to see which authority is honoured
4. Vary only the Host header while keeping the absolute URI fixed
5. Record whether the proxy connected to the URI authority or the Host header
6. Preserve the raw response because proxy error pages are themselves evidence

## Signals

- the connection is made to the host in the absolute URI while Host is ignored
- a proxy error names a host that was never in the Host header
- identical bodies for both authorities indicate one value is silently dropped
- a 400 appears only for mismatched authority, showing the proxy compares them

## Patterns

**1. Absolute URI**

```text
GET http://internal.example.test/admin HTTP/1.1
```

**2. Authority mismatch**

```text
GET http://internal.example.test/ HTTP/1.1
Host: public.example.test
```

**3. Origin control**

```text
GET /admin HTTP/1.1
Host: public.example.test
```

## Pitfalls

- Sending absolute-form requests to an origin server and calling the 400 a defect
- Testing internal hostnames without authorisation covering the proxy itself
- Losing the proxy's own error body, which is the main evidence of routing

## Done when

- both target forms are captured for the same path with status recorded
- the authority actually used for the connection is stated in the notes

## References

- [RFC 9112 - request target forms](https://www.rfc-editor.org/rfc/rfc9112.html)
- [MDN - proxy servers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Proxy_servers_and_tunneling)
