---
name: header-order-and-duplicate-testing
description: "Author requests that vary header order, casing and duplication to expose which layer honours which copy. Use when two components disagree about which duplicate header wins, such as a proxy and an app server"
pack: reqforge
version: 1.0.0
category: networking
tags: [authoring, header-smuggling, parsing]
---

# Header Order and Duplicate Testing

> Author requests that vary header order, casing and duplication to expose which layer honours which copy

**Use when:** two components disagree about which duplicate header wins, such as a proxy and an app server

**Avoid when:** the target stack is known to reject duplicates outright and the program excludes header smuggling

## Procedure

1. Identify a security-relevant header the front end trusts, such as X-Forwarded-For or Authorization
2. Create a variant with the header duplicated, first value trusted and second value attacker chosen
3. Create a second variant reversing the order so the app sees the other copy first
4. Create a third variant that differs only in casing to test case-sensitive lookups
5. Send each variant as its own capture and keep the request bytes with the response
6. Compare which value the response reflects, logs or authorises against

## Signals

- the response reflects one copy while the other copy is ignored entirely
- a 403 changes to a 200 when the duplicate order is reversed
- access logs recorded a different client address than the app enforced
- a header appears twice in the response, hinting the app concatenated both copies

## Patterns

**1. Duplicate X-Forwarded-For**

```text
X-Forwarded-For: 127.0.0.1
X-Forwarded-For: 10.9.9.9
```

**2. Reversed order variant**

```text
X-Forwarded-For: 10.9.9.9
X-Forwarded-For: 127.0.0.1
```

**3. Casing differential**

```text
authorization: Bearer low
Authorization: Bearer high
```

## Pitfalls

- Sending duplicates through a client library that joins them with commas before writing
- Concluding a parser difference from a single order without the reversed control request
- Forgetting that reverse proxies often append rather than replace, changing the tested copy

## Done when

- each ordering variant exists as a separate capture with its own response
- the winning duplicate is named along with the layer that enforced it

## References

- [RFC 9110 - field order](https://www.rfc-editor.org/rfc/rfc9110.html)
- [PortSwigger - HTTP header injection](https://portswigger.net/web-security/request-smuggling)
