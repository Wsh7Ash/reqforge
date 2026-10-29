---
name: hop-by-hop-header-authoring
description: "Craft Connection and Upgrade headers deliberately to test which hops strip, forward or trust them. Use when a proxy chain sits in front of the application and connection-level headers may be mishandled"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, proxy, connection]
---

# Hop by Hop Header Authoring

> Craft Connection and Upgrade headers deliberately to test which hops strip, forward or trust them

**Use when:** a proxy chain sits in front of the application and connection-level headers may be mishandled

**Avoid when:** the tested endpoint is direct-to-origin with no intermediary and the program excludes proxy issues

## Procedure

1. Establish the control request and confirm which proxy headers appear in the response
2. Add a Connection header naming a custom header that the application also consumes
3. Send a variant that keeps the custom header and a variant that omits it for comparison
4. Test Upgrade with an unsupported protocol to observe how the proxy answers
5. Record whether the named header survived to the origin by its effect on the response
6. Keep the set minimal: each hop-by-hop test needs a clear observable outcome before it is worth running

## Signals

- a header named in Connection disappears before the application reads it
- an Upgrade request returns 101 without a real protocol switch
- the proxy forwards Connection tokens verbatim, leaking hop intent to the origin
- Keep-Alive behaviour differs from what the response headers claim

## Patterns

**1. Connection nominates a custom header**

```text
Connection: X-Internal-Role
X-Internal-Role: admin
```

**2. Unsupported upgrade**

```text
Connection: Upgrade
Upgrade: h2c
```

**3. Keep-alive suppression**

```text
Connection: close
Keep-Alive: timeout=0
```

## Pitfalls

- Expecting a header to be stripped without a comparison request that includes it normally
- Treating a 101 response as proof of a working protocol switch instead of a proxy quirk
- Ignoring that Connection token handling differs between HTTP/1.1 and HTTP/2 front ends

## Done when

- the fate of each nominated header is recorded as forwarded, stripped or rewritten
- any proxy quirk found has a paired control request in the capture set

## References

- [RFC 9110 - connection management](https://www.rfc-editor.org/rfc/rfc9110.html)
- [MDN - Connection header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection)
