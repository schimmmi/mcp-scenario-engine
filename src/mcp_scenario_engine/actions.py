"""Action definitions for simulation."""

import random
from typing import Any

from .models import SimulationState


class Action:
    """Base class for simulation actions."""

    name: str
    description: str

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Execute action and return new state and reason."""
        raise NotImplementedError


class StepAction(Action):
    """Advance simulation by one time step."""

    name = "step"
    description = "Advance simulation time by one step"

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Advance time by 1."""
        new_state = state.model_copy()
        new_state.time += 1
        return new_state, f"Advanced simulation time from {state.time} to {new_state.time}"


class SetResourceAction(Action):
    """Set a resource to a specific value."""

    name = "set_resource"
    description = "Set a resource to a specific value"

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Set resource value."""
        resource_name = params.get("resource")
        value = params.get("value")

        if not resource_name:
            raise ValueError("Parameter 'resource' is required")
        if value is None:
            raise ValueError("Parameter 'value' is required")

        new_state = state.model_copy()
        old_value = new_state.resources.get(resource_name, 0.0)
        new_state.resources[resource_name] = float(value)

        return (
            new_state,
            f"Set resource '{resource_name}' from {old_value} to {value}",
        )


class AdjustResourceAction(Action):
    """Adjust a resource by a delta amount."""

    name = "adjust_resource"
    description = "Adjust a resource by adding/subtracting a value"

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Adjust resource value."""
        resource_name = params.get("resource")
        delta = params.get("delta")

        if not resource_name:
            raise ValueError("Parameter 'resource' is required")
        if delta is None:
            raise ValueError("Parameter 'delta' is required")

        new_state = state.model_copy()
        old_value = new_state.resources.get(resource_name, 0.0)
        new_value = old_value + float(delta)
        new_state.resources[resource_name] = new_value

        return (
            new_state,
            f"Adjusted resource '{resource_name}' by {delta} (from {old_value} to {new_value})",
        )


class SetMetricAction(Action):
    """Set a metric to a specific value."""

    name = "set_metric"
    description = "Set a metric to a specific value"

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Set metric value."""
        metric_name = params.get("metric")
        value = params.get("value")

        if not metric_name:
            raise ValueError("Parameter 'metric' is required")
        if value is None:
            raise ValueError("Parameter 'value' is required")

        new_state = state.model_copy()
        old_value = new_state.metrics.get(metric_name, 0.0)
        new_state.metrics[metric_name] = float(value)

        return (
            new_state,
            f"Set metric '{metric_name}' from {old_value} to {value}",
        )


class SetFlagAction(Action):
    """Set a boolean flag."""

    name = "set_flag"
    description = "Set a boolean flag"

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Set flag value."""
        flag_name = params.get("flag")
        value = params.get("value")

        if not flag_name:
            raise ValueError("Parameter 'flag' is required")
        if value is None:
            raise ValueError("Parameter 'value' is required")

        new_state = state.model_copy()
        old_value = new_state.flags.get(flag_name, False)
        new_state.flags[flag_name] = bool(value)

        return (
            new_state,
            f"Set flag '{flag_name}' from {old_value} to {value}",
        )


class AddEntityAction(Action):
    """Add or update an entity."""

    name = "add_entity"
    description = "Add or update an entity in the simulation"

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Add/update entity."""
        entity_id = params.get("entity_id")
        entity_data = params.get("data")

        if not entity_id:
            raise ValueError("Parameter 'entity_id' is required")
        if entity_data is None:
            raise ValueError("Parameter 'data' is required")

        new_state = state.model_copy()
        existed = entity_id in new_state.entities
        new_state.entities[entity_id] = entity_data

        action = "Updated" if existed else "Added"
        return new_state, f"{action} entity '{entity_id}'"


class RemoveEntityAction(Action):
    """Remove an entity."""

    name = "remove_entity"
    description = "Remove an entity from the simulation"

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Remove entity."""
        entity_id = params.get("entity_id")

        if not entity_id:
            raise ValueError("Parameter 'entity_id' is required")

        new_state = state.model_copy()
        if entity_id in new_state.entities:
            del new_state.entities[entity_id]
            return new_state, f"Removed entity '{entity_id}'"
        else:
            return new_state, f"Entity '{entity_id}' not found (no change)"


class SimulateLoadAction(Action):
    """Simulate a load scenario with random variation."""

    name = "simulate_load"
    description = "Simulate a load scenario affecting multiple resources"

    def execute(
        self, state: SimulationState, params: dict[str, Any], rng: random.Random
    ) -> tuple[SimulationState, str]:
        """Simulate load with random variation."""
        load_factor = params.get("load_factor", 1.0)
        variance = params.get("variance", 0.1)

        new_state = state.model_copy()

        # Apply random variation to load
        actual_load = load_factor * (1 + rng.uniform(-variance, variance))

        # Affect CPU and memory resources
        cpu_delta = -10 * actual_load
        memory_delta = -50 * actual_load

        new_state.resources["cpu_available"] = (
            new_state.resources.get("cpu_available", 100.0) + cpu_delta
        )
        new_state.resources["memory_available"] = (
            new_state.resources.get("memory_available", 1000.0) + memory_delta
        )

        # Update metrics
        new_state.metrics["load"] = actual_load
        new_state.time += 1

        return (
            new_state,
            f"Applied load factor {load_factor:.2f} (actual: {actual_load:.2f}), "
            f"CPU: {cpu_delta:.2f}, Memory: {memory_delta:.2f}",
        )


# Action registry
ACTION_REGISTRY: dict[str, type[Action]] = {
    "step": StepAction,
    "set_resource": SetResourceAction,
    "adjust_resource": AdjustResourceAction,
    "set_metric": SetMetricAction,
    "set_flag": SetFlagAction,
    "add_entity": AddEntityAction,
    "remove_entity": RemoveEntityAction,
    "simulate_load": SimulateLoadAction,
}
