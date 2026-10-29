---
name: capture-naming-and-timestamps
description: "Name captures so a later reader can find the exact endpoint, role and variant without opening every file. Use when a session produces dozens of captures that must stay comparable after the fact"
pack: reqforge
version: 1.0.0
category: networking
tags: [capture, workflow, evidence]
---

# Capture Naming and Timestamps

> Name captures so a later reader can find the exact endpoint, role and variant without opening every file

**Use when:** a session produces dozens of captures that must stay comparable after the fact

**Avoid when:** the work is a single throwaway request that will not be revisited

## Procedure

1. Choose a naming scheme of endpoint, role, variant and UTC timestamp
2. Keep the scheme stable for the whole engagement so sorting stays meaningful
3. Write the same identifiers into the capture JSON as structured fields
4. Record the target environment in the name so staging and production never mix
5. Add a session index that lists every capture with its one-line purpose
6. Verify that two captures of the same variant are distinguishable by timestamp only

## Signals

- filenames sort chronologically within a variant
- the environment appears in every filename
- the session index accounts for every capture on disk
- no two captures share a name despite repeated retests

## Patterns

**1. Structured name**

```text
orders-read-admin-baseline-20261028T101500Z.json
```

**2. Index line**

```text
orders-read-admin-baseline -> 200, 1 KB, proves admin read works
```

**3. Environment prefix**

```text
staging_orders-read-admin-….json
```

## Pitfalls

- Naming by sequence only so the file meaning is lost after the session ends
- Mixing environments under one prefix and later sending a staging capture as production proof
- Overwriting on retest, which destroys the earlier state of the target

## Done when

- every capture filename contains endpoint, role, variant and timestamp
- the session index lists all captures with their purpose

## References

- [NIST - incident handling](https://csrc.nist.gov/pubs/sp/800/61/r2/final)
- [OWASP WSTG - reporting](https://owasp.org/www-project-web-security-testing-guide/)
