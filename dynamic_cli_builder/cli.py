"""Legacy shim kept for backward-compatibility.

All actual logic now lives in :pymod:`dynamic_cli_builder.builder` and
:pymod:`dynamic_cli_builder.validators`. This module re-exports the public
APIs so existing imports continue to work.
"""

from __future__ import annotations

import logging
from typing import Any

from dynamic_cli_builder.builder import (
    build_cli,
    execute_command,
    prompt_for_missing_args,
    configure_logging as _configure_logging_level,
)
from dynamic_cli_builder.validators import validate_arg

__all__ = [
    "build_cli",
    "execute_command",
    "prompt_for_missing_args",
    "validate_arg",
    "configure_logging",
    "logging",
]

def configure_logging(enable_logging: bool) -> None:
    """Backward-compat wrapper: enable INFO when True, CRITICAL when False."""
    _configure_logging_level("INFO" if enable_logging else "CRITICAL")

logger = logging.getLogger(__name__)
