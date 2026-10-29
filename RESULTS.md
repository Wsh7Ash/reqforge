# Results

Reproducible evidence for every claim in `README.md`. Nothing here is
projected; each block is copied from a run on this machine.

## Environment

- OS: Windows (MSYS2 shell), Python 3.14.3
- Runtime: Python 3.10+ standard library only; `pytest` as dev dependency
- Network: the test suite opens loopback sockets only; no external host is contacted

## Corpus gate

```text
$ python -m reqforge validate
reqforge: 50/50 skills valid
  ok  steps>=6 signals>=4 patterns>=3 pitfalls>=3 words>=180 refs canonical https
```

Phase distribution: `author` 9, `transmit` 8, `capture` 8, `replay` 8, `compare` 8,
`export` 9. 50 unique slugs, 50 unique titles.

## Test suite

```text
$ python -m pytest -q
...............................                                          [100%]
```

31 tests, all passing. The transport tests run against a raw socket fixture
server that records the bytes it received, so header order, duplicate headers
and body bytes are asserted against the wire rather than against a client
library's view.

## Live demo

A local raw socket server answered on loopback; the request came from
`examples/order.http`.

```text
$ reqforge send examples/order.http --host 127.0.0.1 --port 62214 --out results/captures
http://127.0.0.1:62214  POST /v1/orders
HTTP 201 Created  (15.4 ms)
bytes: request=219 response=175
Content-Type: application/json
Location: /v1/orders/8812
Content-Length: 53
Connection: close

{"order_id":8812,"owner":"user-a","status":"created"}
```

Replay, three attempts, identical outcomes:

```text
$ reqforge replay examples/order.http --count 3
attempts=3 statuses=[201] bodies=1 errors=0
  {"attempt": 1, "body_bytes": 53, "body_sha": "7bc8daaac3b4bb7e", "elapsed_ms": 7.13, "status": 201}
  {"attempt": 2, "body_bytes": 53, "body_sha": "7bc8daaac3b4bb7e", "elapsed_ms": 0.54, "status": 201}
  {"attempt": 3, "body_bytes": 53, "body_sha": "7bc8daaac3b4bb7e", "elapsed_ms": 0.48, "status": 201}
stable
```

Curl export keeps the encoded traversal literal and adds `--path-as-is`:

```text
$ reqforge export examples/traversal.http --to curl --host api.example.test
curl -i --path-as-is \
  -H 'Host: api.example.test' \
  -H 'Accept: */*' \
  'http://api.example.test/v1/files/%2e%2e%2f%2e%2e%2fetc%2fpasswd'
```

HAR conversion from the stored raw capture:

```text
$ reqforge har results/captures/order.raw.http --out results/captures/order.har
wrote 1 entries -> results/captures/order.har

har entry: entries=1 status=201 bodySize=53 url=https://127.0.0.1:62214/v1/orders
```

Diff of a capture against itself, which is the control case:

```text
$ reqforge diff results/captures/order.json results/captures/order.json
identical: no status, header or size change  (exit 0)
```

The full transcript is committed at `results/demo_transcript.txt`.

## Generated artifacts

- `results/catalog.md` — the 50-skill index table
- `results/validation.json` — machine-readable gate report
- `results/captures/order.json`, `order.raw.http` — capture pair from the demo
- `results/captures/order.har` — HAR 1.2 export of that capture
- `pack.json` — manifest with a SHA-256 per skill file

## Known limitations

- The transfer layer speaks HTTP/1.1 over TCP or TLS. HTTP/2 framing is out of
  scope by design; a tool that negotiates h2 cannot promise byte fidelity.
- `har` reconstructs an archive from stored raw captures. It cannot recover the
  scheme or port of a capture that dropped them, so `--scheme` and `--port`
  default to `https` and `443`.
- `replay --count` reports stability, not concurrency. It sends sequentially and
  makes no claim about races between parallel requests.
- The corpus gates check structure, length and hygiene. They cannot judge
  whether a procedure is right for a specific target; that remains a reviewer's
  job.
