# Dynamic CLI Builder – Logic Flow

```mermaid
flowchart TD
    subgraph Developer
        A[Developer] -->|writes| B[Test Suite]
        A -->|edits| C[YAML/JSON Config]
        A -->|defines| D[ACTIONS in Python]
    end

    subgraph Runtime["Runtime Flow (dynamic_cli_builder)"]
        B -->|imports| E[load_config()]
        C -->|read by| E
        E -->|returns| F[config: dict]
        F -->|input| G[build_cli()]
        G -->|returns| H[argparse.ArgumentParser]
        H -->|parses| I[CLI Arguments]
        I -->|produces| J[parsed_args: Namespace]
        J -->|input| K[execute_command()]
        F -->|input| K
        D -->|imported| K
        
        K -->|if --log-level| L[configure_logging()]
        K -->|if -im| M[prompt_for_missing_args()]
        M -->|fills| J
        
        K -->|validates| N[validate_arg() each arg]
        N -->|raises| O[ValueError if invalid]
        
        K -->|calls| P[ACTIONS[command](**args)]
    end

    subgraph Data_Flow["Data Flow"]
        direction LR
        C1[Config File] -->|YAML/JSON| F
        D1[ACTIONS.py] -->|Dict[str, Callable]| K
        I1[CLI Input] -->|argparse| J
        P -->|returns| R[Function Result]
        R -->|printed| T[STDOUT/STDERR]
        O -->|error| T
    end
```

### Key Components

1. **Config Loading**
   - Loads YAML/JSON from file or auto-discovers `config.{yaml,yml,json}`
   - Validates structure and required fields
   - Returns structured `dict` for CLI generation

2. **CLI Construction**
   - Dynamically creates `argparse` parsers from config
   - Handles subcommands, arguments, and help text
   - Applies validation rules (min/max, regex) to arguments

3. **Command Execution**
   - Imports and validates `ACTIONS` dictionary
   - Handles logging configuration (`--log-level`)
   - Manages interactive mode (`-im`) for missing args
   - Validates all arguments before execution

4. **Action Dispatch**
   - Maps command names to Python functions
   - Passes validated arguments as kwargs
   - Handles and reports execution errors

### Error Handling Paths
```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│ Config Load │ ──> │ Validation     │ ──> │ Parse Error │
│ (load.py)   │     │ (validators.py)│     │ (argparse)  │
└─────────────┘     └─────────────────┘     └─────────────┘
        │                   │                       │
        ▼                   ▼                       ▼
┌───────────────────────────────────────────────────────────┐
│                    execute_command()                      │
│  (aggregates errors with context for better UX)          │
└───────────────────────────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌─────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ ValidationError │ │ ExecutionError    │ │ FileNotFoundError │
│ (pre-execution) │ │ (in user's code)  │ │ (config/import)   │
└─────────────────┘ └───────────────────┘ └───────────────────┘
```

### Performance Characteristics
- **O(1)** lookup for command actions
- **O(n)** validation where n = number of arguments
- Single-pass argument validation with early exit on failure
- Lazy loading of action modules (only when needed)

This ASCII diagram shows the high-level call sequence, with arrows indicating data/control flow from configuration loading to final action execution. The optional branches for logging (`--log-level`) and interactive prompting (`-im`) are noted inline.
