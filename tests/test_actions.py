"""Tests for actions."""

import random

from mcp_scenario_engine.actions import (
    ACTION_REGISTRY,
    AddEntityAction,
    AdjustResourceAction,
    RemoveEntityAction,
    SetFlagAction,
    SetMetricAction,
    SetResourceAction,
    SimulateLoadAction,
    StepAction,
)
from mcp_scenario_engine.models import SimulationState


def test_step_action() -> None:
    """Test step action increments time."""
    state = SimulationState(time=5)
    action = StepAction()
    rng = random.Random(42)

    new_state, reason = action.execute(state, {}, rng)

    assert new_state.time == 6
    assert "5" in reason and "6" in reason


def test_set_resource_action() -> None:
    """Test set resource action."""
    state = SimulationState(resources={"cpu": 50.0})
    action = SetResourceAction()
    rng = random.Random(42)

    new_state, reason = action.execute(state, {"resource": "cpu", "value": 75.0}, rng)

    assert new_state.resources["cpu"] == 75.0
    assert "cpu" in reason


def test_adjust_resource_action() -> None:
    """Test adjust resource action."""
    state = SimulationState(resources={"memory": 100.0})
    action = AdjustResourceAction()
    rng = random.Random(42)

    new_state, reason = action.execute(state, {"resource": "memory", "delta": -20.0}, rng)

    assert new_state.resources["memory"] == 80.0
    assert "memory" in reason


def test_set_metric_action() -> None:
    """Test set metric action."""
    state = SimulationState()
    action = SetMetricAction()
    rng = random.Random(42)

    new_state, reason = action.execute(state, {"metric": "load", "value": 0.85}, rng)

    assert new_state.metrics["load"] == 0.85


def test_set_flag_action() -> None:
    """Test set flag action."""
    state = SimulationState()
    action = SetFlagAction()
    rng = random.Random(42)

    new_state, reason = action.execute(state, {"flag": "maintenance", "value": True}, rng)

    assert new_state.flags["maintenance"] is True


def test_add_entity_action() -> None:
    """Test add entity action."""
    state = SimulationState()
    action = AddEntityAction()
    rng = random.Random(42)

    entity_data = {"name": "server1", "status": "active"}
    new_state, reason = action.execute(
        state, {"entity_id": "srv1", "data": entity_data}, rng
    )

    assert "srv1" in new_state.entities
    assert new_state.entities["srv1"] == entity_data


def test_remove_entity_action() -> None:
    """Test remove entity action."""
    state = SimulationState(entities={"srv1": {"name": "server1"}})
    action = RemoveEntityAction()
    rng = random.Random(42)

    new_state, reason = action.execute(state, {"entity_id": "srv1"}, rng)

    assert "srv1" not in new_state.entities


def test_simulate_load_action() -> None:
    """Test simulate load action."""
    state = SimulationState(
        time=0,
        resources={"cpu_available": 100.0, "memory_available": 1000.0},
    )
    action = SimulateLoadAction()
    rng = random.Random(42)

    new_state, reason = action.execute(state, {"load_factor": 1.5}, rng)

    # Resources should decrease
    assert new_state.resources["cpu_available"] < 100.0
    assert new_state.resources["memory_available"] < 1000.0
    # Time should advance
    assert new_state.time == 1
    # Load metric should be set
    assert "load" in new_state.metrics


def test_simulate_load_deterministic() -> None:
    """Test simulate load is deterministic with same seed."""
    state = SimulationState(
        resources={"cpu_available": 100.0, "memory_available": 1000.0},
    )
    action = SimulateLoadAction()

    rng1 = random.Random(42)
    rng2 = random.Random(42)

    new_state1, _ = action.execute(state, {"load_factor": 1.0, "variance": 0.2}, rng1)
    new_state2, _ = action.execute(state, {"load_factor": 1.0, "variance": 0.2}, rng2)

    assert new_state1.resources["cpu_available"] == new_state2.resources["cpu_available"]
    assert (
        new_state1.resources["memory_available"] == new_state2.resources["memory_available"]
    )


def test_action_registry_contains_all_actions() -> None:
    """Test action registry has all expected actions."""
    expected_actions = [
        "step",
        "set_resource",
        "adjust_resource",
        "set_metric",
        "set_flag",
        "add_entity",
        "remove_entity",
        "simulate_load",
    ]

    for action_name in expected_actions:
        assert action_name in ACTION_REGISTRY
