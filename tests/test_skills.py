"""Consistency checks for the bundled Claude Code skills under .claude/skills/."""

import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".claude" / "skills"
SKILL_FILES = sorted(SKILLS_DIR.glob("*/SKILL.md"))

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
# The workspace-root candidates every skill probes in Step 0, in order.
CANDIDATE = re.compile(r"^\d\. `([^`]+/?workspace\.dsl)` → workspace root is `([^`]+)`$", re.M)


def frontmatter(path: Path) -> dict[str, str]:
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    assert match, f"{path} has no YAML frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def test_skills_present():
    assert len(SKILL_FILES) == 6


@pytest.mark.parametrize("path", SKILL_FILES, ids=lambda p: p.parent.name)
def test_frontmatter(path):
    fields = frontmatter(path)
    assert fields.get("name") == path.parent.name
    description = fields.get("description", "")
    assert 0 < len(description) <= 1024
    assert "<" not in description and ">" not in description
    assert fields.get("allowed-tools")


@pytest.mark.parametrize("path", SKILL_FILES, ids=lambda p: p.parent.name)
def test_step_zero_marker(path):
    assert "<!-- STEP-0-SYNC" in path.read_text(encoding="utf-8")


def test_step_zero_candidates_in_sync():
    candidates = {p.parent.name: CANDIDATE.findall(p.read_text(encoding="utf-8")) for p in SKILL_FILES}
    reference = candidates["c4-add-system"]
    assert len(reference) == 4
    for name, found in candidates.items():
        assert found == reference, f"{name} Step 0 candidates drifted from c4-add-system"


def test_readmes_list_every_skill():
    readmes = [SKILLS_DIR / "README.md", SKILLS_DIR.parent.parent / "README.md"]
    for readme in readmes:
        text = readme.read_text(encoding="utf-8")
        for path in SKILL_FILES:
            assert f"`{path.parent.name}`" in text, f"{readme} does not mention {path.parent.name}"
