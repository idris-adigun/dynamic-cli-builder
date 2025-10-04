"""Configuration loader utilities.

Supports YAML (**.yml**, **.yaml**) and JSON (**.json**) configuration files.
If *config_file* is *None*, the loader will attempt to discover a suitable
configuration in the current working directory (``config.{yml,yaml,json}``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional, List

import json
import yaml

def _discover_default(paths: Iterable[Path]) -> Optional[Path]:
    for p in paths:
        if p.exists():
            return p
    return None


def load_config(config_file: str | Path | None = None) -> Dict[str, Any]:
    """Load a configuration file (YAML or JSON).

    Parameters
    ----------
    config_file : str | Path | None, optional
        Path to configuration file. If *None*, the loader will search for
        ``config.yaml``, ``config.yml`` or ``config.json`` in the current
        working directory.
    """
    if config_file is None:
        config_file = _discover_default(
            [Path("config.yaml"), Path("config.yml"), Path("config.json")]
        )
        if config_file is None:
            raise FileNotFoundError("No configuration file found in cwd.")
    else:
        config_file = Path(config_file)

    if not config_file.exists():
        raise FileNotFoundError(config_file)

    suffix = config_file.suffix.lower()
    with config_file.open("r", encoding="utf-8") as f:
        if suffix in {".yml", ".yaml"}:
            cfg = yaml.safe_load(f)
        if suffix == ".json":
            cfg = json.load(f)
        if suffix not in {".yml", ".yaml", ".json"}:
            raise ValueError(f"Unsupported config extension: {suffix}")

    _validate_config_structure(cfg)
    return cfg


def _validate_config_structure(cfg: Dict[str, Any]) -> None:
    """Basic structural validation of the configuration dictionary.

    Raises ValueError with a human-readable message on invalid structures.
    """
    if not isinstance(cfg, dict):
        raise ValueError("Config root must be a mapping (dict)")

    commands = cfg.get("commands")
    if not isinstance(commands, list) or not commands:
        raise ValueError("'commands' must be a non-empty list")

    for idx, cmd in enumerate(commands):
        if not isinstance(cmd, dict):
            raise ValueError(f"commands[{idx}] must be a mapping")
        for key in ("name", "description", "args", "action"):
            if key not in cmd:
                raise ValueError(f"commands[{idx}] missing required key '{key}'")
        if not isinstance(cmd["name"], str) or not cmd["name"]:
            raise ValueError(f"commands[{idx}].name must be a non-empty string")
        if not isinstance(cmd["description"], str):
            raise ValueError(f"commands[{idx}].description must be a string")
        if not isinstance(cmd["action"], str) or not cmd["action"]:
            raise ValueError(f"commands[{idx}].action must be a non-empty string")

        args = cmd["args"]
        if not isinstance(args, list):
            raise ValueError(f"commands[{idx}].args must be a list")
        for aidx, arg in enumerate(args):
            if not isinstance(arg, dict):
                raise ValueError(f"commands[{idx}].args[{aidx}] must be a mapping")
            if "name" not in arg or "type" not in arg:
                raise ValueError(f"commands[{idx}].args[{aidx}] requires 'name' and 'type'")
            if not isinstance(arg["name"], str) or not isinstance(arg["type"], str):
                raise ValueError(f"commands[{idx}].args[{aidx}].name/type must be strings")
            if "rules" in arg and not isinstance(arg["rules"], dict):
                raise ValueError(f"commands[{idx}].args[{aidx}].rules must be a mapping if present")
            if "choices" in arg and not isinstance(arg["choices"], list):
                raise ValueError(f"commands[{idx}].args[{aidx}].choices must be a list if present")
