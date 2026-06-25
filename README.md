# bg-removal

Project Structure

 bg-removal-api/
 ├── app/
 │   ├── main.py
 │   ├── models/
 │   └── utils/
 ├── docker/
 │   └── Dockerfile
 ├── images/
 │   └── test/           <- test images (generate via script)
 ├── scripts/
 │   ├── audit_security.sh
 │   ├── audit_scalability.sh
 │   ├── audit_code_quality.sh
 │   ├── audit_performance.sh
 │   ├── run_all_audits.sh
 │   ├── generate_test_images.py
 │   └── test_images.py
 ├── tests/
 │   └── test_api.py
 ├── .github/
 │   └── workflows/
 │       └── ci-cd.yml
 ├── docs/
 │   └── README.md
 ├── docker-compose.yml
 ├── .dockerignore
 ├── .gitignore
 ├── requirements.txt
 ├── tasks_and_commands.md
 ├── .env
 ├── CONTRIBUTING.md
 ├── SECURITY.md
 ├── LICENCE.md
 └── deploy.sh

---

## Quick Start

```bash
pip install -r requirements.txt
python scripts/generate_test_images.py
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up -d
```

## Running Audits (locally or in CI)

All audits can be run individually or together:

```bash
# Individual audits
bash scripts/audit_security.sh
bash scripts/audit_scalability.sh
bash scripts/audit_code_quality.sh
bash scripts/audit_performance.sh

# All audits sequentially
bash scripts/run_all_audits.sh
```

### What each audit checks

| Audit | Tool | What it checks |
|---|---|---|
| **Security** | bandit, pip-audit | Static security analysis, dependency vulnerabilities |
| **Scalability** | custom | Async patterns, connection pooling, rate limiting, Docker resource limits |
| **Code Quality** | ruff, mypy | Lint, type safety, dead code, hardcoded secrets |
| **Performance** | custom | Import time, blocking calls, caching, compression |

## Testing Images

Generate test images of various sizes, then run them against the API:

```bash
# Generate test images
python scripts/generate_test_images.py

# Test all images against the API
python scripts/test_images.py                           # uses images/test/
python scripts/test_images.py --dir /path/to/images
python scripts/test_images.py --url http://localhost:8000/remove-bg/
python scripts/test_images.py --json                    # JSON output
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --benchmark-only         # performance benchmarks
```
