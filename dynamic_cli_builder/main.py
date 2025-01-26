from dynamic_cli_builder.cli import build_cli, execute_command
from dynamic_cli_builder.loader import load_config


def run_builder(config_path, ACTIONS):
    # Load the YAML configuration
    config = load_config(config_path)
    
    # Build the CLI
    parser = build_cli(config)
    
    # Parse the CLI arguments
    parsed_args = parser.parse_args()
    
    # Execute the appropriate command
    execute_command(parsed_args, config, ACTIONS)