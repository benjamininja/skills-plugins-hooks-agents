"""Every .claude/agents/*.md must have frontmatter Claude Code can load.

Pinned after 2026-10-12: two agents carried an unquoted `model:` value
containing ": ", which is invalid YAML. They could not load anywhere for
three months and nothing reported it.
"""
from pathlib import Path

import pytest
import yaml

AGENTS = sorted((Path(__file__).resolve().parent.parent / ".claude" / "agents").glob("*.md"))
MODELS = {"haiku", "sonnet", "opus", "inherit"}


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---"), "no frontmatter block"
    return yaml.safe_load(text.split("---", 2)[1])


def test_there_are_agents_to_check():
    assert AGENTS


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.name)
def test_agent_frontmatter_loads(path):
    data = frontmatter(path)
    assert data["name"] == path.stem
    assert data["description"].strip()
    model = data.get("model", "inherit")
    assert model in MODELS or model.startswith("claude-"), (
        f"model must be an alias {sorted(MODELS)} or a full model id, got {model!r}"
    )
