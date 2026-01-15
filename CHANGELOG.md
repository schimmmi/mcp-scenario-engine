# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-15

### Fixed
- **Persistence Storage Location**: Changed default storage from `.simulations` to `~/.mcp-scenario-engine/simulations/` to fix `OSError: Read-only file system` when running in Claude Desktop or other read-only contexts
- **History Restoration**: Event history is now correctly restored when loading simulations. Previously, history was serialized but not deserialized, resulting in loaded simulations having only 1 creation event instead of the full audit trail
  - Preserves all event IDs, timestamps, and state deltas
  - Complete audit trail now survives save/load cycles

## [1.0.0] - 2025-01-15

### Added

#### Core Features
- **State Management**: Versioned JSON schema (v1) with complete state snapshots
- **Action System**: 8 implemented actions (step, set_resource, adjust_resource, set_metric, set_flag, add_entity, remove_entity, simulate_load)
- **Constraint Engine**: Server-side validation with automatic rollback on violations
- **Deterministic Execution**: Seed-based random number generation for reproducible simulations
- **Event History**: Complete audit trail with state deltas for every change
- **Timeline Forking**: Branch simulations for parallel "what-if" scenarios

#### World Rules System
- JSON-defined dynamic rules via MCP
- Automatic rule application on `step` actions
- Flexible condition types: comparison, and, or, not, always
- Multiple value sources: resource, metric, flag, metadata, time, value
- Action types: set_resource, set_metric, set_flag, set_metadata
- Value operations: fixed, increment, multiply
- Priority system for rule execution order
- Full CRUD operations for rule management

#### Persistence Layer
- Save simulations with complete state + rules + history
- Load simulations and resume from checkpoints
- Manage multiple simulations
- Survive server restarts
- Metadata inspection without loading full state
- JSON-based storage in `.simulations/` directory

#### MCP Server
- 16 MCP tools for complete simulation control:
  - State management: `get_state`, `get_schema`
  - Action execution: `apply_action`
  - Simulation control: `reset_simulation`, `fork_timeline`, `get_history`
  - World rules: `add_world_rule`, `list_world_rules`, `get_world_rule`, `update_world_rule`, `remove_world_rule`, `clear_world_rules`
  - Persistence: `save_simulation`, `load_simulation`, `list_simulations`, `get_simulation_info`, `delete_simulation`

#### Testing & Quality
- 80%+ test coverage with unit and integration tests
- Type checking with mypy
- Linting with ruff
- Code formatting with black
- Docker deployment support

#### Documentation & Examples
- Comprehensive README with setup instructions
- 4 demo scenarios:
  - Normal simulation run
  - Constraint violation handling
  - Dynamic world rules (DevOps scenario)
  - Persistence workflow
- Complete MCP tool documentation
- State schema documentation

### Technical Details
- Python 3.11+ support
- Built on Model Context Protocol (MCP)
- Pydantic models for type-safe state management
- Structured JSON logging to stderr
- Event sourcing pattern with complete audit trail

[1.0.0]: https://github.com/schimmmi/mcp-scenario-engine/releases/tag/v1.0.0
