# Install uv
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Run as non-root user in /app
RUN useradd -ms /bin/sh app
USER app
WORKDIR /app

# Copy the lockfile and `pyproject.toml` into the image
COPY uv.lock /app/uv.lock
COPY pyproject.toml /app/pyproject.toml

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy the project into the image
COPY . /app

# Sync the project
RUN uv sync --frozen

EXPOSE 10011

ENTRYPOINT ["uv", "run", "uvicorn", "--host", "0.0.0.0", "--port", "10011", "--factory", "lexmachina_agent.server:app"]
