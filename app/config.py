"""
Configuration settings for the Legal Sanctions RAG application.
"""

import os
import secrets
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Document paths
DOCUMENTS_DIR = os.path.join(BASE_DIR, "data", "documents")

# DeepSeek API settings
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"

# OpenRouter API settings
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# Model configurations
MODEL_PROVIDER = os.environ.get("MODEL_PROVIDER", "openrouter")  # "deepseek" or "openrouter"
MODEL_NAME = os.environ.get("MODEL_NAME", "deepseek/deepseek-r1-distill-llama-70b")
EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"  # Good for legal documents
PROCESSING_MODEL = "mistralai/mixtral-8x7b-instruct-v0.1"  # For document processing

# Chroma settings
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma")

# App settings
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
BCRYPT_ROUNDS = 12  # For password hashing
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_hex(32))
JWT_ACCESS_TOKEN_EXPIRES = 60 * 60  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30  # 30 days

# Encryption settings
# Generate a proper Fernet key (url-safe base64-encoded 32-byte key)
import base64
def generate_fernet_key():
    key = base64.urlsafe_b64encode(os.urandom(32))
    return key

DOCUMENT_ENCRYPTION_KEY = os.environ.get("DOCUMENT_ENCRYPTION_KEY", generate_fernet_key())
FERNET_KEY = os.environ.get("FERNET_KEY", "")  # Will be auto-generated if not provided

# Email settings for feedback
MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "")
MAIL_FEEDBACK_RECIPIENT = os.environ.get("MAIL_FEEDBACK_RECIPIENT", "")

# Credit system settings
DEFAULT_CREDITS = int(os.environ.get("DEFAULT_CREDITS", 50))
CREDIT_COST_PER_QUERY = float(os.environ.get("CREDIT_COST_PER_QUERY", 1.0))

# Default datasets
DEFAULT_DATASETS = [
    {"name": "EU-Sanctions", "description": "European Union sanctions regulations and guidelines"},
    {"name": "US-Sanctions", "description": "United States sanctions regulations and guidelines"},
    {"name": "UN-Sanctions", "description": "United Nations sanctions regulations and guidelines"},
]

# Scaling configuration
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))  # 10MB default

# User roles
USER_ROLES = {
    "ADMIN": "admin",
    "USER": "user",
    "GUEST": "guest"
}

# RBAC permissions matrix
ROLE_PERMISSIONS = {
    USER_ROLES["ADMIN"]: ["read", "write", "delete", "manage_users", "manage_system"],
    USER_ROLES["USER"]: ["read", "write"],
    USER_ROLES["GUEST"]: ["read"]
}

# Audit logging
ENABLE_AUDIT_LOGGING = os.environ.get("ENABLE_AUDIT_LOGGING", "True").lower() == "true"
AUDIT_LOG_DIR = os.path.join(BASE_DIR, "data", "audit_logs")

# Amazon S3 settings (for scalable storage)
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.environ.get("AWS_S3_BUCKET", "")
USE_S3_STORAGE = os.environ.get("USE_S3_STORAGE", "False").lower() == "true"

# Document encryption settings
ENCRYPTION_ENABLED = os.environ.get("ENCRYPTION_ENABLED", "True").lower() == "true"
SECURE_PROCESSING = os.environ.get("SECURE_PROCESSING", "True").lower() == "true"

# User registration settings
ALLOW_REGISTRATION = os.environ.get("ALLOW_REGISTRATION", "True").lower() == "true"
REQUIRE_EMAIL_VERIFICATION = os.environ.get("REQUIRE_EMAIL_VERIFICATION", "False").lower() == "true"
ADMIN_APPROVAL_REQUIRED = os.environ.get("ADMIN_APPROVAL_REQUIRED", "False").lower() == "true"

# API rate limiting
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "True").lower() == "true"
RATE_LIMIT_DEFAULT = int(os.environ.get("RATE_LIMIT_DEFAULT", 100))  # Per hour
RATE_LIMIT_AUTH = int(os.environ.get("RATE_LIMIT_AUTH", 10))  # Per minute