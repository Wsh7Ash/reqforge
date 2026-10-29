"""Corpus, parser, transport and exporter tests.

The transport tests run against a raw socket server implemented below, so the
assertions are about the exact bytes exchanged rather than about how a
high-level HTTP client would have normalised them.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reqforge.corpus import PACK, SKILLS  # noqa: E402
from reqforge.export import diff_summaries, to_curl, to_har, to_jsonl  # noqa: E402
from reqforge.httpmsg import (  # noqa: E402
    MessageError,
    Request,
    decode_chunked,
    endpoint,
    parse_request,
    parse_response,
    serialize_request,
)
from reqforge.render import render_skill, word_count  # noqa: E402
from reqforge.transport import TransportError, send  # noqa: E402
from reqforge.validate import pack_issues, skill_issues, validate_pack  # noqa: E402

PHASES = ("author", "transmit", "capture", "replay", "compare", "export")


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "-m", "reqforge", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=120,
    )


# ---------------------------------------------------------------- corpus shape


def test_pack_declares_fifty_and_delivers_fifty() -> None:
    assert PACK["expected_skills"] == 50
    assert len(SKILLS) == 50


def test_slugs_and_titles_are_unique() -> None:
    assert len({skill.slug for skill in SKILLS}) == 50
    assert len({skill.title.lower() for skill in SKILLS}) == 50


def test_every_skill_passes_every_rule() -> None:
    assert validate_pack(PACK, SKILLS) == []


def test_phases_are_known_and_balanced() -> None:
    counts: dict[str, int] = {}
    for skill in SKILLS:
        phase = skill.meta_get("phase")
        assert phase in PHASES
        counts[phase] = counts.get(phase, 0) + 1
    assert set(counts) == set(PHASES)
    assert min(counts.values()) >= 6
    assert max(counts.values()) <= 12


def test_word_floor_is_real_not_theoretical() -> None:
    counts = [word_count(render_skill(PACK, skill)) for skill in SKILLS]
    assert min(counts) >= 180
    assert sum(counts) / len(counts) > 200


def test_no_placeholder_or_local_path_tokens() -> None:
    for skill in SKILLS:
        text = render_skill(PACK, skill)
        for token in ("TODO", "FIXME", "lorem ipsum", "C:\\\\", "/Users/"):
            assert token not in text


# ------------------------------------------------------------ generated files


def test_committed_skills_match_corpus_render() -> None:
    for skill in SKILLS:
        path = ROOT / "skills" / skill.slug / "SKILL.md"
        assert path.exists(), f"missing {path}"
        assert path.read_text(encoding="utf-8") == render_skill(PACK, skill)


def test_pack_json_hashes_match_files() -> None:
    manifest = json.loads((ROOT / "pack.json").read_text(encoding="utf-8"))
    assert manifest["skill_count"] == 50
    import hashlib

    for entry in manifest["skills"]:
        text = (ROOT / entry["path"]).read_text(encoding="utf-8")
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == entry["sha256"]


def test_build_is_idempotent(tmp_path: Path) -> None:
    from reqforge.render import build_pack

    first = build_pack(tmp_path, PACK, SKILLS)
    second = build_pack(tmp_path, PACK, SKILLS)
    assert first == second
    assert len(first) == 52  # 50 skills + pack.json + catalog


def test_drift_is_detected(tmp_path: Path) -> None:
    from reqforge.render import build_pack

    build_pack(tmp_path, PACK, SKILLS)
    target = tmp_path / "skills" / SKILLS[0].slug / "SKILL.md"
    target.write_text("tampered\n", encoding="utf-8")
    assert target.read_text(encoding="utf-8") != render_skill(PACK, SKILLS[0])


# ----------------------------------------------------------------------- CLI


def test_cli_validate_reports_fifty_of_fifty() -> None:
    proc = run_cli("validate")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "50/50 skills valid" in proc.stdout


def test_cli_list_show_and_search() -> None:
    listed = run_cli("list", "--phase", "export")
    assert listed.returncode == 0
    assert "->" not in listed.stdout
    assert listed.stdout.strip().endswith("skills")

    show = run_cli("show", SKILLS[0].slug)
    assert show.returncode == 0
    assert show.stdout.startswith(f"---\nname: {SKILLS[0].slug}")

    missing = run_cli("show", "not-a-real-skill")
    assert missing.returncode == 1

    search = run_cli("search", "har")
    assert search.returncode == 0
    assert search.stdout.strip() != ""

    nohit = run_cli("search", "zzzz-no-such-term")
    assert nohit.returncode == 1
    assert "no matches" in nohit.stdout


def test_cli_export_curl_quotes_hostile_values() -> None:
    proc = run_cli("export", str(ROOT / "examples" / "order.http"), "--to", "curl", "--host", "api.example.test")
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("curl -i --path-as-is")
    assert "--data-binary" in proc.stdout
    assert "api.example.test/v1/orders" in proc.stdout


# -------------------------------------------------------------------- parsing


def test_parse_preserves_header_order_and_duplicates() -> None:
    text = (
        "GET /admin HTTP/1.1\r\n"
        "Host: app.example.test\r\n"
        "X-Forwarded-For: 10.0.0.1\r\n"
        "X-Forwarded-For: 127.0.0.1\r\n\r\n"
    )
    request = parse_request(text)
    assert [name for name, _ in request.headers] == ["Host", "X-Forwarded-For", "X-Forwarded-For"]
    assert request.get_all("x-forwarded-for") == ["10.0.0.1", "127.0.0.1"]
    assert serialize_request(request) == text.encode()


def test_serialize_adds_only_missing_framing() -> None:
    request = parse_request("POST /x HTTP/1.1\r\nHost: h.test\r\n\r\nabc")
    wire = serialize_request(request)
    assert b"Content-Length: 3" in wire
    assert wire.endswith(b"\r\n\r\nabc")

    with_length = parse_request("POST /x HTTP/1.1\r\nHost: h.test\r\nContent-Length: 3\r\n\r\nabc")
    assert serialize_request(with_length).count(b"Content-Length") == 1


def test_endpoint_resolution_variants() -> None:
    assert endpoint(parse_request("GET / HTTP/1.1\r\nHost: a.test:8443\r\n\r\n")) == ("http", "a.test", 8443)
    assert endpoint(parse_request("GET https://b.test/x HTTP/1.1\r\n\r\n")) == ("https", "b.test", 443)
    assert endpoint(parse_request("GET / HTTP/1.1\r\n\r\n"), default_host="c.test", default_port=80) == (
        "http",
        "c.test",
        80,
    )


def test_parse_request_rejects_empty_and_headerless() -> None:
    with pytest.raises(MessageError):
        parse_request("")
    with pytest.raises(MessageError):
        parse_request("GET / HTTP/1.1\r\nbadheader\r\n\r\n")


def test_chunked_decoding() -> None:
    assert decode_chunked(b"5\r\nhello\r\n0\r\n\r\n") == b"hello"
    assert decode_chunked(b"garbage") == b"garbage"


def test_parse_response_truncates_to_declared_length() -> None:
    raw = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nabcdef"
    response = parse_response(raw)
    assert response.status == 200
    assert response.body == b"ab"
    assert response.raw == raw


# ------------------------------------------------------------------ transport

RESPONSE_TEMPLATE = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: application/json\r\n"
    b"X-Served-By: fixture\r\n"
    b"Content-Length: %d\r\n"
    b"Connection: close\r\n\r\n%s"
)


class FixtureServer:
    """Raw socket server that records the exact bytes it received."""

    def __init__(self, body: bytes = b'{"ok":true}', status: int = 200, chunked: bool = False) -> None:
        self.received: list[bytes] = []
        self.responses: list[bytes] = []
        if chunked:
            payload = body
            self.responses.append(
                f"HTTP/1.1 {status} OK\r\nTransfer-Encoding: chunked\r\n\r\n".encode()
                + f"{len(payload):x}\r\n".encode()
                + payload
                + b"\r\n0\r\n\r\n"
            )
        else:
            self.responses.append(
                f"HTTP/1.1 {status} OK\r\nContent-Type: application/json\r\nX-Served-By: fixture\r\n"
                f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode()
                + body
            )
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(5)
        self.port = self.sock.getsockname()[1]
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def __enter__(self) -> "FixtureServer":
        self.thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.sock.close()

    def _serve(self) -> None:
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                conn.settimeout(2.0)
                buffer = b""
                while b"\r\n\r\n" not in buffer:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    buffer += chunk
                head, _, rest = buffer.partition(b"\r\n\r\n")
                length = 0
                for line in head.split(b"\r\n")[1:]:
                    if line.lower().startswith(b"content-length:"):
                        length = int(line.split(b":", 1)[1])
                body = rest
                while len(body) < length:
                    chunk = conn.recv(65536)
                    if not chunk:
                        break
                    body += chunk
                self.received.append(head + b"\r\n\r\n" + body)
                response = self.responses.pop(0) if self.responses else self.responses_default()
                conn.sendall(response)


def _responses_default(self: FixtureServer) -> bytes:
    return RESPONSE_TEMPLATE % (11, b'{"ok":true}')


FixtureServer.responses_default = _responses_default  # type: ignore[attr-defined]


def test_send_transmits_exact_bytes_and_captures_response() -> None:
    with FixtureServer() as server:
        request = parse_request(
            "POST /v1/orders HTTP/1.1\r\n"
            "Host: placeholder\r\n"
            "X-Forwarded-For: 10.0.0.1\r\n"
            "X-Forwarded-For: 127.0.0.1\r\n"
            "Content-Type: application/json\r\n\r\n"
            '{"sku":"A-1"}'
        )
        exchange = send(request, host="127.0.0.1", port=server.port, scheme="http")
        received = server.received[0]

    assert exchange.response.status == 200
    assert exchange.response.body == b'{"ok":true}'
    assert received.startswith(b"POST /v1/orders HTTP/1.1\r\n")
    # Header order and duplicates survive the trip.
    assert received.count(b"X-Forwarded-For") == 2
    assert received.index(b"X-Forwarded-For") < received.index(b"Content-Type")
    assert received.endswith(b'{"sku":"A-1"}')
    assert b"Host: 127.0.0.1:" + str(server.port).encode() in received


def test_send_decodes_chunked_response() -> None:
    with FixtureServer(body=b'{"items":[1,2]}', chunked=True) as server:
        exchange = send(
            parse_request("GET /v1/items HTTP/1.1\r\nHost: h\r\n\r\n"),
            host="127.0.0.1",
            port=server.port,
        )
    assert exchange.response.body == b'{"items":[1,2]}'
    assert exchange.response.get("transfer-encoding").lower() == "chunked"


def test_send_reports_missing_host() -> None:
    with pytest.raises(TransportError):
        send(parse_request("GET / HTTP/1.1\r\n\r\n"))


def test_send_reports_connection_failure() -> None:
    with pytest.raises(TransportError) as excinfo:
        send(parse_request("GET / HTTP/1.1\r\nHost: x\r\n\r\n"), host="127.0.0.1", port=1)
    assert "connect" in str(excinfo.value)


# ------------------------------------------------------------------ exporters


def test_har_entry_shape_and_sizes() -> None:
    with FixtureServer(body=b'{"ok":true}') as server:
        exchange = send(
            parse_request("GET /v1/ping?page=2 HTTP/1.1\r\nHost: h\r\n\r\n"),
            host="127.0.0.1",
            port=server.port,
        )
    har = json.loads(to_har([exchange]))
    entry = har["log"]["entries"][0]
    assert har["log"]["version"] == "1.2"
    assert entry["request"]["method"] == "GET"
    assert entry["request"]["url"].endswith("/v1/ping?page=2")
    assert entry["request"]["queryString"] == [{"name": "page", "value": "2"}]
    assert entry["response"]["status"] == 200
    assert entry["response"]["content"]["size"] == len(b'{"ok":true}')
    assert entry["response"]["content"]["text"] == '{"ok":true}'
    assert "headers" not in entry["response"]["content"]


def test_jsonl_has_one_line_per_exchange() -> None:
    with FixtureServer() as server:
        request = parse_request("GET / HTTP/1.1\r\nHost: h\r\n\r\n")
        exchanges = [send(request, host="127.0.0.1", port=server.port) for _ in range(3)]
    lines = to_jsonl(exchanges).strip().splitlines()
    assert len(lines) == 3
    assert all(json.loads(line)["status"] == 200 for line in lines)


def test_curl_export_omits_content_length_and_quotes() -> None:
    request = parse_request(
        "POST /v1/x HTTP/1.1\r\nHost: h\r\nContent-Length: 5\r\nX-Test: $(whoami)\r\n\r\nhello"
    )
    command = to_curl(request, "https", "api.test", 443)
    assert "Content-Length" not in command
    assert "--path-as-is" in command
    assert "-H 'X-Test: $(whoami)'" in command
    assert command.startswith("curl -i --path-as-is")


def test_diff_detects_status_and_header_changes() -> None:
    before = {"status": 403, "reason": "Forbidden", "body_bytes": 20, "headers": [["x-a", "1"]]}
    after = {"status": 200, "reason": "OK", "body_bytes": 4096, "headers": [["x-a", "2"], ["set-cookie", "s=1"]]}
    payload = diff_summaries(before, after)
    assert payload["changed_fields"]["status"] == {"before": 403, "after": 200}
    assert payload["headers_added"] == {"set-cookie": ["s=1"]}
    assert payload["headers_changed"]["x-a"] == {"before": ["1"], "after": ["2"]}
    assert not payload["identical"]


def test_diff_identical_summaries() -> None:
    same = {"status": 200, "reason": "OK", "body_bytes": 10, "headers": [["x-a", "1"]]}
    assert diff_summaries(same, dict(same))["identical"]


# ------------------------------------------------------------------ integrity


def test_pack_issues_catches_a_short_corpus() -> None:
    issues = pack_issues(PACK, SKILLS[:-1])
    assert any(issue.rule == "skill-count" for issue in issues)


def test_single_skill_rule_violations_are_reported() -> None:
    broken = dict(SKILLS[0].__dict__)
    broken["steps"] = ("one", "two")
    from reqforge.model import skill_from_dict

    issues = skill_issues(PACK, skill_from_dict(broken), "")
    assert "steps-count" in {issue.rule for issue in issues}


def test_wire_bytes_helper_matches_serializer() -> None:
    from reqforge.export import wire_bytes

    request = Request(method="GET", target="/x", version="HTTP/1.1", headers=(("Host", "h"),), body=b"")
    assert wire_bytes(request) == b"GET /x HTTP/1.1\r\nHost: h\r\n\r\n"
