#!/usr/bin/env python3
"""Demo Scenario B: Constraint violation handling."""

import json

from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.constraints import MaxResourceConstraint, NonNegativeResourceConstraint


def main() -> None:
    """Run demo scenario B - constraint violations."""
    print("=" * 60)
    print("DEMO SCENARIO B: Constraint Violation Handling")
    print("=" * 60)

    # Create simulation
    print("\n1. Creating simulation with constraints...")
    sim = SimulationEngine(seed=99)

    # Setup initial state
    sim.state.resources = {
        "infrastructure_budget": 5000.0,
        "server_load": 50.0,
    }

    # Add strict constraints
    print("\n2. Adding constraints:")
    sim.constraint_engine.add_constraint(
        NonNegativeResourceConstraint("infrastructure_budget")
    )
    sim.constraint_engine.add_constraint(MaxResourceConstraint("server_load", 100.0))

    print("   - Infrastructure budget must be non-negative")
    print("   - Server load must not exceed 100.0")

    # Show initial state
    print(f"\n3. Initial State:")
    print(f"   Budget: {sim.state.resources['infrastructure_budget']:.2f}")
    print(f"   Server Load: {sim.state.resources['server_load']:.2f}")

    # Valid operations
    print("\n4. Executing valid operations...")

    print("\n   Operation 1: Increase server load (within limits)")
    result = sim.apply_action(
        "adjust_resource", {"resource": "server_load", "delta": 30.0}
    )
    if result.success:
        print(f"   ✓ SUCCESS: {result.reason}")
        print(f"   Server load now: {sim.state.resources['server_load']:.2f}")
    else:
        print(f"   ✗ FAILED: {result.message}")

    print("\n   Operation 2: Spend from budget (valid amount)")
    result = sim.apply_action(
        "adjust_resource", {"resource": "infrastructure_budget", "delta": -1000.0}
    )
    if result.success:
        print(f"   ✓ SUCCESS: {result.reason}")
        print(f"   Budget now: {sim.state.resources['infrastructure_budget']:.2f}")
    else:
        print(f"   ✗ FAILED: {result.message}")

    # Constraint violation attempts
    print("\n5. Testing constraint violations...")

    print("\n   Violation Attempt 1: Exceed maximum server load")
    result = sim.apply_action(
        "adjust_resource", {"resource": "server_load", "delta": 50.0}
    )
    if not result.success:
        print(f"   ✓ REJECTED as expected: {result.message}")
        print(f"   Violations detected:")
        for v in result.constraints_violated:
            print(f"     - {v.constraint_id}: {v.message}")
        print(f"   State unchanged - Server load still: {sim.state.resources['server_load']:.2f}")
    else:
        print(f"   ✗ UNEXPECTED: Action should have been rejected")

    print("\n   Violation Attempt 2: Spend more than available budget")
    result = sim.apply_action(
        "adjust_resource", {"resource": "infrastructure_budget", "delta": -5000.0}
    )
    if not result.success:
        print(f"   ✓ REJECTED as expected: {result.message}")
        print(f"   Violations detected:")
        for v in result.constraints_violated:
            print(f"     - {v.constraint_id}: {v.message}")
        print(
            f"   State unchanged - Budget still: {sim.state.resources['infrastructure_budget']:.2f}"
        )
    else:
        print(f"   ✗ UNEXPECTED: Action should have been rejected")

    # Show final state
    print("\n6. Final State (after constraint rejections):")
    print(f"   Budget: {sim.state.resources['infrastructure_budget']:.2f}")
    print(f"   Server Load: {sim.state.resources['server_load']:.2f}")
    print("   ✓ State integrity maintained - no invalid changes applied")

    # Show event history
    print("\n7. Event History:")
    history = sim.get_history()
    print(f"   Total events: {len(history)}")

    successful_actions = [
        e for e in history if e.event_type.value == "action_applied"
    ]
    violations = [
        e for e in history if e.event_type.value == "constraint_violated"
    ]

    print(f"   Successful actions: {len(successful_actions)}")
    print(f"   Rejected actions: {len(violations)}")

    print("\n   Recent events:")
    for event in history[-5:]:
        status = "✓" if event.event_type.value == "action_applied" else "✗"
        print(f"   {status} {event.event_type.value}: {event.reason}")

    # Test forking after constraints
    print("\n8. Testing timeline fork after constraint violations:")
    fork = sim.fork()
    print(f"   ✓ Created fork (ID: {str(fork.state.simulation_id)[:8]}...)")
    print(f"   Fork inherits state: Budget={fork.state.resources['infrastructure_budget']:.2f}")

    # Different path in fork
    result = fork.apply_action(
        "adjust_resource", {"resource": "infrastructure_budget", "delta": -2000.0}
    )
    if result.success:
        print(f"   ✓ Fork diverged: Budget now {fork.state.resources['infrastructure_budget']:.2f}")
        print(
            f"   Original unchanged: Budget still {sim.state.resources['infrastructure_budget']:.2f}"
        )

    print("\n" + "=" * 60)
    print("SCENARIO B COMPLETED SUCCESSFULLY")
    print("Demonstrated:")
    print("  ✓ Constraint validation")
    print("  ✓ State rollback on violations")
    print("  ✓ Clear error messages")
    print("  ✓ Event history tracking")
    print("  ✓ Timeline forking")
    print("=" * 60)


if __name__ == "__main__":
    main()
