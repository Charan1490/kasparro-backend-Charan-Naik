.PHONY: up down test logs clean db-shell db-migrate build help

# Default target
.DEFAULT_GOAL := help

# Load environment variables
include .env
export

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services (PostgreSQL + API)
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📊 API: http://localhost:8000"
	@echo "📚 Docs: http://localhost:8000/docs"
	@echo "💓 Health: http://localhost:8000/health"

down: ## Stop all services
	@echo "🛑 Stopping services..."
	docker-compose down
	@echo "✅ Services stopped!"

build: ## Build Docker images
	@echo "🔨 Building Docker images..."
	docker-compose build
	@echo "✅ Build complete!"

test: ## Run test suite
	@echo "🧪 Running tests..."
	docker-compose exec app pytest tests/ -v --cov=. --cov-report=term-missing
	@echo "✅ Tests complete!"

test-local: ## Run tests locally (requires local Python env)
	@echo "🧪 Running tests locally..."
	pytest tests/ -v --cov=. --cov-report=html
	@echo "✅ Tests complete! Coverage report: htmlcov/index.html"

logs: ## View application logs
	docker-compose logs -f app

logs-all: ## View all service logs
	docker-compose logs -f

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-migrate: ## Run database migrations
	docker-compose exec app python -m alembic upgrade head

clean: ## Clean up containers, volumes, and cache
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete!"

restart: ## Restart all services
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted!"

status: ## Show service status
	docker-compose ps

shell: ## Open shell in app container
	docker-compose exec app /bin/bash

format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	black .
	isort .
	@echo "✅ Formatting complete!"

lint: ## Run linters
	@echo "🔍 Running linters..."
	flake8 . --max-line-length=100 --exclude=venv,__pycache__
	mypy . --ignore-missing-imports
	@echo "✅ Linting complete!"

init: ## Initialize project (create .env from .env.example)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file. Please update with your API keys!"; \
	else \
		echo "⚠️  .env file already exists"; \
	fi

dev: ## Start development environment
	@echo "🔧 Starting development environment..."
	docker-compose up --build

smoke-test: ## Run smoke test
	@echo "🔥 Running smoke test..."
	@echo "Testing health endpoint..."
	@curl -s http://localhost:8000/health | python -m json.tool
	@echo "\nTesting data endpoint..."
	@curl -s "http://localhost:8000/data?page=1&page_size=5" | python -m json.tool
	@echo "\nTesting stats endpoint..."
	@curl -s http://localhost:8000/stats | python -m json.tool
	@echo "\n✅ Smoke test complete!"
