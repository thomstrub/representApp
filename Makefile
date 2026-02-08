.PHONY: help install test coverage clean deploy destroy

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing infrastructure dependencies..."
	cd infrastructure && pip install -r requirements.txt

test: ## Run unit tests
	@echo "Running tests..."
	cd backend && pytest

coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	cd backend && pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linting
	@echo "Running linters..."
	cd backend/src && pylint **/*.py || true
	cd backend/src && black --check . || true

format: ## Format code
	@echo "Formatting code..."
	cd backend/src && black .
	cd backend/src && isort .

clean: ## Clean up generated files
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete

synth: ## Synthesize CDK stack
	@echo "Synthesizing CDK stack..."
	cd infrastructure && cdk synth

diff: ## Show differences between deployed and local stack
	@echo "Showing stack diff..."
	cd infrastructure && cdk diff

deploy: ## Deploy to AWS
	@echo "Deploying stack..."
	cd infrastructure && cdk deploy

destroy: ## Destroy AWS resources
	@echo "Destroying stack..."
	cd infrastructure && cdk destroy

bootstrap: ## Bootstrap CDK (first time only)
	@echo "Bootstrapping CDK..."
	cd infrastructure && cdk bootstrap

local-api: ## Start local API with SAM
	@echo "Starting local API..."
	sam local start-api

setup: install ## Complete setup
	@echo "Setup complete!"
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run 'make bootstrap' (first time only)"
	@echo "  3. Run 'make deploy' to deploy to AWS"

.DEFAULT_GOAL := help
