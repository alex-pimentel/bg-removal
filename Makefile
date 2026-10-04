.PHONY: dev dev-build dev-down prod prod-build prod-down test lint clean \
        act-check act-ci act-quality act-audit

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

# GitHub Actions local simulation (requires act + Docker)
ACT := $(shell command -v act 2>/dev/null || (test -x ./bin/act && echo "./bin/act") || echo "")

act-check:
	@if [ -z "$(ACT)" ]; then \
		echo "act is required. Install:"; \
		echo "  curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash -s -- -b /usr/local/bin"; \
		exit 1; \
	fi

act-ci: act-check
	$(ACT) --bind push -W .github/workflows/ci.yml

act-quality: act-check
	$(ACT) --bind push -W .github/workflows/quality.yml

act-audit: act-check
	$(ACT) --bind workflow_dispatch -W .github/workflows/audit.yml

# Cleanup
clean:
	docker compose -f docker/docker-compose.yml down -v
	docker compose -f docker/docker-compose.prod.yml down -v
	docker system prune -f
