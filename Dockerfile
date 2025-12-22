# =============================================================================
# UniAssist Pro - Dockerfile
# =============================================================================
# Simple Dockerfile for DEMO purposes only.
# Docker is OPTIONAL - the MVP runs perfectly without it.
#
# USAGE:
#   docker build -t uniassist-pro .
#   docker run -p 8000:8000 uniassist-pro
#
# NOTE:
#   - No database containers (using in-memory mock data)
#   - No secrets or environment files required
#   - Single container deployment
# =============================================================================

# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
# Set demo secret key (acceptable for MVP, not for production)
ENV SECRET_KEY=mvp-demo-secret-key

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY static/ ./static/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
# Using uvicorn directly for simplicity
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# PRODUCTION DOCKERFILE WOULD INCLUDE:
# =============================================================================
# - Multi-stage build for smaller image
# - Non-root user for security
# - Azure/AWS specific optimizations
# - Health check improvements
# - Secrets management integration
# 
# Example multi-stage build:
# --------------------------
# FROM python:3.11-slim AS builder
# ... install dependencies ...
#
# FROM python:3.11-slim AS runtime
# COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# ... minimal runtime image ...
# =============================================================================
