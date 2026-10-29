---
name: binary-body-preservation
description: "Keep binary bodies byte-exact through capture and export instead of letting text decoding mangle them. Use when a response or request carries images, archives, protobuf or encrypted blobs"
pack: reqforge
version: 1.0.0
category: networking
tags: [capture, binary, encoding]
---

# Binary Body Preservation

> Keep binary bodies byte-exact through capture and export instead of letting text decoding mangle them

**Use when:** a response or request carries images, archives, protobuf or encrypted blobs

**Avoid when:** every body in the engagement is UTF-8 text and binary handling adds no value

## Procedure

1. Detect binary-ness from the content type and from the presence of NUL bytes in the body
2. Store the body as bytes and never decode it into a str for the capture file
3. When embedding in JSON or HAR, base64-encode and mark the encoding explicitly
4. Record the byte length before and after encoding to prove nothing was truncated
5. Verify a round trip by decoding the export and comparing digests
6. Annotate the capture so a human reader knows the text view is not the file

## Signals

- the body digest matches after base64 round trip
- the encoded length equals four thirds of the byte length, rounded up
- no replacement characters appear in the exported text
- the capture declares encoding=base64 wherever text is not literal

## Patterns

**1. Base64 with marker**

```text
"text": "iVBORw0KGgo=", "encoding": "base64"
```

**2. NUL-byte sniff**

```text
is_binary = b'\x00' in body[:4096]
```

**3. Digest round trip**

```text
sha256(body) == sha256(base64.b64decode(encoded))
```

## Pitfalls

- Decoding with errors=replace and silently losing every non-UTF-8 byte
- Using a text-mode file handle on Windows, which rewrites CRLF inside binary data
- Base64-encoding without a marker so readers treat the blob as literal text

## Done when

- the exported body decodes to the original bytes with an identical digest
- the capture states whether the body is literal or base64

## References

- [Python - base64](https://docs.python.org/3/library/base64.html)
- [RFC 4648 - base64 encoding](https://www.rfc-editor.org/rfc/rfc4648.html)
