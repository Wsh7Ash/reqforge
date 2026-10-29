---
name: baseline-candidate-pairing
description: "Keep every test as an explicit baseline and candidate pair so claims rest on a comparison, not an impression. Use when any differential claim is being prepared for a report and needs a control"
pack: reqforge
version: 1.0.0
category: networking
tags: [compare, method, evidence]
---

# Baseline Candidate Pairing

> Keep every test as an explicit baseline and candidate pair so claims rest on a comparison, not an impression

**Use when:** any differential claim is being prepared for a report and needs a control

**Avoid when:** the behaviour is an absolute error such as a stack trace on a public endpoint

## Procedure

1. Capture the expected behaviour first and label it baseline
2. Change exactly one variable and capture the result as candidate
3. State in one sentence what the difference is supposed to prove
4. Verify the pair differs only in the intended variable
5. If the candidate is identical, record the negative result rather than deleting it
6. Attach both files to the finding so a reviewer can recheck the pair

## Signals

- the pair differs in exactly one request field
- the negative result is stored alongside the positive one
- the claim sentence names the variable and the observed effect
- each file name states baseline or candidate

## Patterns

**1. Label in name**

```text
orders-read-baseline.json / orders-read-candidate.json
```

**2. One-variable rule**

```text
only Authorization differs between the pair
```

**3. Negative kept**

```text
candidate identical to baseline -> no finding, retained
```

## Pitfalls

- Reporting a single response as a finding without any control request
- Deleting negative results and losing the evidence that the test was run
- Letting a pair differ in two fields and claiming one caused the effect

## Done when

- every claim references a baseline and a candidate capture
- the differing variable is named explicitly in the notes

## References

- [OWASP WSTG - methodology](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST - evidence integrity](https://csrc.nist.gov/)
