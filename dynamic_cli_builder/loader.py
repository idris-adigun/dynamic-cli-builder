"""Configuration loader utilities.

Supports YAML (**.yml**, **.yaml**) and JSON (**.json**) configuration files.
If *config_file* is *None*, the loader will attempt to discover a suitable
configuration in the current working directory (``config.{yml,yaml,json}``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional

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
            return yaml.safe_load(f)
        if suffix == ".json":
            return json.load(f)
        raise ValueError(f"Unsupported config extension: {suffix}")
