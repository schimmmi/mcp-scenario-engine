"""Dynamic rule system - define rules via JSON/dict."""

from typing import Any

from .models import SimulationState


class DynamicRule:
    """A rule defined by conditions and actions in JSON format."""

    def __init__(
        self,
        rule_id: str,
        condition: dict[str, Any],
        actions: list[dict[str, Any]],
        priority: int = 0,
        description: str = "",
    ):
        """
        Create a dynamic rule.

        Args:
            rule_id: Unique identifier for the rule
            condition: Condition dict that determines when rule applies
            actions: List of action dicts to apply when condition is met
            priority: Priority for rule execution (higher = runs first)
            description: Human-readable description

        Condition format:
        {
            "type": "comparison",
            "left": {"type": "resource", "name": "cpu"},
            "operator": ">",
            "right": {"type": "value", "value": 80}
        }

        Or logical operators:
        {
            "type": "and",
            "conditions": [...]
        }

        Action format:
        {
            "type": "set_metric",
            "metric": "error_rate",
            "value": {"type": "increment", "amount": 0.01}
        }
        {
            "type": "set_flag",
            "flag": "burnout",
            "value": true
        }
        {
            "type": "set_resource",
            "resource": "servers",
            "value": {"type": "increment", "amount": 1}
        }
        {
            "type": "set_metadata",
            "key": "high_cpu_duration",
            "value": {"type": "increment", "amount": 1}
        }
        """
        self.rule_id = rule_id
        self.condition = condition
        self.actions = actions
        self.priority = priority
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        """Convert rule to dictionary for serialization."""
        return {
            "rule_id": self.rule_id,
            "condition": self.condition,
            "actions": self.actions,
            "priority": self.priority,
            "description": self.description,
        }

    def should_apply(self, state: SimulationState) -> bool:
        """Evaluate condition against state."""
        return self._evaluate_condition(self.condition, state)

    def apply(self, state: SimulationState) -> SimulationState:
        """Apply all actions to state."""
        new_state = state.model_copy()

        for action in self.actions:
            new_state = self._apply_action(action, new_state)

        return new_state

    def _evaluate_condition(self, condition: dict[str, Any], state: SimulationState) -> bool:
        """Recursively evaluate condition."""
        cond_type = condition.get("type")

        if cond_type == "comparison":
            left_val = self._get_value(condition["left"], state)
            right_val = self._get_value(condition["right"], state)
            operator = condition["operator"]

            if operator == ">":
                return left_val > right_val
            elif operator == ">=":
                return left_val >= right_val
            elif operator == "<":
                return left_val < right_val
            elif operator == "<=":
                return left_val <= right_val
            elif operator == "==":
                return left_val == right_val
            elif operator == "!=":
                return left_val != right_val
            else:
                raise ValueError(f"Unknown operator: {operator}")

        elif cond_type == "and":
            return all(
                self._evaluate_condition(c, state) for c in condition["conditions"]
            )

        elif cond_type == "or":
            return any(
                self._evaluate_condition(c, state) for c in condition["conditions"]
            )

        elif cond_type == "not":
            return not self._evaluate_condition(condition["condition"], state)

        elif cond_type == "always":
            return True

        else:
            raise ValueError(f"Unknown condition type: {cond_type}")

    def _get_value(self, value_spec: dict[str, Any], state: SimulationState) -> Any:
        """Get value from state based on value spec."""
        val_type = value_spec.get("type")

        if val_type == "value":
            return value_spec["value"]

        elif val_type == "resource":
            return state.resources.get(value_spec["name"], 0.0)

        elif val_type == "metric":
            return state.metrics.get(value_spec["name"], 0.0)

        elif val_type == "flag":
            return state.flags.get(value_spec["name"], False)

        elif val_type == "metadata":
            return state.metadata.get(value_spec["name"], 0)

        elif val_type == "time":
            return state.time

        else:
            raise ValueError(f"Unknown value type: {val_type}")

    def _compute_value(self, value_spec: dict[str, Any] | Any, state: SimulationState) -> float:
        """
        Compute value from formula specification.

        Supports:
        - Simple values: 42 or {"type": "value", "value": 42}
        - State references: {"type": "resource", "name": "cpu"}
        - Arithmetic: {"type": "add", "values": [...]}
        - Complex formulas: nested operations
        """
        if not isinstance(value_spec, dict):
            return float(value_spec)

        val_type = value_spec.get("type")

        # Simple value
        if val_type == "value":
            return float(value_spec["value"])

        # State references
        elif val_type == "resource":
            return float(state.resources.get(value_spec["name"], 0.0))

        elif val_type == "metric":
            return float(state.metrics.get(value_spec["name"], 0.0))

        elif val_type == "time":
            return float(state.time)

        # Arithmetic operations
        elif val_type == "add":
            values = [self._compute_value(v, state) for v in value_spec["values"]]
            return sum(values)

        elif val_type == "subtract":
            left = self._compute_value(value_spec["left"], state)
            right = self._compute_value(value_spec["right"], state)
            return left - right

        elif val_type == "multiply":
            values = [self._compute_value(v, state) for v in value_spec["values"]]
            result = 1.0
            for v in values:
                result *= v
            return result

        elif val_type == "divide":
            numerator = self._compute_value(value_spec["numerator"], state)
            denominator = self._compute_value(value_spec["denominator"], state)
            if denominator == 0:
                raise ValueError("Division by zero")
            return numerator / denominator

        else:
            raise ValueError(f"Unknown value type: {val_type}")

    def _apply_action(
        self, action: dict[str, Any], state: SimulationState
    ) -> SimulationState:
        """Apply a single action to state."""
        action_type = action.get("type")

        if action_type == "set_resource":
            resource = action["resource"]
            value = self._compute_value(action["value"], state)
            state.resources[resource] = float(value)

        elif action_type == "set_metric":
            metric = action["metric"]
            value = self._compute_value(action["value"], state)
            state.metrics[metric] = float(value)

        elif action_type == "set_flag":
            flag = action["flag"]
            value = action["value"]
            state.flags[flag] = bool(value)

        elif action_type == "set_metadata":
            key = action["key"]
            value = self._compute_value(action["value"], state)
            state.metadata[key] = value

        else:
            raise ValueError(f"Unknown action type: {action_type}")

        return state
