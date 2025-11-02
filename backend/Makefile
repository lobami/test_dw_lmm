# Makefile for Campaign Analytics Backend
.PHONY: help install dev test lint migrate seed docker-build docker-up clean

help: ## Show this help message
	@echo "Campaign Analytics Backend - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev: ## Run development server with auto-reload
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run all tests
	pytest -v --cov=app --cov-report=term-missing

test-quiet: ## Run tests quietly
	pytest -q

lint: ## Run code linting
	ruff check .

format: ## Format code with ruff
	ruff format .

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MSG="description")
	alembic revision --autogenerate -m "$(MSG)"

seed: ## Load initial data from CSV files
	python seed.py

clean-tokens: ## Clean up expired refresh tokens
	python scripts/cleanup_refresh_tokens.py

docker-build: ## Build Docker image
	docker build -t campaign-backend:latest .

docker-up: ## Start services with docker-compose
	docker-compose up --build -d

docker-down: ## Stop docker-compose services
	docker-compose down

docker-logs: ## View docker-compose logs
	docker-compose logs -f

deploy-render: ## Instructions for Render deployment
	@echo "To deploy to Render:"
	@echo "1. Push code to GitHub"
	@echo "2. Create Web Service in Render with Docker environment"
	@echo "3. Create PostgreSQL database"
	@echo "4. Set environment variables in Render dashboard"
	@echo "5. Run migration job: alembic upgrade head && python seed.py"

backup: ## Create database backup
	./scripts/backup_db.sh

clean: ## Clean Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
