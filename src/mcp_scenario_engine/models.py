"""Data models for simulation state and events."""

from datetime import datetime, UTC
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of simulation events."""

    SIMULATION_CREATED = "simulation_created"
    SIMULATION_RESET = "simulation_reset"
    ACTION_APPLIED = "action_applied"
    STEP_EXECUTED = "step_executed"
    TIMELINE_FORKED = "timeline_forked"
    CONSTRAINT_VIOLATED = "constraint_violated"


class HistoryEvent(BaseModel):
    """Record of a simulation event."""

    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: EventType
    action_name: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)
    state_delta: dict[str, Any] = Field(default_factory=dict)
    constraints_checked: list[str] = Field(default_factory=list)
    constraints_violated: list[str] = Field(default_factory=list)
    reason: str | None = None


class SimulationState(BaseModel):
    """Current state of the simulation."""

    # Schema version
    schema_version: str = "v1"

    # Simulation metadata
    simulation_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    seed: int | None = None

    # Core state components
    time: int = 0  # Simulation time step
    entities: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    resources: dict[str, float] = Field(default_factory=dict)
    flags: dict[str, bool] = Field(default_factory=dict)

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    def model_copy(self, *, deep: bool = True, **kwargs: Any) -> "SimulationState":
        """Create a deep copy of the state."""
        return super().model_copy(deep=True, update=kwargs)


class ConstraintViolation(BaseModel):
    """Details about a constraint violation."""

    constraint_id: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class ActionResult(BaseModel):
    """Result of executing an action."""

    success: bool
    event_id: UUID
    state_before: SimulationState
    state_after: SimulationState
    delta: dict[str, Any]
    constraints_violated: list[ConstraintViolation] = Field(default_factory=list)
    message: str | None = None
    reason: str | None = None
