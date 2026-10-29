---
name: har-devtools-import
description: "Verify an exported HAR by importing it into a browser before attaching it to a report. Use when a capture set is about to be shared with a client or another tester"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, har, verification]
---

# Har Devtools Import

> Verify an exported HAR by importing it into a browser before attaching it to a report

**Use when:** a capture set is about to be shared with a client or another tester

**Avoid when:** the consumer has an established format other than HAR

## Procedure

1. Open the browser developer tools network panel with an empty recording
2. Import the HAR file and check that every entry appears once
3. Open one entry and confirm request headers, response headers and body are intact
4. Check that the timing column is populated rather than zero everywhere
5. Look for header values that were truncated during export
6. Fix the exporter and re-import rather than shipping an unreadable archive

## Signals

- entry count in the viewer equals the capture count
- request headers in the viewer match the raw request file
- response bodies render as documents rather than empty panels
- no entry shows an error about unsupported encoding

## Patterns

**1. Round-trip check**

```text
capture -> har -> browser import -> compare header counts
```

**2. Body visible**

```text
response tab shows the JSON body, not a blank pane
```

**3. Timing present**

```text
wait time equals the recorded elapsed_ms
```

## Pitfalls

- Shipping a HAR that no viewer can open because of an invalid envelope
- Importing with an active recording and merging live traffic into the archive
- Trusting the file extension instead of performing one real import

## Done when

- the HAR imports in a browser with the expected entry count
- one entry's headers and body are visually compared against the raw capture

## References

- [Chrome DevTools - network analysis](https://developer.chrome.com/docs/devtools/network/)
- [W3C - HAR archive format](https://w3c.github.io/web-performance/specs/HAR/Overview.html)
