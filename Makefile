#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = timestamp
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	@uv sync
	@cp .local.dev.env.example .env


## Run development server
.PHONY: compose compose-down dev
compose:
	@docker compose --env-file .env -f docker-compose.local.dev.yml up --build -d
compose-down:
	@docker compose -f docker-compose.local.dev.yml down
dev:
	@make compose-down
	@make compose
	@sleep 3
	@uv run fastapi dev timestamp/main.py

## Run mkdocs local server
.PHONY: docs
docs:
	uv run zensical serve -f docs/zensical.toml


## Run unit and integration tests with pytest
.PHONY: test
test: 
	uv run pytest tests/


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	uv run ruff format --check
	uv run ruff check


## Format source code with ruff
.PHONY: format
format:
	uv run ruff check --fix
	uv run ruff format


## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Bump project version with patch update
.PHONY: patch
patch:
	@uv version --bump patch
	@git add pyproject.toml
	@git add uv.lock
	@git commit -m "🏷️ release (patch): $$(uv version --short)"
	@git tag $$(uv version --short)


## Bump project version with minor update
.PHONY: minor
minor:
	@uv version --bump minor
	@git add pyproject.toml
	@git add uv.lock
	@git commit -m "🏷️ release (minor): $$(uv version --short)"
	@git tag $$(uv version --short)


## Bump project version with major update
.PHONY: major
major:
	@uv version --bump major
	@git add pyproject.toml
	@git add uv.lock
	@git commit -m "🏷️ release (major): $$(uv version --short)"
	@git tag $$(uv version --short)


## Push committed release tag to origin to trigger GitHub release
.PHONY: release
release:
	@git push origin $$(uv version --short)


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
