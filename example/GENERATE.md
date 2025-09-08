# Quick Generate + Run

This walkthrough shows how to generate a starter config from the existing `actions.py` and run it immediately.

## 1) Generate a config from actions

From the project root:

```
python -m dynamic_cli_builder \
  --actions example/actions.py \
  --generate \
  --format yaml \
  --output example/generated_config.yaml
```

This inspects `example/actions.py` and writes a YAML config at `example/generated_config.yaml`.

## 2) Run a command using the generated config

```
python -m dynamic_cli_builder \
  --config example/generated_config.yaml \
  --actions example/actions.py \
  say_hello --name Alice --age 30
```

Expected output:

```
Hello Alice!, you are 30 years old.
```

Notes:
- The generator infers types and required/default from function signatures and docstrings.
- You can edit `example/generated_config.yaml` to add validation rules (`regex`, `min`, `max`), choices, and richer help text.
