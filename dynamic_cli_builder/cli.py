import argparse
import re
import logging

def configure_logging(enable_logging):
    if enable_logging:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.CRITICAL)  # Disable logging by setting the level to CRITICAL

logger = logging.getLogger(__name__)

def validate_arg(value, rules):
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

def build_cli(config):
    parser = argparse.ArgumentParser(description=config.get("description", "Dynamic CLI"))
    parser.add_argument('-log', action='store_true', help='Enable logging')
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

def prompt_for_missing_args(parsed_args, config):
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

def execute_command(parsed_args, config, ACTIONS):
    configure_logging(parsed_args.log)
    logger.info(f"Executing command: {parsed_args.command}")
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
