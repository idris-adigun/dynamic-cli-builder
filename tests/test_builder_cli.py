"""Tests for CLI building and execution."""
from __future__ import annotations

import os
import sys
from typing import Any, Dict

# ensure package import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from dynamic_cli_builder.builder import build_cli, execute_command


@pytest.fixture()
def sample_config() -> Dict[str, Any]:
    return {
        "description": "sample",
        "commands": [
            {
                "name": "add",
                "description": "Add two numbers",
                "args": [
                    {"name": "a", "type": "int", "help": "A"},
                    {"name": "b", "type": "int", "help": "B"},
                ],
                "action": "add",
            }
        ],
    }


def test_build_and_parse(sample_config):
    parser = build_cli(sample_config)
    ns = parser.parse_args(["add", "--a", "1", "--b", "2"])
    assert ns.command == "add"
    assert ns.a == 1 and ns.b == 2


def test_execute_command(sample_config):
    seen = {}

    def add(a: int, b: int):  # noqa: D401
        seen["result"] = a + b

    actions = {"add": add}
    parser = build_cli(sample_config)
    ns = parser.parse_args(["--log-level", "DEBUG", "add", "--a", "3", "--b", "4"])
    execute_command(ns, sample_config, actions)
    assert seen["result"] == 7
