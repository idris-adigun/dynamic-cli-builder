"""Module execution entry point for *Dynamic CLI Builder*.

Usage
-----
Run your CLI with:

    python -m dynamic_cli_builder [--config CONFIG] [--actions ACTIONS_PY]

Arguments
~~~~~~~~~
--config CONFIG
    Path to YAML/JSON configuration file. If omitted, the loader will attempt
    to locate *config.yaml|yml|json* in the current working directory.
--actions ACTIONS_PY
    Path to a Python file that exposes an ``ACTIONS`` dict mapping *action
    names* to callables. Defaults to ``actions.py`` in the current directory.

This wrapper simply delegates to :pyfunc:`dynamic_cli_builder.run_builder` after
importing the *ACTIONS* mapping.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict

from dynamic_cli_builder import run_builder


def _import_actions(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Actions file not found: {path}")

    spec = importlib.util.spec_from_file_location("actions", str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to import actions module at {path}")

    module = ModuleType("actions")
    spec.loader.exec_module(module)  # type: ignore[arg-type]

    try:
        return getattr(module, "ACTIONS")
    except AttributeError as exc:
        raise AttributeError(
            f"{path} must define a top-level 'ACTIONS' dictionary"
        ) from exc


def main(argv: list[str] | None = None) -> None:  # noqa: D401
    parser = argparse.ArgumentParser(description="Run Dynamic CLI Builder")
    parser.add_argument(
        "--config", "-c", type=str, default=None, 
        help="Path to config file (default: looks for config.yaml, config.yml, or config.json in current directory)"
    )
    parser.add_argument(
        "--actions", "-a", type=str, default="actions.py", 
        help="Path to actions file (default: actions.py in current directory)"
    )

    # If no arguments are provided, show help
    if len(sys.argv) == 1 and (argv is None or len(argv) == 0):
        parser.print_help()
        sys.exit(0)

    args, unknown = parser.parse_known_intermixed_args(argv)

    try:
        actions_path = Path(args.actions).resolve()
        actions_mapping = _import_actions(actions_path)
        
        # Pass through any additional CLI args to the command
        if unknown and unknown[0] not in ["--help", "-h"]:
            # If there's a command, pass it through
            sys.argv = [sys.argv[0], *unknown]
            run_builder(args.config, actions_mapping)
        else:
            # If no command provided, show help
            parser.print_help()
            sys.exit(0)
            
    except (FileNotFoundError, ImportError, AttributeError) as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
