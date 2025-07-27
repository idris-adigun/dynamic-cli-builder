"""Tests for dynamic_cli_builder.loader utilities."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from dynamic_cli_builder.loader import load_config


def _write_sample(tmp_path: Path, ext: str) -> Path:
    sample = {
        "description": "tmp config",
        "commands": [
            {
                "name": "dummy",
                "description": "dummy cmd",
                "args": [],
                "action": "noop",
            }
        ],
    }
    file = tmp_path / f"config{ext}"
    if ext in {".yml", ".yaml"}:
        import yaml  # noqa: WPS433 – runtime import for tests only

        file.write_text(yaml.safe_dump(sample), encoding="utf-8")
    else:
        file.write_text(json.dumps(sample), encoding="utf-8")
    return file


@pytest.mark.parametrize("ext", [".yaml", ".json"])
def test_load_config_supported_formats(tmp_path: Path, ext: str) -> None:
    cfg_path = _write_sample(tmp_path, ext)
    cfg = load_config(cfg_path)
    assert cfg["commands"][0]["name"] == "dummy"


def test_auto_discovery(tmp_path: Path) -> None:
    cfg_path = _write_sample(tmp_path, ".yaml")
    cwd = tmp_path
    # change working directory temporally
    import os
    old = os.getcwd()
    os.chdir(cwd)
    try:
        cfg = load_config()
        assert cfg["description"] == "tmp config"
    finally:
        os.chdir(old)
