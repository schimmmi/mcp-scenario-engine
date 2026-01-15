#!/usr/bin/env python3
"""Demo: Persistence - Save and load simulations."""

from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.dynamic_rules import DynamicRule
from mcp_scenario_engine.persistence import SimulationPersistence


def main() -> None:
    """Run persistence demo."""
    print("=" * 70)
    print("💾 Persistence Demo - Save & Load Simulations")
    print("=" * 70)

    # Use a temporary directory for demo
    persistence = SimulationPersistence(storage_dir=".demo_simulations")
    print(f"\n📁 Storage directory: {persistence.storage_dir.absolute()}")

    # === Create Simulation 1 ===
    print("\n📝 Creating DevOps Simulation...")
    devops_sim = SimulationEngine(seed=42)

    devops_sim.state.resources = {"cpu": 85.0, "servers": 3}
    devops_sim.state.metrics = {"error_rate": 0.01}
    devops_sim.state.flags = {"burnout": False}

    # Add rules
    cpu_rule = DynamicRule(
        rule_id="cpu_overload",
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
                "value": {"type": "increment", "amount": 0.05},
            }
        ],
        priority=0,
        description="High CPU increases error rate",
    )
    devops_sim.world_rule_engine.add_rule(cpu_rule)

    # Run a few steps
    for _ in range(3):
        devops_sim.apply_action("step", {})

    print(f"   Time: {devops_sim.state.time}")
    print(f"   Error Rate: {devops_sim.state.metrics['error_rate']:.3f}")

    # === Save Simulation ===
    print("\n💾 Saving DevOps simulation...")
    file_path = persistence.save_simulation(
        "devops_scenario_1", devops_sim, "High CPU scenario with 3 steps"
    )
    print(f"   ✓ Saved to: {file_path}")

    # === Create Simulation 2 ===
    print("\n📝 Creating Health Simulation...")
    health_sim = SimulationEngine(seed=99)

    health_sim.state.resources = {"stress": 60.0, "energy": 80.0}
    health_sim.state.metrics = {"sleep_quality": 0.8}
    health_sim.state.flags = {"exhausted": False}

    stress_rule = DynamicRule(
        rule_id="high_stress",
        condition={
            "type": "comparison",
            "left": {"type": "resource", "name": "stress"},
            "operator": ">",
            "right": {"type": "value", "value": 70},
        },
        actions=[
            {
                "type": "set_metric",
                "metric": "sleep_quality",
                "value": {"type": "increment", "amount": -0.1},
            }
        ],
        description="High stress reduces sleep quality",
    )
    health_sim.world_rule_engine.add_rule(stress_rule)

    health_sim.apply_action("set_resource", {"resource": "stress", "value": 75.0})
    health_sim.apply_action("step", {})

    print(f"   Stress: {health_sim.state.resources['stress']}")
    print(f"   Sleep Quality: {health_sim.state.metrics['sleep_quality']:.2f}")

    # === Save Simulation 2 ===
    print("\n💾 Saving Health simulation...")
    file_path = persistence.save_simulation(
        "health_scenario_1", health_sim, "Stress impact on sleep"
    )
    print(f"   ✓ Saved to: {file_path}")

    # === List Simulations ===
    print("\n📋 Listing all saved simulations...")
    sims = persistence.list_simulations()
    print(f"   Found {len(sims)} simulations:")
    for sim in sims:
        print(f"   • {sim['name']}: {sim['description']}")
        print(f"     Time: {sim['time']}, Rules: {sim['rule_count']}")

    # === Get Info ===
    print("\n🔍 Getting info about devops_scenario_1...")
    info = persistence.get_simulation_info("devops_scenario_1")
    if info:
        print(f"   Name: {info['name']}")
        print(f"   Description: {info['description']}")
        print(f"   Time: {info['time']}")
        print(f"   Rules: {info['rule_count']}")
        print(f"   History Events: {info['history_count']}")

    # === Load Simulation ===
    print("\n📂 Loading devops_scenario_1...")
    loaded_sim = persistence.load_simulation("devops_scenario_1")
    print(f"   ✓ Loaded successfully")
    print(f"   Time: {loaded_sim.state.time}")
    print(f"   Error Rate: {loaded_sim.state.metrics['error_rate']:.3f}")
    print(f"   Rules: {loaded_sim.world_rule_engine.get_rule_ids()}")

    # === Continue Simulation ===
    print("\n▶️  Continuing loaded simulation...")
    loaded_sim.apply_action("step", {})
    print(f"   Time: {loaded_sim.state.time}")
    print(f"   Error Rate: {loaded_sim.state.metrics['error_rate']:.3f}")

    # === Save Updated ===
    print("\n💾 Saving updated simulation (overwrite)...")
    persistence.save_simulation(
        "devops_scenario_1", loaded_sim, "High CPU scenario - continued"
    )
    print("   ✓ Saved (overwritten)")

    # === Delete Simulation ===
    print("\n🗑️  Deleting health_scenario_1...")
    deleted = persistence.delete_simulation("health_scenario_1")
    if deleted:
        print("   ✓ Deleted successfully")

    # === Final List ===
    print("\n📋 Final simulation list:")
    sims = persistence.list_simulations()
    for sim in sims:
        print(f"   • {sim['name']}: {sim['description']}")

    print("\n" + "=" * 70)
    print("✅ Persistence Demo Complete!")
    print("=" * 70)
    print("\n💡 Key Features:")
    print("   • Save simulations with state + rules + history")
    print("   • Load simulations and continue from checkpoint")
    print("   • List all saved simulations")
    print("   • Get metadata without loading")
    print("   • Delete simulations")
    print("   • Overwrite existing saves")


if __name__ == "__main__":
    main()
