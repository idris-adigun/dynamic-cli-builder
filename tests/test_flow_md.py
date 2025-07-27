"""Ensure FLOW.md diagram stays in sync with CLI steps."""
from __future__ import annotations

from pathlib import Path


def test_flow_md_contains_key_nodes() -> None:
    content = Path("FLOW.md").read_text(encoding="utf-8")
    for keyword in [
        "Test Suite (*.py)",
        "build_cli(config)",
        "execute_command",
    ]:
        assert keyword in content, f"FLOW.md missing {keyword}"
