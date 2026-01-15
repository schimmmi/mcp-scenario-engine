#!/usr/bin/env python3
"""Demo: Evolutionary Game Theory - Hawk-Dove Game with Population Dynamics."""

from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.dynamic_rules import DynamicRule


def main() -> None:
    """Run evolutionary hawk-dove game simulation."""
    print("=" * 70)
    print("🦅 Evolutionary Game Theory - Hawk-Dove Population Dynamics")
    print("=" * 70)

    # Create simulation
    sim = SimulationEngine(seed=42)

    # Initial state: 50% hawks, 50% doves
    sim.state.resources = {
        "hawks": 50.0,
        "doves": 50.0,
        "total_population": 100.0,
    }
    sim.state.metrics = {
        "hawk_fitness": 0.0,
        "dove_fitness": 0.0,
        "average_fitness": 0.0,
        "resource_value": 50.0,  # V = value of resource
        "cost_of_fighting": 100.0,  # C = cost when two hawks fight
    }

    print("\n📊 Hawk-Dove Game:")
    print("   Resource Value (V) = 50")
    print("   Fighting Cost (C) = 100")
    print()
    print("   Payoff Matrix:")
    print("   ┌─────────────┬──────────┬──────────┐")
    print("   │             │ Hawk     │ Dove     │")
    print("   ├─────────────┼──────────┼──────────┤")
    print("   │ Hawk        │ (V-C)/2  │ V        │")
    print("   │             │ = -25    │ = 50     │")
    print("   ├─────────────┼──────────┼──────────┤")
    print("   │ Dove        │ 0        │ V/2      │")
    print("   │             │          │ = 25     │")
    print("   └─────────────┴──────────┴──────────┘")

    # Calculate hawk frequency
    hawk_freq_rule = DynamicRule(
        rule_id="hawk_frequency",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_metric",
                "metric": "hawk_frequency",
                "value": {
                    "type": "divide",
                    "numerator": {"type": "resource", "name": "hawks"},
                    "denominator": {"type": "resource", "name": "total_population"},
                },
            }
        ],
        priority=100,
        description="Calculate proportion of hawks in population",
    )

    # Calculate dove frequency
    dove_freq_rule = DynamicRule(
        rule_id="dove_frequency",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_metric",
                "metric": "dove_frequency",
                "value": {
                    "type": "divide",
                    "numerator": {"type": "resource", "name": "doves"},
                    "denominator": {"type": "resource", "name": "total_population"},
                },
            }
        ],
        priority=100,
        description="Calculate proportion of doves in population",
    )

    # Calculate hawk fitness
    # E(Hawk) = p_hawk * (V-C)/2 + p_dove * V
    hawk_fitness_rule = DynamicRule(
        rule_id="hawk_fitness",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_metric",
                "metric": "hawk_fitness",
                "value": {
                    "type": "add",
                    "values": [
                        # Prob meet hawk * payoff vs hawk
                        {
                            "type": "multiply",
                            "values": [
                                {"type": "metric", "name": "hawk_frequency"},
                                {
                                    "type": "divide",
                                    "numerator": {
                                        "type": "subtract",
                                        "left": {
                                            "type": "metric",
                                            "name": "resource_value",
                                        },
                                        "right": {
                                            "type": "metric",
                                            "name": "cost_of_fighting",
                                        },
                                    },
                                    "denominator": {"type": "value", "value": 2},
                                },
                            ],
                        },
                        # Prob meet dove * payoff vs dove
                        {
                            "type": "multiply",
                            "values": [
                                {"type": "metric", "name": "dove_frequency"},
                                {"type": "metric", "name": "resource_value"},
                            ],
                        },
                    ],
                },
            }
        ],
        priority=50,
        description="Calculate expected fitness for hawk strategy",
    )

    # Calculate dove fitness
    # E(Dove) = p_hawk * 0 + p_dove * V/2
    dove_fitness_rule = DynamicRule(
        rule_id="dove_fitness",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_metric",
                "metric": "dove_fitness",
                "value": {
                    "type": "multiply",
                    "values": [
                        {"type": "metric", "name": "dove_frequency"},
                        {
                            "type": "divide",
                            "numerator": {"type": "metric", "name": "resource_value"},
                            "denominator": {"type": "value", "value": 2},
                        },
                    ],
                },
            }
        ],
        priority=50,
        description="Calculate expected fitness for dove strategy",
    )

    # Calculate average population fitness
    average_fitness_rule = DynamicRule(
        rule_id="average_fitness",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_metric",
                "metric": "average_fitness",
                "value": {
                    "type": "add",
                    "values": [
                        {
                            "type": "multiply",
                            "values": [
                                {"type": "metric", "name": "hawk_frequency"},
                                {"type": "metric", "name": "hawk_fitness"},
                            ],
                        },
                        {
                            "type": "multiply",
                            "values": [
                                {"type": "metric", "name": "dove_frequency"},
                                {"type": "metric", "name": "dove_fitness"},
                            ],
                        },
                    ],
                },
            }
        ],
        priority=40,
        description="Calculate average fitness across population",
    )

    # Update hawk population using replicator dynamics
    # hawks_new = hawks * (1 + (hawk_fitness - avg_fitness) / avg_fitness)
    # Simplified: hawks_new = hawks * hawk_fitness / avg_fitness
    update_hawks_rule = DynamicRule(
        rule_id="update_hawks",
        condition={
            "type": "comparison",
            "left": {"type": "metric", "name": "average_fitness"},
            "operator": ">",
            "right": {"type": "value", "value": 0},
        },
        actions=[
            {
                "type": "set_resource",
                "resource": "hawks",
                "value": {
                    "type": "multiply",
                    "values": [
                        {"type": "resource", "name": "hawks"},
                        {
                            "type": "divide",
                            "numerator": {"type": "metric", "name": "hawk_fitness"},
                            "denominator": {
                                "type": "metric",
                                "name": "average_fitness",
                            },
                        },
                    ],
                },
            }
        ],
        priority=10,
        description="Update hawk population based on relative fitness",
    )

    # Update dove population
    update_doves_rule = DynamicRule(
        rule_id="update_doves",
        condition={
            "type": "comparison",
            "left": {"type": "metric", "name": "average_fitness"},
            "operator": ">",
            "right": {"type": "value", "value": 0},
        },
        actions=[
            {
                "type": "set_resource",
                "resource": "doves",
                "value": {
                    "type": "multiply",
                    "values": [
                        {"type": "resource", "name": "doves"},
                        {
                            "type": "divide",
                            "numerator": {"type": "metric", "name": "dove_fitness"},
                            "denominator": {
                                "type": "metric",
                                "name": "average_fitness",
                            },
                        },
                    ],
                },
            }
        ],
        priority=10,
        description="Update dove population based on relative fitness",
    )

    # Normalize population to 100
    normalize_population_rule = DynamicRule(
        rule_id="normalize_population",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_resource",
                "resource": "total_population",
                "value": {
                    "type": "add",
                    "values": [
                        {"type": "resource", "name": "hawks"},
                        {"type": "resource", "name": "doves"},
                    ],
                },
            },
            # Renormalize hawks
            {
                "type": "set_resource",
                "resource": "hawks",
                "value": {
                    "type": "multiply",
                    "values": [
                        {
                            "type": "divide",
                            "numerator": {"type": "resource", "name": "hawks"},
                            "denominator": {
                                "type": "resource",
                                "name": "total_population",
                            },
                        },
                        {"type": "value", "value": 100},
                    ],
                },
            },
            # Renormalize doves
            {
                "type": "set_resource",
                "resource": "doves",
                "value": {
                    "type": "multiply",
                    "values": [
                        {
                            "type": "divide",
                            "numerator": {"type": "resource", "name": "doves"},
                            "denominator": {
                                "type": "resource",
                                "name": "total_population",
                            },
                        },
                        {"type": "value", "value": 100},
                    ],
                },
            },
            # Reset total
            {
                "type": "set_resource",
                "resource": "total_population",
                "value": {"type": "value", "value": 100},
            },
        ],
        priority=5,
        description="Normalize population to constant size",
    )

    # Add all rules
    sim.world_rule_engine.add_rule(hawk_freq_rule, priority=100)
    sim.world_rule_engine.add_rule(dove_freq_rule, priority=100)
    sim.world_rule_engine.add_rule(hawk_fitness_rule, priority=50)
    sim.world_rule_engine.add_rule(dove_fitness_rule, priority=50)
    sim.world_rule_engine.add_rule(average_fitness_rule, priority=40)
    sim.world_rule_engine.add_rule(update_hawks_rule, priority=10)
    sim.world_rule_engine.add_rule(update_doves_rule, priority=10)
    sim.world_rule_engine.add_rule(normalize_population_rule, priority=5)

    print("\n🔬 Evolutionary Stable Strategy (ESS):")
    print(f"   When C > V, ESS frequency of Hawks = V/C = {50/100}")
    print(f"   Expected equilibrium: 50% Hawks, 50% Doves")

    print("\n🧬 Simulating 20 Generations...")
    print("-" * 70)
    print(
        f"{'Gen':<5} {'Hawks':>7} {'Doves':>7} {'H_Fit':>8} {'D_Fit':>8} {'Avg_Fit':>8}"
    )
    print("-" * 70)

    print(
        f"{'0':<5} {sim.state.resources['hawks']:>7.1f} "
        f"{sim.state.resources['doves']:>7.1f} {'-':>8} {'-':>8} {'-':>8}"
    )

    for gen in range(20):
        sim.apply_action("step", {})

        print(
            f"{gen+1:<5} {sim.state.resources['hawks']:>7.1f} "
            f"{sim.state.resources['doves']:>7.1f} "
            f"{sim.state.metrics['hawk_fitness']:>8.1f} "
            f"{sim.state.metrics['dove_fitness']:>8.1f} "
            f"{sim.state.metrics['average_fitness']:>8.1f}"
        )

    print("-" * 70)
    print(f"\n📈 Equilibrium Reached:")
    print(f"   Hawks: {sim.state.resources['hawks']:.1f}%")
    print(f"   Doves: {sim.state.resources['doves']:.1f}%")
    print(f"   Hawk Fitness: {sim.state.metrics['hawk_fitness']:.2f}")
    print(f"   Dove Fitness: {sim.state.metrics['dove_fitness']:.2f}")

    # Calculate theoretical ESS
    ess_hawk_freq = sim.state.metrics["resource_value"] / sim.state.metrics[
        "cost_of_fighting"
    ]
    print(f"\n   Theoretical ESS: {ess_hawk_freq*100:.1f}% Hawks")
    print(
        f"   Actual Result: {sim.state.resources['hawks']:.1f}% Hawks "
        f"({'✅ Match!' if abs(sim.state.resources['hawks'] - ess_hawk_freq*100) < 5 else '⚠️  Close'})"
    )

    print("\n" + "=" * 70)
    print("✅ Evolutionary Game Theory Demo Complete!")
    print("=" * 70)

    print("\n💡 Key Insights:")
    print("   • Population evolves toward Evolutionary Stable Strategy (ESS)")
    print("   • Replicator dynamics: fitness determines reproduction")
    print("   • Mixed strategy equilibrium emerges naturally")
    print("   • Complex formulas model frequency-dependent selection")
    print("   • When C > V, both strategies coexist at equilibrium")


if __name__ == "__main__":
    main()
