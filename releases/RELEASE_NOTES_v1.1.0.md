# Release Notes v1.1.0

**Feature Release - Complex Formula Support** 🧮

This release adds powerful mathematical formula capabilities to the DynamicRules system, enabling complex calculations in world rules without writing Python code.

## 🎯 What's New

### Complex Mathematical Formulas

World rules can now use advanced mathematical operations to model real-world systems:

```json
{
  "type": "set_resource",
  "resource": "fettmasse",
  "value": {
    "type": "subtract",
    "left": {"type": "resource", "name": "fettmasse"},
    "right": {
      "type": "multiply",
      "values": [
        {
          "type": "divide",
          "numerator": {"type": "metric", "name": "kaloriendefizit"},
          "denominator": {"type": "value", "value": 7700}
        },
        {"type": "value", "value": 7},
        {"type": "metric", "name": "compliance"}
      ]
    }
  }
}
```

This calculates: `fettmasse - ((kaloriendefizit / 7700) * 7 * compliance)`

## ✨ New Operations

### Division
```json
{
  "type": "divide",
  "numerator": {"type": "metric", "name": "calories"},
  "denominator": {"type": "value", "value": 7700}
}
```
- Automatic zero-division protection
- Full precision floating-point math

### Multiplication (Multiple Values)
```json
{
  "type": "multiply",
  "values": [
    {"type": "resource", "name": "price"},
    {"type": "metric", "name": "quantity"},
    {"type": "metric", "name": "tax_rate"}
  ]
}
```
- Multiply any number of values
- Supports mixed sources (resources, metrics, constants)

### Addition (Multiple Values)
```json
{
  "type": "add",
  "values": [
    {"type": "resource", "name": "base_cost"},
    {"type": "resource", "name": "shipping"},
    {"type": "resource", "name": "tax"}
  ]
}
```

### Subtraction
```json
{
  "type": "subtract",
  "left": {"type": "resource", "name": "budget"},
  "right": {"type": "resource", "name": "spent"}
}
```

### Nested Operations
Operations can be arbitrarily nested for complex formulas:
```json
{
  "type": "add",
  "values": [
    {
      "type": "multiply",
      "values": [
        {"type": "resource", "name": "hours"},
        {"type": "metric", "name": "rate"}
      ]
    },
    {
      "type": "divide",
      "numerator": {"type": "resource", "name": "bonus"},
      "denominator": {"type": "value", "value": 12}
    }
  ]
}
```

## 🏋️ Demo: Weight Loss Simulation

New demonstration showing real-world formula usage:

```bash
python examples/demo_weight_loss.py
```

**Features:**
- Fat loss calculation: `(calorie_deficit / 7700) * 7 * compliance`
- Muscle gain: `training_sessions * 0.05 * compliance`
- Body composition tracking over 8 weeks
- Realistic fitness modeling

**Sample Output:**
```
Week     Weight   Change      Fat   Muscle    Fat%
----------------------------------------------------------------------
Start    92.47kg        -   18.55kg   70.16kg   20.1%
1        88.53kg   -3.94kg   18.24kg   70.29kg   20.6%
2        88.35kg   -0.18kg   17.93kg   70.41kg   20.3%
3        88.17kg   -0.18kg   17.62kg   70.54kg   20.0%
4        87.98kg   -0.18kg   17.31kg   70.67kg   19.7%
5        87.80kg   -0.18kg   17.00kg   70.80kg   19.4%
6        87.62kg   -0.18kg   16.70kg   70.92kg   19.1%
7        87.44kg   -0.18kg   16.39kg   71.05kg   18.7%
8        87.26kg   -0.18kg   16.08kg   71.18kg   18.4%

Results: -5.21kg total, -2.47kg fat, +1.02kg muscle, 20.1% → 18.4% body fat
```

## 🎓 Use Cases

This release enables simulations for:

### Health & Fitness
- Calorie/macro tracking with metabolic calculations
- Body composition modeling
- Training load management
- Recovery and adaptation curves

### Economics & Finance
- ROI calculations with multiple variables
- Compound interest formulas
- Cost-benefit analysis
- Portfolio rebalancing

### Science & Engineering
- Physics simulations (force, velocity, acceleration)
- Chemical reactions with rate equations
- Resource depletion models
- Energy efficiency calculations

### Business Operations
- Revenue forecasting with seasonal factors
- Inventory optimization formulas
- Resource allocation calculations
- Performance metrics with multiple inputs

## 🔧 Technical Details

### Implementation
- Complete rewrite of `_compute_value()` method in `dynamic_rules.py`
- Recursive formula evaluation for nested operations
- Type-safe floating-point calculations
- Comprehensive error handling (division by zero, invalid types)

### Backward Compatibility
- ✅ All existing simple value operations still work
- ✅ Old increment/multiply syntax supported
- ✅ No breaking changes to existing rules

### Performance
- Formulas computed on-demand during rule application
- No pre-compilation or caching (keeps it simple)
- Negligible overhead for typical formula complexity

## 📚 Documentation

- Updated README with formula syntax examples
- New demo scenario: `examples/demo_weight_loss.py`
- Inline code documentation for all operations

## 🚀 Upgrade Guide

No changes required! This is a pure feature addition. Existing rules continue to work, and you can start using formulas immediately by:

1. Update your server:
   ```bash
   cd /path/to/mcp-scenario-engine
   git pull
   ```

2. Restart Claude Desktop

3. Create rules with formulas via `add_world_rule` tool

## 🐛 Bug Fixes

None - this is a pure feature release.

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

**Previous Release**: [v1.0.1](https://github.com/schimmmi/mcp-scenario-engine/releases/tag/v1.0.1)
**GitHub Repository**: https://github.com/schimmmi/mcp-scenario-engine
