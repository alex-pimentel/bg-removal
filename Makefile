.PHONY: dev dev-build dev-down prod prod-build prod-down test lint clean

# Development
dev:
	docker compose -f docker/docker-compose.yml up

dev-build:
	docker compose -f docker/docker-compose.yml up --build

dev-down:
	docker compose -f docker/docker-compose.yml down

# Production
prod:
	docker compose -f docker/docker-compose.prod.yml up -d

prod-build:
	docker compose -f docker/docker-compose.prod.yml up -d --build

prod-down:
	docker compose -f docker/docker-compose.prod.yml down

# Testing
test:
	docker compose -f docker/docker-compose.yml exec api pytest

# Linting
lint:
	docker compose -f docker/docker-compose.yml exec api ruff check src/

# Cleanup
clean:
	docker compose -f docker/docker-compose.yml down -v
	docker compose -f docker/docker-compose.prod.yml down -v
	docker system prune -f
