"""Every tracked SKILL.md must have frontmatter Claude Code can load.

Pinned after 2026-10-30: session-rules carried an unquoted ": " in its
description, which is invalid YAML. The skill was missing from every session
and nothing reported it until a dispatched builder failed to load it.
"""
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = [
    ROOT / line
    for line in subprocess.run(
        ["git", "ls-files", "*SKILL.md"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
]


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---"), "no frontmatter block"
    return yaml.safe_load(text.split("---", 2)[1])


def test_there_are_skills_to_check():
    assert SKILLS


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_skill_frontmatter_loads(path):
    data = frontmatter(path)
    assert data["name"].strip()
    assert data["description"].strip()
