---
name: diff-body-normalised
description: "Normalise volatile values out of both bodies before diffing so the remaining difference is the actual signal. Use when two JSON or HTML bodies differ only by tokens, timestamps or generated identifiers"
pack: reqforge
version: 1.0.0
category: networking
tags: [compare, body, normalisation]
---

# Diff Body Normalised

> Normalise volatile values out of both bodies before diffing so the remaining difference is the actual signal

**Use when:** two JSON or HTML bodies differ only by tokens, timestamps or generated identifiers

**Avoid when:** the identifier itself is the subject, such as an enumeration test over returned ids

## Procedure

1. Identify the volatile fields from repeated identical requests, not from assumption
2. Replace each volatile value with a fixed marker in both bodies
3. Normalise key order for JSON before comparing text
4. Diff the normalised bodies and keep the unnormalised pair for the report
5. Inspect the first difference in context rather than only its offset
6. Confirm that no volatile marker is hiding a real value change

## Signals

- the diff shrinks to a single field that is genuinely different
- a repeated request yields an empty diff, proving the markers are correct
- the remaining difference is a role, an amount or a permission flag
- an HTML diff shows a whole block appearing rather than token noise

## Patterns

**1. Marker substitution**

```text
replace csrf token and timestamp with <VAR> in both bodies
```

**2. Canonical JSON**

```text
sort keys before comparing so ordering is not a difference
```

**3. Self-test**

```text
two identical requests must produce an empty normalised diff
```

## Pitfalls

- Normalising a field that actually carries the finding, such as a role name
- Diffing pretty-printed output against compact output and reporting formatting
- Trusting markers without sending the same request twice as a control

## Done when

- a control pair of identical requests produces an empty diff
- the surviving difference is named as a specific field or block

## References

- [RFC 8259 - JSON](https://www.rfc-editor.org/rfc/rfc8259.html)
- [Python - difflib](https://docs.python.org/3/library/difflib.html)
