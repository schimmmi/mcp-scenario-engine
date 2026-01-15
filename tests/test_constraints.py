"""Tests for constraint engine."""

from mcp_scenario_engine.constraints import (
    ConstraintEngine,
    MaxResourceConstraint,
    NonNegativeResourceConstraint,
    TimeMonotonicConstraint,
)
from mcp_scenario_engine.models import SimulationState


def test_non_negative_resource_constraint_pass() -> None:
    """Test non-negative resource constraint passes."""
    state = SimulationState(resources={"cpu": 50.0})
    constraint = NonNegativeResourceConstraint("cpu")

    violation = constraint.validate(state)
    assert violation is None


def test_non_negative_resource_constraint_fail() -> None:
    """Test non-negative resource constraint fails."""
    state = SimulationState(resources={"cpu": -10.0})
    constraint = NonNegativeResourceConstraint("cpu")

    violation = constraint.validate(state)
    assert violation is not None
    assert "non_negative_resource_cpu" == violation.constraint_id
    assert "cannot be negative" in violation.message


def test_max_resource_constraint_pass() -> None:
    """Test max resource constraint passes."""
    state = SimulationState(resources={"memory": 80.0})
    constraint = MaxResourceConstraint("memory", 100.0)

    violation = constraint.validate(state)
    assert violation is None


def test_max_resource_constraint_fail() -> None:
    """Test max resource constraint fails."""
    state = SimulationState(resources={"memory": 120.0})
    constraint = MaxResourceConstraint("memory", 100.0)

    violation = constraint.validate(state)
    assert violation is not None
    assert "max_resource_memory" == violation.constraint_id
    assert "exceeds maximum" in violation.message


def test_time_monotonic_constraint_pass() -> None:
    """Test time monotonic constraint passes."""
    state = SimulationState(time=10)
    constraint = TimeMonotonicConstraint(previous_time=5)

    violation = constraint.validate(state)
    assert violation is None


def test_time_monotonic_constraint_fail() -> None:
    """Test time monotonic constraint fails."""
    state = SimulationState(time=5)
    constraint = TimeMonotonicConstraint(previous_time=10)

    violation = constraint.validate(state)
    assert violation is not None
    assert "time_monotonic" == violation.constraint_id
    assert "cannot go backwards" in violation.message


def test_constraint_engine_multiple_constraints() -> None:
    """Test constraint engine with multiple constraints."""
    state = SimulationState(
        time=10,
        resources={"cpu": -5.0, "memory": 150.0},
    )

    engine = ConstraintEngine()
    engine.add_constraint(NonNegativeResourceConstraint("cpu"))
    engine.add_constraint(MaxResourceConstraint("memory", 100.0))

    violations = engine.validate(state)

    assert len(violations) == 2
    constraint_ids = [v.constraint_id for v in violations]
    assert "non_negative_resource_cpu" in constraint_ids
    assert "max_resource_memory" in constraint_ids


def test_constraint_engine_no_violations() -> None:
    """Test constraint engine with valid state."""
    state = SimulationState(
        time=10,
        resources={"cpu": 50.0, "memory": 80.0},
    )

    engine = ConstraintEngine()
    engine.add_constraint(NonNegativeResourceConstraint("cpu"))
    engine.add_constraint(MaxResourceConstraint("memory", 100.0))

    violations = engine.validate(state)

    assert len(violations) == 0


def test_get_constraint_ids() -> None:
    """Test getting constraint IDs from engine."""
    engine = ConstraintEngine()
    engine.add_constraint(NonNegativeResourceConstraint("cpu"))
    engine.add_constraint(MaxResourceConstraint("memory", 100.0))

    ids = engine.get_constraint_ids()

    assert len(ids) == 2
    assert "non_negative_resource_cpu" in ids
    assert "max_resource_memory" in ids
