# Installation für Claude Desktop

## Schritt 1: Package installieren

```bash
cd /Users/jurgenschilling/workspace/mcp-scenario-engine
python3 -m pip install -e .
```

## Schritt 2: Claude Desktop Config

Öffne deine Claude Desktop Konfiguration:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Füge diesen Block hinzu (oder merge mit bestehender Config):

```json
{
  "mcpServers": {
    "scenario-engine": {
      "command": "python3",
      "args": [
        "-m",
        "mcp_scenario_engine.server"
      ],
      "cwd": "/Users/jurgenschilling/workspace/mcp-scenario-engine",
      "env": {
        "PYTHONPATH": "/Users/jurgenschilling/workspace/mcp-scenario-engine/src"
      }
    }
  }
}
```

**Wichtig**: Passe den `cwd` Pfad an, falls dein Workspace woanders liegt!

## Schritt 3: Claude Desktop neu starten

Starte Claude Desktop komplett neu (nicht nur neu laden).

## Schritt 4: Testen

In Claude Desktop solltest du jetzt diese Tools sehen:
- 🔧 `scenario-engine` MCP Server verfügbar
- Tools: `get_state`, `apply_action`, `reset_simulation`, `fork_timeline`, `get_history`, `get_schema`

### Test-Befehle in Claude:

```
"Zeige mir den aktuellen Simulationszustand"
-> Nutzt get_state

"Führe einen Simulationsschritt aus"
-> Nutzt apply_action mit step

"Setze die Resource 'budget' auf 5000"
-> Nutzt apply_action mit set_resource

"Erstelle einen Fork der Timeline"
-> Nutzt fork_timeline
```

## Troubleshooting

### Server startet nicht?

Test manuell:
```bash
cd /Users/jurgenschilling/workspace/mcp-scenario-engine
python3 -m mcp_scenario_engine.server
```

Sollte JSON auf stdout ausgeben.

### Module not found?

Installiere nochmal:
```bash
python3 -m pip install -e ".[dev]"
```

### Logs anschauen

Der Server loggt nach stderr, check Claude Desktop Logs:
```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp*.log
```

## Manuelle Tests ohne Claude Desktop

```bash
# Demo Scenarios
python3 examples/demo_scenario_a.py
python3 examples/demo_scenario_b.py

# Python REPL
python3
>>> from mcp_scenario_engine import SimulationEngine
>>> sim = SimulationEngine(seed=42)
>>> result = sim.apply_action("step", {})
>>> print(result.success)
```
