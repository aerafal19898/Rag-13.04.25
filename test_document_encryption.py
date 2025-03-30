import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import the DocumentEncryption class
from app.utils.encryption import DocumentEncryption
from app.config import generate_fernet_key

# Generate a test key
key = generate_fernet_key()
print(f"Generated key: {key}")

try:
    # Test creating a DocumentEncryption instance
    document_encryption = DocumentEncryption(key=key)
    print("DocumentEncryption instance created successfully\!")
    
    # Further test: encrypt and decrypt some data
    test_data = "This is a test string to encrypt".encode()
    encrypted = document_encryption.fernet.encrypt(test_data)
    print(f"Encrypted data: {encrypted[:30]}...")
    
    decrypted = document_encryption.fernet.decrypt(encrypted)
    print(f"Decrypted data: {decrypted.decode()}")
    
    assert test_data == decrypted
    print("Encryption/decryption test passed\!")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
