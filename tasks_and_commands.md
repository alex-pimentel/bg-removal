- [ ] **Project Setup & Core Functionality**
  - [ ] Create project structure
  - [ ] Create `requirements.txt`
  - [ ] Create `app/main.py` (FastAPI endpoint)
  - [ ] Create `docker/Dockerfile`
  - [ ] Create `docker/docker-compose.yml`
  - [ ] Create `.github/workflows/ci-cd.yml` (GitHub Actions)

- [ ] **Scalability & Backend Integration**
  - [ ] Create `app/utils/queue_utils.py` (Redis integration)
  - [ ] Create `tests/test_api.py` (Unit tests)
  - [ ] Create `app/utils/utils.py` (Helper functions)
  - [ ] Create `docs/README.md` (Project documentation)

- [ ] **Deployment & Optimization**
  - [ ] Create `docker-compose.yml` (Docker setup)
  - [ ] Create `deploy.sh` (Deployment script)
  - [ ] Add `beszel` to `docker-compose.yml` (Lightweight monitoring)
  - [ ] Create `logs/` directory (Log storage)

- [ ] **Additional Files**
  - [ ] Create `.env` (Environment variables)
  - [ ] Create `CONTRIBUTING.md` (Contribution guidelines)
  - [ ] Create `SECURITY.md` (Security guidelines)
  - [ ] Create `LICENSE` (License file)


### 📌 Commands to Run
- `docker compose up -d` - Run the application locally
- `docker build -t bg-removal-api -f docker/Dockerfile .` - Build the Docker image
- `docker run -p 8000:8000 bg-removal-api` - Run the Docker container
- `pytest tests/` - Run unit tests
- `pip install -r requirements.txt` - Install dependencies
- `uvicorn app.main:app --reload` - Run the app in development mode
- `git commit -am "Initial commit" && git push origin main` - Commit and push changes