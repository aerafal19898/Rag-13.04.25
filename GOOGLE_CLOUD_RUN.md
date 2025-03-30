# Deploying to Google Cloud Run

This guide walks through deploying the Legal Sanctions RAG application to Google Cloud Run.

## Prerequisites

1. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
2. [Docker](https://docs.docker.com/get-docker/) installed
3. A Google Cloud project with billing enabled
4. Necessary API keys (OpenRouter, DeepSeek, etc.)

## Deployment Steps

### 1. Set Up Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Create a Docker Repository

```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create legal-sanctions-rag \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Legal Sanctions RAG"
```

### 3. Store Secrets in Secret Manager

Each environment variable from your `.env` file needs to be stored as a secret:

```bash
# Example for storing API keys
gcloud secrets create OPENROUTER_API_KEY --data-file=- <<< "your-api-key"
gcloud secrets create DEEPSEEK_API_KEY --data-file=- <<< "your-api-key"
gcloud secrets create SECRET_KEY --data-file=- <<< "your-secret-key"
gcloud secrets create JWT_SECRET_KEY --data-file=- <<< "your-jwt-secret-key"
gcloud secrets create DOCUMENT_ENCRYPTION_KEY --data-file=- <<< "your-encryption-key"
gcloud secrets create FERNET_KEY --data-file=- <<< "your-fernet-key"
# Add other secrets as needed
```

### 4. Build and Push Docker Image

```bash
# Configure Docker to use Google Cloud credentials
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build the Docker image
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/legal-sanctions-rag/app:latest .

# Push the image to Google Artifact Registry
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/legal-sanctions-rag/app:latest
```

### 5. Deploy to Cloud Run

```bash
gcloud run deploy legal-sanctions-rag \
    --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/legal-sanctions-rag/app:latest \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated \
    --cpu=2 \
    --memory=4Gi \
    --port=5000 \
    --set-env-vars=HOST=0.0.0.0,PORT=5000,DEBUG=False \
    --update-secrets=OPENROUTER_API_KEY=OPENROUTER_API_KEY:latest,DEEPSEEK_API_KEY=DEEPSEEK_API_KEY:latest,SECRET_KEY=SECRET_KEY:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,DOCUMENT_ENCRYPTION_KEY=DOCUMENT_ENCRYPTION_KEY:latest,FERNET_KEY=FERNET_KEY:latest
```

Customize the CPU and memory settings based on your application needs.

### 6. Set Up Persistent Storage

Since Cloud Run is stateless, you need persistent storage for your documents and database:

**Option A: Use Google Cloud Storage**

1. Create a bucket:
   ```bash
   gsutil mb -l us-central1 gs://your-bucket-name/
   ```

2. Update your application to use GCS for storage or modify the Docker image to mount a Cloud Storage FUSE filesystem.

**Option B: Use a Separate Database Service**

1. Set up a Firestore or another database service for document storage.
2. Update your application configuration to use this service.

### 7. Set Up a Custom Domain (Optional)

```bash
# Map your domain to the Cloud Run service
gcloud beta run domain-mappings create \
    --service=legal-sanctions-rag \
    --domain=yourdomain.com \
    --region=us-central1
```

Follow the DNS verification steps provided by Google Cloud.

## Monitoring and Logging

Cloud Run automatically sends logs to Google Cloud Logging:

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=legal-sanctions-rag" --limit=10
```

You can set up log-based alerts from the Google Cloud Console.

## Scaling and Cost Considerations

- Cloud Run scales to zero when not in use, helping to manage costs
- Set min and max instances based on expected traffic:
  ```bash
  gcloud run services update legal-sanctions-rag \
      --min-instances=1 \
      --max-instances=10
  ```
- Monitor your usage and costs through Google Cloud Console

## Maintenance

- Set up continuous deployment using Cloud Build
- Create a build trigger connected to your repository
- Implement automated testing before deployment