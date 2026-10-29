---
name: noise-versus-signal-triage
description: "Classify every observed difference as expected variance, target defect or unknown before it reaches the report. Use when a batch of captures produced many differences and only a few matter"
pack: reqforge
version: 1.0.0
category: networking
tags: [compare, triage, analysis]
---

# Noise Versus Signal Triage

> Classify every observed difference as expected variance, target defect or unknown before it reaches the report

**Use when:** a batch of captures produced many differences and only a few matter

**Avoid when:** a single clear difference already proves the issue and triage adds nothing

## Procedure

1. List every difference found across the capture set
2. Assign each to expected variance, target defect or unknown with a reason
3. Re-test unknowns with a control that isolates the suspected cause
4. Promote a difference to defect only when it changes a security decision
5. Record why each dismissed difference was dismissed
6. Keep the triage table in the results folder for the next session

## Signals

- a difference changes an access decision rather than only content
- the same difference appears for every role, indicating a shared cause
- a difference disappears on re-test, marking it as variance
- a difference correlates with a specific backend, indicating a pool issue

## Patterns

**1. Three-way label**

```text
variance | defect | unknown with a one-line reason
```

**2. Promotion rule**

```text
must change allow/deny or expose data to become a defect
```

**3. Dismissal record**

```text
timestamp difference dismissed: volatile field
```

## Pitfalls

- Promoting cosmetic differences to findings and losing reviewer trust
- Dismissing a difference as variance without re-testing it once
- Losing the triage record so the next session repeats the same work

## Done when

- every difference carries one of the three labels and a reason
- only security-relevant differences remain as candidate findings

## References

- [OWASP - reporting guidance](https://owasp.org/www-project-web-security-testing-guide/)
- [NIST SP 800-115 - testing](https://csrc.nist.gov/pubs/sp/800/115/final)
