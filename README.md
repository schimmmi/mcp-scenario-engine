# MCP Scenario Engine

**Ein MCP-Server für deterministische Simulation und Szenario-Planung**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-80%25%2B-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()

## Überblick

Der MCP Scenario Engine ist ein Model Context Protocol (MCP) Server, der einen Simulationsraum bereitstellt, in dem KI-Agents Systemzustände abfragen, Aktionen ausführen und Auswirkungen nachvollziehbar simulieren können. Ideal für:

- 🎯 Projektplanung und -simulation
- 🏗️ Infrastruktur-Änderungsplanung
- 🔬 "What-If"-Analysen
- 📊 Deterministische Entscheidungsfindung
- 🌳 Timeline-Forking für alternative Szenarien

## Kernfeatures

### ✅ State Management
- Versioniertes State-Schema (JSON Schema)
- Vollständige State-Snapshots
- Slicing und partielle Abfragen
- Time-stepped Simulation

### ✅ Action System
8 implementierte Actions:
- `step` - Zeit vorwärts bewegen
- `set_resource` - Ressource setzen
- `adjust_resource` - Ressource anpassen
- `set_metric` - Metrik setzen
- `set_flag` - Boolean-Flag setzen
- `add_entity` - Entity hinzufügen/updaten
- `remove_entity` - Entity entfernen
- `simulate_load` - Load-Szenario simulieren (mit Zufall)

### ✅ World Rules (Dynamic)
- JSON-definierte Regeln über MCP
- Automatische Anwendung bei `step` Actions
- Beliebige Conditions (comparison, and, or, not, always)
- Value Sources (resource, metric, flag, metadata, time, value)
- Vielfältige Actions (set_resource, set_metric, set_flag, set_metadata)
- Value Operations (fixed, increment, multiply)
- Prioritätssystem für Regel-Reihenfolge
- Vollständiges Rule Management (CRUD)

### ✅ Constraint Engine
- Serverseitige Validierung
- Automatisches State-Rollback bei Verstößen
- 3+ vordefinierte Constraints:
  - `NonNegativeResourceConstraint`
  - `MaxResourceConstraint`
  - `TimeMonotonicConstraint`
- Klare Fehlermeldungen mit Kontext

### ✅ Determinismus & Reproduzierbarkeit
- Seed-basierte Zufallsgenerierung
- Gleicher Seed → Gleiche Ergebnisse
- Vollständig reproduzierbare Simulationen

### ✅ Audit & Explainability
- Vollständige Event-History
- State-Deltas für jede Änderung
- Constraint-Checks protokolliert
- Structured Logging (JSON)

### ✅ Timeline Forking
- Verzweigung von Simulationen
- Parallele "What-If"-Szenarien
- Unveränderliche Original-Timeline

### ✅ Persistence
- Speichern von State + Rules + History
- Multiple Simulationen verwalten
- Server-Neustart überstehen
- Checkpoints setzen und fortsetzen
- CRUD-Operationen (Save, Load, List, Delete)
- Metadata-Inspektion ohne Laden

## Installation

### Voraussetzungen
- Python 3.11+
- pip oder uv

### Lokale Installation

```bash
# Repository klonen
git clone <repository-url>
cd mcp-scenario-engine

# Abhängigkeiten installieren
make install

# Oder manuell
pip install -e ".[dev]"
```

### Docker

```bash
# Build
docker compose build

# Demo ausführen
docker compose --profile demo run demo

# MCP Server starten
docker compose up mcp-scenario-engine
```

## Schnellstart

### 1. Demo ausführen

```bash
# Beide Demo-Szenarien
make demo

# Oder einzeln
python examples/demo_scenario_a.py
python examples/demo_scenario_b.py
```

### 2. Als Python-Library verwenden

```python
from mcp_scenario_engine import SimulationEngine
from mcp_scenario_engine.constraints import NonNegativeResourceConstraint

# Simulation erstellen
sim = SimulationEngine(seed=42)

# Initial State setzen
sim.state.resources = {"budget": 10000.0, "capacity": 100.0}

# Constraint hinzufügen
sim.constraint_engine.add_constraint(
    NonNegativeResourceConstraint("budget")
)

# Aktionen ausführen
result = sim.apply_action(
    "adjust_resource",
    {"resource": "budget", "delta": -2000.0}
)

if result.success:
    print(f"Neuer Budget: {sim.state.resources['budget']}")
    print(f"Delta: {result.delta}")
else:
    print(f"Fehler: {result.message}")
    for v in result.constraints_violated:
        print(f"  - {v.constraint_id}: {v.message}")
```

### 3. Als MCP Server verwenden

```bash
# Server starten
python -m mcp_scenario_engine.server

# In Claude Desktop konfigurieren (claude_desktop_config.json):
{
  "mcpServers": {
    "scenario-engine": {
      "command": "python",
      "args": ["-m", "mcp_scenario_engine.server"],
      "cwd": "/path/to/mcp-scenario-engine"
    }
  }
}
```

## MCP Tools

Der Server stellt 16 Tools bereit:

### State Management

#### `get_state`
Aktuellen Simulationszustand abrufen.

```json
{}
```

#### `get_schema`
State-Schema abrufen.

```json
{}
```

### Action Execution

#### `apply_action`
Aktion ausführen.

```json
{
  "action": "adjust_resource",
  "params": {
    "resource": "budget",
    "delta": -500.0
  }
}
```

### Simulation Control

#### `reset_simulation`
Simulation zurücksetzen.

```json
{
  "seed": 42
}
```

#### `fork_timeline`
Timeline verzweigen für "What-If"-Szenarien.

```json
{}
```

#### `get_history`
Event-History abrufen.

```json
{
  "limit": 10
}
```

### World Rules (Dynamic)

#### `add_world_rule`
Dynamische Regel hinzufügen, die automatisch bei `step` angewendet wird.

```json
{
  "rule_id": "cpu_overload",
  "condition": {
    "type": "comparison",
    "left": {"type": "resource", "name": "cpu"},
    "operator": ">",
    "right": {"type": "value", "value": 80}
  },
  "actions": [{
    "type": "set_metric",
    "metric": "error_rate",
    "value": {"type": "increment", "amount": 0.05}
  }],
  "priority": 10,
  "description": "Erhöhe Error-Rate bei CPU-Überlast"
}
```

#### `list_world_rules`
Alle aktiven Regeln auflisten.

```json
{}
```

#### `get_world_rule`
Details einer spezifischen Regel abrufen.

```json
{
  "rule_id": "cpu_overload"
}
```

#### `update_world_rule`
Bestehende Regel aktualisieren (partiell).

```json
{
  "rule_id": "cpu_overload",
  "priority": 20,
  "description": "Updated description"
}
```

#### `remove_world_rule`
Regel entfernen.

```json
{
  "rule_id": "cpu_overload"
}
```

#### `clear_world_rules`
Alle Regeln entfernen.

```json
{}
```

### Persistence

#### `save_simulation`
Simulation persistent speichern (State + Rules + History).

```json
{
  "name": "devops_scenario_1",
  "description": "High CPU scenario with 3 steps"
}
```

#### `load_simulation`
Gespeicherte Simulation laden (ersetzt aktuelle Simulation).

```json
{
  "name": "devops_scenario_1"
}
```

#### `list_simulations`
Alle gespeicherten Simulationen auflisten.

```json
{}
```

#### `get_simulation_info`
Metadata einer Simulation abrufen ohne sie zu laden.

```json
{
  "name": "devops_scenario_1"
}
```

#### `delete_simulation`
Gespeicherte Simulation löschen.

```json
{
  "name": "devops_scenario_1"
}
```

## State Schema (v1)

```json
{
  "schema_version": "v1",
  "simulation_id": "uuid",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z",
  "seed": 42,
  "time": 0,
  "entities": {},
  "metrics": {},
  "resources": {},
  "flags": {},
  "metadata": {}
}
```

## Demo-Szenarien

### Szenario A: Normaler Simulationslauf

Demonstriert:
- State-Initialisierung
- Mehrere Action-Typen
- Resource Management
- Entity-Lifecycle
- Metrics Tracking
- Reproduzierbarkeit

```bash
python examples/demo_scenario_a.py
```

**Ausgabe:**
```
============================================================
DEMO SCENARIO A: Normal Simulation Run
============================================================

1. Creating simulation with seed=42...
2. Adding constraints...
   - Budget must be non-negative
   - Team capacity must be non-negative

3. Executing simulation steps...
   ...
   ✓ Advanced to time step 3

6. Testing Reproducibility:
   ✓ Reproducibility verified - identical results with same seed
```

### Szenario B: Constraint-Verstoß

Demonstriert:
- Constraint-Validierung
- State-Rollback bei Verstößen
- Klare Fehlermeldungen
- Event-History
- Timeline-Forking

```bash
python examples/demo_scenario_b.py
```

**Ausgabe:**
```
============================================================
DEMO SCENARIO B: Constraint Violation Handling
============================================================

5. Testing constraint violations...

   Violation Attempt 1: Exceed maximum server load
   ✓ REJECTED as expected: Action rejected due to constraint violations
   Violations detected:
     - max_resource_server_load: Resource 'server_load' exceeds maximum 100.0 (got 130.0)
   State unchanged - Server load still: 80.00
```

### Demo: World Rules (DevOps)

Demonstriert dynamische Regeln:
- JSON-basierte Regel-Definition
- Automatische Kausalität
- Deterministische Weltmodell-Simulation

```bash
python examples/demo_devops_world.py
```

### Demo: Persistence

Demonstriert Persistenz-Features:
- Save/Load von Simulationen
- Multiple Simulation Management
- Continue from Checkpoint
- Delete und List Operations

```bash
python examples/demo_persistence.py
```

**Ausgabe:**
```
✅ Persistence Demo Complete!

💡 Key Features:
   • Save simulations with state + rules + history
   • Load simulations and continue from checkpoint
   • List all saved simulations
   • Get metadata without loading
   • Delete simulations
   • Overwrite existing saves
```

## Testing

```bash
# Alle Tests ausführen
make test

# Mit Coverage
pytest --cov=src --cov-report=html

# Nur Unit-Tests
pytest tests/test_*.py -v

# Nur Integration-Tests
pytest tests/test_integration.py -v
```

**Test-Coverage:** 80%+ (Requirement erfüllt)

## Entwicklung

### Code-Qualität

```bash
# Linting
make lint

# Formatierung
make format

# Type-Checking
mypy src
```

### Struktur

```
mcp-scenario-engine/
├── src/mcp_scenario_engine/
│   ├── __init__.py
│   ├── models.py           # Pydantic Models (State, Events)
│   ├── constraints.py      # Constraint Engine
│   ├── actions.py          # Action Implementations
│   ├── simulation.py       # Core Simulation Engine
│   ├── dynamic_rules.py    # Dynamic Rule System
│   ├── world_rules.py      # World Rule Engine
│   ├── persistence.py      # Persistence Layer
│   └── server.py           # MCP Server (16 Tools)
├── tests/
│   ├── test_simulation.py  # Unit Tests
│   ├── test_constraints.py # Constraint Tests
│   ├── test_actions.py     # Action Tests
│   └── test_integration.py # Integration Tests
├── examples/
│   ├── demo_scenario_a.py  # Demo: Normal Simulation
│   ├── demo_scenario_b.py  # Demo: Constraint Violations
│   ├── demo_devops_world.py # Demo: World Rules
│   └── demo_persistence.py  # Demo: Persistence
├── .simulations/            # Saved Simulations
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── Makefile
└── README.md
```

## Observability

### Structured Logging

Alle Logs werden als JSON ausgegeben:

```json
{
  "event": "action_applied",
  "simulation_id": "123e4567-e89b-12d3-a456-426614174000",
  "action": "adjust_resource",
  "event_id": "456e7890-e89b-12d3-a456-426614174111",
  "timestamp": "2025-01-15T10:30:00.123456Z"
}
```

### Event Types

- `simulation_created` - Simulation erstellt
- `simulation_reset` - Simulation zurückgesetzt
- `action_applied` - Aktion erfolgreich
- `constraint_violated` - Constraint-Verstoß
- `timeline_forked` - Timeline verzweigt

## Akzeptanzkriterien

✅ **State lesen**: `get_state` liefert valides Schema
✅ **Action ausführen**: `apply_action` liefert before/after/delta/event_id
✅ **Constraint greift**: Violations verhindern State-Änderung
✅ **Determinismus**: Gleicher Seed → Gleiche Ergebnisse
✅ **Fork/Branch**: Unveränderliches Original, divergierende Fork

## Definition of Done

### Implementierung ✅
- MCP-Server lauffähig (Docker + venv)
- State-Schema v1 dokumentiert
- 8 Actions implementiert
- Constraint-Engine mit 3+ Regeln
- Determinismus über Seed

### Qualität ✅
- Unit-Tests (80%+ Coverage)
- Integration-Tests (End-to-End)
- Linting/Formatting (ruff/black)
- Type-Checking (mypy)

### Observability ✅
- Structured Logging (JSON)
- Keine Secrets im Log
- Klare Error-Messages

### Dokumentation ✅
- README mit Setup & Beispielen
- Tool-Liste & Schema
- 2 Demo-Szenarien
- Beispiel-Outputs

### Demo ✅
- `make demo` funktioniert
- Szenario A: Normaler Lauf
- Szenario B: Constraint-Handling

## Lizenz

MIT

## Kontakt

Bei Fragen oder Problemen, bitte ein Issue öffnen.
