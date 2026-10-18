FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY src/ src/

CMD ["celery", "-A", "src.worker", "worker", "--loglevel=info", "--concurrency=1"]
