# Dynamic CLI Builder

[![PyPI version](https://img.shields.io/pypi/v/dynamic-cli-builder.svg)](https://pypi.org/project/dynamic-cli-builder/) [![License](https://img.shields.io/github/license/idris-adigun/dynamic-cli-builder)](LICENSE) [![CI](https://github.com/idris-adigun/dynamic-cli-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/idris-adigun/dynamic-cli-builder/actions/workflows/ci.yml)

**Dynamic CLI Builder** simplifies the creation of _interactive, configurable_ command-line interfaces (CLI) for your Python scripts. Define your commands declaratively in YAML or JSON, register the corresponding Python functions, and obtain a production-ready CLI complete with validation, logging, and an optional interactive mode.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Version Information](#version-information)
  - [Version 0.2.x and above](#version-02x-and-above)
  - [Version 0.1.x and below](#version-01x-and-below)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)
- [Generate Config](#generate-config)
- [Best Practices](#best-practices)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

- Declarative – design your CLI in YAML/JSON, no `argparse` boilerplate
- Highly customizable with pluggable validators and hooks
- Supports nested commands & multiple command structures
- Optional interactive mode for prompting missing arguments
- Built-in validation rules (min/max, regex, choices, etc.)
- Structured, configurable logging
- Zero configuration mode with smart defaults

## Installation

Install using pip:

```bash
# Basic installation
pip install dynamic-cli-builder

# For development
pip install -e .
```

This will install the `dcb` command-line tool that you can use to run your CLI applications.

## Version Information

### Version 0.2.3 and above

Starting from version 0.2.0, the CLI interface has been significantly improved with better error handling, more intuitive command structure, and additional features. Key changes include:

- New command structure: `dcb [OPTIONS] COMMAND [ARGS]...`
- Support for both YAML and JSON configuration files
- Built-in interactive mode
- Improved error messages and help text
- Better support for environment variables
- More flexible configuration options

### Version 0.1.x and below

For versions before 0.2.0, the CLI had a different interface and fewer features:

- Old command structure: ` python3 NAME_OF_MAIN_FILE [OPTIONS] COMMAND [ARGS]...`
- Support for both YAML and JSON configuration files
- Built-in interactive mode
- Basic error handling

If you're using version 0.1.x, consider upgrading to the latest version for better features and support. To upgrade:

```bash
pip install --upgrade dynamic-cli-builder
```

> **Note**: Version 0.2.0 includes breaking changes. Please update your configuration files and scripts accordingly.

## Quick Start

### 1. Create a Configuration File

Create a `config.yaml` file to define your CLI structure:

```yaml
commands:
  say_hello:
    help: "Say hello to someone"
    args:
      name:
        type: str
        help: "Name of the person to greet"
        required: true
      age:
        type: int
        help: "Age of the person"
        default: 42
```

### 2. Create an Actions File

Create an `actions.py` file with your command implementations:

```python
def say_hello(name: str, age: int) -> None:
    """Greet a person with their name and age."""
    print(f"Hello {name}, you are {age} years old!")

# Required: Map command names to their implementations
ACTIONS = {
    "say_hello": say_hello
}
```

### 3. Run Your CLI

Use either of these commands to run your CLI:

```bash
# Using the dcb command (recommended)
dcb --config config.yaml say_hello --name Alice

# Or using Python module
python -m dynamic_cli_builder --config config.yaml say_hello --name Alice
```

This will output:

```
Hello Alice, you are 42 years old!
```

## Usage

### Basic Usage

```bash
dcb [OPTIONS] COMMAND [ARGS]...
```

### Available Options

- `--config`, `-c`: Path to config file (default: looks for `config.yaml`, `config.yml`, or `config.json`)
- `--actions`, `-a`: Path to actions file (default: `actions.py` in current directory)
- `--log-level`, `-l`: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--interactive`, `-i`: Enable interactive mode
- `--help`, `-h`: Show help message

### Examples

```bash
# Run with custom config and actions
dcb -c my_config.yaml -a my_actions.py my_command --arg1 value1

# Enable debug logging
dcb -l DEBUG my_command

# Run in interactive mode
dcb -i my_command
```

## Configuration

### File Format

You can use either YAML or JSON for your configuration files. Both formats support the same structure.

#### YAML Example

```yaml
commands:
  greet:
    help: "Greet a person"
    args:
      name:
        type: str
        help: "Person's name"
        required: true
      age:
        type: int
        help: "Person's age"
        default: 42
      title:
        type: str
        help: "Person's title"
        choices: ["Mr", "Mrs", "Ms", "Dr"]
        default: "Mr"
```

#### JSON Example

```json
{
	"commands": {
		"greet": {
			"help": "Greet a person",
			"args": {
				"name": {
					"type": "str",
					"help": "Person's name",
					"required": true
				},
				"age": {
					"type": "int",
					"help": "Person's age",
					"default": 42
				},
				"title": {
					"type": "str",
					"help": "Person's title",
					"choices": ["Mr", "Mrs", "Ms", "Dr"],
					"default": "Mr"
				}
			}
		}
	}
}
```

### Argument Types

Supported argument types:

- `str`: String value (default)
- `int`: Integer value
- `float`: Floating-point number
- `bool`: Boolean flag (no value needed)
- `list`: List of values
- `dict`: Dictionary of values

### Validation Rules

Add validation rules to your arguments:

```yaml
commands:
  create_user:
    help: "Create a new user"
    args:
      username:
        type: str
        help: "Username (3-20 chars, alphanumeric)"
        regex: "^[a-zA-Z0-9_]{3,20}$"
      email:
        type: str
        help: "Email address"
        required: true
      age:
        type: int
        help: "User's age (18-120)"
        min: 18
        max: 120
```

## Advanced Usage

### Logging

Control logging verbosity with the `--log-level` option:

```bash
# Show debug messages
dcb --log-level DEBUG my_command

# Only show errors
dcb --log-level ERROR my_command

# Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Interactive Mode

Enable interactive mode to be prompted for missing required arguments:

```bash
dcb --interactive create_user
```

You'll be prompted to enter values for any missing required arguments.

### Generate Config

Generate a starter YAML/JSON config by pointing the tool at your actions file. The generator introspects your functions, using type hints and defaults to infer argument types and requirements.

```bash
# Print YAML to stdout
python -m dynamic_cli_builder --actions path/to/actions.py --generate

# Write JSON to a file
python -m dynamic_cli_builder --actions path/to/actions.py --generate \
  --format json --output config.json

# Using the console script
dcb --actions path/to/actions.py --generate --format yaml --output config.yaml
```

Behavior:

- Prefers `ACTIONS` mapping in the module; falls back to top-level callables.
- Uses first line of function docstring as command description.
- Infers types from annotations: `str`, `int`, `float`, `bool`; complex types → `list`/`dict`/`json`.
- Marks params without defaults as `required: true`; otherwise sets `default`.
- Skips private names (`_foo`), `*args`, and `**kwargs`.

### Notes on Types

- Primitive types supported: `str`, `int`, `float`, `bool`.
- For complex values (`list`, `dict`, `json`), pass JSON literals, e.g. `--items '["a","b"]'` or `--cfg '{"k":1}'`.
- The `-log` flag is deprecated; prefer `--log-level INFO`.

### Programmatic Usage

Use the builder in your Python code:

```python
from dynamic_cli_builder import run_builder

def greet(name: str, age: int, title: str = "Mr") -> None:
    """Display a greeting."""
    print(f"Hello {title} {name}, you are {age} years old!")

# Define your command mappings
ACTIONS = {
    "greet": greet
}

# Run with custom configuration
config = {
    "commands": {
        "greet": {
            "help": "Greet someone",
            "args": {
                "name": {"type": "str", "required": True},
                "age": {"type": "int", "required": True},
                "title": {"type": "str", "choices": ["Mr", "Mrs", "Ms", "Dr"], "default": "Mr"}
            }
        }
    }
}

if __name__ == "__main__":
    run_builder(config=config, actions=ACTIONS)
```

## Best Practices

1. **Keep Actions Simple**: Each action should do one thing well
2. **Use Type Hints**: Always type hint your action functions
3. **Validate Early**: Use the built-in validation rules when possible
4. **Document Help Text**: Provide clear help text for all commands and arguments
5. **Test Thoroughly**: Test your CLI with various inputs and edge cases

## Roadmap

### Upcoming Features

```yaml
description: "Dynamic CLI Builder Example"
commands:
  - name: say_hello
    description: "Say Hello..."
    args:
      - name: name
        type: str
        help: "Name of the user."
        rules: ""
      - name: age
        type: int
        help: "Age of the user."
        rules:
          min: 1
          max: 99
    action: say_hello
```

In Json:

```json
{
	"description": "Dynamic CLI JSON",
	"commands": [
		{
			"name": "say_hello",
			"description": "Say hello...",
			"args": [
				{
					"name": "name",
					"type": "str",
					"help": "Name of the User.",
					"rules": ""
				},
				{
					"name": "age",
					"type": "str",
					"help": "Age of the User.",
					"rules": {
						"min": 1,
						"max": 10
					}
				}
			],
			"action": "say_hello"
		}
	]
}
```

- for more control, you could also use regex

```yaml
description: "Dynamic CLI Builder Example"
commands:
  - name: say_hello
    description: "Say Hello..."
    args:
      - name: name
        type: str
        help: "Name of the user."
        rules: ""
        required: True
      - name: age
        type: int
        help: "Age of the user."
        rules:
          regex: "^[1-9][0-9]$"
        required: True
    action: say_hello
```

or json equivalent

```json
{
  "description": "Dynamic CLI JSON",
  "commands": [
    {
      "name": "say_hello",
      "description": "Say hello...",
      "args": [
          {
              "name": "name",
              "type": "str",
              "help": "Name of the User.",
              "rules": "",
              "required": true
          },
          {
              "name": "age",
              "type": "str",
              "help": "Age of the User.",
              "required": true
              "rules": {
                  "regex": "^[1-9][0-9]$"
              }
          }
      ],
      "action": "say_hello"

    }
  ]
}
```

### 4. Run the Builder (_main.py_)

To bind this all together

```python
from dynamic_cli_builder import run_builder
from actions import ACTIONS

run_builder('config.yaml', ACTIONS)
```

## Command Reference

### Global Help

```
python3 <name_of_main_file> -h
```

For Instance:

```
python3 main.py -h
```

### Command-Specific Help

```
 python3 <name_of_main_file> <name_of_command> -h
```

For Instance:

```
python3 main.py say_hello --name world --age 99
```

You should see

> Hello World!, you are 99 years old

## Logging & Interactive Mode

logging is set to false by default, to enable logging add _-log_ to your command just after the file name

```
python3 main.py -log say_hello --name world --age 99
```

Output:

> 2025-01-29 12:08:19,518 - INFO - Building CLI with config.

> 2025-01-29 12:08:19,532 - INFO - Executing command: say_hello

> Hello World!, you are 99 years old.

Interactive mode is set to false by default to enable interactive mode, add _-im_ to your command For instance:

```
python3 main.py -im say_hello --name world --age 99
```

## Running the CLI

### 1. Recommended (v0.2+)

Use the module entry-point shipped in `__main__.py`. No imports required – just point the runner at a config file and an _actions_ registry:

```bash
# auto-discover config.yaml & actions.py in CWD
python -m dynamic_cli_builder say_hello --name Alice --age 25

# explicit paths
python -m dynamic_cli_builder \
    --config path/to/config.yaml \
    --actions path/to/actions.py \
    --log-level DEBUG \
    say_hello --name Alice
```

Flags:

- `--config/-c` – YAML/JSON config. If omitted the loader searches `config.{yaml,yml,json}` in CWD.
- `--actions/-a` – Python file exposing `ACTIONS` dict. Defaults to `actions.py` in CWD.
- `--log-level/-v` – `DEBUG|INFO|WARNING|ERROR|CRITICAL` (default `WARNING`). The legacy `-log` flag still enables INFO for backward-compat.
- `-im` – Interactive Mode; prompts for any missing arguments.

### 2. Legacy API (≤ v0.1)

If you were importing functions directly, the _shim_ in `dynamic_cli_builder.cli` keeps things working – but prefer the new API above.

```python
from dynamic_cli_builder import cli  # legacy shim
from my_actions import ACTIONS

config = cli.load_config("config.yaml")
parser = cli.build_cli(config)
args = parser.parse_args()
cli.execute_command(args, config, ACTIONS)
```

All helpers (`build_cli`, `execute_command`, `validate_arg`, etc.) are re-exported so old code continues to run unchanged.

---

## Roadmap

> **Compatibility policy**: We follow [Semantic Versioning](https://semver.org/). All patch and minor releases will remain backward-compatible. Breaking changes will be introduced only in the next **major** release and will be accompanied by a detailed migration guide.

### Mid-term (v0.3.x)

- Enrich validation rules (choices, default values, conditional validation)
- Validate configs with `pydantic` or `jsonschema` before building the CLI
- Provide an interactive wizard for generating YAML/JSON configs
- Automate semantic versioning & releases via `semantic-release` or `bumpver`

### Long-term (v1.0)

- Migrate command parsing to `typer` for rich help text, autocompletion and colored output
- Introduce a plugin architecture for custom argument types, validators and output handlers
- Publish full documentation site (Sphinx + ReadTheDocs) with tutorials and API reference
- Achieve >90 % test coverage and add performance benchmarks
- Offer a Docker image and Gitpod template for instant try-out

### Nice-to-have Explorations

- Terminal UI (TUI) mode powered by `textual` / `rich`
- VS Code extension for live schema preview and command auto-completion

---

## License

MIT License

```
Copyright (c) 2025 Idris Adigun

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

This project is distributed under the [MIT License](LICENSE).
