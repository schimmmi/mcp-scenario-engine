"""Tests for dynamic rules and complex formulas."""

import pytest

from mcp_scenario_engine.dynamic_rules import DynamicRule
from mcp_scenario_engine.models import SimulationState


class TestBasicFormulas:
    """Test basic arithmetic operations in formulas."""

    def test_simple_addition(self):
        """Test addition of multiple values."""
        state = SimulationState(resources={"a": 10.0, "b": 20.0})

        rule = DynamicRule(
            rule_id="test_add",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_resource",
                    "resource": "result",
                    "value": {
                        "type": "add",
                        "values": [
                            {"type": "resource", "name": "a"},
                            {"type": "resource", "name": "b"},
                            {"type": "value", "value": 5},
                        ],
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.resources["result"] == 35.0

    def test_subtraction(self):
        """Test subtraction operation."""
        state = SimulationState(metrics={"balance": 100.0, "cost": 30.0})

        rule = DynamicRule(
            rule_id="test_subtract",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "remaining",
                    "value": {
                        "type": "subtract",
                        "left": {"type": "metric", "name": "balance"},
                        "right": {"type": "metric", "name": "cost"},
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.metrics["remaining"] == 70.0

    def test_multiplication(self):
        """Test multiplication of multiple values."""
        state = SimulationState(metrics={"price": 10.0, "quantity": 5.0, "tax": 1.2})

        rule = DynamicRule(
            rule_id="test_multiply",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "total",
                    "value": {
                        "type": "multiply",
                        "values": [
                            {"type": "metric", "name": "price"},
                            {"type": "metric", "name": "quantity"},
                            {"type": "metric", "name": "tax"},
                        ],
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.metrics["total"] == 60.0  # 10 * 5 * 1.2

    def test_division(self):
        """Test division operation."""
        state = SimulationState(metrics={"total": 100.0, "count": 4.0})

        rule = DynamicRule(
            rule_id="test_divide",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "average",
                    "value": {
                        "type": "divide",
                        "numerator": {"type": "metric", "name": "total"},
                        "denominator": {"type": "metric", "name": "count"},
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.metrics["average"] == 25.0

    def test_division_by_zero_raises_error(self):
        """Test that division by zero raises ValueError."""
        state = SimulationState(metrics={"total": 100.0})

        rule = DynamicRule(
            rule_id="test_divide_zero",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "result",
                    "value": {
                        "type": "divide",
                        "numerator": {"type": "metric", "name": "total"},
                        "denominator": {"type": "value", "value": 0},
                    },
                }
            ],
        )

        with pytest.raises(ValueError, match="Division by zero"):
            rule.apply(state)


class TestNestedFormulas:
    """Test nested and complex formulas."""

    def test_nested_operations(self):
        """Test formula with nested operations: (a + b) * c."""
        state = SimulationState(resources={"a": 5.0, "b": 10.0, "c": 2.0})

        rule = DynamicRule(
            rule_id="test_nested",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_resource",
                    "resource": "result",
                    "value": {
                        "type": "multiply",
                        "values": [
                            {
                                "type": "add",
                                "values": [
                                    {"type": "resource", "name": "a"},
                                    {"type": "resource", "name": "b"},
                                ],
                            },
                            {"type": "resource", "name": "c"},
                        ],
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.resources["result"] == 30.0  # (5 + 10) * 2

    def test_complex_formula(self):
        """Test complex formula: (a / b) * c + d."""
        state = SimulationState(
            metrics={"a": 100.0, "b": 4.0, "c": 3.0, "d": 10.0}
        )

        rule = DynamicRule(
            rule_id="test_complex",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "result",
                    "value": {
                        "type": "add",
                        "values": [
                            {
                                "type": "multiply",
                                "values": [
                                    {
                                        "type": "divide",
                                        "numerator": {"type": "metric", "name": "a"},
                                        "denominator": {"type": "metric", "name": "b"},
                                    },
                                    {"type": "metric", "name": "c"},
                                ],
                            },
                            {"type": "metric", "name": "d"},
                        ],
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.metrics["result"] == 85.0  # (100 / 4) * 3 + 10

    def test_deeply_nested_formula(self):
        """Test deeply nested formula: ((a - b) * c) / (d + e)."""
        state = SimulationState(
            resources={"a": 20.0, "b": 5.0, "c": 4.0, "d": 10.0, "e": 20.0}
        )

        rule = DynamicRule(
            rule_id="test_deep_nested",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_resource",
                    "resource": "result",
                    "value": {
                        "type": "divide",
                        "numerator": {
                            "type": "multiply",
                            "values": [
                                {
                                    "type": "subtract",
                                    "left": {"type": "resource", "name": "a"},
                                    "right": {"type": "resource", "name": "b"},
                                },
                                {"type": "resource", "name": "c"},
                            ],
                        },
                        "denominator": {
                            "type": "add",
                            "values": [
                                {"type": "resource", "name": "d"},
                                {"type": "resource", "name": "e"},
                            ],
                        },
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.resources["result"] == 2.0  # ((20 - 5) * 4) / (10 + 20)


class TestValueSources:
    """Test different value sources in formulas."""

    def test_resource_references(self):
        """Test accessing resource values."""
        state = SimulationState(resources={"cpu": 75.0, "memory": 80.0})

        rule = DynamicRule(
            rule_id="test_resources",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "avg_usage",
                    "value": {
                        "type": "divide",
                        "numerator": {
                            "type": "add",
                            "values": [
                                {"type": "resource", "name": "cpu"},
                                {"type": "resource", "name": "memory"},
                            ],
                        },
                        "denominator": {"type": "value", "value": 2},
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.metrics["avg_usage"] == 77.5

    def test_metric_references(self):
        """Test accessing metric values."""
        state = SimulationState(metrics={"score1": 90.0, "score2": 85.0})

        rule = DynamicRule(
            rule_id="test_metrics",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "total_score",
                    "value": {
                        "type": "add",
                        "values": [
                            {"type": "metric", "name": "score1"},
                            {"type": "metric", "name": "score2"},
                        ],
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.metrics["total_score"] == 175.0

    def test_time_reference(self):
        """Test accessing simulation time."""
        state = SimulationState(time=10)

        rule = DynamicRule(
            rule_id="test_time",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "days_passed",
                    "value": {
                        "type": "multiply",
                        "values": [{"type": "time"}, {"type": "value", "value": 7}],
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.metrics["days_passed"] == 70.0

    def test_mixed_sources(self):
        """Test formula with mixed value sources."""
        state = SimulationState(
            time=5, resources={"base": 100.0}, metrics={"multiplier": 1.5}
        )

        rule = DynamicRule(
            rule_id="test_mixed",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_resource",
                    "resource": "result",
                    "value": {
                        "type": "multiply",
                        "values": [
                            {"type": "resource", "name": "base"},
                            {"type": "metric", "name": "multiplier"},
                            {"type": "time"},
                        ],
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.resources["result"] == 750.0  # 100 * 1.5 * 5


class TestRealWorldFormulas:
    """Test formulas from real-world examples."""

    def test_weight_loss_formula(self):
        """Test body fat loss calculation: (deficit / 7700) * 7 * compliance."""
        state = SimulationState(
            metrics={"calorie_deficit": 400.0, "compliance": 0.85},
            resources={"fat_mass": 20.0},
        )

        rule = DynamicRule(
            rule_id="fat_loss",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_resource",
                    "resource": "fat_mass",
                    "value": {
                        "type": "subtract",
                        "left": {"type": "resource", "name": "fat_mass"},
                        "right": {
                            "type": "multiply",
                            "values": [
                                {
                                    "type": "divide",
                                    "numerator": {
                                        "type": "metric",
                                        "name": "calorie_deficit",
                                    },
                                    "denominator": {"type": "value", "value": 7700},
                                },
                                {"type": "value", "value": 7},
                                {"type": "metric", "name": "compliance"},
                            ],
                        },
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        # (400 / 7700) * 7 * 0.85 ≈ 0.3091
        expected = 20.0 - ((400 / 7700) * 7 * 0.85)
        assert abs(new_state.resources["fat_mass"] - expected) < 0.001

    def test_hawk_dove_fitness(self):
        """Test evolutionary game theory fitness calculation."""
        state = SimulationState(
            metrics={
                "hawk_frequency": 0.5,
                "dove_frequency": 0.5,
                "resource_value": 50.0,
                "fighting_cost": 100.0,
            }
        )

        # E(Hawk) = p_hawk * (V-C)/2 + p_dove * V
        rule = DynamicRule(
            rule_id="hawk_fitness",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "hawk_fitness",
                    "value": {
                        "type": "add",
                        "values": [
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
                                                "name": "fighting_cost",
                                            },
                                        },
                                        "denominator": {"type": "value", "value": 2},
                                    },
                                ],
                            },
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
        )

        new_state = rule.apply(state)
        # 0.5 * ((50 - 100) / 2) + 0.5 * 50 = 0.5 * (-25) + 25 = -12.5 + 25 = 12.5
        assert new_state.metrics["hawk_fitness"] == 12.5


class TestConditionsWithFormulas:
    """Test rule conditions using formula results."""

    def test_condition_with_calculated_value(self):
        """Test condition that compares calculated values."""
        state = SimulationState(resources={"a": 10.0, "b": 5.0, "c": 0.0})

        rule = DynamicRule(
            rule_id="conditional_calc",
            condition={
                "type": "comparison",
                "left": {"type": "resource", "name": "a"},
                "operator": ">",
                "right": {"type": "resource", "name": "b"},
            },
            actions=[
                {
                    "type": "set_resource",
                    "resource": "c",
                    "value": {
                        "type": "subtract",
                        "left": {"type": "resource", "name": "a"},
                        "right": {"type": "resource", "name": "b"},
                    },
                }
            ],
        )

        # Condition should be true (10 > 5)
        assert rule.should_apply(state)

        new_state = rule.apply(state)
        assert new_state.resources["c"] == 5.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_resource_defaults_to_zero(self):
        """Test that missing resources default to 0."""
        state = SimulationState(resources={"a": 10.0})

        rule = DynamicRule(
            rule_id="test_missing",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_resource",
                    "resource": "result",
                    "value": {
                        "type": "add",
                        "values": [
                            {"type": "resource", "name": "a"},
                            {"type": "resource", "name": "b"},  # Missing
                        ],
                    },
                }
            ],
        )

        new_state = rule.apply(state)
        assert new_state.resources["result"] == 10.0

    def test_unknown_value_type_raises_error(self):
        """Test that unknown value type raises error."""
        state = SimulationState()

        rule = DynamicRule(
            rule_id="test_unknown",
            condition={"type": "always"},
            actions=[
                {
                    "type": "set_metric",
                    "metric": "result",
                    "value": {"type": "unknown_operation", "value": 42},
                }
            ],
        )

        with pytest.raises(ValueError, match="Unknown value type"):
            rule.apply(state)
