# Install uv
FROM python:3.13-slim

# Build arguments for metadata
ARG BUILDTIME
ARG VERSION
ARG REVISION

# Add metadata labels
LABEL org.opencontainers.image.title="Lex Machina Agent"
LABEL org.opencontainers.image.description="A2A agent for Lex Machina"
LABEL org.opencontainers.image.vendor="Lex Machina / LexisNexis / RELX"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.source="https://github.com/LexMachinaInc/lexmachina-agent"
LABEL org.opencontainers.image.created="${BUILDTIME}"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.revision="${REVISION}"

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
