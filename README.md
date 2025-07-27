# Dynamic CLI Builder

[![PyPI version](https://img.shields.io/pypi/v/dynamic-cli-builder.svg)](https://pypi.org/project/dynamic-cli-builder/)
[![License](https://img.shields.io/github/license/idris-adigun/dynamic-cli-builder)](LICENSE)
[![CI](https://github.com/idris-adigun/dynamic-cli-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/idris-adigun/dynamic-cli-builder/actions/workflows/ci.yml)

**Dynamic CLI Builder** simplifies the creation of _interactive, configurable_ command-line interfaces (CLI) for your Python scripts.
Define your commands declaratively in YAML or JSON, register the corresponding Python functions, and obtain a production-ready CLI complete with validation, logging, and an optional interactive mode.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Logging & Interactive Mode](#logging--interactive-mode)
- [Roadmap](#roadmap)
- [License](#license)

## Features

- 🏗️  Declarative – design your CLI in YAML/JSON, no `argparse` boilerplate
- ⚙️  Highly customizable with pluggable validators and hooks
- 🔀 Supports nested commands & multiple command structures
- 🖥️  Optional interactive mode for prompting missing arguments
- 🔒 Built-in validation rules (min/max, regex, choices, etc.)
- 📜 Structured, configurable logging

## Installation

To install Dynamic CLI Builder, use the following command:

```bash
pip install dynamic-cli-builder
```

## Quick Start

Here is a simple example to get you started:

### 1. Create Actions

Actions are basically function to be executed base on command. <br> For instance _actions.py_

```python
def say_hello(name: str, age: int):
    print(f"Hello {name}!, you are {age} years old.")

# Action Registry
ACTIONS = {
    "say_hello": say_hello,
}
```

you can have multiple function registered

### 2. Define YAML/JSON Config

_config.yaml_

```yaml
description: "Dynamic CLI Builder Example"
commands:
  - name: say_hello
    description: "Say Hello..."
    args:
      - name: name
        type: str
        help: "Name of the user."
    action: say_hello
```

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
				}
			],
			"action": "say_hello"
		}
	]
}
```

### 3. Add Validation Rules

- min, max validation

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

## Roadmap

> **Compatibility policy**: We follow [Semantic Versioning](https://semver.org/). All patch and minor releases will remain backward-compatible. Breaking changes will be introduced only in the next **major** release and will be accompanied by a detailed migration guide.


### Short-term (v0.2.x)
- Add comprehensive docstrings and type hints across the codebase
- Split core logic into sub-modules (`validators`, `builder`, `io`) for better maintainability
- Extend `loader.py` to load JSON files and add automatic config path discovery
- Ship a `__main__.py` so the package can be run with `python -m dynamic_cli_builder`
- Introduce a pytest test-suite with GitHub Actions CI (linting, unit tests, coverage gate)
- Improve logging with configurable verbosity levels (DEBUG / INFO / WARNING)

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

This project is distributed under the [MIT License](LICENSE).


