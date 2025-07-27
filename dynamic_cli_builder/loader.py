"""Configuration loader utilities.

Currently supports YAML files but can be extended to other formats.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

def load_config(config_file: str | Path) -> Dict[str, Any]:
    """Load a YAML configuration file.

    Parameters
    ----------
    config_file : str | Path
        Path to the ``.yaml`` or ``.yml`` configuration file.

    Returns
    -------
    dict
        Parsed configuration as Python primitives.
    """
    config_file = Path(config_file)
    if not config_file.exists():
        raise FileNotFoundError(config_file)

    with config_file.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f)
