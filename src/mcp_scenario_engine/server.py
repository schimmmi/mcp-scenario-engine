"""MCP Server implementation for scenario engine."""

import json
from typing import Any

import structlog
from mcp.server import Server
from mcp.types import TextContent, Tool

from .constraints import MaxResourceConstraint, NonNegativeResourceConstraint
from .dynamic_rules import DynamicRule
from .models import SimulationState
from .persistence import SimulationPersistence
from .simulation import SimulationEngine

logger = structlog.get_logger()

# Global simulation instance and persistence
sim: SimulationEngine | None = None
persistence = SimulationPersistence()


def get_simulation() -> SimulationEngine:
    """Get or create global simulation instance."""
    global sim
    if sim is None:
        # Create default simulation with common constraints
        initial_state = SimulationState(
            resources={
                "cpu_available": 100.0,
                "memory_available": 1000.0,
                "disk_space": 5000.0,
            },
            metrics={},
            flags={"system_healthy": True},
        )
        sim = SimulationEngine(initial_state=initial_state, seed=42)

        # Add default constraints
        sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("cpu_available"))
        sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("memory_available"))
        sim.constraint_engine.add_constraint(NonNegativeResourceConstraint("disk_space"))
        sim.constraint_engine.add_constraint(MaxResourceConstraint("cpu_available", 100.0))

    return sim


# Create MCP server
app = Server("scenario-engine")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="get_state",
            description="Get the current simulation state",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="apply_action",
            description=(
                "Apply an action to the simulation. "
                "Available actions: step, set_resource, adjust_resource, set_metric, "
                "set_flag, add_entity, remove_entity, simulate_load"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action name to execute",
                    },
                    "params": {
                        "type": "object",
                        "description": "Action parameters",
                        "additionalProperties": True,
                    },
                },
                "required": ["action", "params"],
            },
        ),
        Tool(
            name="reset_simulation",
            description="Reset simulation to initial state",
            inputSchema={
                "type": "object",
                "properties": {
                    "seed": {
                        "type": "number",
                        "description": "Optional random seed for deterministic execution",
                    },
                },
            },
        ),
        Tool(
            name="fork_timeline",
            description="Create a fork of the current simulation timeline",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_history",
            description="Get simulation event history",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of events to return (most recent)",
                    },
                },
            },
        ),
        Tool(
            name="get_schema",
            description="Get the state schema definition",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="add_world_rule",
            description=(
                "Add a dynamic world rule that automatically applies during simulation steps. "
                "Rules are defined by conditions and actions in JSON format."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "description": "Unique identifier for this rule",
                    },
                    "condition": {
                        "type": "object",
                        "description": (
                            "Condition that determines when rule applies. "
                            "Example: {type: 'comparison', left: {type: 'resource', name: 'cpu'}, "
                            "operator: '>', right: {type: 'value', value: 80}}"
                        ),
                        "additionalProperties": True,
                    },
                    "actions": {
                        "type": "array",
                        "description": (
                            "Actions to apply when condition is met. "
                            "Example: [{type: 'set_metric', metric: 'error_rate', "
                            "value: {type: 'increment', amount: 0.01}}]"
                        ),
                        "items": {"type": "object", "additionalProperties": True},
                    },
                },
                "required": ["rule_id", "condition", "actions"],
            },
        ),
        Tool(
            name="list_world_rules",
            description="List all active world rules",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_world_rule",
            description="Get details of a specific world rule by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "description": "ID of the rule to retrieve",
                    },
                },
                "required": ["rule_id"],
            },
        ),
        Tool(
            name="remove_world_rule",
            description="Remove a world rule by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "description": "ID of the rule to remove",
                    },
                },
                "required": ["rule_id"],
            },
        ),
        Tool(
            name="update_world_rule",
            description="Update an existing world rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "description": "ID of the rule to update",
                    },
                    "condition": {
                        "type": "object",
                        "description": "New condition (optional)",
                        "additionalProperties": True,
                    },
                    "actions": {
                        "type": "array",
                        "description": "New actions (optional)",
                        "items": {"type": "object", "additionalProperties": True},
                    },
                    "priority": {
                        "type": "number",
                        "description": "New priority (optional)",
                    },
                    "description": {
                        "type": "string",
                        "description": "New description (optional)",
                    },
                },
                "required": ["rule_id"],
            },
        ),
        Tool(
            name="clear_world_rules",
            description="Remove all world rules",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="save_simulation",
            description="Save the current simulation to disk",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name/ID for the simulation",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="load_simulation",
            description="Load a simulation from disk (replaces current simulation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name/ID of the simulation to load",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="list_simulations",
            description="List all saved simulations",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="delete_simulation",
            description="Delete a saved simulation from disk",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name/ID of the simulation to delete",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="get_simulation_info",
            description="Get metadata about a saved simulation without loading it",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name/ID of the simulation",
                    },
                },
                "required": ["name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    simulation = get_simulation()

    try:
        if name == "get_state":
            state = simulation.get_state()
            return [
                TextContent(
                    type="text",
                    text=json.dumps(state.model_dump(), indent=2, default=str),
                )
            ]

        elif name == "apply_action":
            action = arguments.get("action")
            params = arguments.get("params", {})

            result = simulation.apply_action(action, params)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "success": result.success,
                            "event_id": str(result.event_id),
                            "message": result.message,
                            "reason": result.reason,
                            "delta": result.delta,
                            "constraints_violated": [
                                v.model_dump() for v in result.constraints_violated
                            ],
                            "state_after": result.state_after.model_dump(),
                        },
                        indent=2,
                        default=str,
                    ),
                )
            ]

        elif name == "reset_simulation":
            seed = arguments.get("seed")
            if seed is not None:
                seed = int(seed)

            simulation.reset(seed=seed)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "message": "Simulation reset successfully",
                            "simulation_id": str(simulation.state.simulation_id),
                            "seed": seed,
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "fork_timeline":
            forked = simulation.fork()

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "message": "Timeline forked successfully",
                            "parent_id": str(simulation.state.simulation_id),
                            "child_id": str(forked.state.simulation_id),
                            "forked_at_time": simulation.state.time,
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "get_history":
            limit = arguments.get("limit")
            if limit is not None:
                limit = int(limit)

            history = simulation.get_history(limit=limit)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "count": len(history),
                            "events": [e.model_dump() for e in history],
                        },
                        indent=2,
                        default=str,
                    ),
                )
            ]

        elif name == "get_schema":
            schema = SimulationState.model_json_schema()
            return [
                TextContent(
                    type="text",
                    text=json.dumps(schema, indent=2),
                )
            ]

        elif name == "add_world_rule":
            rule_id = arguments.get("rule_id")
            condition = arguments.get("condition")
            actions = arguments.get("actions")
            priority = arguments.get("priority", 0)
            description = arguments.get("description", "")

            # Create dynamic rule
            rule = DynamicRule(
                rule_id=rule_id,
                condition=condition,
                actions=actions,
                priority=priority,
                description=description,
            )

            # Add to simulation
            simulation.world_rule_engine.add_rule(rule, priority=priority)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "message": f"World rule '{rule_id}' added successfully",
                            "rule_id": rule_id,
                            "condition": condition,
                            "actions": actions,
                            "active_rules": simulation.world_rule_engine.get_rule_ids(),
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "list_world_rules":
            rules = simulation.world_rule_engine.get_rule_ids()
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "count": len(rules),
                            "rules": rules,
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "get_world_rule":
            rule_id = arguments.get("rule_id")
            rule = simulation.world_rule_engine.get_rule(rule_id)

            if rule is None:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"Rule '{rule_id}' not found"},
                            indent=2,
                        ),
                    )
                ]

            # Get rule details
            if hasattr(rule, "to_dict"):
                rule_dict = rule.to_dict()
            else:
                rule_dict = {
                    "rule_id": rule.rule_id,
                    "type": type(rule).__name__,
                }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(rule_dict, indent=2),
                )
            ]

        elif name == "remove_world_rule":
            rule_id = arguments.get("rule_id")
            removed = simulation.world_rule_engine.remove_rule(rule_id)

            if removed:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "message": f"Rule '{rule_id}' removed successfully",
                                "active_rules": simulation.world_rule_engine.get_rule_ids(),
                            },
                            indent=2,
                        ),
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"Rule '{rule_id}' not found"},
                            indent=2,
                        ),
                    )
                ]

        elif name == "update_world_rule":
            rule_id = arguments.get("rule_id")
            existing_rule = simulation.world_rule_engine.get_rule(rule_id)

            if existing_rule is None:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"Rule '{rule_id}' not found"},
                            indent=2,
                        ),
                    )
                ]

            # Get existing values or new ones
            if hasattr(existing_rule, "to_dict"):
                existing_dict = existing_rule.to_dict()
            else:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"Rule '{rule_id}' cannot be updated (not a DynamicRule)"},
                            indent=2,
                        ),
                    )
                ]

            # Update with new values
            new_condition = arguments.get("condition", existing_dict["condition"])
            new_actions = arguments.get("actions", existing_dict["actions"])
            new_priority = arguments.get("priority", existing_dict.get("priority", 0))
            new_description = arguments.get("description", existing_dict.get("description", ""))

            # Create updated rule
            updated_rule = DynamicRule(
                rule_id=rule_id,
                condition=new_condition,
                actions=new_actions,
                priority=new_priority,
                description=new_description,
            )

            # Update in engine
            simulation.world_rule_engine.update_rule(rule_id, updated_rule)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "message": f"Rule '{rule_id}' updated successfully",
                            "rule": updated_rule.to_dict(),
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "clear_world_rules":
            count_before = simulation.world_rule_engine.get_rule_count()
            simulation.world_rule_engine.clear_rules()

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "message": "All world rules cleared",
                            "removed_count": count_before,
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "save_simulation":
            sim_name = arguments.get("name")
            description = arguments.get("description", "")

            file_path = persistence.save_simulation(sim_name, simulation, description)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "message": f"Simulation saved as '{sim_name}'",
                            "name": sim_name,
                            "file": str(file_path),
                            "description": description,
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "load_simulation":
            global sim
            sim_name = arguments.get("name")

            try:
                loaded_sim = persistence.load_simulation(sim_name)
                sim = loaded_sim  # Replace global simulation

                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "message": f"Simulation '{sim_name}' loaded successfully",
                                "name": sim_name,
                                "time": sim.state.time,
                                "seed": sim.state.seed,
                                "rule_count": sim.world_rule_engine.get_rule_count(),
                            },
                            indent=2,
                        ),
                    )
                ]
            except FileNotFoundError:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"Simulation '{sim_name}' not found"},
                            indent=2,
                        ),
                    )
                ]

        elif name == "list_simulations":
            sims = persistence.list_simulations()

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "count": len(sims),
                            "simulations": sims,
                        },
                        indent=2,
                        default=str,
                    ),
                )
            ]

        elif name == "delete_simulation":
            sim_name = arguments.get("name")
            deleted = persistence.delete_simulation(sim_name)

            if deleted:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"message": f"Simulation '{sim_name}' deleted successfully"},
                            indent=2,
                        ),
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"Simulation '{sim_name}' not found"},
                            indent=2,
                        ),
                    )
                ]

        elif name == "get_simulation_info":
            sim_name = arguments.get("name")
            info = persistence.get_simulation_info(sim_name)

            if info:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(info, indent=2, default=str),
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": f"Simulation '{sim_name}' not found"},
                            indent=2,
                        ),
                    )
                ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error("tool_error", tool=name, error=str(e))
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": str(e),
                        "tool": name,
                    },
                    indent=2,
                ),
            )
        ]


async def main() -> None:
    """Run the MCP server."""
    import sys
    from mcp.server.stdio import stdio_server

    # Configure logging to stderr (not stdout, which is used for JSON-RPC)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )

    logger.info("starting_mcp_server", server_name="scenario-engine")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
