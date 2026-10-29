"""reqforge corpus: pack metadata plus 50 authored HTTP exchange skills.

Skills are authored as plain dicts in ``part1``..``part3`` and loaded once
into the validated :class:`~reqforge.model.Skill` shape.
"""

from __future__ import annotations

from typing import Any

from ..model import skill_from_dict
from .part1 import SKILLS as PART1
from .part2 import SKILLS as PART2
from .part3 import SKILLS as PART3

PACK: dict[str, Any] = {
    "name": "reqforge",
    "version": "1.0.0",
    "category": "networking",
    "license": "MIT",
    "runtime": "Claude Code, opencode, or any agent runtime that loads SKILL.md files",
    "description": (
        "50 validated skills for authoring, transmitting, capturing, replaying, "
        "comparing and exporting raw HTTP exchanges, plus a proxy-free request "
        "sender and HAR/curl exporter in one stdlib-only CLI."
    ),
    "expected_skills": 50,
    "meta_keys": ("phase",),
    "requires_verification": False,
}

SKILLS: list[Any] = [skill_from_dict(raw) for raw in (*PART1, *PART2, *PART3)]
