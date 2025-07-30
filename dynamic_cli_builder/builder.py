"""CLI *builder* – responsible for translating a config object into `argparse` parsers."""
from __future__ import annotations

import argparse
import logging
from typing import Any, Dict, Callable

from dynamic_cli_builder.validators import validate_arg

logger = logging.getLogger(__name__)

__all__ = ["build_cli", "prompt_for_missing_args", "execute_command", "configure_logging"]


def configure_logging(level: str = "WARNING") -> None:
    """Configure root logger according to *level* string."""
    logging.basicConfig(level=getattr(logging, level), format="%(asctime)s - %(levelname)s - %(message)s")

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
            arg_type = eval(arg["type"]) if arg["type"] != "json" else str
            if "rules" in arg:
                def custom_type(value: str, rules=arg["rules"]):
                    return validate_arg(value, rules)
                subparsers_help = arg["help"]
                subparser.add_argument(f"--{arg['name']}", type=custom_type, help=subparsers_help, required=arg.get("required", False))
            else:
                subparser.add_argument(f"--{arg['name']}", type=arg_type, help=arg["help"], required=arg.get("required", False))
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
