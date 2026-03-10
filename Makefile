.PHONY: help install dev up down test clean seed migrate

help:
	@echo "Contract Compliance Checker - Available Commands:"
	@echo ""
	@echo "  make install    - Install all dependencies (backend & frontend)"
	@echo "  make dev        - Run development servers locally"
	@echo "  make up         - Start all services with Docker Compose"
	@echo "  make down       - Stop all Docker services"
	@echo "  make test       - Run backend tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make seed       - Seed database with sample clauses"
	@echo "  make clean      - Clean up generated files and caches"
	@echo ""

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✓ Installation complete!"

dev:
	@echo "Starting development servers..."
	@echo "Make sure PostgreSQL is running with pgvector extension"
	@echo ""
	@echo "Starting backend on http://localhost:8000"
	@echo "Starting frontend on http://localhost:3000"
	@echo ""
	cd backend && cp .env.example .env || true
	cd frontend && cp .env.local.example .env.local || true
	@echo "Run these commands in separate terminals:"
	@echo "  Terminal 1: cd backend && uvicorn app.main:app --reload"
	@echo "  Terminal 2: cd frontend && npm run dev"

up:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d
	@echo ""
	@echo "✓ Services started!"
	@echo "  Backend API: http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API Docs: http://localhost:8000/docs"

down:
	@echo "Stopping Docker services..."
	docker-compose down
	@echo "✓ Services stopped!"

test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v
	@echo "✓ Tests complete!"

migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head
	@echo "✓ Migrations complete!"

seed:
	@echo "Seeding database with sample clauses..."
	cd backend && python seed_data.py
	@echo "✓ Database seeded!"

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/uploads/* 2>/dev/null || true
	@echo "✓ Cleanup complete!"

logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

restart:
	@echo "Restarting services..."
	docker-compose restart
	@echo "✓ Services restarted!"
