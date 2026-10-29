---
name: jsonl-append-log
description: "Append one compact JSON record per exchange so a long session stays greppable and cheap to diff. Use when a session runs for hours and captures must be searchable without loading everything in memory"
pack: reqforge
version: 1.0.0
category: networking
tags: [export, jsonl, logging]
---

# Jsonl Append Log

> Append one compact JSON record per exchange so a long session stays greppable and cheap to diff

**Use when:** a session runs for hours and captures must be searchable without loading everything in memory

**Avoid when:** the consumer needs one self-contained archive rather than a stream

## Procedure

1. Define a fixed record schema with target, method, status, sizes and timestamps
2. Write exactly one line per exchange and never rewrite earlier lines
3. Keep field order stable so textual diffs stay readable
4. Include a short body preview rather than the full body
5. Verify every line parses as JSON before closing the session
6. Grep the log for status classes to find anomalies quickly

## Signals

- each line parses independently without context
- line count equals the number of exchanges sent
- a grep for a status code returns only the matching exchanges
- appending during a live session never corrupts earlier records

## Patterns

**1. One line per exchange**

```text
{"target":"/v1/orders","status":200,"ms":41.2}
```

**2. Preview not body**

```text
"body_preview":"{\"items\":[...]}"
```

**3. Parse check**

```text
for line in log: json.loads(line)
```

## Pitfalls

- Pretty-printing each record across multiple lines and breaking line-based tooling
- Storing full bodies and turning a log into a multi-gigabyte file
- Rewriting the file on each append, which risks losing every prior record

## Done when

- every line in the log parses as JSON independently
- line count equals the recorded exchange count for the session

## References

- [JSON Lines format](https://jsonlines.org/)
- [Python - json module](https://docs.python.org/3/library/json.html)
