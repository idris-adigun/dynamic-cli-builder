"""Configuration generator from an actions module.

Introspects a Python module (typically the actions file) to produce a
Dynamic CLI Builder configuration (YAML/JSON compatible dict).
"""
from __future__ import annotations

import inspect
from types import ModuleType
from typing import Any, Dict, Optional, get_origin, get_args


def _infer_type_name(annotation: Any) -> str:
    if annotation is inspect.Signature.empty:
        return "str"
    if annotation is bool:
        return "bool"
    if annotation is int:
        return "int"
    if annotation is float:
        return "float"
    if annotation is str:
        return "str"

    origin = get_origin(annotation)
    if origin in (list, tuple):
        return "list"
    if origin in (dict,):
        return "dict"
    # fall back to json for unknown/complex types
    return "json"


def _build_command(name: str, func: Any) -> Dict[str, Any]:
    sig = inspect.signature(func)
    doc = (func.__doc__ or "").strip().splitlines()[0] if func.__doc__ else ""
    args = []
    for param in sig.parameters.values():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            # skip *args/**kwargs
            continue
        arg: Dict[str, Any] = {
            "name": param.name,
            "type": _infer_type_name(param.annotation),
            "help": f"Argument {param.name}",
        }
        if param.default is not inspect._empty:
            arg["default"] = param.default
        else:
            arg["required"] = True
        args.append(arg)

    return {
        "name": name,
        "description": doc or f"Command {name}",
        "args": args,
        "action": name,
    }


def generate_config(module: ModuleType, actions_mapping: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate a config dict from a module.

    If ``actions_mapping`` is provided, uses its keys as command names and
    values as callables. Otherwise, discovers top-level callables not starting
    with an underscore.
    """
    commands = []
    if actions_mapping:
        for name, func in actions_mapping.items():
            if callable(func):
                commands.append(_build_command(name, func))
    else:
        for name, obj in module.__dict__.items():
            if name.startswith("_"):
                continue
            if callable(obj):
                commands.append(_build_command(name, obj))

    return {
        "description": f"Generated config from {getattr(module, '__name__', 'module')}",
        "commands": commands,
    }


def dump_config(cfg: Dict[str, Any], fmt: str = "yaml") -> str:
    fmt = fmt.lower()
    if fmt == "json":
        import json

        return json.dumps(cfg, indent=2)
    elif fmt in ("yaml", "yml"):
        import yaml

        return yaml.safe_dump(cfg, sort_keys=False)
    raise ValueError("Unsupported format. Use 'yaml' or 'json'.")

