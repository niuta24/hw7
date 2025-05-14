FROM python:3.10-slim

RUN pip install --no-cache-dir uvicorn fastapi celery redis requests

WORKDIR /app
COPY app /app
