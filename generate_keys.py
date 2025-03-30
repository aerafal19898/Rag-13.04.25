#!/usr/bin/env python
"""
Script to generate secure keys for the application's .env file.
"""

import os
import secrets
import base64
from cryptography.fernet import Fernet

def generate_secret_key(length=32):
    """Generate a secure random string suitable for SECRET_KEY."""
    return secrets.token_hex(length)

def generate_fernet_key():
    """Generate a Fernet key for encryption."""
    return Fernet.generate_key().decode()

def main():
    # Check if .env already exists
    if os.path.exists('.env'):
        print("Warning: .env file already exists. Creating .env.new instead.")
        env_file = '.env.new'
    else:
        env_file = '.env'
    
    # Read the .env.example file
    with open('.env.example', 'r') as f:
        env_content = f.read()
    
    # Generate keys
    secret_key = generate_secret_key()
    jwt_secret_key = generate_secret_key()
    document_encryption_key = generate_secret_key()
    fernet_key = generate_fernet_key()
    
    # Replace the placeholders
    env_content = env_content.replace('SECRET_KEY=', f'SECRET_KEY={secret_key}')
    env_content = env_content.replace('JWT_SECRET_KEY=', f'JWT_SECRET_KEY={jwt_secret_key}')
    env_content = env_content.replace('DOCUMENT_ENCRYPTION_KEY=', f'DOCUMENT_ENCRYPTION_KEY={document_encryption_key}')
    env_content = env_content.replace('FERNET_KEY=', f'FERNET_KEY={fernet_key}')
    
    # Write to the .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"Generated secure keys and saved to {env_file}")
    print("Make sure to add your API keys and other configuration values.")

if __name__ == '__main__':
    main()