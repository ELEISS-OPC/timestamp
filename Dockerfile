# This Dockerfile is a production-ready container for the Docuisine backend service
# It uses the Astral UV base image with Python 3.12 on Debian Bookworm
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ARG COMMIT_HASH
ARG VERSION

ENV COMMIT_HASH=${COMMIT_HASH}
ENV VERSION=${VERSION}
ENV MODE=production
ENV DEPLOYMENT=docker

COPY timestamp/ ./timestamp/
COPY README.md .
COPY LICENSE .
COPY requirements.txt .

RUN echo "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health/').read())" > healthcheck.py
RUN uv venv
RUN uv pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["uv", "run", "fastapi", "run", "timestamp/main.py", "--host", "0.0.0.0", "--port", "8000"]
