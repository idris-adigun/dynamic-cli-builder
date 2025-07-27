"""Validation helpers for Dynamic CLI Builder.

This module centralises all argument-validation logic so that it can be
re-used by both the CLI builder and any external consumers.
"""
from __future__ import annotations

import argparse
import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)

__all__ = ["validate_arg"]


def validate_arg(value: str, rules: Dict[str, Any]) -> str:  # noqa: D401
    """Validate *value* against *rules* and return the original value.

    Supported rule keys
    -------------------
    regex : str
        Regular expression the value must match.
    min / max : int or float
        Numeric boundaries enforced after coercion with ``float``.

    Raises
    ------
    argparse.ArgumentTypeError
        If *value* does not satisfy any rule.
    """
    logger.debug("Validating argument %s with rules %s", value, rules)

    if "regex" in rules and not re.match(rules["regex"], value):
        logger.error("Value %s does not match regex %s", value, rules["regex"])
        raise argparse.ArgumentTypeError(
            f"Value '{value}' does not match regex '{rules['regex']}'"
        )

    if "min" in rules and float(value) < rules["min"]:
        logger.error("Value %s is less than min %s", value, rules["min"])
        raise argparse.ArgumentTypeError(
            f"Value '{value}' is less than minimum allowed value {rules['min']}"
        )

    if "max" in rules and float(value) > rules["max"]:
        logger.error("Value %s is greater than max %s", value, rules["max"])
        raise argparse.ArgumentTypeError(
            f"Value '{value}' is greater than maximum allowed value {rules['max']}"
        )

    return value
