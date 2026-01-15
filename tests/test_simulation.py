"""Tests for simulation engine."""

import pytest

from mcp_scenario_engine.constraints import (
    ConstraintEngine,
    MaxResourceConstraint,
    NonNegativeResourceConstraint,
)
from mcp_scenario_engine.models import SimulationState
from mcp_scenario_engine.simulation import SimulationEngine


def test_simulation_creation() -> None:
    """Test simulation engine creation."""
    sim = SimulationEngine(seed=42)

    assert sim.state.seed == 42
    assert sim.state.time == 0
    assert len(sim.history) == 1  # Creation event


def test_get_state() -> None:
    """Test getting simulation state."""
    sim = SimulationEngine(seed=42)
    state = sim.get_state()

    assert isinstance(state, SimulationState)
    assert state.seed == 42


def test_reset_simulation() -> None:
    """Test resetting simulation."""
    sim = SimulationEngine(seed=42)
    original_id = sim.state.simulation_id

    # Apply some actions
    sim.apply_action("step", {})
    sim.apply_action("step", {})

    assert sim.state.time == 2

    # Reset
    sim.reset(seed=99)

    assert sim.state.simulation_id != original_id
    assert sim.state.time == 0
    assert sim.state.seed == 99
    assert len(sim.history) == 1  # Only reset event


def test_step_action() -> None:
    """Test step action."""
    sim = SimulationEngine(seed=42)

    result = sim.apply_action("step", {})

    assert result.success
    assert sim.state.time == 1
    assert result.state_after.time == 1
    assert result.state_before.time == 0


def test_set_resource_action() -> None:
    """Test set resource action."""
    sim = SimulationEngine(seed=42)

    result = sim.apply_action("set_resource", {"resource": "cpu", "value": 50.0})

    assert result.success
    assert sim.state.resources["cpu"] == 50.0


def test_adjust_resource_action() -> None:
    """Test adjust resource action."""
    sim = SimulationEngine(seed=42)

    sim.apply_action("set_resource", {"resource": "memory", "value": 100.0})
    result = sim.apply_action("adjust_resource", {"resource": "memory", "delta": -20.0})

    assert result.success
    assert sim.state.resources["memory"] == 80.0


def test_set_metric_action() -> None:
    """Test set metric action."""
    sim = SimulationEngine(seed=42)

    result = sim.apply_action("set_metric", {"metric": "load", "value": 0.75})

    assert result.success
    assert sim.state.metrics["load"] == 0.75


def test_set_flag_action() -> None:
    """Test set flag action."""
    sim = SimulationEngine(seed=42)

    result = sim.apply_action("set_flag", {"flag": "maintenance_mode", "value": True})

    assert result.success
    assert sim.state.flags["maintenance_mode"] is True


def test_add_entity_action() -> None:
    """Test add entity action."""
    sim = SimulationEngine(seed=42)

    entity_data = {"name": "server1", "status": "active"}
    result = sim.apply_action("add_entity", {"entity_id": "srv1", "data": entity_data})

    assert result.success
    assert "srv1" in sim.state.entities
    assert sim.state.entities["srv1"] == entity_data


def test_remove_entity_action() -> None:
    """Test remove entity action."""
    sim = SimulationEngine(seed=42)

    # Add then remove
    sim.apply_action("add_entity", {"entity_id": "srv1", "data": {"name": "server1"}})
    result = sim.apply_action("remove_entity", {"entity_id": "srv1"})

    assert result.success
    assert "srv1" not in sim.state.entities


def test_simulate_load_action_deterministic() -> None:
    """Test simulate load action is deterministic with same seed."""
    sim1 = SimulationEngine(seed=42)
    sim1.state.resources["cpu_available"] = 100.0
    sim1.state.resources["memory_available"] = 1000.0

    sim2 = SimulationEngine(seed=42)
    sim2.state.resources["cpu_available"] = 100.0
    sim2.state.resources["memory_available"] = 1000.0

    # Apply same action
    result1 = sim1.apply_action("simulate_load", {"load_factor": 1.5})
    result2 = sim2.apply_action("simulate_load", {"load_factor": 1.5})

    # Should produce identical results
    assert result1.success and result2.success
    assert sim1.state.resources["cpu_available"] == sim2.state.resources["cpu_available"]
    assert (
        sim1.state.resources["memory_available"] == sim2.state.resources["memory_available"]
    )


def test_constraint_violation_prevents_state_change() -> None:
    """Test that constraint violations prevent state changes."""
    sim = SimulationEngine(seed=42)
    sim.state.resources["cpu"] = 50.0
    sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("cpu"))

    # Try to set negative value
    result = sim.apply_action("set_resource", {"resource": "cpu", "value": -10.0})

    assert not result.success
    assert len(result.constraints_violated) == 1
    assert "non_negative" in result.constraints_violated[0].constraint_id
    # State should remain unchanged
    assert sim.state.resources["cpu"] == 50.0


def test_max_resource_constraint() -> None:
    """Test maximum resource constraint."""
    sim = SimulationEngine(seed=42)
    sim.state.resources["cpu"] = 50.0
    sim.constraint_engine.add_constraint(MaxResourceConstraint("cpu", 100.0))

    # Try to exceed maximum
    result = sim.apply_action("set_resource", {"resource": "cpu", "value": 150.0})

    assert not result.success
    assert len(result.constraints_violated) == 1
    assert sim.state.resources["cpu"] == 50.0


def test_history_tracking() -> None:
    """Test event history tracking."""
    sim = SimulationEngine(seed=42)

    assert len(sim.history) == 1  # Creation event

    sim.apply_action("step", {})
    sim.apply_action("set_resource", {"resource": "cpu", "value": 75.0})

    history = sim.get_history()
    assert len(history) == 3

    # Check event types
    assert history[0].event_type.value == "simulation_created"
    assert history[1].event_type.value == "action_applied"
    assert history[2].event_type.value == "action_applied"


def test_get_history_with_limit() -> None:
    """Test getting limited history."""
    sim = SimulationEngine(seed=42)

    for i in range(10):
        sim.apply_action("step", {})

    history = sim.get_history(limit=5)
    assert len(history) == 5


def test_fork_timeline() -> None:
    """Test forking simulation timeline."""
    sim = SimulationEngine(seed=42)

    # Advance original
    sim.apply_action("step", {})
    sim.apply_action("set_resource", {"resource": "cpu", "value": 50.0})

    # Fork
    forked = sim.fork()

    assert forked.state.simulation_id != sim.state.simulation_id
    assert forked.state.time == sim.state.time
    assert forked.state.resources["cpu"] == 50.0
    assert forked.state.metadata["forked_from"] == str(sim.state.simulation_id)

    # Diverge timelines
    sim.apply_action("set_resource", {"resource": "cpu", "value": 25.0})
    forked.apply_action("set_resource", {"resource": "cpu", "value": 75.0})

    assert sim.state.resources["cpu"] == 25.0
    assert forked.state.resources["cpu"] == 75.0


def test_deterministic_execution() -> None:
    """Test deterministic execution with same seed."""
    sim1 = SimulationEngine(seed=42)
    sim2 = SimulationEngine(seed=42)

    actions = [
        ("step", {}),
        ("set_resource", {"resource": "cpu", "value": 100.0}),
        ("simulate_load", {"load_factor": 1.0, "variance": 0.2}),
        ("step", {}),
        ("adjust_resource", {"resource": "cpu", "delta": -10.0}),
    ]

    for action, params in actions:
        sim1.apply_action(action, params)
        sim2.apply_action(action, params)

    # States should be identical
    assert sim1.state.time == sim2.state.time
    assert sim1.state.resources == sim2.state.resources
    assert sim1.state.metrics == sim2.state.metrics


def test_action_with_invalid_params() -> None:
    """Test action with missing required parameters."""
    sim = SimulationEngine(seed=42)

    with pytest.raises(ValueError, match="required"):
        sim.apply_action("set_resource", {})


def test_unknown_action() -> None:
    """Test applying unknown action."""
    sim = SimulationEngine(seed=42)

    with pytest.raises(ValueError, match="Unknown action"):
        sim.apply_action("nonexistent_action", {})


def test_delta_computation() -> None:
    """Test state delta computation."""
    sim = SimulationEngine(seed=42)

    result = sim.apply_action("set_resource", {"resource": "cpu", "value": 50.0})

    assert "resources" in result.delta
    assert result.delta["resources"]["after"]["cpu"] == 50.0
