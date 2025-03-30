import sys
import os
from pathlib import Path

# Add the project root directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

from app.config import generate_fernet_key
from app.utils.encryption import DocumentEncryption

# Test if the encryption works
key = generate_fernet_key()
print(f"Generated key: {key}")

try:
    # Create a DocumentEncryption instance
    document_encryption = DocumentEncryption(key=key)
    print("DocumentEncryption instance created successfully\!")
    
    # Try importing app.main
    print("Trying to import app.main...")
    from app.main import document_encryption as app_document_encryption
    print("Successfully imported app.main\!")
    
    # Check if document_encryption is properly initialized
    print(f"App document_encryption was properly initialized: {app_document_encryption is not None}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
