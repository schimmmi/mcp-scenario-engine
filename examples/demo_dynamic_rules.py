#!/usr/bin/env python3
"""Demo: Dynamic Rules - Define rules via JSON."""

from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.dynamic_rules import DynamicRule


def main() -> None:
    """Run simulation with dynamically defined rules."""
    print("=" * 70)
    print("🎯 Dynamic Rules Demo - Define Rules via JSON")
    print("=" * 70)

    # Create simulation
    sim = SimulationEngine(seed=42)

    # Setup initial state
    sim.state.resources = {
        "cpu": 40.0,
        "servers": 3,
    }
    sim.state.metrics = {
        "error_rate": 0.01,
    }
    sim.state.flags = {
        "burnout": False,
    }

    print("\n📊 Initial State:")
    print(f"   CPU: {sim.state.resources['cpu']}")
    print(f"   Servers: {sim.state.resources['servers']}")
    print(f"   Error Rate: {sim.state.metrics['error_rate']}")
    print(f"   Burnout: {sim.state.flags['burnout']}")

    # === Rule 1: CPU Tracker ===
    print("\n" + "=" * 70)
    print("📜 Rule 1: CPU Tracker (tracks high CPU duration)")
    print("=" * 70)

    cpu_tracker_rule = DynamicRule(
        rule_id="cpu_tracker",
        condition={"type": "always"},  # Always track
        actions=[
            {
                "type": "set_metadata",
                "key": "high_cpu_duration",
                "value": {
                    "type": "increment" if sim.state.resources.get("cpu", 0) > 80 else "value",
                    "amount": 1,
                } if sim.state.resources.get("cpu", 0) > 80 else 0,
            }
        ],
    )

    # Simpler version - just increment when CPU > 80
    cpu_tracker_rule = DynamicRule(
        rule_id="cpu_tracker",
        condition={
            "type": "comparison",
            "left": {"type": "resource", "name": "cpu"},
            "operator": ">",
            "right": {"type": "value", "value": 80},
        },
        actions=[
            {
                "type": "set_metadata",
                "key": "high_cpu_duration",
                "value": {"type": "increment", "amount": 1},
            }
        ],
    )

    sim.world_rule_engine.add_rule(cpu_tracker_rule)
    print("✅ Rule added:")
    print(f"   Condition: cpu > 80")
    print(f"   Action: high_cpu_duration++")

    # === Rule 2: High CPU increases error rate ===
    print("\n" + "=" * 70)
    print("📜 Rule 2: High CPU → Error Rate++")
    print("=" * 70)

    high_cpu_rule = DynamicRule(
        rule_id="high_cpu_errors",
        condition={
            "type": "comparison",
            "left": {"type": "resource", "name": "cpu"},
            "operator": ">",
            "right": {"type": "value", "value": 80},
        },
        actions=[
            {
                "type": "set_metric",
                "metric": "error_rate",
                "value": {"type": "increment", "amount": 0.01},
            }
        ],
    )

    sim.world_rule_engine.add_rule(high_cpu_rule)
    print("✅ Rule added:")
    print(f"   Condition: cpu > 80")
    print(f"   Action: error_rate += 0.01")

    # === Rule 3: Burnout after 3 high-CPU steps ===
    print("\n" + "=" * 70)
    print("📜 Rule 3: High CPU for 3 steps → Burnout")
    print("=" * 70)

    burnout_rule = DynamicRule(
        rule_id="burnout",
        condition={
            "type": "and",
            "conditions": [
                {
                    "type": "comparison",
                    "left": {"type": "resource", "name": "cpu"},
                    "operator": ">",
                    "right": {"type": "value", "value": 80},
                },
                {
                    "type": "comparison",
                    "left": {"type": "metadata", "name": "high_cpu_duration"},
                    "operator": ">=",
                    "right": {"type": "value", "value": 3},
                },
            ],
        },
        actions=[
            {
                "type": "set_flag",
                "flag": "burnout",
                "value": True,
            }
        ],
    )

    sim.world_rule_engine.add_rule(burnout_rule)
    print("✅ Rule added:")
    print(f"   Condition: cpu > 80 AND high_cpu_duration >= 3")
    print(f"   Action: burnout = true")

    # === Test the rules ===
    print("\n" + "=" * 70)
    print("🧪 Testing Rules")
    print("=" * 70)

    print("\n1️⃣  Normal operation (CPU = 40)")
    result = sim.apply_action("step", {})
    print(f"   {result.reason}")
    print(f"   Error Rate: {sim.state.metrics['error_rate']:.3f} (unchanged)")

    print("\n2️⃣  Increase CPU to 85 (> 80)")
    sim.apply_action("set_resource", {"resource": "cpu", "value": 85.0})
    print(f"   CPU now: {sim.state.resources['cpu']}")

    print("\n3️⃣  Step 1 with high CPU")
    result = sim.apply_action("step", {})
    print(f"   {result.reason}")
    print(f"   Error Rate: {sim.state.metrics['error_rate']:.3f} ✨ (increased!)")
    print(f"   High CPU Duration: {sim.state.metadata.get('high_cpu_duration', 0)}")
    print(f"   Burnout: {sim.state.flags['burnout']}")

    print("\n4️⃣  Step 2 with high CPU")
    result = sim.apply_action("step", {})
    print(f"   Error Rate: {sim.state.metrics['error_rate']:.3f}")
    print(f"   High CPU Duration: {sim.state.metadata.get('high_cpu_duration', 0)}")
    print(f"   Burnout: {sim.state.flags['burnout']}")

    print("\n5️⃣  Step 3 with high CPU")
    result = sim.apply_action("step", {})
    print(f"   Error Rate: {sim.state.metrics['error_rate']:.3f}")
    print(f"   High CPU Duration: {sim.state.metadata.get('high_cpu_duration', 0)}")
    print(f"   Burnout: {sim.state.flags['burnout']} ⚠️  (BURNOUT!)")

    # === Summary ===
    print("\n" + "=" * 70)
    print("✅ Dynamic Rules Work!")
    print("=" * 70)
    print("\n🎯 Rules defined via JSON:")
    print("   • Conditions: comparisons, and/or/not, always")
    print("   • Actions: set_resource, set_metric, set_flag, set_metadata")
    print("   • Values: increment, multiply, or fixed")
    print("\n🌍 You can define ANY rule you want via MCP!")


if __name__ == "__main__":
    main()
