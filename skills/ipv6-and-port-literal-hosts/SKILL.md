---
name: ipv6-and-port-literal-hosts
description: "Address hosts by literal IP and explicit port to bypass name-based controls and confirm which authority is enforced. Use when access rules are hostname-based and the hypothesis is that a direct address bypasses them"
pack: reqforge
version: 1.0.0
category: networking
tags: [transmit, addressing, bypass]
---

# IPv6 and Port Literal Hosts

> Address hosts by literal IP and explicit port to bypass name-based controls and confirm which authority is enforced

**Use when:** access rules are hostname-based and the hypothesis is that a direct address bypasses them

**Avoid when:** the program explicitly excludes direct-to-IP testing or the origin is unreachable by address

## Procedure

1. Resolve the hostname and record the addresses the target actually answers on
2. Send the normal hostname request as the control and keep its status and body
3. Send the same request with the IP in both the connection and the Host header
4. Send a variant with the IP for the connection and the hostname in Host, then the reverse
5. Test IPv6 literal syntax in brackets to check address parsing in the edge
6. Compare all responses to determine which layer applied the hostname restriction

## Signals

- the IP-addressed request succeeds where the hostname request was denied
- a certificate mismatch warning shows the edge expects the hostname only
- a 421 or 404 for the IP form proves hostname-based virtual hosting
- IPv6 literal requests fail to parse, indicating an address-family gap in the edge

## Patterns

**1. IP in connection and Host**

```text
GET /admin HTTP/1.1
Host: 203.0.113.10
```

**2. Split authority**

```text
connect 203.0.113.10:443 | Host: app.example.test
```

**3. IPv6 literal**

```text
GET /admin HTTP/1.1
Host: [2001:db8::10]
```

## Pitfalls

- Bypassing a WAF and then reporting it as an application access control defect
- Forgetting that virtual hosting legitimately returns a default site for bare IPs
- Leaving out the hostname control request so the comparison proves nothing

## Done when

- address and Host pairings are captured with the responding layer identified
- any bypass is described as an edge control gap rather than an app bug

## References

- [RFC 3986 - host syntax](https://www.rfc-editor.org/rfc/rfc3986.html)
- [RFC 4291 - IPv6 addressing](https://www.rfc-editor.org/rfc/rfc4291.html)
