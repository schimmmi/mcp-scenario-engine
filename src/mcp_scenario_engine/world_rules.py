"""World rules and domain logic for simulations."""

from typing import Protocol

from .models import SimulationState


class WorldRule(Protocol):
    """Protocol for world rules that apply automatic state transitions."""

    rule_id: str

    def apply(self, state: SimulationState) -> SimulationState:
        """Apply rule and return modified state."""
        ...

    def should_apply(self, state: SimulationState) -> bool:
        """Check if rule should be applied to current state."""
        ...


class DevOpsLoadRule:
    """DevOps rule: High CPU increases error rate."""

    rule_id = "devops_high_cpu_errors"

    def __init__(self, cpu_threshold: float = 80.0, error_increment: float = 0.01) -> None:
        self.cpu_threshold = cpu_threshold
        self.error_increment = error_increment

    def should_apply(self, state: SimulationState) -> bool:
        """Apply when CPU exceeds threshold."""
        cpu = state.resources.get("cpu", 0.0)
        return cpu > self.cpu_threshold

    def apply(self, state: SimulationState) -> SimulationState:
        """Increase error rate when CPU is high."""
        new_state = state.model_copy()
        current_error_rate = new_state.metrics.get("error_rate", 0.0)
        new_state.metrics["error_rate"] = current_error_rate + self.error_increment
        return new_state


class DevOpsBurnoutRule:
    """DevOps rule: High CPU for long time causes burnout."""

    rule_id = "devops_burnout"

    def __init__(
        self, cpu_threshold: float = 80.0, duration_threshold: int = 3
    ) -> None:
        self.cpu_threshold = cpu_threshold
        self.duration_threshold = duration_threshold

    def should_apply(self, state: SimulationState) -> bool:
        """Apply when CPU has been high for duration."""
        cpu = state.resources.get("cpu", 0.0)
        high_cpu_duration = state.metadata.get("high_cpu_duration", 0)
        return cpu > self.cpu_threshold and high_cpu_duration >= self.duration_threshold

    def apply(self, state: SimulationState) -> SimulationState:
        """Set burnout flag when threshold reached."""
        new_state = state.model_copy()
        new_state.flags["burnout"] = True
        return new_state


class DevOpsCPUTracker:
    """Track how long CPU has been high."""

    rule_id = "devops_cpu_tracker"

    def __init__(self, cpu_threshold: float = 80.0) -> None:
        self.cpu_threshold = cpu_threshold

    def should_apply(self, state: SimulationState) -> bool:
        """Always apply to track CPU."""
        return True

    def apply(self, state: SimulationState) -> SimulationState:
        """Update high CPU duration counter."""
        new_state = state.model_copy()
        cpu = new_state.resources.get("cpu", 0.0)

        if cpu > self.cpu_threshold:
            current = new_state.metadata.get("high_cpu_duration", 0)
            new_state.metadata["high_cpu_duration"] = current + 1
        else:
            new_state.metadata["high_cpu_duration"] = 0

        return new_state


class DevOpsScaleUpRule:
    """DevOps rule: Auto-scale when CPU is very high."""

    rule_id = "devops_auto_scale"

    def __init__(
        self, cpu_threshold: float = 90.0, max_servers: int = 10
    ) -> None:
        self.cpu_threshold = cpu_threshold
        self.max_servers = max_servers

    def should_apply(self, state: SimulationState) -> bool:
        """Apply when CPU is critical and we can scale."""
        cpu = state.resources.get("cpu", 0.0)
        servers = state.resources.get("servers", 1)
        return cpu > self.cpu_threshold and servers < self.max_servers

    def apply(self, state: SimulationState) -> SimulationState:
        """Add a server and reduce CPU proportionally."""
        new_state = state.model_copy()
        current_servers = new_state.resources.get("servers", 1)
        current_cpu = new_state.resources.get("cpu", 0.0)

        # Add server
        new_servers = current_servers + 1
        new_state.resources["servers"] = new_servers

        # Redistribute CPU load
        total_capacity_before = current_servers * 40
        total_capacity_after = new_servers * 40
        load_ratio = total_capacity_before / total_capacity_after
        new_state.resources["cpu"] = current_cpu * load_ratio

        return new_state


class WorldRuleEngine:
    """Engine that applies world rules during simulation steps."""

    def __init__(self) -> None:
        self.rules: list[WorldRule] = []

    def add_rule(self, rule: WorldRule, priority: int = 0) -> None:
        """Add a world rule with optional priority (higher = runs first)."""
        self.rules.append(rule)
        # Sort by priority if rule has priority attribute
        if hasattr(rule, "priority"):
            self.rules.sort(key=lambda r: getattr(r, "priority", 0), reverse=True)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID. Returns True if removed, False if not found."""
        for i, rule in enumerate(self.rules):
            if rule.rule_id == rule_id:
                self.rules.pop(i)
                return True
        return False

    def get_rule(self, rule_id: str) -> WorldRule | None:
        """Get a rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def update_rule(self, rule_id: str, new_rule: WorldRule) -> bool:
        """Update an existing rule. Returns True if updated, False if not found."""
        for i, rule in enumerate(self.rules):
            if rule.rule_id == rule_id:
                self.rules[i] = new_rule
                return True
        return False

    def clear_rules(self) -> None:
        """Remove all rules."""
        self.rules.clear()

    def apply_rules(self, state: SimulationState) -> tuple[SimulationState, list[str]]:
        """Apply all applicable rules and return new state + applied rule IDs."""
        current_state = state
        applied_rules: list[str] = []

        for rule in self.rules:
            if rule.should_apply(current_state):
                current_state = rule.apply(current_state)
                applied_rules.append(rule.rule_id)

        return current_state, applied_rules

    def get_rule_ids(self) -> list[str]:
        """Get list of all rule IDs."""
        return [r.rule_id for r in self.rules]

    def get_rule_count(self) -> int:
        """Get number of active rules."""
        return len(self.rules)
