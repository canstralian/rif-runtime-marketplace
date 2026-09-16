#!/usr/bin/env python3
"""Validate marketplace, plugin, and skill structure."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
marketplace = root / ".claude-plugin" / "marketplace.json"

data = json.loads(marketplace.read_text())
assert data["name"] == "rif-runtime-marketplace"
assert isinstance(data["owner"], dict)
assert data["plugins"]

skill_count = 0

for plugin in data["plugins"]:
    assert plugin["name"]
    source = root / plugin["source"]
    assert source.is_dir(), source
    manifest = source / ".claude-plugin" / "plugin.json"
    assert manifest.is_file(), manifest
    pm = json.loads(manifest.read_text())
    assert pm["name"] == plugin["name"]
    assert pm["version"] == plugin["version"], (
        f"{plugin['name']}: plugin.json version {pm['version']} != "
        f"marketplace entry {plugin['version']}"
    )

    for skill_dir in sorted((source / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        assert skill_file.is_file(), skill_file
        text = skill_file.read_text()
        frontmatter = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        assert frontmatter, f"{skill_file}: missing YAML frontmatter"
        fields = dict(
            re.findall(r"^(\w+):\s*(.+)$", frontmatter.group(1), re.MULTILINE)
        )
        assert fields.get("name") == skill_dir.name, (
            f"{skill_file}: frontmatter name {fields.get('name')!r} != "
            f"directory {skill_dir.name!r}"
        )
        assert fields.get("description"), f"{skill_file}: missing description"
        skill_count += 1

print(f"Marketplace structure: OK ({skill_count} skills)")
