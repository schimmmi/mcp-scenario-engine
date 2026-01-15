"""Integration tests for end-to-end scenarios."""

from mcp_scenario_engine.constraints import NonNegativeResourceConstraint
from mcp_scenario_engine.simulation import SimulationEngine


def test_full_simulation_scenario() -> None:
    """Test complete simulation scenario."""
    # Create simulation
    sim = SimulationEngine(seed=42)
    sim.state.resources["budget"] = 1000.0
    sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("budget"))

    # Execute multiple steps
    sim.apply_action("step", {})
    assert sim.state.time == 1

    # Set initial metrics
    sim.apply_action("set_metric", {"metric": "project_progress", "value": 0.0})

    # Adjust budget
    result = sim.apply_action("adjust_resource", {"resource": "budget", "delta": -100.0})
    assert result.success
    assert sim.state.resources["budget"] == 900.0

    # Update progress
    sim.apply_action("set_metric", {"metric": "project_progress", "value": 0.1})

    # Verify history
    history = sim.get_history()
    assert len(history) > 0


def test_constraint_violation_scenario() -> None:
    """Test scenario with constraint violations."""
    # Setup simulation with constraints
    sim = SimulationEngine(seed=42)
    sim.state.resources["server_capacity"] = 10.0
    sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("server_capacity"))

    # Successfully reduce capacity
    result = sim.apply_action(
        "adjust_resource", {"resource": "server_capacity", "delta": -5.0}
    )
    assert result.success
    assert sim.state.resources["server_capacity"] == 5.0

    # Try to exceed capacity (should fail)
    result = sim.apply_action(
        "adjust_resource", {"resource": "server_capacity", "delta": -10.0}
    )
    assert not result.success
    assert len(result.constraints_violated) == 1
    # State should be unchanged
    assert sim.state.resources["server_capacity"] == 5.0


def test_forking_and_divergence() -> None:
    """Test forking timeline and diverging paths."""
    # Create main simulation
    main = SimulationEngine(seed=42)
    main.state.resources["investment"] = 1000.0

    # Make some progress
    main.apply_action("step", {})
    main.apply_action("adjust_resource", {"resource": "investment", "delta": -200.0})

    # Fork at decision point
    fork = main.fork()

    # Main timeline: conservative approach
    main.apply_action("adjust_resource", {"resource": "investment", "delta": -100.0})
    main.apply_action("set_flag", {"flag": "conservative", "value": True})

    # Fork timeline: aggressive approach
    fork.apply_action("adjust_resource", {"resource": "investment", "delta": -500.0})
    fork.apply_action("set_flag", {"flag": "aggressive", "value": True})

    # Verify divergence
    assert main.state.resources["investment"] == 700.0
    assert fork.state.resources["investment"] == 300.0
    assert main.state.flags.get("conservative") is True
    assert fork.state.flags.get("aggressive") is True


def test_entity_lifecycle() -> None:
    """Test entity creation, modification, and removal."""
    sim = SimulationEngine(seed=42)

    # Add entities
    sim.apply_action(
        "add_entity",
        {"entity_id": "task1", "data": {"name": "Setup Database", "status": "pending"}},
    )
    sim.apply_action(
        "add_entity",
        {"entity_id": "task2", "data": {"name": "Deploy API", "status": "pending"}},
    )

    assert len(sim.state.entities) == 2

    # Update entity
    sim.apply_action(
        "add_entity",
        {"entity_id": "task1", "data": {"name": "Setup Database", "status": "completed"}},
    )

    assert sim.state.entities["task1"]["status"] == "completed"

    # Remove entity
    sim.apply_action("remove_entity", {"entity_id": "task1"})

    assert "task1" not in sim.state.entities
    assert len(sim.state.entities) == 1


def test_reproducibility_scenario() -> None:
    """Test that identical operations produce identical results."""
    # Create two simulations with same seed
    sim1 = SimulationEngine(seed=12345)
    sim2 = SimulationEngine(seed=12345)

    # Initialize same resources
    for sim in [sim1, sim2]:
        sim.state.resources["cpu_available"] = 100.0
        sim.state.resources["memory_available"] = 1000.0

    # Execute identical sequence
    operations = [
        ("step", {}),
        ("simulate_load", {"load_factor": 1.0}),
        ("step", {}),
        ("simulate_load", {"load_factor": 1.5}),
        ("set_metric", {"metric": "utilization", "value": 0.85}),
    ]

    for action, params in operations:
        sim1.apply_action(action, params)
        sim2.apply_action(action, params)

    # Results should be identical
    assert sim1.state.time == sim2.state.time
    assert sim1.state.resources == sim2.state.resources
    assert sim1.state.metrics == sim2.state.metrics


def test_complex_load_simulation() -> None:
    """Test complex load simulation scenario."""
    sim = SimulationEngine(seed=42)

    # Initialize system resources
    sim.state.resources.update(
        {
            "cpu_available": 100.0,
            "memory_available": 1000.0,
            "disk_space": 5000.0,
        }
    )

    # Add constraints
    sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("cpu_available"))
    sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("memory_available"))

    # Run load simulation
    for i in range(5):
        result = sim.apply_action("simulate_load", {"load_factor": 0.8 + i * 0.1})
        if not result.success:
            # Hit resource limit
            break

    # System should have consumed resources
    assert sim.state.resources["cpu_available"] < 100.0
    assert sim.state.resources["memory_available"] < 1000.0
    assert sim.state.time > 0


def test_history_and_audit_trail() -> None:
    """Test complete audit trail through simulation."""
    sim = SimulationEngine(seed=42)

    # Execute various operations
    operations = [
        ("step", {}),
        ("set_resource", {"resource": "funds", "value": 1000.0}),
        ("adjust_resource", {"resource": "funds", "delta": -250.0}),
        ("set_flag", {"flag": "project_active", "value": True}),
    ]

    for action, params in operations:
        sim.apply_action(action, params)

    # Get complete history
    history = sim.get_history()

    # Should have creation event + all operations
    assert len(history) >= len(operations) + 1

    # Verify event structure
    for event in history:
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.event_type is not None

    # Check that action events have proper data
    action_events = [e for e in history if e.event_type.value == "action_applied"]
    assert len(action_events) == len(operations)

    for event in action_events:
        assert event.action_name is not None
        assert isinstance(event.params, dict)
