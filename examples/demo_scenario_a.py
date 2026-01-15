#!/usr/bin/env python3
"""Demo Scenario A: Normal simulation run with multiple actions."""

import json

from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.constraints import NonNegativeResourceConstraint


def main() -> None:
    """Run demo scenario A - normal simulation."""
    print("=" * 60)
    print("DEMO SCENARIO A: Normal Simulation Run")
    print("=" * 60)

    # Create simulation with seed for reproducibility
    print("\n1. Creating simulation with seed=42...")
    sim = SimulationEngine(seed=42)

    # Setup initial state
    sim.state.resources = {
        "budget": 10000.0,
        "team_capacity": 40.0,
        "server_capacity": 100.0,
    }

    # Add constraints
    print("\n2. Adding constraints...")
    sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("budget"))
    sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("team_capacity"))

    print("   - Budget must be non-negative")
    print("   - Team capacity must be non-negative")

    # Execute simulation steps
    print("\n3. Executing simulation steps...")

    # Step 1: Initialize project
    print("\n   Step 1: Initialize project")
    result = sim.apply_action(
        "add_entity",
        {
            "entity_id": "project_alpha",
            "data": {
                "name": "Alpha Project",
                "phase": "planning",
                "priority": "high",
            },
        },
    )
    print(f"   ✓ {result.reason}")

    # Step 2: Allocate budget
    print("\n   Step 2: Allocate initial budget")
    result = sim.apply_action(
        "adjust_resource", {"resource": "budget", "delta": -2000.0}
    )
    print(f"   ✓ {result.reason}")
    print(f"   Remaining budget: {sim.state.resources['budget']:.2f}")

    # Step 3: Assign team
    print("\n   Step 3: Assign team members")
    result = sim.apply_action(
        "adjust_resource", {"resource": "team_capacity", "delta": -10.0}
    )
    print(f"   ✓ {result.reason}")
    print(f"   Available capacity: {sim.state.resources['team_capacity']:.2f} hours/week")

    # Step 4: Track progress
    print("\n   Step 4: Set initial metrics")
    sim.apply_action("set_metric", {"metric": "project_progress", "value": 0.15})
    sim.apply_action("set_metric", {"metric": "risk_level", "value": 0.3})
    print("   ✓ Set project_progress = 0.15")
    print("   ✓ Set risk_level = 0.3")

    # Step 5: Advance time
    print("\n   Step 5: Advance simulation")
    for i in range(3):
        sim.apply_action("step", {})
    print(f"   ✓ Advanced to time step {sim.state.time}")

    # Step 6: Update project status
    print("\n   Step 6: Update project status")
    sim.apply_action(
        "add_entity",
        {
            "entity_id": "project_alpha",
            "data": {
                "name": "Alpha Project",
                "phase": "implementation",
                "priority": "high",
            },
        },
    )
    print("   ✓ Project moved to implementation phase")

    # Display final state
    print("\n4. Final State:")
    print(f"   Time: {sim.state.time}")
    print(f"   Budget: {sim.state.resources['budget']:.2f}")
    print(f"   Team Capacity: {sim.state.resources['team_capacity']:.2f}")
    print(f"   Metrics: {json.dumps(sim.state.metrics, indent=6)}")

    # Show history
    print("\n5. Event History:")
    history = sim.get_history()
    print(f"   Total events: {len(history)}")
    for i, event in enumerate(history[-5:], 1):
        print(f"   [{i}] {event.event_type.value}: {event.reason}")

    # Test reproducibility
    print("\n6. Testing Reproducibility:")
    sim2 = SimulationEngine(seed=42)
    sim2.state.resources = {
        "budget": 10000.0,
        "team_capacity": 40.0,
        "server_capacity": 100.0,
    }
    sim2.constraint_engine.add_constraint(NonNegativeResourceConstraint("budget"))

    # Execute same actions
    sim2.apply_action(
        "add_entity",
        {
            "entity_id": "project_alpha",
            "data": {"name": "Alpha Project", "phase": "planning", "priority": "high"},
        },
    )
    sim2.apply_action("adjust_resource", {"resource": "budget", "delta": -2000.0})
    sim2.apply_action("adjust_resource", {"resource": "team_capacity", "delta": -10.0})

    if sim.state.resources["budget"] == sim2.state.resources["budget"]:
        print("   ✓ Reproducibility verified - identical results with same seed")
    else:
        print("   ✗ Reproducibility check failed")

    print("\n" + "=" * 60)
    print("SCENARIO A COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
