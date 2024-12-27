import yaml

def load_config(config_file: str):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)
