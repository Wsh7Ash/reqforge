---
name: capture-metadata-minimum
description: "Record the minimum per-exchange metadata that makes a capture defensible without re-running the test. Use when captures will support a report that another person must review and trust"
pack: reqforge
version: 1.0.0
category: networking
tags: [capture, metadata, evidence]
---

# Capture Metadata Minimum

> Record the minimum per-exchange metadata that makes a capture defensible without re-running the test

**Use when:** captures will support a report that another person must review and trust

**Avoid when:** the capture is an exploratory request whose result will not be cited

## Procedure

1. Record the resolved host, port and scheme actually used for the connection
2. Record the UTC time the request was sent and the elapsed milliseconds to the last byte
3. Record request byte length and response byte length separately from body lengths
4. Record the status code and reason phrase exactly as received
5. Record the client version that produced the capture so replay is reproducible
6. Include the redirect target when the server returned one, marked as not followed

## Signals

- every capture answers who, where, when and what without external notes
- byte counts reconcile with the raw files on disk
- the client version identifies the exact tool build used
- redirect targets appear as data rather than being silently consumed

## Patterns

**1. Metadata block**

```text
{host, port, scheme, sent_at, elapsed_ms, status, bytes}
```

**2. Separate sizes**

```text
request_bytes=312 response_bytes=2048 body_bytes=1900
```

**3. Unfollowed redirect**

```text
status=302 redirect_target=https://login.example.test/
```

## Pitfalls

- Recording only a status code, which cannot distinguish an empty denial from data
- Storing local timestamps without a zone, making correlation across logs ambiguous
- Omitting the port so a non-default service cannot be retested exactly

## Done when

- each capture contains host, port, scheme, timestamps, status and byte counts
- the metadata matches the raw capture files byte for byte

## References

- [W3C - HAR archive format](https://w3c.github.io/web-performance/specs/HAR/Overview.html)
- [OWASP - logging cheat sheet](https://cheatsheetseries.owasp.org/)
