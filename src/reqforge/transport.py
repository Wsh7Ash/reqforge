"""Socket-level HTTP transport: one request in, one raw response out.

The transport deliberately implements none of the client features that hide
server behaviour: no redirect following, no automatic decompression, no header
injection beyond framing, no connection pool, no retry. What the file says is
what goes on the wire.
"""

from __future__ import annotations

import socket
import ssl
import time
from dataclasses import dataclass, field
from typing import Any

from .httpmsg import Request, Response, endpoint, parse_response, serialize_request


class TransportError(RuntimeError):
    """A connection, TLS or read failure the caller must see verbatim."""


@dataclass
class Exchange:
    """One request/response pair, with the bytes preserved on both sides."""

    request: Request
    request_bytes: bytes
    response: Response
    host: str
    port: int
    scheme: str
    elapsed_ms: float
    sent_at: str
    redirect_target: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        return {
            "scheme": self.scheme,
            "host": self.host,
            "port": self.port,
            "method": self.request.method,
            "target": self.request.target,
            "sent_at": self.sent_at,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "request_bytes": len(self.request_bytes),
            "status": self.response.status,
            "reason": self.response.reason,
            "response_bytes": len(self.response.raw),
            "body_bytes": len(self.response.body),
            "headers": [[name, value] for name, value in self.response.headers],
            "redirect_target": self.redirect_target,
        }


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _connect(host: str, port: int, scheme: str, timeout: float) -> socket.socket:
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
    except OSError as exc:
        raise TransportError(f"connect {host}:{port} failed: {exc}") from exc
    if scheme == "https":
        context = ssl.create_default_context()
        try:
            sock = context.wrap_socket(sock, server_hostname=host)
        except ssl.SSLError as exc:
            sock.close()
            raise TransportError(f"tls handshake with {host} failed: {exc}") from exc
    return sock


def _read_head(sock: socket.socket) -> bytes:
    buffer = b""
    while b"\r\n\r\n" not in buffer and b"\n\n" not in buffer:
        try:
            chunk = sock.recv(65536)
        except socket.timeout as exc:
            raise TransportError("timed out while reading response head") from exc
        if not chunk:
            break
        buffer += chunk
        if len(buffer) > 4 * 1024 * 1024:
            raise TransportError("response head exceeded 4 MiB without a terminator")
    return buffer


def _read_body(sock: socket.socket, buffer: bytes, length: int, chunked: bool) -> bytes:
    if chunked:
        body = buffer
        while not body.endswith(b"0\r\n\r\n") and b"\r\n0\r\n\r\n" not in body:
            chunk = sock.recv(65536)
            if not chunk:
                break
            body += chunk
        return body
    if length >= 0:
        body = buffer
        while len(body) < length:
            chunk = sock.recv(min(65536, length - len(body)))
            if not chunk:
                break
            body += chunk
        return body
    body = buffer
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            break
        body += chunk
    return body


def send(
    request: Request,
    *,
    host: str | None = None,
    port: int | None = None,
    scheme: str | None = None,
    connect_timeout: float = 10.0,
    read_timeout: float = 20.0,
) -> Exchange:
    """Transmit ``request`` exactly once and return the captured exchange."""
    resolved_scheme, resolved_host, resolved_port = endpoint(
        request, default_host=host or "", default_port=port or 0
    )
    if scheme:
        resolved_scheme = scheme.lower()
    if port is not None:
        resolved_port = port
    if not resolved_host:
        raise TransportError("no host: pass --host or include a Host header")
    if resolved_scheme not in ("http", "https"):
        raise TransportError(f"unsupported scheme {resolved_scheme!r}")

    host_override = resolved_host
    if resolved_port not in (80, 443):
        host_override = f"{resolved_host}:{resolved_port}"
    payload = serialize_request(request, host=host_override)

    started = time.perf_counter()
    sock = _connect(resolved_host, resolved_port, resolved_scheme, connect_timeout)
    try:
        sock.settimeout(read_timeout)
        try:
            sock.sendall(payload)
        except OSError as exc:
            raise TransportError(f"write failed: {exc}") from exc
        raw = _read_head(sock)
        if not raw:
            raise TransportError("server closed the connection without a response")
        head_end = raw.find(b"\r\n\r\n")
        separator = 4
        if head_end == -1:
            head_end = raw.find(b"\n\n")
            separator = 2
        if head_end == -1:
            raise TransportError("response head was never terminated")
        head = raw[:head_end]
        body_buffer = raw[head_end + separator :]
        lowered = head.lower()
        length = -1
        for line in lowered.replace(b"\r\n", b"\n").split(b"\n"):
            if line.startswith(b"content-length:"):
                value = line.split(b":", 1)[1].strip()
                if value.isdigit():
                    length = int(value)
        chunked = b"transfer-encoding:" in lowered and b"chunked" in lowered
        body = _read_body(sock, body_buffer, max(length, 0), chunked)
    finally:
        elapsed = (time.perf_counter() - started) * 1000
        sock.close()

    response = parse_response(head + b"\r\n\r\n" + body)
    redirect = ""
    if response.status in (301, 302, 303, 307, 308):
        redirect = response.get("location")
    return Exchange(
        request=request,
        request_bytes=payload,
        response=response,
        host=resolved_host,
        port=resolved_port,
        scheme=resolved_scheme,
        elapsed_ms=elapsed,
        sent_at=_now(),
        redirect_target=redirect,
    )
