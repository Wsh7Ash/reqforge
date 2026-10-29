---
name: sni-and-host-header-divergence
description: "Send a TLS server name that differs from the Host header to see which layer decides routing and certificates. Use when a shared edge terminates TLS for many tenants and tenant isolation is part of the scope"
pack: reqforge
version: 1.0.0
category: networking
tags: [transmit, tls, virtual-hosting]
---

# SNI and Host Header Divergence

> Send a TLS server name that differs from the Host header to see which layer decides routing and certificates

**Use when:** a shared edge terminates TLS for many tenants and tenant isolation is part of the scope

**Avoid when:** the target is a single-tenant host where the certificate and host header must match by design

## Procedure

1. Confirm the certificate presented for the intended server name as the control
2. Connect with the intended SNI and send a Host header for a different tenant on the same edge
3. Repeat with the SNI pointing at the tenant and the Host header at the original host
4. Record the certificate subject and the response body for both orders
5. Determine whether routing follows SNI, Host, or a mixture of both
6. Stop if any variant returns another tenant's data, and preserve the capture unmodified

## Signals

- a certificate for one tenant is served while the Host header names another
- the response body belongs to the host named in Host while the TLS session names a different tenant
- a 421 or 400 appears only when SNI and Host disagree, proving the edge checks both
- the same path returns different applications depending solely on the SNI value

## Patterns

**1. Divergent pair**

```text
SNI: tenant-a.edge.example | Host: tenant-b.edge.example
```

**2. Reverse order control**

```text
SNI: tenant-b.edge.example | Host: tenant-a.edge.example
```

**3. Edge rejection cue**

```text
HTTP/1.1 421 Misdirected Request
```

## Pitfalls

- Testing tenant isolation without written authorisation covering both tenants
- Comparing responses without recording which SNI produced which certificate
- Assuming a 421 means isolation is intact rather than that only one pairing is checked

## Done when

- each SNI and Host pairing has a capture with certificate subject recorded
- the routing decision point is named as SNI, Host, or both

## References

- [RFC 6066 - server name indication](https://www.rfc-editor.org/rfc/rfc6066.html)
- [Python - ssl server_hostname](https://docs.python.org/3/library/ssl.html)
