# Dynamic CLI Builder — User Specification and Stories

## Overview

Dynamic CLI Builder generates command‑line interfaces from declarative YAML/JSON configs and dispatches to Python callables provided in an `ACTIONS` registry. The execution flow is: load config → build `argparse` parser → parse args → validate → dispatch → execute. It also includes a generator that can introspect an actions module to scaffold a config.

Key modules:
- `dynamic_cli_builder/loader.py`: Config discovery and loading (YAML/JSON)
- `dynamic_cli_builder/builder.py`: Parser construction, interactive prompting, execution
- `dynamic_cli_builder/validators.py`: Per‑argument validation (regex/min/max)
- `dynamic_cli_builder/__main__.py`: Module entry point importing `ACTIONS`
- `dynamic_cli_builder/__init__.py`: `run_builder(config_path, ACTIONS)` helper
 - `dynamic_cli_builder/generator.py`: Generate/dump config from actions module or `ACTIONS`

## Personas

- Developer (Library User): Defines actions and configuration; builds and ships a CLI.
- CLI User (End User): Runs the commands defined by the developer.
- Maintainer (Contributor): Evolves the library, fixes bugs, adds features/tests.

## Goals

- Declarative CLI definition via YAML/JSON (no manual argparse).
- Map subcommands to Python functions via `ACTIONS`.
- Validate inputs with regex/min/max rules.
- Optional interactive prompting for missing args.
- Configurable logging verbosity.

## Non‑Goals

- Rich/complex type parsing beyond basic primitives.
- Full configuration schema validation.
- Plugins/autocompletion or advanced TUI (not yet).
- Built‑in environment variable expansion for args (not implemented).

## Architecture

1) Loading: `load_config(config_file)` reads YAML/JSON; if `None`, auto‑discovers `config.{yaml,yml,json}` in CWD.
2) Building: `build_cli(config)` creates an `argparse` parser with subcommands and options from the config.
3) Validation: Arg rules (`regex|min|max`) applied via custom `type=` converter calling `validators.validate_arg`.
4) Dispatch: `execute_command(ns, config, ACTIONS)` looks up the action and calls it with parsed kwargs.
5) Generator (optional): `generate_config(module, ACTIONS?)` builds a config dict by inspecting functions (type hints, defaults, docstrings first line). `dump_config(cfg, fmt)` renders YAML/JSON.
6) Entrypoints:
   - CLI: `python -m dynamic_cli_builder` or console script `dcb`.
   - API: `run_builder(config_path, ACTIONS)` for embedding in scripts.

## Installation

```
pip install dynamic-cli-builder
```

Requires Python 3.6+. Dependency: `pyyaml`.

## CLI Interface

General form:

```
dcb [--config PATH] [--actions PATH] COMMAND [--arg value ...] [--log-level LEVEL] [-im] [-log]
python -m dynamic_cli_builder [--config PATH] [--actions PATH] COMMAND [...]
```

Runner options (handled before command parsing):
- `--config, -c`: Path to YAML/JSON config (auto‑discovers if omitted).
- `--actions, -a`: Path to Python file exporting `ACTIONS` (defaults to `actions.py`).
 - `--generate, -g`: Generate a config from the actions module and print it or save with `--output`.
 - `--format, -f`: Output format when generating (`yaml`|`json`, default `yaml`).
 - `--output, -o`: Output path for generated config (`-` for stdout, default `-`).

Global options (handled by the built parser):
- `--log-level, -v`: `DEBUG|INFO|WARNING|ERROR|CRITICAL` (default `WARNING`).
- `-log`: Deprecated; forces INFO level when present.
- `-im`: Interactive mode; prompt for missing args.

## Configuration Schema

Top level:
- `description` (str): CLI description.
- `commands` (list): Command objects.

Command object:
- `name` (str): Subcommand name.
- `description` (str): Help/description.
- `args` (list): Argument objects.
- `action` (str): Name of callable in `ACTIONS`.

Argument object:
- `name` (str): Argument name (used as `--name`).
- `type` (str): One of basic types (`str`, `int`, `float`, `bool`) and complex types parsed from JSON (`list`, `dict`, `json`).
- `help` (str): Help text.
- `required` (bool, optional): Whether required (default False).
- `rules` (dict, optional): Validation rules supporting keys:
  - `regex` (str): Must match.
  - `min` (number): Minimum numeric value.
  - `max` (number): Maximum numeric value.

Example (YAML):

```
description: Demo
commands:
  - name: greet
    description: Say hi
    args:
      - { name: name, type: str, help: Name, required: true }
      - { name: age,  type: int, help: Age,  rules: { min: 1, max: 120 } }
    action: greet
```

## Actions Contract

Developers provide an `ACTIONS` dict mapping action names to callables. Callable parameter names must match arg names. Example:

```python
def greet(name: str, age: int) -> None:
    print(f"Hello {name}! You are {age}.")

ACTIONS = {"greet": greet}
```

## Validation Rules

`validators.validate_arg(value, rules)` enforces:
- `regex`: raises `argparse.ArgumentTypeError` if not matched.
- `min`/`max`: numeric bounds after `float(value)` conversion.

## Interactive Mode

With `-im`, any missing args for the chosen command are prompted via `input()` until validation succeeds. Values are then assigned on the parsed namespace and used for execution.

## Logging

- `--log-level` sets the root logger level with a standard formatter.
- `-log` (deprecated) forces INFO level regardless of `--log-level`.

## Programmatic API

```python
from dynamic_cli_builder import run_builder
from actions import ACTIONS

run_builder("config.yaml", ACTIONS)
```

## Entry Points

- Module: `python -m dynamic_cli_builder`
- Console scripts: `dcb`, `dynamic-cli-builder`

## Errors & Handling

- Missing config or path: `FileNotFoundError`.
- Unsupported extension: `ValueError`.
- Missing `ACTIONS` in actions file: `AttributeError` (during import in entrypoint).
- Unknown `action` key at runtime: `ValueError` in `execute_command`.
- Validation failures: `argparse.ArgumentTypeError` (printed by argparse).

## Security & Constraints

- Safe type conversion map (no `eval`): `str`, `int`, `float`, `bool`; `list`/`dict`/`json` parsed via JSON.
- Config schema is validated structurally at load time (basic checks), not with a full JSON Schema/Pydantic model.

## Compatibility

- `dynamic_cli_builder.cli` exists as a legacy shim that re‑exports builder/validator functions.
- Some README roadmap features (env vars, plugins) are not implemented yet.

## Examples

CLI:

```
python -m dynamic_cli_builder --config example/config.yaml --actions example/actions.py say_hello --name Alice --age 25
```

Programmatic (see `example/main.py`).

## Testing

Covered areas:
- Loader (YAML/JSON + auto‑discovery)
- Builder (parse + command execution)
- Validators (success/failure cases)
- Entrypoint (`__main__`) import and execution

See `tests/test_loader.py`, `tests/test_builder_cli.py`, `tests/test_additional.py`, `tests/test_flow_md.py`.

## Known Gaps

- No environment variable integration for arguments or config defaults.
- No JSON Schema/Pydantic validation of configs (only basic structure checks).
- Generator does not parse per-parameter docstrings for help text; uses a generic help string.

## User Stories

Developer
- As a developer, I can define a CLI in YAML/JSON with commands, args, and an action mapping, so I can generate a working CLI without writing argparse code.
  - Acceptance: Given a config with one command and two args, the parser accepts `COMMAND --arg1 v1 --arg2 v2` and dispatches to the `ACTIONS` function with matching kwargs.
- As a developer, I can add validation rules (regex/min/max) so invalid inputs are rejected early.
  - Acceptance: Regex mismatch and out‑of‑bounds values produce argparse errors.
- As a developer, I can enable interactive mode to prompt for missing required arguments.
  - Acceptance: With `-im`, missing args are prompted; valid inputs lead to successful execution.
- As a developer, I can set logging verbosity to see debug/info/warnings as needed.
  - Acceptance: `--log-level INFO` shows info logs; `-log` also enables INFO.
- As a developer, I can run the CLI via the module or console script with optional `--config` and `--actions` paths.
  - Acceptance: `python -m dynamic_cli_builder -c config.yaml -a actions.py command ...` executes properly.
- As a developer, I can auto-generate a starter config from my actions module so I don’t have to write YAML/JSON from scratch.
  - Acceptance: `--actions path --generate` prints valid YAML/JSON; functions in `ACTIONS` are converted to commands with inferred arg types and defaults; private names and varargs are skipped.

CLI User
- As a CLI user, I can discover commands and arguments via `-h` so I know how to use the tool.
  - Acceptance: No command prints usage/help; `COMMAND -h` shows arg help.
- As a CLI user, I can run a command and receive expected output from the underlying action.
  - Acceptance: `say_hello --name Bob --age 30` prints the expected greeting (with provided example actions).

Maintainer
- As a maintainer, I can ensure configs load correctly and errors are clear.
  - Acceptance: Unsupported or missing files produce explicit exceptions.
- As a maintainer, I can rely on tests covering builder, loader, validators, and entrypoint behaviors.
  - Acceptance: Tests run and cover the described areas.
- As a maintainer, I can clean the legacy shim without breaking existing imports from `dynamic_cli_builder.cli`.
  - Acceptance: The shim re‑exports `build_cli`, `execute_command`, `configure_logging`, and `validate_arg` only.

## Acceptance Criteria (Cross‑cutting)

- Valid config + actions → action receives correctly typed parameters.
- Validation errors surface as argparse errors with helpful messages.
- Interactive mode prompts until valid values are provided.
- Logging level changes reflect in the output.
 - Generator produces a config that can be saved and used by `load_config` and `build_cli` without edits for simple cases.

## Generated Config Review Checklist

Use this quick checklist after generating a config from your actions file:
- Names/descriptions: Confirm command names and descriptions read well; adjust as needed.
- Arguments: Verify each parameter appears with the right `type` and `help`.
- Required/defaults: Ensure required flags are correct and defaults match intent.
- Validation: Add `rules` (regex/min/max), `choices`, and richer help where appropriate.
- Structure: Reorder commands/args for readability if desired.
- Security: Avoid exposing sensitive arguments or defaults; consider masking/separating secrets.

## Future Stories (Roadmap)

- Support `choices` and default values per argument; reflect in help text.
- Parse list/dict/json values (e.g., `--items '["a","b"]'`) with safe coercers.
- Environment variable integration for arguments and defaults; document precedence with CLI flags.
- Validate configs against a JSON Schema or Pydantic model before building the CLI.
- Improve legacy shim by fully delegating and removing dead code.

## Codebase Notes

- Type conversion implemented via a safe mapping; complex values parsed from JSON literals.
- Generator prefers `ACTIONS` mapping when present; otherwise inspects top-level callables.
- Clean `dynamic_cli_builder/cli.py` so it only re‑exports from `builder`/`validators` and retains a minimal `configure_logging` shim if needed.
- Align README with implemented features or implement missing items mentioned (choices, env vars) and add tests.
