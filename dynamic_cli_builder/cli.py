import argparse
import re


def validate_arg(value, rules):
    if "regex" in rules:
        if not re.match(rules["regex"], value):
            raise argparse.ArgumentTypeError(f"Value '{value}' does not match regex '{rules['regex']}'")
    if "min" in rules and float(value) < rules["min"]:
        raise argparse.ArgumentTypeError(f"Value '{value}' is less than minimum allowed value {rules['min']}")
    if "max" in rules and float(value) > rules["max"]:
        raise argparse.ArgumentTypeError(f"Value '{value}' is greater than maximum allowed value {rules['max']}")
    return value


def build_cli(config):
    parser = argparse.ArgumentParser(description=config.get("description", "Dynamic CLI"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in config["commands"]:
        subparser = subparsers.add_parser(command["name"], description=command["description"])
        for arg in command["args"]:
            arg_type = eval(arg["type"]) if arg["type"] != "json" else str
            if "rules" in arg:
                def custom_type(value, rules=arg["rules"]):
                    return validate_arg(value, rules)
                subparser.add_argument(f"--{arg['name']}", type=custom_type, help=arg["help"])
            else:
                subparser.add_argument(f"--{arg['name']}", type=arg_type, help=arg["help"])
    
    return parser

def execute_command(parsed_args, config, ACTIONS):
    for command in config["commands"]:
        if parsed_args.command == command["name"]:
            func = ACTIONS.get(command["action"])
            if not func:
                raise ValueError(f"Action '{command['action']}' not defined.")
            args = {arg["name"]: getattr(parsed_args, arg["name"], None) for arg in command["args"]}
            func(**args)
