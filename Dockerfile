# Use Python 3.11 slim image
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy only dependency file first (for Docker layer caching)
COPY pyproject.toml ./

# Install dependencies using uv
# This layer will be cached unless pyproject.toml changes
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy source files (changes here won't trigger dependency reinstall)
COPY mashov_mcp_server.py ./
COPY mashov_client.py ./
COPY config.py ./

# Set environment variables (can be overridden at runtime)
ENV MASHOV_USERNAME=""
ENV MASHOV_PASSWORD=""
ENV MASHOV_SEMEL=""
ENV MASHOV_YEAR="2025"

# Run the MCP server
CMD ["python", "mashov_mcp_server.py"]

