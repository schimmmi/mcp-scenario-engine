# Multi-stage build for MCP Scenario Engine
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir build

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Build wheel
RUN python -m build --wheel

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy wheel from builder
COPY --from=builder /app/dist/*.whl ./

# Install the wheel
RUN pip install --no-cache-dir *.whl && rm *.whl

# Copy examples
COPY examples/ ./examples/

# Default command runs the MCP server
CMD ["python", "-m", "mcp_scenario_engine.server"]
