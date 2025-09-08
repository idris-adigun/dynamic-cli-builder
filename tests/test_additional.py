"""Additional tests to boost coverage near 100 %."""
from __future__ import annotations

import importlib
import os
import sys

# ensure package import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path
from types import ModuleType
from typing import Any, Dict

import pytest

import dynamic_cli_builder.builder as builder_mod
from dynamic_cli_builder.validators import validate_arg
from dynamic_cli_builder.loader import load_config


# ---------------------------------------------------------------------------
# validators
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("value", "rules"),
    [
        ("abc", {"regex": r"^[a-z]{3}$"}),
        ("10", {"min": 5, "max": 20}),
        ("5", {"min": 5}),
        ("5", {"max": 10}),
    ],
)
def test_validate_arg_success(value: str, rules: Dict[str, Any]) -> None:
    assert validate_arg(value, rules) == value


@pytest.mark.parametrize(
    ("value", "rules"),
    [
        ("ab", {"regex": r"^[a-z]{3}$"}),
        ("1", {"min": 5}),
        ("30", {"max": 10}),
    ],
)
def test_validate_arg_failure(value: str, rules: Dict[str, Any]) -> None:
    with pytest.raises(Exception):
        validate_arg(value, rules)


# ---------------------------------------------------------------------------
# prompt_for_missing_args (interactive)
# ---------------------------------------------------------------------------

def test_prompt_for_missing_args(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = {
        "description": "demo",
        "commands": [
            {
                "name": "echo",
                "description": "Echo",
                "args": [
                    {"name": "msg", "type": "str", "help": "message", "rules": {}},
                ],
                "action": "echo",
            }
        ],
    }
    parser = builder_mod.build_cli(cfg)
    ns = parser.parse_args(["echo"])

    # provide input value "hi"
    monkeypatch.setattr("builtins.input", lambda _: "hi")
    builder_mod.prompt_for_missing_args(ns, cfg)
    assert ns.msg == "hi"


# ---------------------------------------------------------------------------
# __main__ entry point
# ---------------------------------------------------------------------------

def _write_temp_files(tmp_path: Path) -> Path:
    # actions.py
    actions_py = tmp_path / "actions.py"
    actions_py.write_text(
        """
from typing import Dict, Any

def greet(name: str) -> None:
    print(f'Hi {name}!')

ACTIONS: Dict[str, Any] = {'greet': greet}
""",
        encoding="utf-8",
    )
    # config.yaml
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
description: demo
commands:
  - name: greet
    description: Say hi
    args:
      - name: name
        type: str
        help: Name
    action: greet
""",
        encoding="utf-8",
    )
    return tmp_path


def test_main_module_exec(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    tdir = _write_temp_files(tmp_path)
    sys_path_orig = list(sys.path)
    sys.path.insert(0, str(tdir))
    monkeypatch.chdir(tdir)

    # build argv mimicking module call
    argv = ["--config", "config.yaml", "--actions", "actions.py", "greet", "--name", "Ada"]
    monkeypatch.setattr(sys, "argv", ["dynamic_cli_builder"] + argv)

    # Import reload to execute main
    mod = importlib.import_module("dynamic_cli_builder.__main__")
    # call main directly for coverage
    mod.main(argv)

    out, _ = capsys.readouterr()
    assert "Hi Ada!" in out

    # reset sys.path
    sys.path[:] = sys_path_orig


# ---------------------------------------------------------------------------
# cli shim re-exports
# ---------------------------------------------------------------------------

def test_cli_shim_exports() -> None:
    shim = importlib.import_module("dynamic_cli_builder.cli")
    for attr in [
        "build_cli",
        "execute_command",
        "configure_logging",
        "validate_arg",
    ]:
        assert hasattr(shim, attr)


def test_bool_and_json_types(tmp_path: Path) -> None:
    cfg = {
        "description": "types",
        "commands": [
            {
                "name": "echo",
                "description": "Echo",
                "args": [
                    {"name": "flag", "type": "bool", "help": "flag", "default": False},
                    {"name": "items", "type": "list", "help": "list", "default": [1]},
                    {"name": "obj", "type": "dict", "help": "dict", "default": {"a": 1}},
                ],
                "action": "echo",
            }
        ],
    }
    seen: Dict[str, Any] = {}

    def echo(flag: bool, items, obj) -> None:  # type: ignore[no-untyped-def]
        seen.update(flag=flag, items=items, obj=obj)

    import dynamic_cli_builder.builder as b
    p = b.build_cli(cfg)
    ns = p.parse_args([
        "echo",
        "--flag", "true",
        "--items", "[1,2,3]",
        "--obj", '{"k": 2}',
    ])
    b.execute_command(ns, cfg, {"echo": echo})
    assert seen["flag"] is True
    assert seen["items"] == [1, 2, 3]
    assert seen["obj"] == {"k": 2}


def test_config_schema_validation_errors(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("description: oops\ncommands: []\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(bad)
