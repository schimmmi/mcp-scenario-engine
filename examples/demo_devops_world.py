#!/usr/bin/env python3
"""Demo: DevOps World with automatic rule application."""

from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.world_rules import (
    DevOpsBurnoutRule,
    DevOpsCPUTracker,
    DevOpsLoadRule,
    DevOpsScaleUpRule,
)


def main() -> None:
    """Run DevOps world simulation with automatic rules."""
    print("=" * 70)
    print("🌍 DevOps World Simulation - Automatic Rule Application")
    print("=" * 70)

    # Create simulation
    sim = SimulationEngine(seed=42)

    # Setup DevOps world state
    sim.state.resources = {
        "cpu": 40.0,  # Current CPU usage
        "servers": 3,  # Number of servers
    }
    sim.state.metrics = {
        "error_rate": 0.01,  # Error rate
        "load": 0.5,  # System load
    }
    sim.state.flags = {
        "burnout": False,  # Team burnout flag
    }

    # Add world rules
    print("\n📜 Installing World Rules:")
    sim.world_rule_engine.add_rule(DevOpsCPUTracker(cpu_threshold=80.0))
    print("   ✓ CPU Tracker (tracks high CPU duration)")

    sim.world_rule_engine.add_rule(DevOpsLoadRule(cpu_threshold=80.0, error_increment=0.01))
    print("   ✓ High CPU → Error Rate++ (threshold: 80)")

    sim.world_rule_engine.add_rule(
        DevOpsBurnoutRule(cpu_threshold=80.0, duration_threshold=3)
    )
    print("   ✓ High CPU for 3 steps → Burnout")

    sim.world_rule_engine.add_rule(DevOpsScaleUpRule(cpu_threshold=90.0, max_servers=10))
    print("   ✓ Auto-scale at 90% CPU")

    # Show initial state
    print(f"\n📊 Initial State:")
    print(f"   CPU: {sim.state.resources['cpu']}")
    print(f"   Servers: {sim.state.resources['servers']}")
    print(f"   Error Rate: {sim.state.metrics['error_rate']}")
    print(f"   Burnout: {sim.state.flags['burnout']}")
    print(f"   Time: {sim.state.time}")

    # === Phase 1: Normal operation ===
    print("\n" + "=" * 70)
    print("📈 Phase 1: Normal Operation (CPU < 80)")
    print("=" * 70)

    result = sim.apply_action("step", {})
    print(f"\n⏱️  Step 1:")
    print(f"   {result.reason}")
    print(f"   CPU: {sim.state.resources['cpu']} (no rules triggered)")
    print(f"   Error Rate: {sim.state.metrics['error_rate']}")

    # === Phase 2: High load ===
    print("\n" + "=" * 70)
    print("🔥 Phase 2: High Load (CPU > 80)")
    print("=" * 70)

    print("\n🚀 Increasing CPU to 85...")
    sim.apply_action("set_resource", {"resource": "cpu", "value": 85.0})

    for step in range(1, 4):
        result = sim.apply_action("step", {})
        print(f"\n⏱️  Step {step}:")
        print(f"   {result.reason}")
        print(f"   CPU: {sim.state.resources['cpu']}")
        print(f"   Error Rate: {sim.state.metrics['error_rate']:.3f}")
        print(f"   High CPU Duration: {sim.state.metadata.get('high_cpu_duration', 0)}")
        print(f"   Burnout: {sim.state.flags['burnout']}")

    # === Phase 3: Critical load triggers auto-scale ===
    print("\n" + "=" * 70)
    print("🚨 Phase 3: Critical Load (CPU > 90) → Auto-Scale")
    print("=" * 70)

    print("\n💥 Increasing CPU to 95...")
    sim.apply_action("set_resource", {"resource": "cpu", "value": 95.0})

    result = sim.apply_action("step", {})
    print(f"\n⏱️  Step after critical load:")
    print(f"   {result.reason}")
    print(f"   CPU: {sim.state.resources['cpu']:.2f} (auto-scaled!)")
    print(f"   Servers: {sim.state.resources['servers']}")
    print(f"   Error Rate: {sim.state.metrics['error_rate']:.3f}")

    # === Summary ===
    print("\n" + "=" * 70)
    print("📋 Simulation Summary")
    print("=" * 70)

    history = sim.get_history()
    print(f"\n📚 Total Events: {len(history)}")

    step_events = [e for e in history if e.action_name == "step"]
    print(f"\n⏱️  Step Events with Rules:")
    for event in step_events:
        if "World rules applied:" in (event.reason or ""):
            print(f"   Time {event.state_delta.get('time', {}).get('after', '?')}: {event.reason}")

    print(f"\n🎯 Final State:")
    print(f"   Time: {sim.state.time}")
    print(f"   CPU: {sim.state.resources['cpu']:.2f}")
    print(f"   Servers: {sim.state.resources['servers']}")
    print(f"   Error Rate: {sim.state.metrics['error_rate']:.3f}")
    print(f"   Burnout: {sim.state.flags['burnout']}")

    print("\n" + "=" * 70)
    print("✅ World Rules Successfully Applied Automatically!")
    print("=" * 70)
    print("\n🌟 Key Observations:")
    print("   • Rules trigger automatically on 'step'")
    print("   • CPU > 80 increases error rate")
    print("   • CPU > 80 for 3 steps causes burnout")
    print("   • CPU > 90 triggers auto-scaling")
    print("   • The system is now a true WORLD MODEL! 🌍")


if __name__ == "__main__":
    main()
