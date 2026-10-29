# Usage

## Install

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

Without installing, `PYTHONPATH=src python -m reqforge ...` works too.

## Send one request

```bash
reqforge send examples/order.http --host 127.0.0.1 --port 8080
```

Output is the resolved target, status line, elapsed time, byte counts, response
headers and a body preview limited by `--preview` (default 2000 characters).
With `--out DIR` two files are written:

| File | Contents |
|---|---|
| `<name>.raw.http` | `### REQUEST ###` / `### RESPONSE ###` transcript, byte faithful |
| `<name>.json` | summary: host, port, scheme, status, sizes, headers, timing, redirect |

`--json` prints the same summary to stdout, plus `body_preview`.

## Redirects stay visible

A 3xx is never followed. The summary carries `redirect_target` and the human
output prints `redirect: <location> (not followed)`, so the hop can be tested
on its own terms afterwards.

## Replay for stability

```bash
reqforge replay examples/order.http --count 5 --host api.example.test --port 443
```

Reports `distinct_statuses`, `distinct_bodies`, `errors` and one line per
attempt with a short body digest. A run with transport errors is reported as
`inconclusive`, never `stable`.

## Export

```bash
reqforge export examples/order.http --to curl --host api.example.test --scheme https --port 443
reqforge export examples/order.http --to jsonl
reqforge export examples/order.http --to raw      # exact wire bytes
```

The curl command uses `--path-as-is` (traversal survives), `--data-binary`
(newlines survive) and omits `Content-Length` so the client recomputes it.
Values are single-quoted with the close-escape-reopen pattern, so
`$(whoami)` in a header stays literal instead of executing.

## Compare captures

```bash
reqforge diff captures/orders-as-user.json captures/orders-as-admin.json
reqforge diff before.json after.json --json
```

Exit code is 0 when identical and 1 when anything differs, which is what makes
it usable as a gate. Fields compared: status, reason, body bytes, response
bytes, scheme, host, port, method, target, elapsed time, plus header
additions, removals and changes.

## HAR for a report

```bash
reqforge har results/captures/*.raw.http --out results/orders.har --scheme https --port 443
```

The archive is HAR 1.2 and imports into browser developer tools. Sizes come
from the captured byte counts; binary bodies are base64 with `encoding` set.

## Browse the skills

```bash
reqforge list
reqforge list --phase export --json
reqforge search har binary
reqforge show curl-safe-quoting
```

Skills are also plain files at `skills/<slug>/SKILL.md`, ready for Claude Code,
opencode, or any runtime that loads skill directories.

## Regenerate artifacts

```bash
reqforge build
```

Rewrites `skills/`, `pack.json`, `results/catalog.md` and
`results/validation.json`. Output is byte deterministic: running it twice
produces identical files, and CI fails if a committed file differs from a
fresh render.

## Operational notes

- Always set `--connect-timeout` and `--read-timeout` when looping over many
  hosts; a filtered port otherwise stalls the batch.
- A `warning: Content-Length X but body is Y bytes` line means the file is
  internally inconsistent. It is sent as written on purpose: fixing it
  silently would defeat framing tests.
- Captures contain live credentials if the request had any. Redact before
  attaching them anywhere; `reqforge export --to raw` does not redact.
