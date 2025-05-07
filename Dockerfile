# 1. Use a specific Python base image
FROM python:3.11-slim-bullseye AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# --- Dependency Installation Stage ---
FROM base AS builder

# Install system dependencies if needed (e.g., for psycopg2, libmagic)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Application Stage ---
FROM base AS final

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
WORKDIR /app

# Copy application code
# Ensure the paths here match your project structure
COPY ./app ./app

# Copy Alembic migrations files
COPY alembic.ini .
COPY alembic ./alembic

# Expose the port the app runs on
EXPOSE 8000

# Define the default command to run migrations then start the application
CMD ["sh", "-c", "alembic upgrade head && gunicorn app.services.api_gateway:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000"]

# --- Kubernetes/Helm Notes ---
# For Kubernetes deployment:
# 1. Build and push this image to a container registry (e.g., Docker Hub, GCR, ECR).
# 2. Create Kubernetes Deployment and Service manifests (e.g., in a 'kubernetes/' directory).
# 3. Define environment variables, secrets, volumes, and resource requests/limits in the manifests.
# 4. Consider using Helm charts (e.g., in a 'helm/' directory) for templating and managing Kubernetes resources.
# 5. Configure Horizontal Pod Autoscaler (HPA) based on CPU/memory usage or custom metrics.