# Campaign Analytics - Root Makefile
# Manage both backend and frontend from project root

.PHONY: help install dev build test clean docker-up docker-down deploy-info

help: ## Show this help message
	@echo "Campaign Analytics - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (backend + frontend)
	@echo "Installing backend dependencies..."
	cd backend && make install
	@echo "Installing frontend dependencies..."
	cd frontend && make install

dev: ## Start both backend and frontend in development mode
	@echo "Starting development servers..."
	@echo "Backend will be available at: http://localhost:8000"
	@echo "Frontend will be available at: http://localhost:5173"
	@echo "API Docs available at: http://localhost:8000/docs"
	@echo ""
	@echo "Starting backend in background..."
	cd backend && make dev &
	@echo "Waiting 3 seconds for backend to start..."
	sleep 3
	@echo "Starting frontend..."
	cd frontend && make dev

build: ## Build frontend for production
	cd frontend && make build

test: ## Run all tests (backend + frontend)
	@echo "Running backend tests..."
	cd backend && make test
	@echo "Running frontend tests..."
	cd frontend && make test

lint: ## Run linting for both projects
	@echo "Linting backend..."
	cd backend && make lint
	@echo "Linting frontend..."
	cd frontend && make lint

clean: ## Clean all build artifacts and dependencies
	cd backend && make clean
	cd frontend && make clean

setup-env: ## Copy environment example files
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "Environment files created. Please edit them with your settings."

migrate: ## Run database migrations
	cd backend && make migrate

seed: ## Load initial data
	cd backend && make seed

docker-up: ## Start services with docker-compose
	cd backend && make docker-up

docker-down: ## Stop docker-compose services
	cd backend && make docker-down

deploy-info: ## Show deployment information
	@echo "=== Campaign Analytics Deployment Guide ==="
	@echo ""
	@echo "Backend (Render Web Service):"
	@echo "- Environment: Docker"
	@echo "- Root Directory: backend"
	@echo "- Required ENV vars: DATABASE_URL, SECRET_KEY, FRONTEND_ORIGINS"
	@echo ""
	@echo "Frontend (Render Static Site):"
	@echo "- Environment: Node"
	@echo "- Root Directory: frontend"
	@echo "- Required ENV vars: VITE_API_URL"
	@echo ""
	@echo "See README.md for complete deployment instructions."

check: ## Run all checks (lint, test, build)
	make lint
	make test
	make build
	@echo "All checks passed! ✅"
