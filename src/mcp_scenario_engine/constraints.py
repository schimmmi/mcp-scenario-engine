"""Constraint validation engine."""

from typing import Protocol

from .models import ConstraintViolation, SimulationState


class Constraint(Protocol):
    """Protocol for constraint validators."""

    constraint_id: str

    def validate(self, state: SimulationState) -> ConstraintViolation | None:
        """Validate state against constraint. Returns violation if constraint is broken."""
        ...


class NonNegativeResourceConstraint:
    """Ensures resources cannot go negative."""

    def __init__(self, resource_name: str) -> None:
        self.constraint_id = f"non_negative_resource_{resource_name}"
        self.resource_name = resource_name

    def validate(self, state: SimulationState) -> ConstraintViolation | None:
        """Check if resource is non-negative."""
        value = state.resources.get(self.resource_name, 0.0)
        if value < 0:
            return ConstraintViolation(
                constraint_id=self.constraint_id,
                message=f"Resource '{self.resource_name}' cannot be negative (got {value})",
                context={"resource": self.resource_name, "value": value},
            )
        return None


class MaxResourceConstraint:
    """Ensures resources don't exceed maximum."""

    def __init__(self, resource_name: str, max_value: float) -> None:
        self.constraint_id = f"max_resource_{resource_name}"
        self.resource_name = resource_name
        self.max_value = max_value

    def validate(self, state: SimulationState) -> ConstraintViolation | None:
        """Check if resource is below maximum."""
        value = state.resources.get(self.resource_name, 0.0)
        if value > self.max_value:
            return ConstraintViolation(
                constraint_id=self.constraint_id,
                message=f"Resource '{self.resource_name}' exceeds maximum {self.max_value} (got {value})",
                context={
                    "resource": self.resource_name,
                    "value": value,
                    "max_value": self.max_value,
                },
            )
        return None


class TimeMonotonicConstraint:
    """Ensures time only moves forward."""

    constraint_id = "time_monotonic"

    def __init__(self, previous_time: int | None = None) -> None:
        self.previous_time = previous_time

    def validate(self, state: SimulationState) -> ConstraintViolation | None:
        """Check if time is monotonically increasing."""
        if self.previous_time is not None and state.time < self.previous_time:
            return ConstraintViolation(
                constraint_id=self.constraint_id,
                message=f"Time cannot go backwards (was {self.previous_time}, now {state.time})",
                context={"previous": self.previous_time, "current": state.time},
            )
        return None


class ConstraintEngine:
    """Validates state against defined constraints."""

    def __init__(self) -> None:
        self.constraints: list[Constraint] = []

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the engine."""
        self.constraints.append(constraint)

    def validate(self, state: SimulationState) -> list[ConstraintViolation]:
        """Validate state against all constraints."""
        violations: list[ConstraintViolation] = []
        for constraint in self.constraints:
            violation = constraint.validate(state)
            if violation:
                violations.append(violation)
        return violations

    def get_constraint_ids(self) -> list[str]:
        """Get list of all constraint IDs."""
        return [c.constraint_id for c in self.constraints]
