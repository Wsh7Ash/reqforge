---
name: curl-safe-quoting
description: "Quote generated shell commands so header values and payloads survive a shell instead of being expanded. Use when an exported command will be pasted into a shell by someone else"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, shell, safety]
---

# Curl Safe Quoting

> Quote generated shell commands so header values and payloads survive a shell instead of being expanded

**Use when:** an exported command will be pasted into a shell by someone else

**Avoid when:** the command is only an internal intermediate that is never copy-pasted

## Procedure

1. Wrap every dynamic value in single quotes
2. Escape embedded single quotes with the close-escape-reopen pattern
3. Reject values containing NUL bytes instead of emitting a broken command
4. Avoid interpolation by never using double quotes around user-derived values
5. Print a placeholder for secrets rather than the value itself
6. Test the command with a value containing a quote, a dollar sign and a backtick

## Signals

- a value with a single quote still round-trips through the shell intact
- dollar signs and backticks are transmitted literally, not expanded
- the command fails loudly on a NUL byte instead of truncating
- secrets appear as placeholders in the output

## Patterns

**1. Single-quote escaping**

```text
'value with '\'' quote'
```

**2. Literal metacharacters**

```text
-H 'X-Test: $(whoami) `id`'
```

**3. NUL rejection**

```text
raise on '\x00' before emitting the command
```

## Pitfalls

- Using double quotes and letting a header value expand as a command substitution
- Forgetting the JSON body needs quoting too, not just the headers
- Printing a real bearer token because the template was filled in place

## Done when

- a hostile value round-trips through the shell without execution
- secrets are replaced by clear placeholders in every emitted command

## References

- [POSIX shell quoting](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- [curl - manual](https://curl.se/docs/manpage.html)
