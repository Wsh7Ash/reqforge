---
name: request-line-target-fidelity
description: "Keep traversal sequences, double slashes and encoded octets in the request target instead of normalising them away. Use when the hypothesis depends on how a front end normalises a path before a back end routes it"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, path-traversal, normalisation]
---

# Request Line Target Fidelity

> Keep traversal sequences, double slashes and encoded octets in the request target instead of normalising them away

**Use when:** the hypothesis depends on how a front end normalises a path before a back end routes it

**Avoid when:** the target is a plain documented endpoint where path tricks are already ruled out by the program

## Procedure

1. Write the target exactly as the test requires, including percent escapes and dot segments
2. Disable any client-side path joining so the literal string reaches the socket
3. Record the normalised variant beside the literal one to test both in a single session
4. Send the literal form first so a 404 cannot be confused with a rewriting proxy
5. Compare status and body against the plain path to see whether normalisation happened
6. Document which layer normalised the target, using response headers and body shape as evidence

## Signals

- a 301 to a cleaned path reveals front-end normalisation before routing
- identical bodies for literal and clean paths suggest the proxy rewrote the target
- a 400 with a parse error names the layer that rejected the target syntax
- differing cache keys for both forms indicate divergent normalisation upstream

## Patterns

**1. Dot segments kept literal**

```text
GET /api/v1/users/../admin/keys HTTP/1.1
```

**2. Encoded traversal variant**

```text
GET /api/v1/files/%2e%2e%2f%2e%2e%2fetc%2fpasswd HTTP/1.1
```

**3. Double slash differential**

```text
GET //api//v1//users HTTP/1.1
```

## Pitfalls

- Most HTTP libraries collapse dot segments before sending, which silently kills the test
- Assuming a 404 means the route is absent when a proxy rejected the unnormalised target
- Testing encoded and literal forms in one request instead of as separate comparable captures

## Done when

- both literal and normalised targets are captured with distinct timestamps
- the layer responsible for normalisation is named in the notes

## References

- [RFC 3986 - path normalisation](https://www.rfc-editor.org/rfc/rfc3986.html)
- [OWASP - path traversal](https://owasp.org/www-community/attacks/Path_Traversal)
