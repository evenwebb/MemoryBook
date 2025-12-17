.PHONY: help build up down restart logs clean init-db

help:
	@echo "MemoryBook - Self-hostable Image Gallery"
	@echo ""
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs        - View logs"
	@echo "  make clean       - Remove containers and volumes"
	@echo "  make init-db    - Initialize database with default categories"
	@echo "  make shell-backend - Open shell in backend container"
	@echo "  make shell-frontend - Open shell in frontend container"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

init-db:
	docker-compose exec backend python -m app.core.init_db

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

