.DEFAULT_GOAL := help
PY ?= python

.PHONY: help install browsers run web telegram cli check lint format test clean docker docker-logs

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install runtime + dev dependencies
	$(PY) -m pip install -U pip
	$(PY) -m pip install -r requirements.txt -r requirements-dev.txt

browsers: ## Install the Playwright Chromium build
	$(PY) -m playwright install chromium

run: ## Run Telegram bot + web dashboard
	$(PY) main.py both

web: ## Run the web dashboard + REST API only
	$(PY) main.py web

telegram: ## Run the Telegram bot only
	$(PY) main.py telegram

cli: ## Run one command: make cli CMD="open example.com"
	$(PY) main.py cli "$(CMD)"

check: ## Diagnose the model endpoint
	$(PY) main.py check

lint: ## Lint with ruff
	ruff check .
	ruff format --check .

format: ## Auto-format with ruff
	ruff check --fix .
	ruff format .

test: ## Run the test suite
	pytest -q

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info

docker: ## Build and start the container stack
	docker compose up -d --build

docker-logs: ## Follow container logs
	docker compose logs -f
