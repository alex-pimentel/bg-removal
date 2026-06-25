# Background Removal API

## 📌 Overview
This project provides a FastAPI endpoint for removing backgrounds from images using the rembg library. The application is containerized using Docker and includes a GitHub Actions CI/CD pipeline.

## 🚀 Features
- FastAPI endpoint for background removal
- Docker containerization
- GitHub Actions CI/CD pipeline
- Redis integration for background processing
- Beszel for lightweight monitoring
- Unit tests for API endpoints

## 📦 Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/bg-removal-api.git
   ```

1. Run with Docker Compose:
   ```bash
   docker compose up -d
   ```

1. Access the API at `http://localhost:8000` and Beszel monitoring at `http://localhost:8090`.