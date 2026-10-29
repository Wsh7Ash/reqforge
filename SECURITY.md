# Security

## What this tool does

reqforge transmits HTTP requests you author, byte for byte, to a host you
specify. It has no discovery, no wordlists, no exploitation payloads and no
scheduled activity. It is a client, and the operator decides the target.

## Authorised use only

Use it exclusively against systems you own or have written permission to test,
and stay inside the published scope of any bug-bounty programme. Nothing in
this repository grants that permission. Requests sent through reqforge are
logged by the target the same way any client's traffic is.

## Recommended operating rules

- Run against a scoped target list, not an address range.
- Keep `--count` small on `replay`; it deliberately has no internal rate limiter.
- Store captures outside the repository if they contain live credentials.
- Redact tokens, cookies and personal data before attaching a capture to a
  report, ticket or chat message.

## Reporting a vulnerability in this tool

If you find a defect in reqforge itself, open a private security advisory on
the repository rather than a public issue. Include the version, the request
file that triggers it, and the observed response. Never include live
credentials in a report.

## Data handling

The tool writes only the files you ask for: a `.raw.http` transcript and a
`.json` summary under `--out`, plus generated skill files during `build`. It
does not phone home, does not collect telemetry, and has no runtime
dependencies beyond the Python standard library.
