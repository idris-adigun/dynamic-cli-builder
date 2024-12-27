import argparse


def build_cli(config):
    parser = argparse.ArgumentParser(description=config.get("description", "Dynamic CLI"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in config["commands"]:
        subparser = subparsers.add_parser(command["name"], description=command["description"])
        for arg in command["args"]:
            arg_type = eval(arg["type"]) if arg["type"] != "json" else str
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
