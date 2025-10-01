.PHONY: help install install-dev test test-cov lint format clean run db-upgrade db-downgrade docker-build docker-run deploy-staging deploy-prod

# Default target
help: ## Show this help message
	@echo "SAMMS.FO - Development Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install black isort flake8 bandit safety pytest pytest-cov pytest-mock factory-boy

# Testing
test: ## Run all tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

test-unit: ## Run only unit tests
	pytest tests/unit/ -v

test-integration: ## Run only integration tests
	pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	pytest tests/e2e/ -v -s

# Code Quality
lint: ## Run linting checks
	flake8 app/ tests/ scripts/
	@echo "✅ Linting passed"

format: ## Format code with black and isort
	black app/ tests/ scripts/
	isort app/ tests/ scripts/
	@echo "✅ Code formatted"

format-check: ## Check code formatting without modifying
	black --check --diff app/ tests/ scripts/
	isort --check-only --diff app/ tests/ scripts/

security: ## Run security checks
	bandit -r app/ -f txt
	safety check

# Database
db-init: ## Initialize database
	flask db init

db-migrate: ## Create new migration
	flask db migrate -m "$(msg)"

db-upgrade: ## Upgrade database to latest migration
	flask db upgrade

db-downgrade: ## Downgrade database
	flask db downgrade

# Development
run: ## Run development server
	python run.py

run-debug: ## Run development server with debug
	export FLASK_ENV=development && python run.py

shell: ## Start Flask shell
	flask shell

# Docker
docker-build: ## Build Docker image
	docker build -t samms-fo -f deploy/Dockerfile .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env samms-fo

docker-compose-up: ## Start all services with docker-compose
	docker-compose -f deploy/docker-compose.yml up -d

docker-compose-down: ## Stop all services
	docker-compose -f deploy/docker-compose.yml down

# Deployment
deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	# Add your staging deployment commands here
	@echo "✅ Deployed to staging"

deploy-prod: ## Deploy to production environment
	@echo "🎯 Deploying to production..."
	# Add your production deployment commands here
	@echo "✅ Deployed to production"

# Scripts
add-samples: ## Add sample products to database
	python scripts/add_sample_products.py

inspect-db: ## Inspect database contents
	python scripts/inspect_db.py

migrate-passwords: ## Migrate password column
	python scripts/migrate_password_column.py

add-phone-column: ## Add phone column to users table
	python scripts/add_phone_column.py

# Cleanup
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/
	@echo "✅ Cleanup completed"

clean-all: clean ## Clean everything including venv
	rm -rf .venv/
	@echo "✅ Full cleanup completed"

# Health checks
health: ## Run health checks
	curl -f http://localhost:8095/health || echo "❌ Health check failed"
	curl -f http://localhost:8095/ready || echo "❌ Readiness check failed"

# CI/CD simulation
ci: lint test-cov security ## Run full CI pipeline locally
	@echo "✅ All CI checks passed"

# Environment setup
setup: ## Initial project setup
	python -m venv .venv
	@echo "✅ Virtual environment created"
	@echo "Run 'source .venv/bin/activate' (Linux/Mac) or '.venv\\Scripts\\activate' (Windows)"
	@echo "Then run 'make install-dev' to install dependencies"

# Help for Windows users
setup-windows: ## Setup for Windows users
	python -m venv .venv
	@echo "✅ Virtual environment created"
	@echo "Run '.venv\\Scripts\\activate' to activate"
	@echo "Then run 'make install-dev' to install dependencies"