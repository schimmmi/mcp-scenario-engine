"""Persistence layer for simulations."""

import json
import os
from pathlib import Path
from typing import Any

from .dynamic_rules import DynamicRule
from .models import SimulationState
from .simulation import SimulationEngine


class SimulationPersistence:
    """Handles saving and loading simulations to/from disk."""

    def __init__(self, storage_dir: str | Path | None = None):
        """Initialize persistence layer."""
        if storage_dir is None:
            # Use user's home directory for writable storage
            home = Path.home()
            storage_dir = home / ".mcp-scenario-engine" / "simulations"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_simulation(
        self, name: str, engine: SimulationEngine, description: str = ""
    ) -> Path:
        """
        Save a simulation to disk.

        Args:
            name: Name/ID for the simulation
            engine: SimulationEngine to save
            description: Optional description

        Returns:
            Path to saved file
        """
        # Serialize state
        state_dict = engine.state.model_dump(mode="json")

        # Serialize rules
        rules_data = []
        for rule in engine.world_rule_engine.rules:
            if hasattr(rule, "to_dict"):
                rules_data.append(rule.to_dict())
            else:
                # Fallback for non-dynamic rules
                rules_data.append(
                    {
                        "rule_id": rule.rule_id,
                        "type": type(rule).__name__,
                        "note": "Cannot serialize this rule type fully",
                    }
                )

        # Serialize constraints
        constraints_data = []
        for constraint in engine.constraint_engine.constraints:
            constraints_data.append(
                {
                    "constraint_id": constraint.constraint_id,
                    "type": type(constraint).__name__,
                }
            )

        # Serialize history
        history_data = [event.model_dump(mode="json") for event in engine.history]

        # Create save data
        save_data = {
            "name": name,
            "description": description,
            "state": state_dict,
            "rules": rules_data,
            "constraints": constraints_data,
            "history": history_data,
            "seed": engine.state.seed,
        }

        # Write to file
        file_path = self.storage_dir / f"{name}.json"
        with open(file_path, "w") as f:
            json.dump(save_data, f, indent=2, default=str)

        return file_path

    def load_simulation(self, name: str) -> SimulationEngine:
        """
        Load a simulation from disk.

        Args:
            name: Name/ID of the simulation

        Returns:
            Loaded SimulationEngine

        Raises:
            FileNotFoundError: If simulation doesn't exist
        """
        file_path = self.storage_dir / f"{name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Simulation '{name}' not found")

        with open(file_path, "r") as f:
            save_data = json.load(f)

        # Restore state
        state = SimulationState(**save_data["state"])

        # Create engine
        engine = SimulationEngine(initial_state=state, seed=save_data.get("seed"))

        # Restore rules (only DynamicRules for now)
        for rule_data in save_data.get("rules", []):
            if rule_data.get("type") != "Cannot serialize this rule type fully":
                rule = DynamicRule(
                    rule_id=rule_data["rule_id"],
                    condition=rule_data["condition"],
                    actions=rule_data["actions"],
                    priority=rule_data.get("priority", 0),
                    description=rule_data.get("description", ""),
                )
                engine.world_rule_engine.add_rule(rule)

        # Note: Constraints are not restored (would need constraint registry)
        # History is embedded in state, but we could restore it if needed

        return engine

    def list_simulations(self) -> list[dict[str, Any]]:
        """
        List all saved simulations.

        Returns:
            List of simulation metadata
        """
        simulations = []

        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                simulations.append(
                    {
                        "name": data.get("name", file_path.stem),
                        "description": data.get("description", ""),
                        "time": data.get("state", {}).get("time", 0),
                        "seed": data.get("seed"),
                        "created_at": data.get("state", {}).get("created_at"),
                        "updated_at": data.get("state", {}).get("updated_at"),
                        "rule_count": len(data.get("rules", [])),
                        "file": str(file_path),
                    }
                )
            except Exception:
                # Skip corrupted files
                continue

        return sorted(simulations, key=lambda x: x.get("updated_at", ""), reverse=True)

    def delete_simulation(self, name: str) -> bool:
        """
        Delete a saved simulation.

        Args:
            name: Name/ID of the simulation

        Returns:
            True if deleted, False if not found
        """
        file_path = self.storage_dir / f"{name}.json"

        if file_path.exists():
            file_path.unlink()
            return True

        return False

    def simulation_exists(self, name: str) -> bool:
        """Check if a simulation exists."""
        file_path = self.storage_dir / f"{name}.json"
        return file_path.exists()

    def get_simulation_info(self, name: str) -> dict[str, Any] | None:
        """Get metadata about a simulation without loading it."""
        file_path = self.storage_dir / f"{name}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            return {
                "name": data.get("name", name),
                "description": data.get("description", ""),
                "time": data.get("state", {}).get("time", 0),
                "seed": data.get("seed"),
                "created_at": data.get("state", {}).get("created_at"),
                "updated_at": data.get("state", {}).get("updated_at"),
                "rule_count": len(data.get("rules", [])),
                "constraint_count": len(data.get("constraints", [])),
                "history_count": len(data.get("history", [])),
            }
        except Exception:
            return None
