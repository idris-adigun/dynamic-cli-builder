# Dynamic CLI Builder – Logic Flow

```text
┌──────────────────────┐
│      Developer       │
└─────────┬────────────┘
          │ `pytest`
          ▼
┌──────────────────────┐
│   Test Suite (*.py)  │
└─────────┬────────────┘
          │ imports
          ▼
┌──────────────────────┐
│  YAML/JSON Config    │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ load_config()        │
│  → returns dict      │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ build_cli(config)    │
│  → argparse.Parser   │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ parser.parse_args()  │
│  → Namespace         │
└─────────┬────────────┘
          │
          ▼
┌───────────────────────────────────────────┐
│ execute_command(ns, config, ACTIONS)      │
└─────────┬─────────────────────────────────┘
          │          (if -v/--log-level)          
          │ configure_logging(level)             
          ▼
┌──────────────────────┐         yes (-im) ──┐
│ validate_arg()       │<────────────────────┘
└─────────┬────────────┘                     
          │                                  
          ▼                                  
┌──────────────────────┐                     
│  ACTIONS[command]    │                     
│  (actual function)   │                     
└──────────────────────┘                     
```

This ASCII diagram shows the high-level call sequence, with arrows indicating data/control flow from configuration loading to final action execution. The optional branches for logging (`--log-level`) and interactive prompting (`-im`) are noted inline.
