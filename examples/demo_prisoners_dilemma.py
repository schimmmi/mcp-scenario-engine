#!/usr/bin/env python3
"""Demo: Prisoner's Dilemma - Game Theory Simulation."""

from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.dynamic_rules import DynamicRule


def main() -> None:
    """Run iterated prisoner's dilemma simulation."""
    print("=" * 70)
    print("🎮 Prisoner's Dilemma - Iterated Game Theory Simulation")
    print("=" * 70)

    # Create simulation
    sim = SimulationEngine(seed=42)

    # Initial state
    sim.state.metrics = {
        "player1_total_score": 0.0,
        "player2_total_score": 0.0,
        "player1_cooperated_last": 1.0,  # 1 = cooperate, 0 = defect
        "player2_cooperated_last": 1.0,
    }
    sim.state.resources = {
        "player1_cooperates": 1.0,  # Start with cooperation
        "player2_cooperates": 1.0,
    }
    sim.state.metadata = {
        "strategy1": "Tit-for-Tat",
        "strategy2": "Tit-for-Tat",
    }

    print("\n📊 Payoff Matrix:")
    print("   Both cooperate (C,C): (+3, +3)")
    print("   P1 defects, P2 cooperates (D,C): (+5, +0)")
    print("   P1 cooperates, P2 defects (C,D): (+0, +5)")
    print("   Both defect (D,D): (+1, +1)")

    print("\n🎯 Strategies:")
    print("   Player 1: Tit-for-Tat (copy opponent's last move)")
    print("   Player 2: Tit-for-Tat (copy opponent's last move)")

    # Rule 1: Calculate Player 1's payoff
    # Payoff = (if both_coop: 3) + (if i_defect_they_coop: 5) + (if both_defect: 1)
    p1_payoff_rule = DynamicRule(
        rule_id="player1_payoff",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_metric",
                "metric": "player1_total_score",
                "value": {
                    "type": "add",
                    "values": [
                        {"type": "metric", "name": "player1_total_score"},
                        # Both cooperate: 3 points
                        {
                            "type": "multiply",
                            "values": [
                                {"type": "resource", "name": "player1_cooperates"},
                                {"type": "resource", "name": "player2_cooperates"},
                                {"type": "value", "value": 3},
                            ],
                        },
                        # I defect, they cooperate: 5 points
                        {
                            "type": "multiply",
                            "values": [
                                {
                                    "type": "subtract",
                                    "left": {"type": "value", "value": 1},
                                    "right": {
                                        "type": "resource",
                                        "name": "player1_cooperates",
                                    },
                                },
                                {"type": "resource", "name": "player2_cooperates"},
                                {"type": "value", "value": 5},
                            ],
                        },
                        # Both defect: 1 point
                        {
                            "type": "multiply",
                            "values": [
                                {
                                    "type": "subtract",
                                    "left": {"type": "value", "value": 1},
                                    "right": {
                                        "type": "resource",
                                        "name": "player1_cooperates",
                                    },
                                },
                                {
                                    "type": "subtract",
                                    "left": {"type": "value", "value": 1},
                                    "right": {
                                        "type": "resource",
                                        "name": "player2_cooperates",
                                    },
                                },
                                {"type": "value", "value": 1},
                            ],
                        },
                    ],
                },
            }
        ],
        priority=10,
        description="Calculate Player 1's payoff based on actions",
    )

    # Rule 2: Calculate Player 2's payoff (symmetric)
    p2_payoff_rule = DynamicRule(
        rule_id="player2_payoff",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_metric",
                "metric": "player2_total_score",
                "value": {
                    "type": "add",
                    "values": [
                        {"type": "metric", "name": "player2_total_score"},
                        # Both cooperate: 3 points
                        {
                            "type": "multiply",
                            "values": [
                                {"type": "resource", "name": "player2_cooperates"},
                                {"type": "resource", "name": "player1_cooperates"},
                                {"type": "value", "value": 3},
                            ],
                        },
                        # I defect, they cooperate: 5 points
                        {
                            "type": "multiply",
                            "values": [
                                {
                                    "type": "subtract",
                                    "left": {"type": "value", "value": 1},
                                    "right": {
                                        "type": "resource",
                                        "name": "player2_cooperates",
                                    },
                                },
                                {"type": "resource", "name": "player1_cooperates"},
                                {"type": "value", "value": 5},
                            ],
                        },
                        # Both defect: 1 point
                        {
                            "type": "multiply",
                            "values": [
                                {
                                    "type": "subtract",
                                    "left": {"type": "value", "value": 1},
                                    "right": {
                                        "type": "resource",
                                        "name": "player2_cooperates",
                                    },
                                },
                                {
                                    "type": "subtract",
                                    "left": {"type": "value", "value": 1},
                                    "right": {
                                        "type": "resource",
                                        "name": "player1_cooperates",
                                    },
                                },
                                {"type": "value", "value": 1},
                            ],
                        },
                    ],
                },
            }
        ],
        priority=10,
        description="Calculate Player 2's payoff based on actions",
    )

    # Rule 3: Store last moves
    store_last_moves_rule = DynamicRule(
        rule_id="store_last_moves",
        condition={"type": "always"},
        actions=[
            {
                "type": "set_metric",
                "metric": "player1_cooperated_last",
                "value": {"type": "resource", "name": "player1_cooperates"},
            },
            {
                "type": "set_metric",
                "metric": "player2_cooperated_last",
                "value": {"type": "resource", "name": "player2_cooperates"},
            },
        ],
        priority=5,
        description="Store last round's moves for next iteration",
    )

    # Rule 4: Tit-for-Tat strategy for Player 1
    # Copy opponent's last move (only after round 1)
    tit_for_tat_p1_rule = DynamicRule(
        rule_id="tit_for_tat_p1",
        condition={
            "type": "comparison",
            "left": {"type": "time"},
            "operator": ">",
            "right": {"type": "value", "value": 0},
        },
        actions=[
            {
                "type": "set_resource",
                "resource": "player1_cooperates",
                "value": {"type": "metric", "name": "player2_cooperated_last"},
            }
        ],
        priority=1,
        description="Player 1 uses Tit-for-Tat: copy opponent's last move",
    )

    # Rule 5: Tit-for-Tat strategy for Player 2
    tit_for_tat_p2_rule = DynamicRule(
        rule_id="tit_for_tat_p2",
        condition={
            "type": "comparison",
            "left": {"type": "time"},
            "operator": ">",
            "right": {"type": "value", "value": 0},
        },
        actions=[
            {
                "type": "set_resource",
                "resource": "player2_cooperates",
                "value": {"type": "metric", "name": "player1_cooperated_last"},
            }
        ],
        priority=1,
        description="Player 2 uses Tit-for-Tat: copy opponent's last move",
    )

    # Add rules
    sim.world_rule_engine.add_rule(p1_payoff_rule, priority=10)
    sim.world_rule_engine.add_rule(p2_payoff_rule, priority=10)
    sim.world_rule_engine.add_rule(store_last_moves_rule, priority=5)
    sim.world_rule_engine.add_rule(tit_for_tat_p1_rule, priority=1)
    sim.world_rule_engine.add_rule(tit_for_tat_p2_rule, priority=1)

    print("\n🎲 Simulating 10 Rounds...")
    print("-" * 70)
    print(f"{'Round':<7} {'P1 Move':<10} {'P2 Move':<10} {'P1 Score':<12} {'P2 Score':<12}")
    print("-" * 70)

    for round_num in range(10):
        # Get current moves (before step)
        p1_move = "Cooperate" if sim.state.resources["player1_cooperates"] == 1 else "Defect"
        p2_move = "Cooperate" if sim.state.resources["player2_cooperates"] == 1 else "Defect"

        # Apply step (rules will calculate payoffs and update strategies)
        sim.apply_action("step", {})

        # Show results
        print(
            f"{round_num+1:<7} {p1_move:<10} {p2_move:<10} "
            f"{sim.state.metrics['player1_total_score']:<12.0f} "
            f"{sim.state.metrics['player2_total_score']:<12.0f}"
        )

    print("-" * 70)
    print(f"\n📈 Final Scores:")
    print(f"   Player 1 (Tit-for-Tat): {sim.state.metrics['player1_total_score']:.0f}")
    print(f"   Player 2 (Tit-for-Tat): {sim.state.metrics['player2_total_score']:.0f}")

    # Now test against "Always Defect" strategy
    print("\n" + "=" * 70)
    print("🔄 New Game: Tit-for-Tat vs Always Defect")
    print("=" * 70)

    sim2 = SimulationEngine(seed=42)
    sim2.state.metrics = {
        "player1_total_score": 0.0,
        "player2_total_score": 0.0,
        "player1_cooperated_last": 1.0,
        "player2_cooperated_last": 0.0,  # Always defect
    }
    sim2.state.resources = {
        "player1_cooperates": 1.0,
        "player2_cooperates": 0.0,  # Always defect
    }

    # Add same rules but modify P2 strategy
    sim2.world_rule_engine.add_rule(p1_payoff_rule, priority=10)
    sim2.world_rule_engine.add_rule(p2_payoff_rule, priority=10)
    sim2.world_rule_engine.add_rule(store_last_moves_rule, priority=5)
    sim2.world_rule_engine.add_rule(tit_for_tat_p1_rule, priority=1)

    # Player 2 always defects (no strategy rule needed - stays at 0)

    print("\n🎯 Strategies:")
    print("   Player 1: Tit-for-Tat")
    print("   Player 2: Always Defect")

    print("\n🎲 Simulating 10 Rounds...")
    print("-" * 70)
    print(f"{'Round':<7} {'P1 Move':<10} {'P2 Move':<10} {'P1 Score':<12} {'P2 Score':<12}")
    print("-" * 70)

    for round_num in range(10):
        p1_move = "Cooperate" if sim2.state.resources["player1_cooperates"] == 1 else "Defect"
        p2_move = "Cooperate" if sim2.state.resources["player2_cooperates"] == 1 else "Defect"

        sim2.apply_action("step", {})

        print(
            f"{round_num+1:<7} {p1_move:<10} {p2_move:<10} "
            f"{sim2.state.metrics['player1_total_score']:<12.0f} "
            f"{sim2.state.metrics['player2_total_score']:<12.0f}"
        )

    print("-" * 70)
    print(f"\n📈 Final Scores:")
    print(f"   Player 1 (Tit-for-Tat): {sim2.state.metrics['player1_total_score']:.0f}")
    print(f"   Player 2 (Always Defect): {sim2.state.metrics['player2_total_score']:.0f}")

    print("\n" + "=" * 70)
    print("✅ Game Theory Demo Complete!")
    print("=" * 70)

    print("\n💡 Key Insights:")
    print("   • Tit-for-Tat vs Tit-for-Tat: Mutual cooperation (30, 30)")
    print("   • Tit-for-Tat vs Always Defect: Retaliation prevents exploitation")
    print("   • Formulas calculate payoffs based on complex action combinations")
    print("   • Strategies can be changed by modifying rules via MCP")


if __name__ == "__main__":
    main()
