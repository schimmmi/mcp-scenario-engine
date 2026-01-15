# Release Notes v1.0.0

**MCP Scenario Engine - First Stable Release** 🚀

The MCP Scenario Engine is a Model Context Protocol (MCP) server that provides a deterministic simulation environment for AI agents to plan, test, and analyze system changes before implementation.

## 🎯 What is it?

A powerful simulation framework that enables:
- **Project Planning**: Simulate project timelines, resource allocation, and constraints
- **Infrastructure Changes**: Model system changes before applying them
- **What-If Analysis**: Fork timelines to explore alternative scenarios
- **Deterministic Testing**: Same seed → same results, every time
- **Audit Trail**: Complete history of every state change and decision

## ✨ Key Features

### 🔧 Dynamic World Rules
Define your own simulation rules via JSON:
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
  }]
}
```

### 💾 Persistence
Save and resume simulations:
- Save complete state + rules + history
- Load and continue from any checkpoint
- Manage multiple simulation scenarios
- Survives server restarts

### 🎲 Determinism
Reproducible simulations with seed-based randomness:
- Same seed → identical results
- Perfect for testing and validation
- Compare alternative approaches

### 🛡️ Constraint Engine
Automatic validation with rollback:
- Define constraints on resources, metrics, and state
- Violations automatically prevent invalid state changes
- Clear error messages with context

### 🌳 Timeline Forking
Explore alternatives without losing your progress:
- Fork at any point
- Run parallel scenarios
- Compare outcomes

## 📦 What's Included

### 16 MCP Tools
Complete control over simulations through Claude Desktop or any MCP client:
- State management & queries
- Action execution
- Dynamic rule management (CRUD)
- Persistence operations
- Timeline forking
- Event history

### 4 Demo Scenarios
- **Scenario A**: Normal simulation workflow
- **Scenario B**: Constraint violation handling
- **DevOps Demo**: Dynamic world rules in action
- **Persistence Demo**: Save/load workflow

### Production Ready
- 80%+ test coverage
- Type-safe with mypy
- Structured logging
- Docker deployment
- Comprehensive documentation

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/schimmmi/mcp-scenario-engine.git
cd mcp-scenario-engine
make install
```

### Run Demo

```bash
make demo
```

### Use with Claude Desktop

Add to `claude_desktop_config.json`:

```json
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

## 📊 Use Cases

### DevOps Scenario Planning
Model infrastructure changes:
- CPU load → error rates
- Scaling triggers
- Cascading failures
- Team burnout from on-call

### Project Management
Simulate project execution:
- Resource allocation
- Budget constraints
- Timeline dependencies
- Team capacity

### System Design
Test design decisions:
- Load patterns
- Failure modes
- Recovery strategies
- Performance under constraints

## 🔬 Example: DevOps Simulation

```python
from mcp_scenario_engine import SimulationEngine

# Create deterministic simulation
sim = SimulationEngine(seed=42)

# Set initial state
sim.state.resources = {"cpu": 85.0, "memory": 60.0}
sim.state.metrics = {"error_rate": 0.05}

# Add dynamic rule: high CPU → increased errors
sim.world_rule_engine.add_rule(
    DynamicRule(
        rule_id="cpu_overload",
        condition={
            "type": "comparison",
            "left": {"type": "resource", "name": "cpu"},
            "operator": ">",
            "right": {"type": "value", "value": 80}
        },
        actions=[{
            "type": "set_metric",
            "metric": "error_rate",
            "value": {"type": "increment", "amount": 0.05}
        }]
    )
)

# Run simulation
result = sim.apply_action("step", {})
# error_rate automatically increased to 0.10
```

## 🎓 Documentation

- **README.md**: Complete setup and usage guide
- **CHANGELOG.md**: Detailed version history
- **Examples**: 4 working demos in `examples/`
- **Tests**: Reference implementations in `tests/`

## 🤝 Contributing

This is the initial stable release. Feedback, issues, and contributions are welcome!

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Built with:
- Model Context Protocol (MCP)
- Pydantic for type-safe models
- pytest for comprehensive testing
- structlog for observability

---

**Full Changelog**: https://github.com/schimmmi/mcp-scenario-engine/blob/main/CHANGELOG.md
