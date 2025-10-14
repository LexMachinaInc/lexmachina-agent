.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry src

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml

.PHONY: run
run: ## Run the development server
	@echo "🚀 Starting application"
	@uv run uvicorn --reload --host localhost --port 10011 --factory lexmachina_agent.server:app

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

a2a-inspector-source-url := https://github.com/LexMachinaInc/a2a-inspector/archive/refs/heads/fix-docker.tar.gz

vendor/a2a-inspector: ## Vendor the a2a-inspector code
	@echo "🚀 Vendoring a2a-inspector code"
	@mkdir -p vendor/a2a-inspector
	@curl -L $(a2a-inspector-source-url) | tar -xz -C vendor/a2a-inspector --strip-components=1

.PHONY: compose-up
compose-up: vendor/a2a-inspector ## Start the application using docker-compose
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

.DEFAULT_GOAL := help
