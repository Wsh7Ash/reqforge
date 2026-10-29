---
name: har-entry-shape
description: "Build HAR 1.2 entries from the captured bytes so a reviewer can import the transcript into familiar tooling. Use when an exchange must be shared in a format browsers and analysis tools already read"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, har, interoperability]
---

# Har Entry Shape

> Build HAR 1.2 entries from the captured bytes so a reviewer can import the transcript into familiar tooling

**Use when:** an exchange must be shared in a format browsers and analysis tools already read

**Avoid when:** the consumer only needs a single curl command and HAR overhead adds nothing

## Procedure

1. Create the log object with version 1.2 and a creator block naming your tool
2. For each exchange, write startedDateTime, time and a request object
3. Fill request method, absolute url, httpVersion, headers and queryString
4. Fill the response status, statusText, headers and content block
5. Set headers and body sizes from the captured lengths rather than estimates
6. Validate the output with a JSON parser and one real import before shipping it

## Signals

- the HAR opens in a browser developer tools network panel
- entry count equals the number of captures included
- sizes in the file match the raw capture byte counts
- query parameters are split from the path exactly as sent

## Patterns

**1. Log envelope**

```text
{"log":{"version":"1.2","creator":{...},"entries":[]}}
```

**2. Sizes from capture**

```text
headersSize = raw_len - body_len
```

**3. Absolute url**

```text
https://api.example.test:8443/v1/orders?page=2
```

## Pitfalls

- Guessing sizes instead of deriving them from the captured byte counts
- Omitting the creator block, which some importers reject as invalid
- Writing a relative URL, which breaks the entry in every HAR viewer

## Done when

- the HAR parses and imports with the expected number of entries
- sizes in the HAR match the raw captures byte for byte

## References

- [W3C - HAR archive format](https://w3c.github.io/web-performance/specs/HAR/Overview.html)
- [Chrome DevTools - HAR import](https://developer.chrome.com/docs/devtools/network/)
