# Dynamic CLI Builder

Dynamic CLI Builder is a tool to help you create command-line interfaces (CLI) dynamically with ease.

## Features

- Easy to use
- Highly customizable
- Supports multiple command structures

## Installation

To install Dynamic CLI Builder, use the following command:

```bash
pip install dynamic-cli-builder
```

## Usage

Here is a simple example to get you started:

#### Create Actions

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

#### Create yaml config

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

#### Add rules for custom validation

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
      - name: age
        type: int
        help: "Age of the user."
        rules:
          min: 1
          max: 99
    action: say_hello
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
      - name: age
        type: int
        help: "Age of the user."
        rules:
          regex: "^[1-9][0-9]$"
    action: say_hello
```

#### Main file _main.py_

To bind this all together

```python
from dynamic_cli_builder import run_builder
from actions import ACTIONS

run_builder('config.yaml', ACTIONS)
```

#### CLI Command

##### Global Help

```
python3 <name_of_main_file> -h
```

For Instance:

```
python3 main.py -h
```

#### command specific help

```
 python3 <name_of_main_file> <name_of_command> -h
```

For Instance:

```
python3 main.py say_hello --name world --age 4530000000
```

You should see

> Hello World!, you are 4530000000 years old
