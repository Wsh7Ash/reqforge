# Changelog

## 1.0.0

First release.

- `send`: raw request file to socket, optional capture pair, unfollowed redirects
- `replay`: N attempts, distinct statuses and body digests, inconclusive on transport errors
- `export`: curl, raw wire bytes, JSONL record
- `har`: raw captures to HAR 1.2, with `--scheme` and `--port` for captures that dropped them
- `diff`: status, sizes, timing and header multiset comparison with a CI-friendly exit code
- 50 validated skills across author, transmit, capture, replay, compare and export
- Corpus harness: byte-deterministic render, SHA-256 manifest, six strength floors
- `#` comment lines in request files; body-less request files without a trailing blank line
- Warning when a declared `Content-Length` disagrees with the body, without altering the bytes
