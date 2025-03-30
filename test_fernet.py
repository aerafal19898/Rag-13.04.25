import base64
import os
from cryptography.fernet import Fernet

def generate_fernet_key():
    key = base64.urlsafe_b64encode(os.urandom(32))
    return key

# Generate a new key
key = generate_fernet_key()
print(f"Generated key: {key}")

# Test creating a Fernet instance
fernet = Fernet(key)
print("Fernet instance created successfully")

# Test encryption/decryption
test_data = b"Test encryption data"
encrypted = fernet.encrypt(test_data)
print(f"Encrypted: {encrypted}")

decrypted = fernet.decrypt(encrypted)
print(f"Decrypted: {decrypted}")

assert test_data == decrypted
print("Encryption/decryption test passed\!")
