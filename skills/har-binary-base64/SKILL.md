---
name: har-binary-base64
description: "Mark binary response content as base64 in HAR so a viewer shows a file instead of mangled text. Use when an exported transcript includes images, archives or protobuf bodies"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, har, binary]
---

# Har Binary Base64

> Mark binary response content as base64 in HAR so a viewer shows a file instead of mangled text

**Use when:** an exported transcript includes images, archives or protobuf bodies

**Avoid when:** every response is plain text, where the encoding field is redundant

## Procedure

1. Detect binary content from the media type and from NUL bytes in the body
2. Base64-encode the body and set encoding to base64 on the content object
3. Keep the decoded size as the content size, not the encoded length
4. Record the original media type exactly as received
5. Verify a decode of the exported value reproduces the captured digest
6. Note in the report that the body is encoded so reviewers are not confused

## Signals

- the exported entry renders as a downloadable file in a HAR viewer
- decode of the base64 value matches the captured sha256
- content size equals the raw body length, not the encoded length
- the media type matches the response header exactly

## Patterns

**1. Encoded content**

```text
"content":{"size":4096,"mimeType":"image/png","encoding":"base64"}
```

**2. Digest check**

```text
sha256(decode(text)) == capture_sha256
```

**3. Size semantics**

```text
size is decoded bytes, text length is larger
```

## Pitfalls

- Marking text bodies as base64, which makes them unreadable for no reason
- Setting size to the base64 string length and inflating every reported figure
- Dropping the encoding field so viewers render base64 as literal text

## Done when

- binary entries decode to the original bytes with a matching digest
- content size reflects decoded length for every entry

## References

- [W3C - HAR archive format](https://w3c.github.io/web-performance/specs/HAR/Overview.html)
- [RFC 4648 - base64](https://www.rfc-editor.org/rfc/rfc4648.html)
