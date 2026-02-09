# Copilot Instructions for lexmachina-agent

## Project Overview

This is an **A2A (Agent-to-Agent) agent** for Lex Machina that provides search suggestions through a standardized agent API. The agent integrates with external Lex Machina APIs to generate and enrich search suggestions for legal data queries.

## Architecture & Key Components

### Core Components
- **`server.py`**: Main entry point that sets up the A2A Starlette application with agent capabilities
- **`agent_executor.py`**: Contains the core business logic for API authentication, search processing, and parallel data enrichment
- **A2A Framework**: Built on the `a2a-sdk[http-server]` for standardized agent communication

### Data Flow
1. Agent receives text queries through A2A protocol
2. `LexmachinaAgentExecutor` processes queries using `LexMachinaAPIAgent`
3. API calls are made to `/search/ai_suggested` endpoint for initial suggestions
4. Each suggestion is enriched in parallel by fetching descriptions from their respective URLs
5. Results are returned as JSON artifacts through the A2A event system

## Configuration Patterns

### Environment Variables (Required)
The agent supports multiple authentication methods via environment variables:
```bash
# Option 1: Direct token
API_TOKEN=your_token_here

# Option 2: OAuth2 client credentials
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret

# Option 3: Delegation URL (not yet implemented)
DELEGATION_URL=your_delegation_url

# API base URL (defaults to production)
API_BASE_URL=https://law.lexmachina.com
```

### Configuration Error Handling
- Custom exception hierarchy: `ConfigurationError`, `RequiredConfigurationError`, `MissingConfigurationError`
- Validation ensures at least one authentication method is provided
- OAuth2 token fetching is handled synchronously during agent initialization

## Development Workflow

### Essential Commands
```bash
# Setup development environment (installs pre-commit hooks)
just install

# Run all quality checks (lock file, linting, type checking, dependency analysis)
just check

# Start development server with auto-reload
just run  # Starts on localhost:10011

# Run tests with coverage
just test

# Build documentation
just docs
```

### Code Quality Standards
- **Python 3.13+ required** (`requires-python = ">=3.13,<4.0"`)
- **Ruff** for linting and formatting (120 char line length)
- **MyPy** for type checking with strict settings (`disallow_untyped_defs = true`)
- **Pre-commit hooks** enforce quality on every commit
- **pytest** with coverage reporting

## Key Integration Points

### A2A Protocol Integration
- Agent implements `AgentExecutor` interface with `execute()` and `cancel()` methods
- Uses `EventQueue` for asynchronous task completion
- Returns results as `TextPart` artifacts with JSON string content
- Agent card defines capabilities: single skill "search_suggestions" with example queries

### HTTP Client Patterns
- **AsyncIO**: All external API calls use `httpx.AsyncClient` for non-blocking operations
- **Parallel Processing**: `asyncio.gather()` used to enrich multiple suggestions simultaneously
- **Error Handling**: HTTP errors are caught and returned as error objects rather than raising exceptions

### Agent Skill Definition
Example queries the agent handles:
- "What is the average time to resolution for contracts cases in SDNY in the last 3 months?"
- "Time to trial in a Los Angeles County case before Judge Randy Rhodes?"
- "Reversal rate for employment cases in the 5th circuit?"

## Project-Specific Conventions

### Package Structure
- Uses `src/` layout with `lexmachina_agent` package
- Console script entry point: `lexmachina-agent = "lexmachina_agent.server:main"`
- Dependencies managed with **uv** (see `uv.lock`)

### Testing & CI/CD
- Tests in `tests/` directory (pytest auto-discovery)
- Tox configuration for Python 3.13 testing
- GitHub Actions CI/CD pipeline (see `.github/workflows/`)
- Documentation built with MkDocs Material theme

### Container Deployment
- Multi-stage Dockerfile using Python 3.13-slim base
- UV package manager for fast dependency installation
- Frozen lockfile deployment (`uv sync --frozen`)

## Common Patterns to Follow

1. **Configuration**: Always use `APIAgentConfiguration` class for environment-based config
2. **API Clients**: Create stateful agent classes that hold HTTP clients and auth headers
3. **Error Handling**: Return error objects in response data rather than raising exceptions
4. **Async Processing**: Use `asyncio.gather()` for parallel external API calls
5. **Logging**: Use module-level loggers (`logger = logging.getLogger(__name__)`)
6. **Type Hints**: All function signatures must include type annotations (enforced by MyPy)
