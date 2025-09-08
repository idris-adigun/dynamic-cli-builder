from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from dynamic_cli_builder.generator import generate_config, dump_config


def _write_actions(tmp: Path) -> Path:
    f = tmp / "actions.py"
    f.write_text(
        '''
from typing import Dict, Any, List, Dict as D

def greet(name: str, age: int = 21) -> None:
    """Say hello"""
    pass

def configify(items: List[int], meta: D[str, int] = {"a": 1}, flag: bool = False):
    pass

def _private(x: int):
    pass

def echo(msg):
    pass

ACTIONS: Dict[str, Any] = {
    'greet': greet,
    'configify': configify,
}
''',
        encoding="utf-8",
    )
    return f


def test_generate_config_prefers_actions(tmp_path: Path) -> None:
    actions_py = _write_actions(tmp_path)

    # import module
    spec = importlib.util.spec_from_file_location("actions", str(actions_py))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    cfg = generate_config(module, getattr(module, "ACTIONS"))
    cmds = {c["name"]: c for c in cfg["commands"]}
    assert set(cmds.keys()) == {"greet", "configify"}
    greet_args = {a["name"]: a for a in cmds["greet"]["args"]}
    assert greet_args["name"]["type"] == "str"
    assert greet_args["age"]["type"] == "int" and "default" in greet_args["age"]


def test_dump_yaml_json_roundtrip(tmp_path: Path) -> None:
    actions_py = _write_actions(tmp_path)
    spec = importlib.util.spec_from_file_location("actions", str(actions_py))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    cfg = generate_config(module)
    y = dump_config(cfg, "yaml")
    j = dump_config(cfg, "json")
    assert "commands:" in y
    assert j.strip().startswith("{")


def test_main_generate_stdout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    actions_py = _write_actions(tmp_path)
    import dynamic_cli_builder.__main__ as main_mod

    argv = [
        "--actions", str(actions_py),
        "--generate",
        "--format", "yaml",
    ]
    monkeypatch.setattr(sys, "argv", ["dynamic_cli_builder"] + argv)
    main_mod.main(argv)
    out, _ = capsys.readouterr()
    assert "commands:" in out
