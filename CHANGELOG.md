# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2025-09-08

### Added
- Choices support for arguments via `choices` in config; validated after type conversion.
- Default values support for arguments via `default` in config.
- Safe type conversion map (replaces `eval`): supports `str`, `int`, `float`, `bool`, and JSON‑based `list`/`dict`/`json`.
- Basic configuration schema validation during `load_config` with clear error messages.
- Documentation: Added `docs/spec.md` detailing user spec and stories.

### Changed
- Cleaned legacy shim `dynamic_cli_builder/cli.py` to pure re‑exports with a small backward‑compat logging wrapper.
- README updated to clarify supported types, recommend JSON literals for complex values, and mark `-log` as deprecated.

### Fixed
- Prevent unsafe type evaluation when building the CLI.

### Tests
- Expanded tests to cover choices/default behavior, bool and JSON parsing, and schema validation errors.

---

## [0.2.0] - 2025-01-01
- Initial 0.2 series (structure per README); details omitted here.
