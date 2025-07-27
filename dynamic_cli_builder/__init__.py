"""Public package interface for *Dynamic CLI Builder*.

Expose the high-level :pyfunc:`run_builder` helper that glues together
configuration loading, CLI construction and command execution.
"""

from __future__ import annotations

from typing import Any, Dict, Callable

from dynamic_cli_builder.cli import build_cli, execute_command
from dynamic_cli_builder.loader import load_config


def run_builder(config_path: str, ACTIONS: Dict[str, Callable[..., Any]]) -> None:
    """Entry point for quickly wiring the builder into a script.

    Parameters
    ----------
    config_path : str
        Path to YAML/JSON configuration describing the CLI structure.
    ACTIONS : dict[str, Callable[..., Any]]
        Mapping of *action name* to callable implementing the logic.
    """
    # Load the YAML configuration
    config = load_config(config_path)
    
    # Build the CLI
    parser = build_cli(config)
    
    # Parse the CLI arguments
    parsed_args = parser.parse_args()
    
    # Execute the appropriate command
    execute_command(parsed_args, config, ACTIONS)