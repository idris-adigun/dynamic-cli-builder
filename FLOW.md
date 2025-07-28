# Dynamic CLI Builder – Architecture

## System Flow

See the full interactive diagram: [docs/architecture.mmd](docs/architecture.mmd)

```mermaid
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#f0f0f0',
      'primaryTextColor': '#000',
      'primaryBorderColor': '#666',
      'lineColor': '#333',
      'fontFamily': 'monospace'
    }
  }
}%%

flowchart TD
    Developer[("👨‍💻 Developer")] -->|writes| Tests[Test Suite (*.py)]
    Developer -->|edits| Config[YAML/JSON Config]
    Developer -->|defines| Actions[ACTIONS.py]
    
    Tests -->|imports| load_config
    Config -->|read by| load_config
    
    subgraph Runtime["dynamic_cli_builder Runtime"]
        load_config -->|dict| build_cli(config)
        build_cli(config) -->|parser| parse_args
        parse_args -->|Namespace| execute_command
        Actions -->|imported| execute_command
        
        execute_command -->|validate| validate_arg
        execute_command -->|log| configure_logging
        execute_command -->|prompt| prompt_missing
        
        execute_command -->|call| run_action["ACTIONS[command](**kwargs)"]
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
