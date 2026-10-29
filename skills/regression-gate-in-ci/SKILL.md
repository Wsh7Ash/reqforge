---
name: regression-gate-in-ci
description: "Turn a stored baseline into a CI gate that fails when a rewritten rule starts letting a denied request through. Use when a client wants the fix to stay fixed across future deploys of their own stack"
pack: reqforge
version: 1.0.0
category: networking
tags: [compare, ci, regression]
---

# Regression Gate in Ci

> Turn a stored baseline into a CI gate that fails when a rewritten rule starts letting a denied request through

**Use when:** a client wants the fix to stay fixed across future deploys of their own stack

**Avoid when:** the target is a third-party program where CI access is impossible or out of scope

## Procedure

1. Choose the smallest request that must remain denied
2. Store it as a fixture with the expected status recorded
3. Send it against the target in CI with credentials from secrets only
4. Fail the job when the status differs from the recorded expectation
5. Emit the capture as a build artifact so failures are diagnosable
6. Keep the fixtures in version control and require review on change

## Signals

- the job fails only when the expectation is violated
- artifacts contain the raw request and response for each failure
- credentials never appear in the repository or the logs
- the fixture set is small enough to run on every commit

## Patterns

**1. Expectation file**

```text
{"request": "req.http", "expect_status": 403}
```

**2. Artifact upload**

```text
actions/upload-artifact with captures/
```

**3. Secret injection**

```text
token read from env in CI only, never committed
```

## Pitfalls

- Committing a live token into the fixture so the gate cannot run safely
- Asserting an exact body string that changes on every deploy
- Running against production on every commit without rate limiting

## Done when

- the gate fails on an intentional expectation mismatch in a local run
- no credential material appears in the repository or the logs

## References

- [GitHub Actions - workflow syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [OWASP - CI/CD security](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
