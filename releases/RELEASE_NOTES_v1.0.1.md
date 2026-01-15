# Release Notes v1.0.1

**Bug Fix Release** 🐛

This patch release fixes two critical bugs discovered in v1.0.0 that affected the persistence layer when running in Claude Desktop and other MCP clients.

## 🐛 Bug Fixes

### 1. Fixed Read-Only Filesystem Error

**Problem:**
- Server crashed on startup in Claude Desktop with `OSError: [Errno 30] Read-only file system: '.simulations'`
- MCP servers often run in read-only contexts where creating directories in the current working directory is not allowed

**Solution:**
- Changed default storage location from `.simulations` to `~/.mcp-scenario-engine/simulations/`
- Uses user's home directory which is always writable
- Added `parents=True` to `mkdir()` for nested directory creation

**Impact:**
- ✅ Server now starts successfully in Claude Desktop
- ✅ Persistence works in all environments
- ✅ User data stored in standard home directory location

### 2. Fixed Event History Not Restored on Load

**Problem:**
- Event history was correctly saved but not restored when loading simulations
- After loading, simulations only had 1 "simulation_created" event instead of the full audit trail
- Comment in code said "History is embedded in state, but we could restore it if needed" but it was never implemented

**Solution:**
- Added history restoration in `load_simulation()` method
- Clears auto-generated creation event before restoring saved history
- Deserializes all `HistoryEvent` objects with full fidelity

**Impact:**
- ✅ Complete audit trail preserved across save/load cycles
- ✅ Event IDs preserved
- ✅ Timestamps preserved
- ✅ State deltas preserved
- ✅ Full simulation reproducibility

## 🧪 Verification

Both fixes have been verified with comprehensive testing:

### Storage Location Test
```bash
# Server starts successfully in Claude Desktop
# No OSError on initialization
# Simulations saved to ~/.mcp-scenario-engine/simulations/
```

### History Restoration Test
```
Before save: 4 history events
After load:  4 history events ✅

Event IDs:    Preserved ✅
Timestamps:   Preserved ✅
State deltas: Preserved ✅
```

## 📦 Upgrade Instructions

### For Claude Desktop Users

1. **Stop Claude Desktop**
2. **Update the server** (if installed via git):
   ```bash
   cd /path/to/mcp-scenario-engine
   git pull origin main
   ```
3. **Restart Claude Desktop**

### For Docker Users

```bash
docker compose pull
docker compose up -d mcp-scenario-engine
```

### For Python Package Users

```bash
pip install --upgrade mcp-scenario-engine
```

## 🔄 Migration

No migration needed! Existing saved simulations will continue to work:
- Old simulations saved in `.simulations/` can be manually moved to `~/.mcp-scenario-engine/simulations/` if desired
- History in existing saves will now be properly restored on load

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## 🙏 Thanks

Thanks to the early testers who reported these issues!

---

**Previous Release**: [v1.0.0](https://github.com/schimmmi/mcp-scenario-engine/releases/tag/v1.0.0)
