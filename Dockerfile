FROM python:3.12-slim

WORKDIR /app

# Get the latest uv version and install it
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy the pyproject.toml and uv.lock files
COPY pyproject.toml uv.lock ./

# Install the dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "stellar.main:app", "--host", "0.0.0.0", "--port", "8000"]
