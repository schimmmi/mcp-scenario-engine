# MCP Scenario Engine

**An MCP Server for Deterministic Simulation and Scenario Planning**

[![CI](https://github.com/YOUR_USERNAME/mcp-scenario-engine/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/mcp-scenario-engine/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

The MCP Scenario Engine is a Model Context Protocol (MCP) server that provides a simulation space where AI agents can query system states, execute actions, and simulate impacts in a traceable manner.

**With complex formula support**, you can now model sophisticated systems including game theory, economics, health tracking, and scientific simulations—all through JSON-defined rules.

### Use Cases

- 🎯 **Project Planning**: Resource allocation, timeline simulation
- 🏗️ **Infrastructure**: Capacity planning, load testing
- 🔬 **Scientific Modeling**: Physics, chemistry, biology simulations
- 📊 **Economics & Finance**: Market dynamics, auctions, investments
- 🎮 **Game Theory**: Strategic interactions, Nash equilibrium, evolutionary dynamics
- 🏋️ **Health & Fitness**: Body composition, nutrition, training optimization
- 🌳 **What-If Analysis**: Timeline forking for alternative scenarios

## Core Features

### ✅ State Management
- Versioned state schema (JSON Schema)
- Complete state snapshots
- Slicing and partial queries
- Time-stepped simulation

### ✅ Action System
8 implemented actions:
- `step` - Advance time forward
- `set_resource` - Set resource value
- `adjust_resource` - Adjust resource by delta
- `set_metric` - Set metric value
- `set_flag` - Set boolean flag
- `add_entity` - Add/update entity
- `remove_entity` - Remove entity
- `simulate_load` - Simulate load scenario (with randomness)

### ✅ World Rules (Dynamic)
- JSON-defined rules via MCP
- Automatic application on `step` actions
- Flexible conditions (comparison, and, or, not, always)
- Value sources (resource, metric, flag, metadata, time, value)
- Multiple action types (set_resource, set_metric, set_flag, set_metadata)
- **Complex formulas** with arithmetic operations:
  - Addition: `{"type": "add", "values": [...]}`
  - Subtraction: `{"type": "subtract", "left": ..., "right": ...}`
  - Multiplication: `{"type": "multiply", "values": [...]}`
  - Division: `{"type": "divide", "numerator": ..., "denominator": ...}`
  - Nested operations for complex calculations
- Priority system for rule execution order
- Full rule management (CRUD operations)

### ✅ Constraint Engine
- Server-side validation
- Automatic state rollback on violations
- 3+ predefined constraints:
  - `NonNegativeResourceConstraint`
  - `MaxResourceConstraint`
  - `TimeMonotonicConstraint`
- Clear error messages with context

### ✅ Determinism & Reproducibility
- Seed-based random number generation
- Same seed → Same results
- Fully reproducible simulations

### ✅ Audit & Explainability
- Complete event history
- State deltas for every change
- Constraint checks logged
- Structured logging (JSON)

### ✅ Timeline Forking
- Branch simulations
- Parallel "what-if" scenarios
- Immutable original timeline

### ✅ Persistence
- Save state + rules + history
- Manage multiple simulations
- Survive server restarts
- Set checkpoints and resume
- CRUD operations (Save, Load, List, Delete)
- Metadata inspection without loading
- Storage in `~/.mcp-scenario-engine/simulations/`

## Installation

### Prerequisites
- Python 3.11+
- pip or uv

### Local Installation

```bash
# Clone repository
git clone https://github.com/schimmmi/mcp-scenario-engine.git
cd mcp-scenario-engine

# Install dependencies
make install

# Or manually
pip install -e ".[dev]"
```

### Docker

#### Build and Run Demos

```bash
# Build Docker image
docker compose build

# Run all demo scenarios
docker compose --profile demo run demo

# Run specific demo
docker compose run demo python examples/demo_scenario_a.py
docker compose run demo python examples/demo_weight_loss.py
docker compose run demo python examples/demo_prisoners_dilemma.py
```

#### Start MCP Server

**Option 1: Standalone Server**
```bash
# Start server in background
docker compose up -d mcp-scenario-engine

# View logs
docker compose logs -f mcp-scenario-engine

# Stop server
docker compose down
```

**Option 2: Use with Claude Desktop**

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scenario-engine": {
      "command": "docker",
      "args": [
        "compose",
        "-f",
        "/path/to/mcp-scenario-engine/docker-compose.yml",
        "run",
        "--rm",
        "mcp-scenario-engine"
      ]
    }
  }
}
```

**Important Notes:**
- Replace `/path/to/mcp-scenario-engine` with actual path
- Docker must be running before starting Claude Desktop
- Simulations are saved inside the container (mount a volume to persist)

**Mount Volume for Persistence:**

```yaml
# Add to docker-compose.yml under mcp-scenario-engine service:
volumes:
  - ~/.mcp-scenario-engine:/root/.mcp-scenario-engine
```

This saves simulations to your home directory instead of the container.

**📖 For complete Docker documentation, see [DOCKER.md](DOCKER.md)**

## Quick Start

### 1. Run Demo

```bash
# Both demo scenarios
make demo

# Or individually
python examples/demo_scenario_a.py
python examples/demo_scenario_b.py
```

### 2. Use as Python Library

```python
from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.constraints import NonNegativeResourceConstraint

# Create simulation
sim = SimulationEngine(seed=42)

# Set initial state
sim.state.resources = {"budget": 10000.0, "capacity": 100.0}

# Add constraint
sim.constraint_engine.add_constraint(
    NonNegativeResourceConstraint("budget")
)

# Execute actions
result = sim.apply_action(
    "adjust_resource",
    {"resource": "budget", "delta": -2000.0}
)

if result.success:
    print(f"New budget: {sim.state.resources['budget']}")
    print(f"Delta: {result.delta}")
else:
    print(f"Error: {result.message}")
    for v in result.constraints_violated:
        print(f"  - {v.constraint_id}: {v.message}")
```

### 3. Use as MCP Server

```bash
# Start server
python -m mcp_scenario_engine.server

# Configure in Claude Desktop (claude_desktop_config.json):
{
  "mcpServers": {
    "scenario-engine": {
      "command": "python",
      "args": ["-m", "mcp_scenario_engine.server"],
      "cwd": "/path/to/mcp-scenario-engine"
    }
  }
}
```

## MCP Tools

The server provides 16 tools:

### State Management

#### `get_state`
Get current simulation state.

```json
{}
```

#### `get_schema`
Get state schema definition.

```json
{}
```

### Action Execution

#### `apply_action`
Execute an action.

```json
{
  "action": "adjust_resource",
  "params": {
    "resource": "budget",
    "delta": -500.0
  }
}
```

### Simulation Control

#### `reset_simulation`
Reset simulation to initial state.

```json
{
  "seed": 42
}
```

#### `fork_timeline`
Fork timeline for "what-if" scenarios.

```json
{}
```

#### `get_history`
Get event history.

```json
{
  "limit": 10
}
```

### World Rules (Dynamic)

#### `add_world_rule`
Add dynamic rule that automatically applies on `step` actions.

```json
{
  "rule_id": "cpu_overload",
  "condition": {
    "type": "comparison",
    "left": {"type": "resource", "name": "cpu"},
    "operator": ">",
    "right": {"type": "value", "value": 80}
  },
  "actions": [{
    "type": "set_metric",
    "metric": "error_rate",
    "value": {"type": "increment", "amount": 0.05}
  }],
  "priority": 10,
  "description": "Increase error rate on CPU overload"
}
```

#### `list_world_rules`
List all active rules.

```json
{}
```

#### `get_world_rule`
Get details of a specific rule.

```json
{
  "rule_id": "cpu_overload"
}
```

#### `update_world_rule`
Update existing rule (partial update).

```json
{
  "rule_id": "cpu_overload",
  "priority": 20,
  "description": "Updated description"
}
```

#### `remove_world_rule`
Remove a rule.

```json
{
  "rule_id": "cpu_overload"
}
```

#### `clear_world_rules`
Remove all rules.

```json
{}
```

### Persistence

#### `save_simulation`
Save simulation persistently (State + Rules + History).

```json
{
  "name": "devops_scenario_1",
  "description": "High CPU scenario with 3 steps"
}
```

#### `load_simulation`
Load saved simulation (replaces current simulation).

```json
{
  "name": "devops_scenario_1"
}
```

#### `list_simulations`
List all saved simulations.

```json
{}
```

#### `get_simulation_info`
Get simulation metadata without loading it.

```json
{
  "name": "devops_scenario_1"
}
```

#### `delete_simulation`
Delete a saved simulation.

```json
{
  "name": "devops_scenario_1"
}
```

## State Schema (v1)

```json
{
  "schema_version": "v1",
  "simulation_id": "uuid",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z",
  "seed": 42,
  "time": 0,
  "entities": {},
  "metrics": {},
  "resources": {},
  "flags": {},
  "metadata": {}
}
```

## Demo Scenarios

### Scenario A: Normal Simulation Run

Demonstrates:
- State initialization
- Multiple action types
- Resource management
- Entity lifecycle
- Metrics tracking
- Reproducibility

```bash
python examples/demo_scenario_a.py
```

**Output:**
```
============================================================
DEMO SCENARIO A: Normal Simulation Run
============================================================

1. Creating simulation with seed=42...
2. Adding constraints...
   - Budget must be non-negative
   - Team capacity must be non-negative

3. Executing simulation steps...
   ...
   ✓ Advanced to time step 3

6. Testing Reproducibility:
   ✓ Reproducibility verified - identical results with same seed
```

### Scenario B: Constraint Violations

Demonstrates:
- Constraint validation
- State rollback on violations
- Clear error messages
- Event history
- Timeline forking

```bash
python examples/demo_scenario_b.py
```

**Output:**
```
============================================================
DEMO SCENARIO B: Constraint Violation Handling
============================================================

5. Testing constraint violations...

   Violation Attempt 1: Exceed maximum server load
   ✓ REJECTED as expected: Action rejected due to constraint violations
   Violations detected:
     - max_resource_server_load: Resource 'server_load' exceeds maximum 100.0 (got 130.0)
   State unchanged - Server load still: 80.00
```

### Demo: World Rules (DevOps)

Demonstrates dynamic rules:
- JSON-based rule definition
- Automatic causality
- Deterministic world model simulation

```bash
python examples/demo_devops_world.py
```

### Demo: Persistence

Demonstrates persistence features:
- Save/load simulations
- Multiple simulation management
- Continue from checkpoint
- Delete and list operations

```bash
python examples/demo_persistence.py
```

**Output:**
```
✅ Persistence Demo Complete!

💡 Key Features:
   • Save simulations with state + rules + history
   • Load simulations and continue from checkpoint
   • List all saved simulations
   • Get metadata without loading
   • Delete simulations
   • Overwrite existing saves
```

### Demo: Weight Loss Simulation (Complex Formulas)

Demonstrates complex formula support:
- Division: `(calorie_deficit / 7700) * 7 * compliance`
- Multiplication of multiple variables
- Addition and subtraction
- Nested operations
- Real-world body composition modeling

```bash
python examples/demo_weight_loss.py
```

**Output:**
```
Week     Weight   Change      Fat   Muscle    Fat%
----------------------------------------------------------------------
Start    92.47kg        -   18.55kg   70.16kg   20.1%
1        88.53kg   -3.94kg   18.24kg   70.29kg   20.6%
2        88.35kg   -0.18kg   17.93kg   70.41kg   20.3%
...
8        87.26kg   -0.18kg   16.08kg   71.18kg   18.4%

Results: -5.21kg weight, -2.47kg fat, +1.02kg muscle, body fat: 20.1% → 18.4%
```

### Demo: Game Theory Simulations

Demonstrates game-theoretic models with complex strategic interactions:

#### Prisoner's Dilemma (Iterated Game)
```bash
python examples/demo_prisoners_dilemma.py
```

**Features:**
- Iterated prisoner's dilemma with payoff matrices
- Tit-for-Tat vs Tit-for-Tat (mutual cooperation)
- Tit-for-Tat vs Always Defect (retaliation)
- Strategic formulas calculating payoffs from action combinations

**Output:**
```
Round   P1 Move    P2 Move    P1 Score     P2 Score
----------------------------------------------------------------------
1       Cooperate  Cooperate  3            3
...
10      Cooperate  Cooperate  30           30

Tit-for-Tat vs Always Defect:
1       Cooperate  Defect     0            5
2       Defect     Defect     1            6
...
```

#### Evolutionary Game Theory (Hawk-Dove)
```bash
python examples/demo_evolutionary_game.py
```

**Features:**
- Population dynamics with Hawks and Doves
- Frequency-dependent fitness calculations
- Replicator dynamics: `hawks_new = hawks * (hawk_fitness / avg_fitness)`
- Evolutionary Stable Strategy (ESS) emergence
- Complex nested formulas for payoffs

**Output:**
```
Gen     Hawks   Doves    H_Fit    D_Fit  Avg_Fit
----------------------------------------------------------------------
1        50.0    50.0     12.5     12.5     12.5
...
20       50.0    50.0     12.5     12.5     12.5

Equilibrium: 50% Hawks (matches theoretical ESS!)
```

#### Auction Theory (Vickrey Second-Price)
```bash
python examples/demo_auction_theory.py
```

**Features:**
- Sealed-bid second-price auction
- Truth-telling incentive demonstration
- Winner's surplus calculation: `valuation - payment`
- Dominant strategy analysis
- Compares truthful vs strategic bidding

**Output:**
```
Winner: Bidder 3
Payment: $95.00 (second-highest bid)
Winner's Surplus: $25.00

Truth-telling test:
• Underbidding → Lost auction, $25 regret
• Overbidding → Same surplus ($25), no benefit
```

## Testing

```bash
# Run all tests
make test

# With coverage
pytest --cov=src --cov-report=html

# Unit tests only
pytest tests/test_*.py -v

# Integration tests only
pytest tests/test_integration.py -v
```

**Test Coverage:** 80%+ (requirement met)

## Development

### Code Quality

```bash
# Linting
make lint

# Formatting
make format

# Type checking
mypy src
```

### Structure

```
mcp-scenario-engine/
├── src/mcp_scenario_engine/
│   ├── __init__.py
│   ├── models.py           # Pydantic Models (State, Events)
│   ├── constraints.py      # Constraint Engine
│   ├── actions.py          # Action Implementations
│   ├── simulation.py       # Core Simulation Engine
│   ├── dynamic_rules.py    # Dynamic Rule System
│   ├── world_rules.py      # World Rule Engine
│   ├── persistence.py      # Persistence Layer
│   └── server.py           # MCP Server (16 Tools)
├── tests/
│   ├── test_simulation.py  # Unit Tests
│   ├── test_constraints.py # Constraint Tests
│   ├── test_actions.py     # Action Tests
│   └── test_integration.py # Integration Tests
├── examples/
│   ├── demo_scenario_a.py  # Demo: Normal Simulation
│   ├── demo_scenario_b.py  # Demo: Constraint Violations
│   ├── demo_devops_world.py # Demo: World Rules
│   └── demo_persistence.py  # Demo: Persistence
├── .simulations/            # Saved Simulations
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── Makefile
└── README.md
```

## Observability

### Structured Logging

All logs are output as JSON:

```json
{
  "event": "action_applied",
  "simulation_id": "123e4567-e89b-12d3-a456-426614174000",
  "action": "adjust_resource",
  "event_id": "456e7890-e89b-12d3-a456-426614174111",
  "timestamp": "2025-01-15T10:30:00.123456Z"
}
```

### Event Types

- `simulation_created` - Simulation created
- `simulation_reset` - Simulation reset
- `action_applied` - Action successful
- `constraint_violated` - Constraint violation
- `timeline_forked` - Timeline forked

## Acceptance Criteria

✅ **Read state**: `get_state` returns valid schema
✅ **Execute action**: `apply_action` returns before/after/delta/event_id
✅ **Constraint enforcement**: Violations prevent state changes
✅ **Determinism**: Same seed → Same results
✅ **Fork/Branch**: Immutable original, diverging fork

## Definition of Done

### Implementation ✅
- MCP server operational (Docker + venv)
- State schema v1 documented
- 8 actions implemented
- Constraint engine with 3+ rules
- Determinism via seed

### Quality ✅
- Unit tests (80%+ coverage)
- Integration tests (end-to-end)
- Linting/Formatting (ruff/black)
- Type checking (mypy)

### Observability ✅
- Structured logging (JSON)
- No secrets in logs
- Clear error messages

### Documentation ✅
- README with setup & examples
- Tool list & schema
- 4 demo scenarios
- Example outputs

### Demo ✅
- `make demo` works
- Scenario A: Normal run
- Scenario B: Constraint handling
- Demo: World rules
- Demo: Persistence

## License

MIT

## Contact

For questions or issues, please open an issue on GitHub.
