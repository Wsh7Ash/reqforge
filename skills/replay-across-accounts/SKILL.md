---
name: replay-across-accounts
description: "Replay one captured request with each role's credential to test authorization at the object level. Use when two or more legitimate accounts exist and object ownership must be verified"
pack: reqforge
version: 1.0.0
category: networking
tags: [replay, authorization, accounts]
---

# Replay Across Accounts

> Replay one captured request with each role's credential to test authorization at the object level

**Use when:** two or more legitimate accounts exist and object ownership must be verified

**Avoid when:** only one account is authorised for the engagement and cross-role access is untestable

## Procedure

1. Capture the request with the owner's credential as the working baseline
2. Swap only the credential for the second role and keep every identifier unchanged
3. Send as the second role and record status, body bytes and any data returned
4. Repeat with no credential to separate authentication failure from authorization failure
5. Repeat with a credential that is expired to see whether expiry is enforced
6. Compare the four responses and classify the access decision for that object

## Signals

- the second role receives the owner's data with a 200
- a 404 for the second role while the owner sees 200 leaks object existence
- an anonymous request reaches a cached copy of privileged content
- an expired token is accepted, proving expiry is not checked

## Patterns

**1. Credential swap only**

```text
same path, same body, Authorization replaced
```

**2. Anonymous control**

```text
no Authorization header at all
```

**3. Expired token probe**

```text
token with exp in the past
```

## Pitfalls

- Also changing the object identifier, which turns an authorization test into enumeration
- Assuming a 403 means the control works when the other role is legitimately granted access
- Using accounts created for different tenants and attributing isolation to a role check

## Done when

- each role's response is captured for the identical request bytes
- the access decision per object is stated as allow, deny or unclear

## References

- [OWASP - BOLA](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [RFC 6750 - bearer token usage](https://www.rfc-editor.org/rfc/rfc6750.html)
