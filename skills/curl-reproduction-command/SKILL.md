---
name: curl-reproduction-command
description: "Emit a curl command that reproduces the captured exchange closely enough for a triager to run it. Use when a report needs one copy-paste command rather than an attachment bundle"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, curl, reproduction]
---

# Curl Reproduction Command

> Emit a curl command that reproduces the captured exchange closely enough for a triager to run it

**Use when:** a report needs one copy-paste command rather than an attachment bundle

**Avoid when:** the request depends on a raw socket behaviour curl cannot express, such as duplicate Host headers

## Procedure

1. Render the method, absolute URL and every header in original order
2. Use --path-as-is so traversal sequences survive the client
3. Send the body with --data-binary to avoid newline stripping
4. Omit content length so the client computes it from the actual bytes
5. Mark any value that must be replaced before running, such as a token
6. Run the generated command yourself once and confirm the status matches

## Signals

- the generated command returns the same status as the capture
- path traversal appears literally in the command without normalisation
- the body arrives with embedded newlines intact
- no credential appears in clear text in the command you attach

## Patterns

**1. Faithful flags**

```text
curl -i --path-as-is -X POST --data-binary @body.json
```

**2. Header order**

```text
-H 'Host: api.example.test' -H 'X-Tenant: 42'
```

**3. Placeholder token**

```text
-H 'Authorization: Bearer <TOKEN>'
```

## Pitfalls

- Letting curl follow redirects, which hides the response you meant to show
- Using -d instead of --data-binary and silently stripping trailing newlines
- Attaching a command containing a live token to a report

## Done when

- the emitted command reproduces the captured status when run once
- no live credential remains in the exported command

## References

- [curl - manual](https://curl.se/docs/manpage.html)
- [RFC 9112 - request target](https://www.rfc-editor.org/rfc/rfc9112.html)
