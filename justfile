# Justfile for lexmachina-agent
# See https://just.systems/ for more information

# Install the virtual environment and install the pre-commit hooks
install:
    @echo "🚀 Creating virtual environment using uv"
    @uv sync
    @uv run pre-commit install

# Run code quality tools
check:
    @echo "🚀 Checking lock file consistency with 'pyproject.toml'"
    @uv lock --locked
    @echo "🚀 Linting code: Running pre-commit"
    @uv run pre-commit run -a
    @echo "🚀 Static type checking: Running mypy"
    @uv run mypy
    @echo "🚀 Checking for obsolete dependencies: Running deptry"
    @uv run deptry src

# Test the code with pytest
test:
    @echo "🚀 Testing code: Running pytest"
    @uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

# Run the development server
run:
    @echo "🚀 Starting application"
    @uv run uvicorn --reload --host localhost --port 10011 --factory lexmachina_agent.server:app

# Build wheel file
build: clean-build
    @echo "🚀 Creating wheel file"
    @uvx --from build pyproject-build --installer uv

# Clean build artifacts
clean-build:
    @echo "🚀 Removing build artifacts"
    @uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

# Test if documentation can be built without warnings or errors
docs-test:
    @uv run mkdocs build -s

# Build and serve the documentation
docs:
    @uv run mkdocs serve

# Show available recipes
help:
    @just --list

# Vendor the a2a-inspector code
vendor-a2a-inspector:
    @echo "🚀 Vendoring a2a-inspector code"
    @mkdir -p vendor/a2a-inspector
    @curl -L https://github.com/LexMachinaInc/a2a-inspector/archive/refs/heads/fix-docker.tar.gz | tar -xz -C vendor/a2a-inspector --strip-components=1

# Start the application using docker-compose
compose-up: vendor-a2a-inspector
    @echo "🚀 Starting application using docker-compose"
    @if command -v nerdctl >/dev/null 2>&1 && nerdctl compose --help >/dev/null 2>&1; then \
        echo "Using nerdctl compose"; \
        nerdctl compose up; \
    elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then \
        echo "Using docker compose"; \
        docker compose up; \
    elif command -v docker-compose >/dev/null 2>&1; then \
        echo "Using docker-compose"; \
        docker-compose up; \
    else \
        echo "❌ Neither nerdctl compose nor docker compose/docker-compose is available."; \
        exit 1; \
    fi
