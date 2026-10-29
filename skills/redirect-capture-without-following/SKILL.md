---
name: redirect-capture-without-following
description: "Capture redirect responses as terminal facts so each hop can be tested on its own terms. Use when an authentication or routing decision is made at a redirect hop you have not yet inspected"
pack: reqforge
version: 1.0.0
category: networking
tags: [capture, redirects, auth]
---

# Redirect Capture Without Following

> Capture redirect responses as terminal facts so each hop can be tested on its own terms

**Use when:** an authentication or routing decision is made at a redirect hop you have not yet inspected

**Avoid when:** the objective is to walk a normal multi-step login flow end to end

## Procedure

1. Send the request with redirect following disabled at the transport level
2. Capture the 3xx response including every Location and Set-Cookie header
3. Identify the exact URL the redirect names, including query and fragment handling
4. Send the follow-up request manually so the hop is a separate capture
5. Test the redirect target directly to see whether it enforces the same checks
6. Record whether the Location value reflects user input, which is the open-redirect signal

## Signals

- the Location header contains an attacker-controlled host or scheme
- the redirect target is reachable without the credential the redirect implies
- Set-Cookie appears on the redirect hop, indicating session material issued before auth
- the redirect chain changes host, exposing a trust boundary crossing

## Patterns

**1. Location reflection**

```text
Location: https://app.example.test/?next=//evil.example
```

**2. Hop as its own capture**

```text
302 captured, then GET /dashboard sent manually
```

**3. Session issued early**

```text
Set-Cookie: sid=… on a 302 from /login
```

## Pitfalls

- Letting the client follow redirects automatically and losing the decision point
- Assuming a 302 to login means the request was rejected rather than processed first
- Ignoring fragment handling, which some redirectors pass through untouched

## Done when

- the 3xx hop is stored with its headers before any follow-up request
- the follow-up hop exists as a separate capture with its own status

## References

- [RFC 9110 - redirection](https://www.rfc-editor.org/rfc/rfc9110.html)
- [OWASP - unvalidated redirects](https://cheatsheetseries.owasp.org/)
