"""Exchange exporters: HAR 1.2, curl, JSONL and verbatim raw captures.

Each exporter is a pure function over a captured :class:`~reqforge.transport.Exchange`
so a transcript can be re-rendered without re-sending anything.
"""

from __future__ import annotations

import base64
import json
import re
import shlex
from typing import Any, Iterable, Sequence
from urllib.parse import urlsplit

from .httpmsg import Request, header_map, parse_request, serialize_request
from .transport import Exchange

TEXT_HINT = re.compile(r"^(text/|application/(json|xml|javascript|x-www-form-urlencoded|graphql))", re.I)


def absolute_url(request: Request, scheme: str, host: str, port: int) -> str:
    """Build the URL a browser or curl would use for this request line."""
    if request.target.startswith(("http://", "https://")):
        return request.target
    suffix = "" if port in (80, 443) else f":{port}"
    target = request.target if request.target.startswith("/") else "/" + request.target
    return f"{scheme}://{host}{suffix}{target}"


def request_headers(request: Request) -> list[dict[str, str]]:
    return [{"name": name, "value": value} for name, value in request.headers]


def response_headers(exchange: Exchange) -> list[dict[str, str]]:
    return [{"name": name, "value": value} for name, value in exchange.response.headers]


def _post_data(request: Request) -> dict[str, Any] | None:
    if not request.body:
        return None
    mime = request.get("content-type") or "application/octet-stream"
    try:
        return {"mimeType": mime, "text": request.body.decode("utf-8")}
    except UnicodeDecodeError:
        return {
            "mimeType": mime,
            "text": base64.b64encode(request.body).decode("ascii"),
            "encoding": "base64",
        }


def har_entry(exchange: Exchange) -> dict[str, Any]:
    """One HAR 1.2 entry built from the captured bytes, without re-reading them."""
    url = absolute_url(exchange.request, exchange.scheme, exchange.host, exchange.port)
    parts = urlsplit(url)
    query = [
        {"name": piece.split("=", 1)[0], "value": piece.split("=", 1)[1] if "=" in piece else ""}
        for piece in parts.query.split("&")
        if piece
    ]
    mime = exchange.response.get("content-type") or ""
    content: dict[str, Any] = {
        "size": len(exchange.response.body),
        "mimeType": mime,
    }
    if TEXT_HINT.match(mime) or not mime:
        content["text"] = exchange.response.body_text
    else:
        content["text"] = base64.b64encode(exchange.response.body).decode("ascii")
        content["encoding"] = "base64"
    size = len(exchange.response.body)
    return {
        "startedDateTime": exchange.sent_at,
        "time": round(exchange.elapsed_ms, 3),
        "request": {
            "method": exchange.request.method,
            "url": url,
            "httpVersion": exchange.request.version,
            "cookies": [],
            "headers": request_headers(exchange.request),
            "queryString": query,
            "headersSize": len(exchange.request_bytes) - len(exchange.request.body),
            "bodySize": len(exchange.request.body),
            **({"postData": _post_data(exchange.request)} if exchange.request.body else {}),
        },
        "response": {
            "status": exchange.response.status,
            "statusText": exchange.response.reason,
            "httpVersion": exchange.response.version,
            "cookies": [],
            "headers": response_headers(exchange),
            "content": content,
            "redirectURL": exchange.response.get("location"),
            "headersSize": len(exchange.response.raw) - size,
            "bodySize": size,
        },
        "cache": {},
        "timings": {
            "blocked": -1,
            "dns": -1,
            "connect": -1,
            "send": 0,
            "wait": round(exchange.elapsed_ms, 3),
            "receive": 0,
            "ssl": -1,
        },
        "comment": f"reqforge {exchange.scheme}://{exchange.host}:{exchange.port}",
    }


def to_har(exchanges: Sequence[Exchange], *, version: str = "1.0.0") -> str:
    """Serialise exchanges as a HAR 1.2 archive that DevTools and jq can read."""
    payload = {
        "log": {
            "version": "1.2",
            "creator": {"name": "reqforge", "version": version},
            "entries": [har_entry(exchange) for exchange in exchanges],
        }
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def _shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def to_curl(request: Request, scheme: str = "http", host: str = "", port: int = 80) -> str:
    """Render a request as a single copy-pasteable curl command."""
    url = absolute_url(request, scheme, host, port)
    lines = ["curl -i --path-as-is"]
    if request.method.upper() not in ("GET", "HEAD"):
        lines.append(f"-X {request.method.upper()}")
    for name, value in request.headers:
        if name.lower() in ("content-length",):
            continue
        lines.append(f"-H {_shell_quote(f'{name}: {value}')}")
    if request.body:
        try:
            lines.append(f"--data-binary {_shell_quote(request.body.decode('utf-8'))}")
        except UnicodeDecodeError:
            encoded = base64.b64encode(request.body).decode("ascii")
            lines.append(f"--data-binary {_shell_quote(encoded)} # base64, decode before use")
    lines.append(_shell_quote(url))
    return " \\\n  ".join(lines) + "\n"


def to_jsonl(exchanges: Iterable[Exchange]) -> str:
    """One compact JSON record per exchange, safe to append to a test log."""
    out = []
    for exchange in exchanges:
        record = exchange.summary()
        record["request_headers"] = request_headers(exchange.request)
        record["body_preview"] = exchange.response.body_text[:400]
        out.append(json.dumps(record, ensure_ascii=False))
    return "\n".join(out) + ("\n" if out else "")


def to_raw(exchange: Exchange) -> str:
    """The request and response exactly as they crossed the socket."""
    try:
        request_text = exchange.request_bytes.decode("utf-8")
    except UnicodeDecodeError:
        request_text = exchange.request_bytes.decode("latin-1")
    try:
        response_text = exchange.response.raw.decode("utf-8")
    except UnicodeDecodeError:
        response_text = exchange.response.raw.decode("latin-1")
    return (
        "### REQUEST ###\n"
        + request_text
        + ("\n" if not request_text.endswith("\n") else "")
        + "\n### RESPONSE ###\n"
        + response_text
        + ("\n" if not response_text.endswith("\n") else "")
    )


def diff_summaries(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Compare two capture summaries field by field: status, body, headers."""
    fields = ("status", "reason", "body_bytes", "response_bytes", "scheme", "host", "port", "method", "target", "elapsed_ms")
    changes = {
        field: {"before": before.get(field), "after": after.get(field)}
        for field in fields
        if before.get(field) != after.get(field)
    }
    old = header_map([tuple(pair) for pair in before.get("headers", [])])
    new = header_map([tuple(pair) for pair in after.get("headers", [])])
    added = {k: v for k, v in new.items() if k not in old}
    removed = {k: v for k, v in old.items() if k not in new}
    changed = {k: (old[k], new[k]) for k in new if k in old and new[k] != old[k]}
    return {
        "changed_fields": changes,
        "headers_added": added,
        "headers_removed": removed,
        "headers_changed": {k: {"before": v[0], "after": v[1]} for k, v in changed.items()},
        "identical": not changes and not added and not removed and not changed,
    }


def request_from_file(text: str) -> Request:
    """Convenience wrapper kept next to the exporters for CLI symmetry."""
    return parse_request(text)


def wire_bytes(request: Request, host: str | None = None) -> bytes:
    return serialize_request(request, host=host)


def shell_wordcount_guard(command: str) -> str:
    """Fail loudly rather than emit a command that is obviously unsafe to run."""
    if "\x00" in command:
        raise ValueError("refusing to emit a command containing NUL bytes")
    return shlex.split(command.splitlines()[0])[0]
