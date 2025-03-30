# Deployment Guide

This document provides instructions for deploying the Legal Sanctions RAG application in various environments.

## Prerequisites

- Python 3.11+
- pip
- Docker and Docker Compose (for containerized deployment)
- Access to environment variables (API keys, etc.)

## Local Deployment

### Using Python directly

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and fill in the required values.

4. Run the application:
   ```bash
   python run.py
   ```

### Using Docker Compose

1. Create a `.env` file based on `.env.example` and fill in the required values.

2. Build and start the container:
   ```bash
   docker-compose up -d
   ```

3. The application will be available at http://localhost:5000

## Production Deployment Options

### 1. Cloud VM Deployment (AWS EC2, Google Compute Engine, etc.)

1. Set up a VM with Python 3.11+
2. Clone the repository
3. Follow the local deployment steps above
4. Set up a reverse proxy (Nginx) and SSL (Let's Encrypt)
5. Use systemd or supervisor to manage the application process

### 2. Platform as a Service (PaaS)

#### Heroku

1. Install the Heroku CLI
2. Create a `Procfile` with:
   ```
   web: python run.py
   ```
3. Set environment variables in Heroku dashboard
4. Deploy with:
   ```bash
   git push heroku main
   ```

#### Render

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python run.py`
4. Configure environment variables

### 3. Containerized Deployment

#### AWS Elastic Container Service (ECS)

1. Create an ECR repository
2. Build and push the Docker image
3. Create an ECS cluster, task definition, and service
4. Configure environment variables in the task definition

#### Google Cloud Run

1. Build and push the Docker image to Google Container Registry
2. Deploy to Cloud Run with environment variables

## Database Considerations

This application uses local file storage for ChromaDB. For production, consider:

1. Using persistent volumes for Docker deployments
2. Setting up a managed database for production use
3. Implementing regular backups

## Environment Variable Security

For production:
1. Never commit `.env` files to version control
2. Use secret management services (AWS Secrets Manager, GCP Secret Manager)
3. Rotate secrets regularly

## Monitoring and Logging

1. Configure application logging to an external service (CloudWatch, Stackdriver)
2. Set up monitoring for the application health and performance
3. Implement alerting for critical errors