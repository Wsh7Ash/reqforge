---
name: invalid-but-parseable-request-lines
description: "Author request lines that are illegal in the spec yet accepted by common parsers to reveal lenient routing. Use when routing rules are enforced by a reverse proxy that may normalise differently from the origin"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, parser-differential, routing]
---

# Invalid but Parseable Request Lines

> Author request lines that are illegal in the spec yet accepted by common parsers to reveal lenient routing

**Use when:** routing rules are enforced by a reverse proxy that may normalise differently from the origin

**Avoid when:** the program treats malformed-request testing as out of scope or requires negotiated permission

## Procedure

1. List the request-line deviations worth testing: lowercase method, extra spaces, HTTP/1.0 version
2. Send the legal form first and record its status as the control for that endpoint
3. Send one deviation at a time and keep every other byte identical to the control
4. Note whether the response came from the proxy or the application by its error body shape
5. Test whether a case-varied method still reaches a handler with different authentication rules
6. Stop at the first accepted deviation and expand it into a minimal, reportable reproduction

## Signals

- a lowercase method returns the same body as the canonical one, proving case-insensitive routing
- an HTTP/1.0 request skips a check that the 1.1 path enforces
- extra whitespace before the target reaches the application without a 400
- proxy-generated error pages disappear when a deviation is applied

## Patterns

**1. Lowercase method**

```text
get /api/v1/me HTTP/1.1
```

**2. Version rollback**

```text
GET /admin HTTP/1.0
Host: app.example.test
```

**3. Extra whitespace**

```text
GET  /api/v1/me  HTTP/1.1
```

## Pitfalls

- Bundling several deviations into one request so the accepted one cannot be isolated
- Assuming any 400 came from the origin when the proxy often answers first
- Escalating to a report before confirming the deviation changes an access decision

## Done when

- each accepted deviation has a control request and a single-variable variant captured
- the answering layer is identified for both the control and the variant

## References

- [RFC 9112 - request line](https://www.rfc-editor.org/rfc/rfc9112.html)
- [PortSwigger - HTTP/2 request smuggling](https://portswigger.net/research/http2)
