# reqforge

Send, capture, replay, compare and export raw HTTP exchanges without a proxy.
One stdlib-only CLI, plus **50 validated skill files** for the whole
request-authoring to evidence-export workflow.

Burp and friends are excellent, but they sit between you and the socket: they
normalise, follow redirects, reorder headers and rewrite bodies. When the bug
lives in exactly that normalisation, you need a tool that transmits the bytes
you wrote and nothing else. That is all reqforge does.

```text
reqforge send  order.http --host 127.0.0.1 --port 8080 --out captures/
reqforge replay order.http --host api.example.test --port 443 -count 5
reqforge export order.http --to curl --host api.example.test
reqforge export order.http --to jsonl
reqforge har captures/order.raw.http --out captures/orders.har
reqforge diff captures/baseline.json captures/candidate.json
```

## Why this exists

| Problem | What an intercepting proxy does | What reqforge does |
|---|---|---|
| You want the exact header order | Reorders by its own model | Writes headers in file order |
| You want a 302 as a fact | Follows it | Stores it, reports `redirect: <target>` |
| You want duplicate `X-Forwarded-For` | May merge or drop | Sends both, in order |
| You want the raw response bytes | Re-renders | Saves the captured octets and a SHA-256 |
| You want machine-readable output | Vendor format | HAR 1.2, JSONL, curl, `.raw.http` |
| You want it scriptable in CI | GUI-bound | Exit codes, `--json`, no network in tests |

## Commands

| Command | Purpose |
|---|---|
| `send FILE` | Transmit one raw request, print status/headers/body, optionally write captures |
| `replay FILE --count N` | Send N times, report distinct statuses, body digests and stability |
| `export FILE --to curl\|raw\|jsonl` | Emit a reproduction command, wire bytes or a JSON record |
| `har FILE...` | Convert `.raw.http` captures into a HAR 1.2 archive |
| `diff A B` | Compare two capture JSONs: status, sizes, headers added/removed/changed |
| `validate` | Run every corpus rule and check generated files match the source |
| `list` / `show` / `search` | Browse the 50 skills by phase, tag or keyword |
| `build` | Regenerate `skills/`, `pack.json` and `results/` |

Global flags worth knowing: `--host`, `--port`, `--scheme`,
`--connect-timeout`, `--read-timeout`, `--preview`, `--json`, `--out`.

## Request files

A request file is what a proxy's request pane shows you, comments welcome:

```text
# placeholders: host
POST /v1/orders HTTP/1.1
Host: api.example.test
Content-Type: application/json
X-Forwarded-For: 10.0.0.1
X-Forwarded-For: 127.0.0.1
Content-Length: 40

{"sku":"A-1","quantity":1,"note":"x"}
```

Lines starting with `#` never reach the wire. A file with no body needs no
trailing blank line. The only bytes added at send time are those framing
requires: a `Host` header when the file has none, and `Content-Length` when a
body exists without a length or `Transfer-Encoding`.

## The 50 skills

Six phases, roughly balanced, each skill a self-contained procedure with
signals, code patterns, pitfalls and done-when criteria:

| Phase | Skills | Covers |
|---|---|---|
| `author` | 9 | Request-line fidelity, header order and duplicates, framing, content-type mismatch, credential matrices, templates, malformed-but-parseable lines, hop-by-hop headers |
| `transmit` | 8 | Raw socket send, timeouts, partial responses, SNI vs Host, absolute-form through a proxy, IP/port literals, head-then-body reads, early responses |
| `capture` | 8 | Verbatim captures, framing decode, binary preservation, naming, metadata minimums, redirects as facts, transport failures as evidence, multi-step transcripts |
| `replay` | 8 | Determinism, single-variable mutation, pacing, cross-account swaps, variance reports, post-revocation replay, method sweeps, byte-preserving bodies |
| `compare` | 8 | Status and size, header sets, normalised bodies, across hosts, baseline/candidate pairing, noise triage, CI regression gates, timing interpretation |
| `export` | 9 | HAR entries, binary base64, DevTools import, curl reproduction, shell quoting, JSONL logs, report transcripts, finding evidence, redaction |

```text
reqforge list --phase export
reqforge search har binary
reqforge show curl-safe-quoting
```

Every skill is generated from a Python corpus dict, rendered byte
deterministically, hashed into `pack.json`, and re-checked by `validate`, so
the committed `SKILL.md` files cannot drift from the source of truth.

## Install

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
reqforge send examples/order.http --host 127.0.0.1 --port 8080
```

Python 3.10+. No runtime dependencies, no network access in the test suite.

## Scope and safety

reqforge is a client. It sends whatever you point it at, exactly as written,
with no rate limiting of its own beyond `--count`. Only use it against systems
you are authorised to test; `SECURITY.md` states the same in more detail.

## Layout

```text
src/reqforge/httpmsg.py    parse/serialise requests and responses
src/reqforge/transport.py  socket transport, one exchange per call
src/reqforge/export.py     HAR, curl, JSONL, raw transcript, diff
src/reqforge/cli.py        send / replay / export / har / diff + corpus commands
src/reqforge/corpus/       50 skills authored as dicts (part1..part3)
src/reqforge/validate.py   structure, strength and hygiene floors
skills/<slug>/SKILL.md     generated, committed, hash-checked
```

MIT licensed.
