#!/usr/bin/env python3
"""Demo: Weight Loss Simulation with Complex Formulas."""

from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.dynamic_rules import DynamicRule


def main() -> None:
    """Run weight loss simulation demo."""
    print("=" * 70)
    print("🏋️  Weight Loss Simulation - Complex Formulas Demo")
    print("=" * 70)

    # Create simulation
    sim = SimulationEngine(seed=42)

    # Set initial state
    sim.state.metrics = {
        "kaloriendefizit": 400.0,  # Daily calorie deficit
        "training_sessions_pro_woche": 3.0,  # Weekly training sessions
        "compliance": 0.85,  # 85% adherence to plan
    }
    sim.state.resources = {
        "gewicht": 92.47,  # Total weight in kg
        "fettmasse": 18.55,  # Fat mass in kg
        "muskelmasse": 70.16,  # Muscle mass in kg
    }

    print("\n📊 Initial State:")
    print(f"   Calorie Deficit: {sim.state.metrics['kaloriendefizit']} kcal/day")
    print(
        f"   Training Sessions: {sim.state.metrics['training_sessions_pro_woche']}/week"
    )
    print(f"   Compliance: {sim.state.metrics['compliance']*100:.0f}%")
    print(f"   Weight: {sim.state.resources['gewicht']:.2f} kg")
    print(f"   Fat Mass: {sim.state.resources['fettmasse']:.2f} kg")
    print(f"   Muscle Mass: {sim.state.resources['muskelmasse']:.2f} kg")

    # Add complex formula rule: Fat loss = (Calorie_Deficit / 7700) * 7 * Compliance
    # 7700 kcal = 1 kg fat, 7 = days per week
    fettabbau_rule = DynamicRule(
        rule_id="weekly_fat_loss",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_resource",
                "resource": "fettmasse",
                "value": {
                    "type": "subtract",
                    "left": {"type": "resource", "name": "fettmasse"},
                    "right": {
                        "type": "multiply",
                        "values": [
                            {
                                "type": "divide",
                                "numerator": {
                                    "type": "metric",
                                    "name": "kaloriendefizit",
                                },
                                "denominator": {"type": "value", "value": 7700},
                            },
                            {"type": "value", "value": 7},  # Days per week
                            {"type": "metric", "name": "compliance"},
                        ],
                    },
                },
            }
        ],
        priority=10,
        description="Calculate weekly fat loss based on calorie deficit",
    )

    # Add muscle gain rule: Muscle_Gain = Training_Sessions * 0.05 * Compliance
    # 0.05 kg = 50g muscle gain per training session (realistic for beginners)
    muskel_rule = DynamicRule(
        rule_id="weekly_muscle_gain",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_resource",
                "resource": "muskelmasse",
                "value": {
                    "type": "add",
                    "values": [
                        {"type": "resource", "name": "muskelmasse"},
                        {
                            "type": "multiply",
                            "values": [
                                {
                                    "type": "metric",
                                    "name": "training_sessions_pro_woche",
                                },
                                {"type": "value", "value": 0.05},
                                {"type": "metric", "name": "compliance"},
                            ],
                        },
                    ],
                },
            }
        ],
        priority=5,
        description="Calculate weekly muscle gain based on training frequency",
    )

    # Update total weight rule
    gewicht_update_rule = DynamicRule(
        rule_id="update_total_weight",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_resource",
                "resource": "gewicht",
                "value": {
                    "type": "add",
                    "values": [
                        {"type": "resource", "name": "fettmasse"},
                        {"type": "resource", "name": "muskelmasse"},
                    ],
                },
            }
        ],
        priority=1,
        description="Update total weight (fat + muscle)",
    )

    sim.world_rule_engine.add_rule(fettabbau_rule, priority=10)
    sim.world_rule_engine.add_rule(muskel_rule, priority=5)
    sim.world_rule_engine.add_rule(gewicht_update_rule, priority=1)

    print("\n📝 World Rules:")
    print("   1. Weekly fat loss: (deficit/7700) * 7 * compliance")
    print("   2. Weekly muscle gain: training_sessions * 0.05 * compliance")
    print("   3. Total weight: fat_mass + muscle_mass")

    print("\n🏃 Simulating 8 Weeks...")
    print("-" * 70)
    print(
        f"{'Week':<6} {'Weight':>8} {'Change':>8} {'Fat':>8} {'Muscle':>8} {'Fat%':>7}"
    )
    print("-" * 70)

    start_weight = sim.state.resources["gewicht"]
    prev_weight = start_weight

    print(
        f"{'Start':<6} {start_weight:>7.2f}kg {'-':>8} "
        f"{sim.state.resources['fettmasse']:>7.2f}kg "
        f"{sim.state.resources['muskelmasse']:>7.2f}kg "
        f"{sim.state.resources['fettmasse']/start_weight*100:>6.1f}%"
    )

    for woche in range(8):
        sim.apply_action("step", {})
        gewicht = sim.state.resources["gewicht"]
        change = gewicht - prev_weight
        fat_pct = sim.state.resources["fettmasse"] / gewicht * 100

        print(
            f"{woche+1:<6} {gewicht:>7.2f}kg {change:>+7.2f}kg "
            f"{sim.state.resources['fettmasse']:>7.2f}kg "
            f"{sim.state.resources['muskelmasse']:>7.2f}kg "
            f"{fat_pct:>6.1f}%"
        )

        prev_weight = gewicht

    print("-" * 70)
    total_loss = start_weight - sim.state.resources["gewicht"]
    fat_loss = 18.55 - sim.state.resources["fettmasse"]
    muscle_gain = sim.state.resources["muskelmasse"] - 70.16

    print(f"\n📈 Results after 8 weeks:")
    print(f"   Total weight loss: {total_loss:.2f} kg")
    print(f"   Fat loss: {fat_loss:.2f} kg")
    print(f"   Muscle gain: {muscle_gain:.2f} kg")
    print(f"   Body fat %: {18.55/start_weight*100:.1f}% → {fat_pct:.1f}%")

    print("\n" + "=" * 70)
    print("✅ Complex Formula Demo Complete!")
    print("=" * 70)

    print("\n💡 Formula Features Demonstrated:")
    print("   • Division: (deficit / 7700)")
    print("   • Multiplication of multiple variables: value1 * value2 * value3")
    print("   • Addition: fat_mass + muscle_mass")
    print("   • Subtraction: current - decrease")
    print("   • Nested formulas: ((a / b) * c * d)")
    print("   • State references: metrics, resources")
    print("   • Automatic rule application on each step")


if __name__ == "__main__":
    main()
