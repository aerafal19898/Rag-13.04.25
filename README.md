# Secure Document RAG Platform

A high-security web application for querying confidential legal documents using DeepSeek R1 with RAG (Retrieval Augmented Generation).

## Enterprise Security Features

- **End-to-end document encryption** with secure in-memory processing
- **Role-based access control (RBAC)** with customizable permission matrix
- **Multi-factor authentication** with app, email, and SMS options
- **Comprehensive audit logging** for enhanced security and compliance
- **Credit-based access system** for usage control and monetization
- **Secure document processing** with sanitization and validation
- **Private API access** with JWT authentication
- **Encrypted document search** with user-based filtering
- **Complete audit trail** for document operations and user actions

## Advanced RAG Features

- Chat interface with streaming response
- Multiple dataset selection with hybrid vector search
- Secure document processing to create custom datasets
- Specialized in legal document processing and retrieval
- Powered by DeepSeek R1 Distill Llama 70B for accurate responses
- Multi-approach document processing with fallback mechanisms

## Requirements

- Python 3.9+
- Flask with JWT authentication
- ChromaDB for vector storage
- HuggingFace Transformers
- Cryptography libraries
- Document processing tools

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables in a `.env` file:

```bash
# API keys
OPENROUTER_API_KEY=your_openrouter_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Security keys (generate with secrets.token_hex())
SECRET_KEY=generate_a_secure_random_key
JWT_SECRET_KEY=generate_another_secure_random_key
DOCUMENT_ENCRYPTION_KEY=generate_a_32_byte_key_for_encryption

# Email settings for feedback and notifications
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your_username
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=noreply@example.com
MAIL_FEEDBACK_RECIPIENT=feedback@example.com

# Optional AWS S3 settings for scalable storage
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
USE_S3_STORAGE=false  # Set to true to use S3

# Optional feature flags
DEBUG=false  # Set to true for development
ENCRYPTION_ENABLED=true
SECURE_PROCESSING=true
ENABLE_AUDIT_LOGGING=true
ALLOW_REGISTRATION=true
REQUIRE_EMAIL_VERIFICATION=false
ADMIN_APPROVAL_REQUIRED=false
```

## Production Deployment

For production deployment, the platform supports various options:

1. **Docker deployment**:
   - Build the Docker image: `docker build -t secure-rag .`
   - Run with environment variables: `docker run -p 5000:5000 --env-file .env secure-rag`

2. **Cloud deployment** (AWS example):
   - Update S3 settings in `.env`
   - Set up an EC2 instance or ECS service
   - Configure auto-scaling based on load
   - Use a load balancer for high availability

3. **On-premises deployment**:
   - Set up a production WSGI server:
   ```bash
   pip install waitress gunicorn
   waitress-serve --port=5000 --call 'run:app'
   ```
   - Use nginx as a reverse proxy for SSL termination

## Development Usage

1. Start the application in development mode:

```bash
python run.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Register an admin account and login

4. Use the interface to:
   - Chat with the AI about legal documents
   - Upload and process confidential documents securely
   - Manage users, permissions, and credits
   - Monitor usage and audit logs

## API Access

The platform provides a secure API for integration with other systems:

```bash
# Get an access token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "user@example.com", "password": "your_password"}'

# Use the token for authenticated requests
curl -X GET http://localhost:5000/api/secure-documents/123 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Full API documentation is available at `/api/docs` when running the application.

## Secure Document Processing

The platform implements multiple layers of security for document processing:

1. **Document encryption**:
   - All uploaded documents are immediately encrypted using Fernet symmetric encryption
   - Document metadata is stored separately from encrypted content
   - Encryption keys are never stored with the documents

2. **In-memory processing**:
   - Documents are processed entirely in memory, never written to disk unencrypted
   - Temporary decryption is done in secure memory buffers
   - Memory is zeroed after processing

3. **User-based access control**:
   - Documents are linked to specific user accounts
   - Role-based permissions determine who can access each document
   - All document access is logged for audit purposes

4. **Secure document viewing**:
   - Temporary access tokens with short expiration times
   - Streaming document delivery to prevent full downloads
   - Watermarking and access tracking

## Comprehensive Security Measures

The platform implements these security best practices:

- **API Security**:
  - JWT-based authentication with short-lived tokens
  - Rate limiting to prevent brute force attacks
  - CORS protections against cross-site request forgery

- **Infrastructure Security**:
  - Optional S3 integration for enterprise storage
  - Load balancer support for high availability
  - Containerized deployment for isolation

- **Compliance Features**:
  - GDPR-compliant user data handling
  - Comprehensive logging for regulatory requirements
  - Credit-based access for controlled usage

## Technologies Used

- **Backend**: Flask with JWT authentication
- **Vector Storage**: ChromaDB for high-performance retrieval
- **Embeddings**: BGE-Large-v1.5 optimized for legal documents
- **Security**: Fernet encryption, bcrypt password hashing
- **Document Processing**: Multi-method extraction with fallbacks
- **LLM Integration**: DeepSeek R1 Distill Llama 70B via OpenRouter

## License

MIT