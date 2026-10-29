# Contributing

## Local loop

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest -q
python -m reqforge validate
```

## Changing the corpus

Skills live in `src/reqforge/corpus/part1.py` .. `part3.py` as plain dicts.
After any edit:

```bash
python -m reqforge build     # regenerate skills/, pack.json and results/
pytest -q                    # includes the "no drift" assertions
```

Never edit `skills/**/SKILL.md` by hand: it is generated, hashed into
`pack.json`, and `validate` fails when the file and the render disagree.

A new skill must clear every floor: six steps, four signals, three patterns,
three pitfalls, two done-when items, one canonical `https` reference, 180
rendered words, kebab-case tags, and a unique slug and title.

## Changing the transport

Byte fidelity is the contract. If a change adds header injection, redirect
following, decompression, retries or pooling, it changes what the tool
observes and needs a very good reason. Add a test that asserts the bytes a
fixture server received, not the bytes a client library reported.

## Style

- Standard library only at runtime; `pytest` is the only dev dependency.
- Type hints on public functions, `from __future__ import annotations` at the top.
- No network in tests. A loopback socket fixture is the pattern to copy.
- Keep `README.md`, `docs/USAGE.md` and `RESULTS.md` truthful; if a number
  changes, re-run and paste the real output.

## Commits

One logical change per commit, message stating why rather than restating the
diff.
