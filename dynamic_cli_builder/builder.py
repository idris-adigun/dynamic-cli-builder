"""CLI *builder* – responsible for translating a config object into `argparse` parsers."""
from __future__ import annotations

import argparse
import logging
from typing import Any, Dict, Callable, Callable as _Callable

import json

from dynamic_cli_builder.validators import validate_arg

logger = logging.getLogger(__name__)

__all__ = ["build_cli", "prompt_for_missing_args", "execute_command", "configure_logging"]


def configure_logging(level: str = "WARNING") -> None:
    """Configure root logger according to *level* string."""
    logging.basicConfig(level=getattr(logging, level), format="%(asctime)s - %(levelname)s - %(message)s")

def _str2bool(val: str) -> bool:
    truthy = {"1", "true", "t", "yes", "y", "on"}
    falsy = {"0", "false", "f", "no", "n", "off"}
    v = val.strip().lower()
    if v in truthy:
        return True
    if v in falsy:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {val}")


def _type_converter(type_name: str) -> _Callable[[str], Any]:
    """Return a safe converter function for a configured type name."""
    mapping: Dict[str, _Callable[[str], Any]] = {
        "str": str,
        "int": int,
        "float": float,
        "bool": _str2bool,
        # For complex types, expect JSON literals (e.g. '[1,2]' or '{"a":1}')
        "json": lambda s: json.loads(s),
        "list": lambda s: json.loads(s),
        "dict": lambda s: json.loads(s),
    }
    return mapping.get(type_name, str)


def build_cli(config: Dict[str, Any]) -> argparse.ArgumentParser:
    """Construct an `argparse.ArgumentParser` based on *config*."""
    parser = argparse.ArgumentParser(description=config.get("description", "Dynamic CLI"))
    parser.add_argument("-log", action="store_true", help="(Deprecated) enable INFO logging")
    parser.add_argument("-v", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="WARNING", help="Set log verbosity level")
    parser.add_argument("-im", action="store_true", help="Enable Interactive Mode")

    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in config["commands"]:
        logger.debug("Adding command: %s", command["name"])
        subparser = subparsers.add_parser(command["name"], description=command["description"])
        for arg in command["args"]:
            target_type = _type_converter(arg.get("type", "str"))

            # Build a converter that validates (if rules present) and then coerces
            def make_converter(rules: Dict[str, Any] | None, to_type: _Callable[[str], Any]):
                def _convert(raw: str) -> Any:
                    # Always validate against string input first
                    if rules is not None:
                        validate_arg(raw, rules)
                    # Then coerce to target type
                    try:
                        return to_type(raw)
                    except Exception as exc:  # pragma: no cover - argparse surfaces message
                        raise argparse.ArgumentTypeError(str(exc)) from exc
                return _convert

            converter = make_converter(arg.get("rules"), target_type)

            # Coerce choices to the same type argparse will compare against
            coerced_choices = None
            if "choices" in arg and arg["choices"] is not None:
                coerced_choices = []
                for c in arg["choices"]:
                    try:
                        coerced_choices.append(target_type(c) if isinstance(c, str) else c)
                    except Exception:  # keep original if cannot coerce
                        coerced_choices.append(c)

            subparser.add_argument(
                f"--{arg['name']}",
                type=converter,
                help=arg.get("help"),
                required=arg.get("required", False),
                choices=coerced_choices,
                default=arg.get("default"),
            )
    return parser


def prompt_for_missing_args(parsed_args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """Interactively ask for values missing on the CLI (when `-im` is supplied)."""
    for command in config["commands"]:
        if parsed_args.command == command["name"]:
            for arg in command["args"]:
                if getattr(parsed_args, arg["name"]) is None:
                    while True:
                        value = input(f"Please enter a value for {arg['name']}: ")
                        try:
                            validate_arg(value, arg["rules"])
                            break
                        except argparse.ArgumentTypeError as exc:
                            print(exc)
                    setattr(parsed_args, arg["name"], value)


def execute_command(parsed_args: argparse.Namespace, config: Dict[str, Any], ACTIONS: Dict[str, Callable[..., Any]]) -> None:
    """Execute the python function mapped to *parsed_args.command*."""
    effective_level = "INFO" if parsed_args.log else parsed_args.log_level
    configure_logging(effective_level)

    if parsed_args.im:
        prompt_for_missing_args(parsed_args, config)

    for command in config["commands"]:
        if parsed_args.command == command["name"]:
            func = ACTIONS.get(command["action"])
            if func is None:
                raise ValueError(f"Action '{command['action']}' not defined.")
            args = {arg["name"]: getattr(parsed_args, arg["name"], None) for arg in command["args"]}
            logger.debug("Executing action %s with args %s", command["action"], args)
            func(**args)
