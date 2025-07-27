"""Legacy shim kept for backward-compatibility.

All actual logic now lives in :pymod:`dynamic_cli_builder.builder` and
:pymod:`dynamic_cli_builder.validators`. Importing from this module will
continue to work, but new code should depend on the dedicated sub-modules.
"""

from __future__ import annotations

import argparse
import logging
from typing import Any, Callable, Dict

from dynamic_cli_builder.builder import (
    build_cli,
    execute_command,
    prompt_for_missing_args,
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
    """Configure the global logging settings.

    Parameters
    ----------
    enable_logging : bool
        When *True*, sets the root logger level to ``INFO`` and enables a
        human-readable formatter. When *False*, logging is silenced by raising
        the level to ``CRITICAL``.
    """
    if enable_logging:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.CRITICAL)  # Disable logging by setting the level to CRITICAL

logger = logging.getLogger(__name__)

def validate_arg(value: str, rules: Dict[str, Any]) -> str:
    """Validate a single CLI argument against a set of *rules*.

    Supported rule keys
    -------------------
    regex : str
        Regular expression the value must match.
    min / max : int or float
        Numeric boundaries enforced after coercion with ``float``.

    Returns
    -------
    str
        The *value* if validation succeeds.

    Raises
    ------
    argparse.ArgumentTypeError
        If *value* does not satisfy the rules.
    """
    logger.debug(f"Validating argument: {value} with rules: {rules}")
    if "regex" in rules:
        if not re.match(rules["regex"], value):
            logger.error(f"Value '{value}' does not match regex '{rules['regex']}'")
            raise argparse.ArgumentTypeError(f"Value '{value}' does not match regex '{rules['regex']}'")
    if "min" in rules and float(value) < rules["min"]:
        logger.error(f"Value '{value}' is less than minimum allowed value {rules['min']}")
        raise argparse.ArgumentTypeError(f"Value '{value}' is less than minimum allowed value {rules['min']}")
    if "max" in rules and float(value) > rules["max"]:
        logger.error(f"Value '{value}' is greater than maximum allowed value {rules['max']}")
        raise argparse.ArgumentTypeError(f"Value '{value}' is greater than maximum allowed value {rules['max']}")
    return value

# --- legacy implementations removed in favour of re-exported versions ---

    parser = argparse.ArgumentParser(description=config.get("description", "Dynamic CLI"))
    parser.add_argument('-log', action='store_true', help='Enable logging')
    parser.add_argument('-im', action='store_true', help='Enable Interactive Mode')
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in config["commands"]:
        logger.debug(f"Adding command: {command['name']}")
        subparser = subparsers.add_parser(command["name"], description=command["description"])
        for arg in command["args"]:
            arg_type = eval(arg["type"]) if arg["type"] != "json" else str
            if "rules" in arg:
                def custom_type(value, rules=arg["rules"]):
                    return validate_arg(value, rules)
                subparser.add_argument(f"--{arg['name']}", type=custom_type, help=arg["help"], required=arg.get("required", False))
            else:
                subparser.add_argument(f"--{arg['name']}", type=arg_type, help=arg["help"], required=arg.get("required", False))
    
    return parser

def prompt_for_missing_args(parsed_args: argparse.Namespace, config: Dict[str, Any]) -> None:
    for command in config["commands"]:
        if parsed_args.command == command["name"]:
            for arg in command["args"]:
                if getattr(parsed_args, arg["name"]) is None:
                    while True:
                        value = input(f"Please enter a value for {arg['name']}: ")
                        try:
                            validate_arg(value, arg["rules"])
                            break
                        except argparse.ArgumentTypeError as e:
                            print(e)
                    setattr(parsed_args, arg["name"], value)

def execute_command(
    parsed_args: argparse.Namespace,
    config: Dict[str, Any],
    ACTIONS: Dict[str, Callable[..., Any]],
) -> None:
    configure_logging(parsed_args.log)
    logger.info(f"Executing command: {parsed_args.command}")
    if(parsed_args.im):
        prompt_for_missing_args(parsed_args, config)
    for command in config["commands"]:
        if parsed_args.command == command["name"]:
            func = ACTIONS.get(command["action"])
            if not func:
                logger.error(f"Action '{command['action']}' not defined.")
                raise ValueError(f"Action '{command['action']}' not defined.")
            args = {arg["name"]: getattr(parsed_args, arg["name"], None) for arg in command["args"]}
            logger.debug(f"Executing action: {command['action']} with args: {args}")
            func(**args)
