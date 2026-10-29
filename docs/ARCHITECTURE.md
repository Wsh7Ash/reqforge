# Architecture

Four layers, each with one job, so byte fidelity is never accidental.

## 1. Message layer — `httpmsg.py`

`parse_request` reads a request the way a proxy pane shows it and keeps:

- the request line exactly as written,
- headers in arrival order, duplicates included, casing untouched,
- the body as raw bytes,
- `#` comment lines only as authoring aids, never on the wire.

`serialize_request` re-emits those bytes and adds only what framing requires.
`parse_response` splits status, headers, body and keeps `raw` so a capture can
be replayed into a HAR without a second network call. Obsolete line folding is
preserved by joining continuation lines onto the header that owns them.

## 2. Transport layer — `transport.py`

One call, one exchange: connect (with timeout), optional TLS with the real
server name for SNI, `sendall` of the serialised bytes, read the head until the
terminator, then read the body according to `Transfer-Encoding`,
`Content-Length` or connection close.

Deliberately absent: redirect following, decompression, retries, pooling,
header injection beyond framing. Each of those hides server behaviour that a
tester is usually trying to observe.

Failures are typed. `TransportError` carries the phase text (`connect`,
`write`, `read head`, `read body`) so a caller can store a failure as evidence
instead of losing it in a traceback.

## 3. Export layer — `export.py`

Pure functions over a captured `Exchange`:

- `har_entry` — HAR 1.2 entry with sizes derived from the captured lengths
  (never guessed) and base64 marked explicitly for binary bodies,
- `to_curl` — a reproduction command with `--path-as-is` and `--data-binary`,
  with `Content-Length` omitted so the client recomputes it,
- `to_jsonl` — one compact record per exchange, safe to append,
- `to_raw` — the labelled request/response transcript used in reports,
- `diff_summaries` — status, size, timing and header multiset comparison.

## 4. Corpus layer — `corpus/`, `render.py`, `validate.py`

Skills are Python dicts in three parts. `render_skill` is a pure function, so
the same corpus always produces byte-identical markdown; CR bytes inside code
blocks are shown as visible escapes so files stay line-ending independent.
`build_pack` writes `skills/`, `pack.json` (SHA-256 per file) and
`results/catalog.md`.

`validate.py` enforces the floors that make "50/50 valid" meaningful: at least
six steps, four signals, three patterns, three pitfalls, two done-when items,
one canonical https reference, 180 rendered words, no placeholder tokens, no
machine-local paths, unique slugs and titles, exact skill count.

## Data flow for one test

```text
order.http ──parse──▶ Request ──serialize──▶ bytes ──socket──▶ server
                        │                                      │
                        │◀────────────── raw response bytes ◀──┘
                        ▼
                   Exchange ──▶ captures/*.json  (summary)
                        │      captures/*.raw.http (transcript)
                        ├──▶ HAR 1.2 (attachment)
                        ├──▶ curl (reproduction)
                        └──▶ diff (baseline vs candidate)
```

## Test strategy

The suite runs a raw socket fixture server in a thread that records the exact
bytes it receives. That makes fidelity assertions real rather than
theoretical: header order, duplicate headers and body bytes are compared
against what the server saw, not against what a client library reported.

No test touches the network, so CI is deterministic and safe to run anywhere.
