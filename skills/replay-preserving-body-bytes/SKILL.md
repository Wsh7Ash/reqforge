---
name: replay-preserving-body-bytes
description: "Replay with the original body octets intact so signature checks and parsers see exactly what they saw before. Use when a request is signed, hashed or parsed strictly and any re-serialisation would break it"
pack: reqforge
version: 1.0.0
category: networking
tags: [replay, integrity, bytes]
---

# Replay Preserving Body Bytes

> Replay with the original body octets intact so signature checks and parsers see exactly what they saw before

**Use when:** a request is signed, hashed or parsed strictly and any re-serialisation would break it

**Avoid when:** the body is a small JSON object the server reparses with no integrity check

## Procedure

1. Store the request body as raw bytes alongside the capture, never as parsed JSON
2. Replay using those bytes without a JSON round trip that would reorder keys
3. Confirm the byte length matches the content length header before sending
4. Test one deliberate re-serialisation to confirm whether key order matters
5. Record whether the server accepted the reordered body, which reveals strictness
6. Keep the accepted byte sequence as the canonical reproduction for the report

## Signals

- the reordered body is rejected with a signature or parse error
- duplicate JSON keys survive only when the raw bytes are preserved
- whitespace differences change a hash-based signature result
- the accepted body length equals the original capture exactly

## Patterns

**1. Bytes not objects**

```text
body = capture_body_bytes, not json.dumps(payload)
```

**2. Key order probe**

```text
{"a":1,"b":2} versus {"b":2,"a":1}
```

**3. Duplicate key**

```text
{"role":"user","role":"admin"} kept literal
```

## Pitfalls

- Re-encoding a body through a JSON library and silently dropping duplicate keys
- Normalising whitespace in a body that is hashed for integrity
- Losing the original bytes when the capture stored only a pretty-printed copy

## Done when

- the replay body digest equals the capture body digest
- the effect of re-serialisation is recorded as accepted or rejected

## References

- [RFC 8259 - JSON](https://www.rfc-editor.org/rfc/rfc8259.html)
- [OWASP - parameter pollution](https://owasp.org/www-community/attacks/)
