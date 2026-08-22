#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
marketplace = root / ".claude-plugin" / "marketplace.json"

data = json.loads(marketplace.read_text())
assert data["name"] == "rif-runtime-marketplace"
assert isinstance(data["owner"], dict)
assert data["plugins"]

for plugin in data["plugins"]:
    assert plugin["name"]
    source = root / plugin["source"]
    assert source.is_dir(), source
    manifest = source / ".claude-plugin" / "plugin.json"
    assert manifest.is_file(), manifest
    pm = json.loads(manifest.read_text())
    assert pm["name"] == plugin["name"]

print("Marketplace structure: OK")
