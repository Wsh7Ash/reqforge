"""Raw HTTP/1.1 message parsing that preserves what the hunter actually wrote.

Nothing here normalises casing, reorders headers, rewrites the request target
or re-encodes the body. A request typed by hand is transmitted byte for byte,
because duplicate headers, odd casing and malformed-but-accepted framing are
exactly what a lot of server-side bugs live in.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Sequence

CRLF = b"\r\n"
HEADER_END = b"\r\n\r\n"


class MessageError(ValueError):
    """Raised when the raw text cannot be read as an HTTP message."""


@dataclass(frozen=True)
class Request:
    """A raw HTTP request: request line, ordered headers, raw body bytes."""

    method: str
    target: str
    version: str
    headers: tuple[tuple[str, str], ...]
    body: bytes = b""

    @property
    def host_header(self) -> str:
        for name, value in self.headers:
            if name.lower() == "host":
                return value.strip()
        return ""

    def get_all(self, name: str) -> list[str]:
        lowered = name.lower()
        return [value for key, value in self.headers if key.lower() == lowered]

    def get(self, name: str, default: str = "") -> str:
        values = self.get_all(name)
        return values[-1] if values else default

    def has(self, name: str) -> bool:
        return bool(self.get_all(name))

    def with_header(self, name: str, value: str) -> "Request":
        """Replace the first occurrence of ``name`` in place, or append it."""
        lowered = name.lower()
        out: list[tuple[str, str]] = []
        replaced = False
        for key, existing in self.headers:
            if key.lower() == lowered and not replaced:
                out.append((key, value))
                replaced = True
            else:
                out.append((key, existing))
        if not replaced:
            out.append((name, value))
        return replace(self, headers=tuple(out))

    def without_header(self, name: str) -> "Request":
        lowered = name.lower()
        return replace(
            self, headers=tuple((k, v) for k, v in self.headers if k.lower() != lowered)
        )


@dataclass(frozen=True)
class Response:
    """A decoded HTTP response plus the exact bytes that arrived on the wire."""

    status: int
    reason: str
    version: str
    headers: tuple[tuple[str, str], ...]
    body: bytes
    raw: bytes

    def get_all(self, name: str) -> list[str]:
        lowered = name.lower()
        return [value for key, value in self.headers if key.lower() == lowered]

    def get(self, name: str, default: str = "") -> str:
        values = self.get_all(name)
        return values[-1] if values else default

    @property
    def body_text(self) -> str:
        charset = "utf-8"
        for part in self.get("content-type").split(";"):
            part = part.strip()
            if part.lower().startswith("charset="):
                charset = part.split("=", 1)[1].strip() or "utf-8"
        try:
            return self.body.decode(charset, errors="replace")
        except LookupError:
            return self.body.decode("utf-8", errors="replace")


def _split_head(raw: bytes, *, strict: bool = True) -> tuple[bytes, bytes]:
    index = raw.find(HEADER_END)
    if index == -1:
        # Tolerate bare-LF files saved by hand or copied out of a terminal.
        index = raw.find(b"\n\n")
        if index == -1:
            if strict:
                raise MessageError("no blank line separating head from body")
            # A body-less request file may end at the last header line.
            return raw, b""
        return raw[:index], raw[index + 2 :]
    return raw[:index], raw[index + len(HEADER_END) :]


def _head_lines(head: bytes) -> list[str]:
    text = head.replace(CRLF, b"\n").decode("latin-1")
    # Lines starting with # are authoring comments, the same convention .http
    # files use, and never reach the wire.
    return [
        line for line in text.split("\n") if line.strip() and not line.lstrip().startswith("#")
    ]


def _parse_headers(lines: Iterable[str]) -> tuple[tuple[str, str], ...]:
    headers: list[tuple[str, str]] = []
    for line in lines:
        if line[:1] in (" ", "\t") and headers:
            # Obsolete line folding: keep the bytes with the header that owns them.
            name, value = headers[-1]
            headers[-1] = (name, f"{value} {line.strip()}")
            continue
        if ":" not in line:
            raise MessageError(f"header without a colon: {line!r}")
        name, value = line.split(":", 1)
        headers.append((name.strip(), value.strip()))
    return tuple(headers)


def parse_request(text: str | bytes) -> Request:
    """Read a request written the way a proxy's request pane shows it."""
    raw = text.encode("utf-8") if isinstance(text, str) else text
    if not raw.strip():
        raise MessageError("request file is empty")
    head, body = _split_head(raw, strict=False)
    lines = _head_lines(head)
    if not lines:
        raise MessageError("request has no request line")
    parts = lines[0].split()
    if len(parts) == 2:
        method, target = parts
        version = "HTTP/1.1"
    elif len(parts) == 3:
        method, target, version = parts
    else:
        raise MessageError(f"unreadable request line: {lines[0]!r}")
    if not version.upper().startswith("HTTP/"):
        raise MessageError(f"not an HTTP version: {version!r}")
    # A trailing blank line inside the body block is content, never separator noise.
    return Request(
        method=method,
        target=target,
        version=version,
        headers=_parse_headers(lines[1:]),
        body=body,
    )


def serialize_request(request: Request, *, host: str | None = None) -> bytes:
    """Render the request for the wire, optionally overriding the Host header.

    The only bytes added are those the framing needs: a Host header when the
    file has none and the caller supplied one, and Content-Length when a body
    is present and no length or Transfer-Encoding header exists.
    """
    outgoing = request
    if host:
        if outgoing.has("host"):
            outgoing = outgoing.with_header("Host", host)
        else:
            outgoing = outgoing.with_header("Host", host)
    if (
        outgoing.body
        and not outgoing.has("content-length")
        and not outgoing.has("transfer-encoding")
    ):
        outgoing = outgoing.with_header("Content-Length", str(len(outgoing.body)))

    lines = [f"{outgoing.method} {outgoing.target} {outgoing.version}"]
    lines.extend(f"{name}: {value}" for name, value in outgoing.headers)
    head = ("\r\n".join(lines) + "\r\n\r\n").encode("latin-1", errors="replace")
    return head + outgoing.body


def endpoint(request: Request, default_host: str = "", default_port: int = 0) -> tuple[str, str, int]:
    """Resolve (scheme, host, port) from the target and Host header."""
    scheme = "https" if default_port == 443 else "http"
    host = default_host or request.host_header
    if request.target.startswith(("http://", "https://")):
        body = request.target.split("://", 1)[1]
        authority = body.split("/", 1)[0]
        scheme = request.target.split("://", 1)[0].lower()
        host = authority
    if ":" in host:
        hostname, _, maybe_port = host.rpartition(":")
        if maybe_port.isdigit():
            host, default_port = hostname, int(maybe_port)
    return scheme, host, default_port or (443 if scheme == "https" else 80)


def decode_chunked(body: bytes) -> bytes:
    """Decode a chunked body so exports show content instead of framing."""
    out = bytearray()
    position = 0
    while position < len(body):
        line_end = body.find(CRLF, position)
        if line_end == -1:
            return bytes(out) + body[position:]
        size_text = body[position:line_end].split(b";")[0].strip()
        try:
            size = int(size_text, 16)
        except ValueError:
            return bytes(out) + body[position:]
        position = line_end + 2
        if size == 0:
            return bytes(out)
        out.extend(body[position : position + size])
        position += size + 2
    return bytes(out)


def parse_response(raw: bytes) -> Response:
    """Split a response into status, ordered headers, body and original bytes."""
    if not raw:
        raise MessageError("empty response")
    head, body = _split_head(raw)
    lines = _head_lines(head)
    if not lines:
        raise MessageError("response has no status line")
    status_line = lines[0]
    parts = status_line.split(" ", 2)
    if len(parts) < 2:
        raise MessageError(f"unreadable status line: {status_line!r}")
    version = parts[0]
    try:
        status = int(parts[1])
    except ValueError as exc:
        raise MessageError(f"status code is not numeric: {parts[1]!r}") from exc
    reason = parts[2] if len(parts) > 2 else ""
    headers = _parse_headers(lines[1:])

    transfer = ""
    length = ""
    for name, value in headers:
        if name.lower() == "transfer-encoding":
            transfer = value.lower()
        if name.lower() == "content-length":
            length = value.strip()
    if "chunked" in transfer:
        body = decode_chunked(body)
    elif length.isdigit() and len(body) > int(length):
        # Never trust a longer capture than the framing declares.
        body = body[: int(length)]
    return Response(
        status=status,
        reason=reason,
        version=version,
        headers=headers,
        body=body,
        raw=raw,
    )


def header_map(headers: Sequence[tuple[str, str]]) -> dict[str, list[str]]:
    """Group headers case-insensitively while keeping every value."""
    out: dict[str, list[str]] = {}
    for name, value in headers:
        out.setdefault(name.lower(), []).append(value)
    return out
