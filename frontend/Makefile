# Makefile for Campaign Analytics Frontend
.PHONY: help install dev build test lint preview clean

help: ## Show this help message
	@echo "Campaign Analytics Frontend - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Node.js dependencies
	npm ci

dev: ## Start development server
	npm run dev

build: ## Build for production
	npm run build

test: ## Run all tests
	npm run test

test-ui: ## Run tests with UI
	npm run test:ui

test-coverage: ## Run tests with coverage
	npm run test -- --coverage

lint: ## Run ESLint
	npm run lint

lint-fix: ## Fix ESLint issues automatically
	npm run lint -- --fix

preview: ## Preview production build locally
	npm run preview

type-check: ## Run TypeScript type checking
	npx tsc --noEmit

clean: ## Clean node_modules and dist
	rm -rf node_modules dist

clean-install: clean install ## Clean install dependencies

deploy-render: ## Instructions for Render deployment
	@echo "To deploy to Render:"
	@echo "1. Push code to GitHub"
	@echo "2. Create Static Site in Render"
	@echo "3. Set VITE_API_URL environment variable"
	@echo "4. Deploy will run automatically"

env-example: ## Copy environment example file
	cp .env.example .env
	@echo "Environment file created. Please edit .env with your settings."

check-build: build ## Check if build works correctly
	@echo "Build completed successfully!"
	@ls -la dist/