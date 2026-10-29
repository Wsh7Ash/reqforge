"""reqforge command line interface.

Shared corpus commands (validate / list / show / search / build) come from the
pack harness. The domain commands are the reason this repo exists:

    reqforge send req.http --host 127.0.0.1 --port 8080
    reqforge send req.http --json --out captures/
    reqforge export req.http --to curl --host api.example.com --port 443 --scheme https
    reqforge diff captures/a.json captures/b.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .corpus import PACK, SKILLS
from .export import diff_summaries, to_curl, to_har, to_jsonl, to_raw
from .httpmsg import MessageError, endpoint, parse_request
from .render import build_pack, render_skill, word_count
from .transport import TransportError, send
from .validate import (
    MAX_DESCRIPTION,
    MIN_DONE,
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_SUMMARY,
    MIN_WORDS,
    Issue,
    validate_pack,
)

PHASE_ORDER = ("author", "transmit", "capture", "replay", "compare", "export")

FLOORS = {
    "min_steps": MIN_STEPS,
    "min_signals": MIN_SIGNALS,
    "min_patterns": MIN_PATTERNS,
    "min_pitfalls": MIN_PITFALLS,
    "min_done_when": MIN_DONE,
    "min_summary_chars": MIN_SUMMARY,
    "min_words": MIN_WORDS,
    "max_description_chars": MAX_DESCRIPTION,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _report(issues: list[Issue], total: int, as_json: bool, title: str) -> int:
    bad = {issue.slug for issue in issues if issue.slug}
    valid = total - len(bad)
    if as_json:
        print(
            json.dumps(
                {
                    "pack": title,
                    "checked": total,
                    "valid": valid,
                    "passed": not issues,
                    "floors": FLOORS,
                    "issues": [
                        {"slug": i.slug, "rule": i.rule, "message": i.message} for i in issues
                    ],
                },
                indent=2,
            )
        )
    else:
        print(f"{title}: {valid}/{total} skills valid")
        for issue in issues:
            print(f"  FAIL {issue}")
        if not issues:
            print(
                f"  ok  steps>={MIN_STEPS} signals>={MIN_SIGNALS} patterns>={MIN_PATTERNS} "
                f"pitfalls>={MIN_PITFALLS} words>={MIN_WORDS} refs canonical https"
            )
    return 0 if not issues else 1


def cmd_validate(args: argparse.Namespace) -> int:
    issues = validate_pack(PACK, SKILLS)
    root = Path(args.root) if args.root else repo_root()
    if not args.skip_files:
        for skill in SKILLS:
            path = root / "skills" / skill.slug / "SKILL.md"
            if not path.exists():
                issues.append(Issue(skill.slug, "file-missing", "SKILL.md missing"))
                continue
            if path.read_text(encoding="utf-8") != render_skill(PACK, skill):
                issues.append(Issue(skill.slug, "file-drift", "SKILL.md differs from corpus render"))
    return _report(issues, len(SKILLS), args.json, PACK["name"])


def cmd_list(args: argparse.Namespace) -> int:
    skills = [
        skill
        for skill in SKILLS
        if (not args.tag or args.tag in skill.tags)
        and (not args.phase or skill.meta_get("phase") == args.phase)
    ]
    if args.json:
        print(
            json.dumps(
                [
                    {
                        "slug": s.slug,
                        "title": s.title,
                        "tags": list(s.tags),
                        "meta": s.meta,
                        "words": word_count(render_skill(PACK, s)),
                    }
                    for s in skills
                ],
                indent=2,
            )
        )
        return 0
    for skill in skills:
        print(f"{skill.slug:44s} {skill.meta_get('phase', '-'):10s} {skill.title}")
    print(f"-- {len(skills)} skills")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    for skill in SKILLS:
        if skill.slug == args.slug:
            print(render_skill(PACK, skill), end="")
            return 0
    print(f"unknown skill: {args.slug}", file=sys.stderr)
    return 1


def cmd_search(args: argparse.Namespace) -> int:
    terms = [term.lower() for term in args.terms]
    scored: list[tuple[int, Any]] = []
    for skill in SKILLS:
        haystack = " ".join(
            [skill.slug, skill.title, skill.summary, " ".join(skill.tags), " ".join(skill.steps)]
        ).lower()
        score = sum(haystack.count(term) for term in terms)
        if score:
            scored.append((score, skill))
    scored.sort(key=lambda pair: (-pair[0], pair[1].slug))
    for score, skill in scored[: args.limit]:
        print(f"{score:3d}  {skill.slug:44s} {skill.title}")
    if not scored:
        print("no matches")
        return 1
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else repo_root()
    build_pack(root, PACK, SKILLS)
    issues = validate_pack(PACK, SKILLS)
    for skill in SKILLS:
        path = root / "skills" / skill.slug / "SKILL.md"
        if path.read_text(encoding="utf-8") != render_skill(PACK, skill):
            issues.append(Issue(skill.slug, "file-drift", "render mismatch"))
    bad = {issue.slug for issue in issues if issue.slug}
    report = {
        "pack": PACK["name"],
        "version": PACK["version"],
        "expected_skills": PACK.get("expected_skills", len(SKILLS)),
        "checked": len(SKILLS),
        "valid": len(SKILLS) - len(bad),
        "passed": not issues,
        "floors": FLOORS,
        "issues": [{"slug": i.slug, "rule": i.rule, "message": i.message} for i in issues],
    }
    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)
    (results / "validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"built {len(SKILLS)} skills -> {root / 'skills'}")
    return 0 if not issues else 1


# --------------------------------------------------------------- send command


def load_request(path: str) -> Any:
    return parse_request(Path(path).read_bytes())


def _length_warning(request: Any) -> str:
    """Warn when the declared length disagrees with the body, without editing it."""
    declared = request.get("content-length")
    if not declared or request.has("transfer-encoding"):
        return ""
    if not declared.strip().isdigit():
        return f"warning: Content-Length is not numeric: {declared!r}"
    if int(declared) != len(request.body):
        return (
            f"warning: Content-Length {declared} but body is {len(request.body)} bytes; "
            "sent as written, server may wait for the rest"
        )
    return ""


def cmd_send(args: argparse.Namespace) -> int:
    try:
        request = load_request(args.file)
        exchange = send(
            request,
            host=args.host,
            port=args.port,
            scheme=args.scheme,
            connect_timeout=args.connect_timeout,
            read_timeout=args.read_timeout,
        )
    except (OSError, MessageError, TransportError) as exc:
        print(f"send failed: {exc}", file=sys.stderr)
        return 2

    warning = _length_warning(request)
    if warning:
        print(warning, file=sys.stderr)

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = Path(args.file).stem or "exchange"
        (out_dir / f"{stem}.raw.http").write_text(to_raw(exchange), encoding="utf-8", newline="\n")
        (out_dir / f"{stem}.json").write_text(
            json.dumps(exchange.summary(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        payload = exchange.summary()
        payload["body_preview"] = exchange.response.body_text[: args.preview]
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    response = exchange.response
    print(
        f"{exchange.scheme}://{exchange.host}:{exchange.port}  "
        f"{exchange.request.method} {exchange.request.target}"
    )
    print(f"HTTP {response.status} {response.reason}  ({exchange.elapsed_ms:.1f} ms)")
    print(f"bytes: request={len(exchange.request_bytes)} response={len(response.raw)}")
    for name, value in response.headers:
        print(f"{name}: {value}")
    if response.body:
        print()
        print(response.body_text[: args.preview])
    if exchange.redirect_target:
        print()
        print(f"redirect: {exchange.redirect_target} (not followed)")
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    """Send the same request N times and report status/body stability."""
    try:
        request = load_request(args.file)
    except (OSError, MessageError) as exc:
        print(f"cannot read request: {exc}", file=sys.stderr)
        return 2
    results: list[dict[str, Any]] = []
    for index in range(args.count):
        try:
            exchange = send(
                request,
                host=args.host,
                port=args.port,
                scheme=args.scheme,
                read_timeout=args.read_timeout,
            )
        except TransportError as exc:
            results.append({"attempt": index + 1, "error": str(exc)})
            continue
        results.append(
            {
                "attempt": index + 1,
                "status": exchange.response.status,
                "body_bytes": len(exchange.response.body),
                "body_sha": __import__("hashlib").sha256(exchange.response.body).hexdigest()[:16],
                "elapsed_ms": round(exchange.elapsed_ms, 2),
            }
        )
    statuses = {entry.get("status") for entry in results if "status" in entry}
    bodies = {entry.get("body_sha") for entry in results if "body_sha" in entry}
    errors = [entry for entry in results if "error" in entry]
    payload = {
        "attempts": args.count,
        "distinct_statuses": sorted(s for s in statuses if s is not None),
        "distinct_bodies": len(bodies),
        # A run with transport errors is inconclusive, never stable.
        "stable": not errors and len(statuses) == 1 and len(bodies) <= 1,
        "errors": len(errors),
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"attempts={args.count} statuses={payload['distinct_statuses']} "
            f"bodies={payload['distinct_bodies']} errors={payload['errors']}"
        )
        for entry in results:
            print("  " + json.dumps(entry, sort_keys=True))
        if errors:
            print("inconclusive: transport errors during replay")
        else:
            print("stable" if payload["stable"] else "variable")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    try:
        request = load_request(args.file)
    except (OSError, MessageError) as exc:
        print(f"cannot read request: {exc}", file=sys.stderr)
        return 2
    scheme, host, port = endpoint(request, default_host=args.host or "", default_port=args.port or 0)
    if args.scheme:
        scheme = args.scheme
    if args.port:
        port = args.port
    if args.to == "curl":
        sys.stdout.write(to_curl(request, scheme, host, port))
        return 0
    if args.to == "raw":
        sys.stdout.write(serialize_for_preview(request, host))
        return 0
    if args.to == "jsonl":
        print(
            json.dumps(
                {
                    "method": request.method,
                    "target": request.target,
                    "version": request.version,
                    "scheme": scheme,
                    "host": host,
                    "port": port,
                    "headers": [[n, v] for n, v in request.headers],
                    "body_bytes": len(request.body),
                },
                ensure_ascii=False,
            )
        )
        return 0
    print(f"unsupported export target: {args.to}", file=sys.stderr)
    return 2


def serialize_for_preview(request: Any, host: str | None) -> str:
    from .httpmsg import serialize_request

    return serialize_request(request, host=host).decode("latin-1")


def cmd_diff(args: argparse.Namespace) -> int:
    try:
        before = json.loads(Path(args.before).read_text(encoding="utf-8"))
        after = json.loads(Path(args.after).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read captures: {exc}", file=sys.stderr)
        return 2
    payload = diff_summaries(before, after)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if payload["identical"]:
            print("identical: no status, header or size change")
        for field, change in payload["changed_fields"].items():
            print(f"{field}: {change['before']} -> {change['after']}")
        for name, values in payload["headers_added"].items():
            print(f"+ header {name}: {', '.join(values)}")
        for name, values in payload["headers_removed"].items():
            print(f"- header {name}: {', '.join(values)}")
        for name, change in payload["headers_changed"].items():
            print(f"~ header {name}: {change['before']} -> {change['after']}")
    return 0 if payload["identical"] else 1


def cmd_har(args: argparse.Namespace) -> int:
    """Convert one or more raw capture files into a HAR archive."""
    from .httpmsg import parse_response
    from .transport import Exchange
    from .transport import _now  # local import keeps the public API small

    exchanges = []
    for path in args.files:
        text = Path(path).read_text(encoding="utf-8")
        if "### REQUEST ###" not in text or "### RESPONSE ###" not in text:
            print(f"not a raw capture: {path}", file=sys.stderr)
            return 2
        head, rest = text.split("### RESPONSE ###", 1)
        request_text = head.split("### REQUEST ###", 1)[1].strip("\n")
        request = parse_request(request_text)
        response = parse_response(rest.strip("\n").encode("utf-8"))
        host_header = request.host_header or "unknown"
        scheme, host, port = endpoint(request, default_port=args.port)
        if args.scheme:
            scheme = args.scheme
        exchanges.append(
            Exchange(
                request=request,
                request_bytes=request_text.encode("utf-8"),
                response=response,
                host=host or host_header,
                port=port,
                scheme=scheme,
                elapsed_ms=0.0,
                sent_at=_now(),
            )
        )
    out = to_har(exchanges, version=__version__)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8", newline="\n")
        print(f"wrote {len(exchanges)} entries -> {args.out}")
    else:
        sys.stdout.write(out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PACK["name"], description=PACK["description"])
    parser.add_argument("--version", action="version", version=f"{PACK['name']} {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="run every corpus rule and check disk sync")
    p.add_argument("--json", action="store_true")
    p.add_argument("--root", default=None)
    p.add_argument("--skip-files", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("list", help="list skills")
    p.add_argument("--tag", default=None)
    p.add_argument("--phase", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="print one SKILL.md")
    p.add_argument("slug")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("search", help="rank skills by keyword")
    p.add_argument("terms", nargs="+")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("build", help="regenerate skills/, pack.json and results/")
    p.add_argument("--root", default=None)
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("send", help="transmit a raw request once and show the response")
    p.add_argument("file")
    p.add_argument("--host", default=None)
    p.add_argument("--port", type=int, default=None)
    p.add_argument("--scheme", default=None, choices=["http", "https"])
    p.add_argument("--connect-timeout", type=float, default=10.0)
    p.add_argument("--read-timeout", type=float, default=20.0)
    p.add_argument("--preview", type=int, default=2000)
    p.add_argument("--out", default=None, help="directory for .raw.http and .json captures")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("replay", help="send the same request N times and compare results")
    p.add_argument("file")
    p.add_argument("--count", type=int, default=3)
    p.add_argument("--host", default=None)
    p.add_argument("--port", type=int, default=None)
    p.add_argument("--scheme", default=None, choices=["http", "https"])
    p.add_argument("--read-timeout", type=float, default=20.0)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_replay)

    p = sub.add_parser("export", help="render a request as curl, raw bytes or a JSON record")
    p.add_argument("file")
    p.add_argument("--to", required=True, choices=["curl", "raw", "jsonl"])
    p.add_argument("--host", default=None)
    p.add_argument("--port", type=int, default=None)
    p.add_argument("--scheme", default=None, choices=["http", "https"])
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("diff", help="compare two capture JSON files")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("har", help="convert raw captures into a HAR 1.2 archive")
    p.add_argument("files", nargs="+")
    p.add_argument("--out", default=None)
    p.add_argument("--scheme", default=None, choices=["http", "https"])
    p.add_argument("--port", type=int, default=443)
    p.set_defaults(func=cmd_har)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
