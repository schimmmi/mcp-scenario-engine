# Docker Usage Guide

Complete guide for using MCP Scenario Engine with Docker.

## Quick Start

```bash
# Build image
docker compose build

# Run demos
docker compose --profile demo run demo

# Start MCP server
docker compose up mcp-scenario-engine
```

## Running Demos

### All Demos

```bash
docker compose --profile demo run demo
```

This runs:
- Scenario A: Normal simulation
- Scenario B: Constraint violations

### Specific Demos

```bash
# Weight loss simulation
docker compose run demo python examples/demo_weight_loss.py

# Game theory
docker compose run demo python examples/demo_prisoners_dilemma.py
docker compose run demo python examples/demo_evolutionary_game.py
docker compose run demo python examples/demo_auction_theory.py

# DevOps world rules
docker compose run demo python examples/demo_devops_world.py

# Persistence
docker compose run demo python examples/demo_persistence.py
```

## Using with Claude Desktop

### Method 1: Docker Compose (Recommended)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scenario-engine": {
      "command": "docker",
      "args": [
        "compose",
        "-f",
        "/absolute/path/to/mcp-scenario-engine/docker-compose.yml",
        "run",
        "--rm",
        "mcp-scenario-engine"
      ]
    }
  }
}
```

**Important:**
- Use absolute path, not relative (e.g., `/Users/john/mcp-scenario-engine/docker-compose.yml`)
- Docker Desktop must be running before starting Claude Desktop
- Each invocation creates a fresh container

### Method 2: Direct Docker Run

```json
{
  "mcpServers": {
    "scenario-engine": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "mcp-scenario-engine:latest"
      ]
    }
  }
}
```

First build the image:
```bash
docker build -t mcp-scenario-engine:latest .
```

## Persistence Setup

By default, simulations are saved inside the container and lost when it stops. To persist data:

### Option 1: Uncomment Volume in docker-compose.yml

Edit `docker-compose.yml`:

```yaml
services:
  mcp-scenario-engine:
    volumes:
      - ./examples:/app/examples:ro
      - ~/.mcp-scenario-engine:/root/.mcp-scenario-engine  # Uncomment this line
```

### Option 2: Custom Volume

```yaml
volumes:
  - /path/to/persistent/storage:/root/.mcp-scenario-engine
```

### Option 3: Named Docker Volume

```yaml
volumes:
  - simulation-data:/root/.mcp-scenario-engine

volumes:
  simulation-data:
```

List saved simulations:
```bash
docker compose run mcp-scenario-engine ls -la /root/.mcp-scenario-engine/simulations/
```

## Development Workflow

### Live Code Changes

Mount source code for development:

```yaml
services:
  mcp-scenario-engine:
    volumes:
      - ./src:/app/src
      - ./examples:/app/examples
```

Changes take effect on restart (no rebuild needed).

### Run Tests in Docker

```bash
# All tests
docker compose run demo pytest

# With coverage
docker compose run demo pytest --cov=src --cov-report=html

# Specific test
docker compose run demo pytest tests/test_simulation.py -v
```

### Interactive Shell

```bash
# Python shell with package loaded
docker compose run demo python

# Bash shell
docker compose run demo bash
```

## Troubleshooting

### Container Won't Start

```bash
# View logs
docker compose logs mcp-scenario-engine

# Check if port is in use
docker compose ps

# Remove old containers
docker compose down
docker system prune
```

### Claude Desktop Can't Connect

1. **Verify Docker is running:**
   ```bash
   docker ps
   ```

2. **Test manually:**
   ```bash
   echo '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | \
   docker compose run --rm mcp-scenario-engine
   ```

   Should output JSON response with server info.

3. **Check paths:**
   - Use absolute paths in `claude_desktop_config.json`
   - Verify `docker-compose.yml` exists at that path

4. **Restart Claude Desktop:**
   - Completely quit (not just close window)
   - Restart Docker Desktop
   - Start Claude Desktop

### Simulations Not Persisting

1. **Check volume mount:**
   ```bash
   docker compose config | grep volumes
   ```

2. **Verify permissions:**
   ```bash
   ls -la ~/.mcp-scenario-engine
   ```

3. **Test save/load:**
   ```bash
   docker compose run demo python examples/demo_persistence.py
   docker compose run mcp-scenario-engine ls -la /root/.mcp-scenario-engine/simulations/
   ```

## Performance Tips

### Reduce Startup Time

**Use pre-built image:**
```bash
# Build once
docker compose build

# Start quickly (uses cached image)
docker compose up mcp-scenario-engine
```

**Cache Python packages:**
```dockerfile
# In Dockerfile, before copying source:
COPY pyproject.toml .
RUN pip install -e .
COPY src/ ./src/
```

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  mcp-scenario-engine:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

## Advanced Usage

### Multi-Stage Build (Smaller Image)

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --user .

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "-m", "mcp_scenario_engine.server"]
```

### Health Check

```yaml
services:
  mcp-scenario-engine:
    healthcheck:
      test: ["CMD", "python", "-c", "import mcp_scenario_engine; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Network Mode (Claude Desktop Communication)

```yaml
services:
  mcp-scenario-engine:
    network_mode: "host"  # May help with some connection issues
```

## Security Considerations

- Container runs as root by default
- Simulations stored in `/root/.mcp-scenario-engine`
- No external network access needed (stdio only)
- Runs in isolated container namespace

**To run as non-root:**

```dockerfile
RUN useradd -m simuser
USER simuser
WORKDIR /home/simuser/app
```

Then mount volumes to `/home/simuser/.mcp-scenario-engine`.

## FAQ

**Q: Can I use Docker Desktop alternatives (Podman, Rancher)?**
A: Yes, but change `docker` to `podman` in config.

**Q: Does it work on Windows/Linux?**
A: Yes, Docker works cross-platform. Adjust paths accordingly:
- Windows: `C:\\Users\\...`
- Linux/macOS: `/home/...` or `/Users/...`

**Q: Can I run multiple servers?**
A: Yes, but change container names and ports if exposing any.

**Q: Memory usage?**
A: ~50-100MB idle, ~200MB during heavy simulation.

## See Also

- [README.md](README.md) - General documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [docker-compose.yml](docker-compose.yml) - Service configuration
- [Dockerfile](Dockerfile) - Image definition
