# Task List: Deploying the Legal Sanctions RAG Application

This document outlines the tasks required to deploy the Legal Sanctions RAG application to a production environment with a custom domain and HTTPS. It builds upon the initial development setup and incorporates best practices for security, scalability, and maintainability.

**Assumptions:**
*   Source code is managed in a Git repository (e.g., GitHub).
*   Target deployment environment is a Linux server (e.g., Ubuntu on a Cloud VM).
*   Familiarity with Docker, Nginx, databases, and basic server administration.

---

## Phase 0: Preparation & Local Setup

*These tasks ensure the codebase is ready for containerization and production configuration.*

-   [x] **Generate `requirements.txt`:** Create a definitive list of all Python dependencies with pinned versions (`pip freeze > requirements.txt`). Ensure development-only dependencies are handled appropriately (e.g., separate `requirements-dev.txt`).
-   [x] **Create `Dockerfile`:**
    -   Use a specific, slim base image (e.g., `python:3.11-slim-bullseye`).
    -   Copy `requirements.txt` and install dependencies in a separate layer to leverage Docker build caching.
    -   Copy application code (`app`, relevant config files, etc.).
    -   Set up a non-root user to run the application.
    -   Define the default command (`CMD` or `ENTRYPOINT`) to run the application using a production server like Gunicorn with Uvicorn workers (e.g., `gunicorn app.services.api_gateway:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000`).
    -   Expose the application port (e.g., `EXPOSE 8000`).
-   [x] **Configure `.dockerignore`:** Exclude unnecessary files/directories (`.git`, `__pycache__`, `.venv`, temporary data, etc.) from the Docker build context.
-   [x] **Local Docker Testing:** Build the image (`docker build`) and run the container (`docker run`), ensuring it starts correctly and necessary ports are exposed. Test basic connectivity if possible.
-   [x] **Setup Database Migration Tool:** Initialize Alembic (or chosen alternative) to manage PostgreSQL schema changes based on your models (likely requiring an ORM like SQLAlchemy or adapting SQL scripts). Create initial migration script.

---

## Phase 1: Core Infrastructure Setup (Server-Side)

*Provisioning and configuring the necessary server-side components.*

-   [x] **Provision Server:** Set up a virtual machine or cloud instance (e.g., AWS EC2, GCP Compute Engine, DigitalOcean Droplet) with your chosen Linux distribution (e.g., Ubuntu 22.04).
-   [x] **Basic Server Setup:**
    -   Configure firewall rules (allowing SSH, HTTP, HTTPS).
    -   Install essential packages (e.g., `docker`, `docker-compose`, `nginx`, `certbot` with its Nginx plugin).
    -   Enable necessary services (`docker`, `nginx`).
-   [x] **Setup PostgreSQL Database:**
    -   Install PostgreSQL server OR provision a managed database service (e.g., AWS RDS, Google Cloud SQL).
    *   Create a dedicated database and user for the RAG application.
    *   Configure secure access (strong passwords, network rules limiting access, ideally configure TLS).
    *   Note down connection details (host, port, user, password, database name).
-   [x] **Setup Redis Instance:**
    -   Install Redis server OR provision a managed Redis service.
    *   Configure password authentication (`requirepass`).
    *   Configure memory limits (`maxmemory`) and eviction policy (`maxmemory-policy`, e.g., `allkeys-lru`).
    *   Ensure Redis is only accessible from the application server (network rules).
    *   Note down connection details (host, port, password).
-   [x] **Setup Production ChromaDB:**
    -   Use Docker Compose or Kubernetes to run the official ChromaDB container.
    -   Mount a persistent volume to store the vector data (`/chroma/chroma`).
    -   Configure network access so only the application server can reach ChromaDB.
    -   Note down the internal access endpoint (e.g., `http://chromadb:8000` if using Docker Compose networking).

---

## Phase 2: Application Configuration for Production

*Modifying the application code and configuration to work with the production infrastructure.*

-   [x] **Implement Secret Management:**
    -   Remove ALL hardcoded secrets (DB passwords, Redis passwords, JWT secret key, external API keys like DeepSeek) from the codebase and configuration files.
    -   Plan to inject secrets via environment variables during container runtime (preferred method).
-   [x] **Update Application Configuration (`ConfigManager` / Environment):**
    -   Ensure configuration can read database, Redis, and ChromaDB connection details from environment variables.
    -   Set `API_DEBUG=False` or equivalent production flag.
    -   Configure production logging (structured JSON format recommended, appropriate log level).
-   [x] **Integrate PostgreSQL:**
    -   If not already using an ORM, adapt `DatabaseManager` (or introduce SQLAlchemy/similar) to connect to PostgreSQL using environment variables.
    -   Ensure all SQL queries are compatible with PostgreSQL syntax.
-   [x] **Integrate Redis:**
    -   Update `AuthService` and `CacheManager` (or use a library like `fastapi-session`) to connect to the production Redis instance using environment variables.
    -   Ensure all code using caching handles potential connection issues gracefully (though in production, connection should be reliable).
-   [x] **Integrate Production ChromaDB:**
    -   Update code (likely `DatabaseManager` or `VectorStoreManager`) to connect to the production ChromaDB instance using its configured endpoint (via environment variable).

---

## Phase 3: Deployment & Networking

*Getting the container running on the server and accessible via the custom domain.*

-   [x] **Initial Container Deployment:** Copy the application code/Dockerfile to the server (or use CI/CD later) and build the image. Run the container using `docker run` or `docker-compose up`, injecting production environment variables (especially secrets).
-   [x] **Run Initial Database Migrations:** Execute the Alembic (or chosen tool) command inside the running container or via an entrypoint script to apply the initial database schema to PostgreSQL (`alembic upgrade head`).
-   [x] **Configure Nginx:**
    -   Create an Nginx server block for your domain listening on port 80.
    -   Configure `proxy_pass` to forward requests (e.g., for `/api/`) to the running application container (e.g., `http://127.0.0.1:8000` or the container's internal IP/port).
    -   Set necessary proxy headers (`Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`).
    -   Reload Nginx (`sudo systemctl reload nginx`). Test HTTP access.
-   [ ] **Configure DNS:**
    -   Go to your domain registrar/DNS provider.
    -   Create an `A` record pointing your domain (`yourdomain.com`) and subdomain (`www.yourdomain.com` or `api.yourdomain.com`) to your server's public IP address.
-   [ ] **Enable HTTPS with Certbot:**
    -   Run `sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com` (adjust domains as needed). Follow prompts to obtain and install SSL certificates. Certbot should automatically modify your Nginx config to handle port 443 and SSL termination.
    -   Verify automatic renewal is scheduled (`sudo systemctl list-timers | grep certbot` or check cron jobs).
    -   Test HTTPS access (`https://yourdomain.com`).

---

## Phase 4: Automation & Observability (CI/CD, Monitoring)

*Making the deployment process repeatable and adding visibility.*

-   [ ] **Setup CI Pipeline (e.g., GitHub Actions):**
    -   Trigger on push/pull request to main branches.
    -   Run linters (e.g., Flake8, Black).
    -   Run unit tests.
    -   *Optional but Recommended:* Run integration tests using service containers (PostgreSQL, Redis via Docker Compose `services`).
    -   Build Docker image.
    -   Push tagged image to a container registry (Docker Hub, GHCR, etc.).
-   [ ] **Setup CD Pipeline (e.g., GitHub Actions):**
    -   Trigger on merge/push to the main branch (or manually).
    -   Securely connect to the production server (SSH keys stored as secrets).
    -   Pull the latest Docker image from the registry.
    -   **Run database migrations (`alembic upgrade head`) *before* starting the new container.**
    -   Stop the old container and start the new one (implement rolling or blue-green later for zero downtime).
-   [ ] **Setup Monitoring:**
    -   Instrument FastAPI application using `prometheus-fastapi-instrumentator` or similar to expose a `/metrics` endpoint. Include RAG-specific metrics (ChromaDB latency, external API latency/errors).
    -   Install and configure Prometheus to scrape the `/metrics` endpoint.
    -   Install and configure Grafana, connect it to Prometheus, and build dashboards to visualize key application and RAG metrics.
-   [ ] **Setup Rate Limiting:**
    -   Integrate middleware like `fastapi-limiter` into the FastAPI app.
    -   Configure limits (e.g., per IP, potentially per user ID if available early in request) backed by the production Redis instance.
-   [ ] **Configure Log Aggregation (Optional but Recommended):**
    -   Configure the application container to output structured logs (JSON) to `stdout/stderr`.
    -   Set up a log collector (e.g., Promtail, Fluentd) to ship logs to a centralized system (e.g., Loki, Elasticsearch).

---

## Phase 5: Application-Specific RAG Components & Strategy

*Implementing and refining the core RAG functionality for production.*

-   [ ] **Implement `VectorStoreManager`:** Replace the placeholder `vector_store.py` with actual logic to interact with the production ChromaDB instance (create/delete collections, add/query embeddings). Refactor `DatabaseManager` if necessary to use this service.
-   [ ] **Implement Document Ingestion/Update Pipeline:**
    -   Design and implement the process for monitoring sources of legal sanctions documents.
    *   Implement the pipeline steps: Document fetching, processing (`DocumentProcessor`), embedding generation, and upserting into the production ChromaDB via `VectorStoreManager`.
    *   Determine how this pipeline will be triggered (manual, scheduled job, webhook, part of CD).
-   [ ] **Define & Implement Backup Strategy:**
    -   Implement automated, regular backups for the PostgreSQL database.
    -   Implement automated, regular backups for the ChromaDB persistent volume (e.g., volume snapshots).
    -   Test the restore process for both databases.
-   [ ] **Refine RAG-Specific Monitoring:** Ensure the dashboards created in Phase 4 effectively visualize the RAG pipeline's health and performance.
-   [ ] **Implement `BackupManager` (Optional):** Replace the placeholder `backup_manager.py` if specific application-level backup coordination logic is needed beyond infrastructure backups. (Infrastructure backups are usually sufficient).

---

This task list provides a detailed path forward. Remember to tackle these items sequentially, testing thoroughly at each stage. Good luck! 