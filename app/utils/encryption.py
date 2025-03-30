"""
Encryption utilities for secure document handling.
"""

import os
import base64
import json
import time
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, Union, BinaryIO
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class DocumentEncryption:
    """Handles encryption and decryption of documents and metadata."""
    
    def __init__(self, key: Optional[str] = None, storage_dir: Optional[str] = None):
        """Initialize the encryption handler.
        
        Args:
            key: Optional encryption key. If not provided, will be generated or loaded.
            storage_dir: Directory for storing encryption keys.
        """
        # Set up storage directory
        if storage_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            storage_dir = os.path.join(base_dir, "data", "secure")
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize or load key
        self.key = self._initialize_key(key)
        self.fernet = Fernet(self.key)
        
        # Create a directory for encrypted documents
        self.encrypted_dir = os.path.join(self.storage_dir, "encrypted")
        os.makedirs(self.encrypted_dir, exist_ok=True)
    
    def _initialize_key(self, key: Optional[str]) -> bytes:
        """Initialize or load the encryption key.
        
        Args:
            key: Optional encryption key to use.
            
        Returns:
            Bytes representation of the key.
        """
        key_file = os.path.join(self.storage_dir, "encryption_key.key")
        
        if key:
            # Use provided key
            # Handle different key formats
            if isinstance(key, str) and str(key).startswith("b'") and str(key).endswith("'"):
                # Handle string representation of bytes
                encoded_key = eval(key)
            elif isinstance(key, str):
                encoded_key = key.encode()
            else:
                encoded_key = key
                
            # Save key to disk
            with open(key_file, 'wb') as f:
                f.write(encoded_key)
            return encoded_key
        
        # If no key provided, try to load existing key or generate a new one
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        
        # Generate a new key
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        
        return key
    
    def encrypt_file(self, file_path: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Encrypt a file and store metadata.
        
        Args:
            file_path: Path to the file to encrypt
            user_id: Optional user ID to associate with the file
            
        Returns:
            Dictionary with metadata about the encrypted file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file metadata
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Generate encrypted file ID
        encrypted_id = f"enc_{int(time.time())}_{secrets.token_hex(8)}"
        
        # Read and encrypt the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
            encrypted_data = self.fernet.encrypt(file_data)
        
        # Save encrypted file
        encrypted_file_path = os.path.join(self.encrypted_dir, f"{encrypted_id}.enc")
        with open(encrypted_file_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Create metadata
        metadata = {
            "id": encrypted_id,
            "original_name": file_name,
            "encrypted_path": encrypted_file_path,
            "original_size": file_size,
            "encrypted_size": len(encrypted_data),
            "extension": file_extension,
            "mime_type": self._get_mime_type(file_extension),
            "encrypted_at": time.time(),
            "user_id": user_id,
            "checksum": self._generate_checksum(file_data)
        }
        
        # Save metadata
        metadata_file = os.path.join(self.storage_dir, f"{encrypted_id}.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def decrypt_file(self, encrypted_id: str, output_path: Optional[str] = None) -> Union[bytes, str]:
        """Decrypt a file by ID.
        
        Args:
            encrypted_id: ID of the encrypted file
            output_path: Optional path to save the decrypted file
            
        Returns:
            Decrypted file content as bytes, or path to the decrypted file
        """
        # Load metadata
        metadata_file = os.path.join(self.storage_dir, f"{encrypted_id}.json")
        if not os.path.exists(metadata_file):
            raise FileNotFoundError(f"Encrypted file metadata not found: {encrypted_id}")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        encrypted_file_path = metadata.get("encrypted_path")
        if not encrypted_file_path or not os.path.exists(encrypted_file_path):
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
        
        # Read and decrypt the file
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
        
        # Save to output path if specified
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            return output_path
        
        return decrypted_data
    
    def decrypt_to_memory(self, encrypted_id: str) -> bytes:
        """Decrypt a file to memory.
        
        Args:
            encrypted_id: ID of the encrypted file
            
        Returns:
            Decrypted file content as bytes
        """
        return self.decrypt_file(encrypted_id)
    
    def get_file_metadata(self, encrypted_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for an encrypted file.
        
        Args:
            encrypted_id: ID of the encrypted file
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata_file = os.path.join(self.storage_dir, f"{encrypted_id}.json")
        if not os.path.exists(metadata_file):
            return None
        
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    def list_encrypted_files(self, user_id: Optional[str] = None) -> list:
        """List all encrypted files, optionally filtered by user.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of file metadata dictionaries
        """
        files = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json') and not filename.startswith('encryption_key'):
                file_path = os.path.join(self.storage_dir, filename)
                
                with open(file_path, 'r') as f:
                    metadata = json.load(f)
                    
                    # Filter by user_id if provided
                    if user_id is None or metadata.get("user_id") == user_id:
                        files.append(metadata)
        
        return files
    
    def delete_encrypted_file(self, encrypted_id: str) -> bool:
        """Delete an encrypted file and its metadata.
        
        Args:
            encrypted_id: ID of the encrypted file
            
        Returns:
            True if deletion was successful, False otherwise
        """
        metadata = self.get_file_metadata(encrypted_id)
        if not metadata:
            return False
        
        # Delete encrypted file
        encrypted_file_path = metadata.get("encrypted_path")
        if encrypted_file_path and os.path.exists(encrypted_file_path):
            os.remove(encrypted_file_path)
        
        # Delete metadata file
        metadata_file = os.path.join(self.storage_dir, f"{encrypted_id}.json")
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
        
        return True
    
    def _get_mime_type(self, extension: str) -> str:
        """Get MIME type from file extension."""
        mime_types = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.html': 'text/html',
            '.htm': 'text/html'
        }
        
        return mime_types.get(extension.lower(), 'application/octet-stream')
    
    def _generate_checksum(self, data: bytes) -> str:
        """Generate a checksum for data integrity validation."""
        hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
        hasher.update(data)
        return base64.b64encode(hasher.finalize()).decode('utf-8')


class SecureTemporaryAccess:
    """Manages secure temporary access to decrypted documents."""
    
    def __init__(self, encryption_handler: DocumentEncryption):
        """Initialize secure access handler.
        
        Args:
            encryption_handler: DocumentEncryption instance
        """
        self.encryption_handler = encryption_handler
        self.temp_dir = os.path.join(self.encryption_handler.storage_dir, "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Clean up any old temporary files
        self._cleanup_temp_files()
    
    def get_temporary_access(self, encrypted_id: str, max_age_seconds: int = 300) -> Dict[str, Any]:
        """Provide temporary access to a decrypted document.
        
        Args:
            encrypted_id: ID of the encrypted file
            max_age_seconds: Maximum age of temporary file in seconds
            
        Returns:
            Dict with temp file info
        """
        # Get metadata
        metadata = self.encryption_handler.get_file_metadata(encrypted_id)
        if not metadata:
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_id}")
        
        # Generate a random token for this access
        access_token = secrets.token_hex(16)
        
        # Create temporary filename
        original_name = metadata.get("original_name", "document")
        extension = metadata.get("extension", "")
        temp_filename = f"temp_{access_token}{extension}"
        temp_path = os.path.join(self.temp_dir, temp_filename)
        
        # Decrypt to temporary file
        self.encryption_handler.decrypt_file(encrypted_id, temp_path)
        
        # Create access record
        expires_at = time.time() + max_age_seconds
        
        access_info = {
            "access_token": access_token,
            "encrypted_id": encrypted_id,
            "temp_path": temp_path,
            "expires_at": expires_at,
            "original_name": original_name,
            "mime_type": metadata.get("mime_type", "application/octet-stream")
        }
        
        # Save access record
        access_file = os.path.join(self.temp_dir, f"{access_token}.json")
        with open(access_file, 'w') as f:
            json.dump(access_info, f, indent=2)
        
        return access_info
    
    def verify_access(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Verify access token and return access info if valid.
        
        Args:
            access_token: Access token
            
        Returns:
            Access info dict or None if invalid/expired
        """
        access_file = os.path.join(self.temp_dir, f"{access_token}.json")
        if not os.path.exists(access_file):
            return None
        
        with open(access_file, 'r') as f:
            access_info = json.load(f)
        
        # Check if expired
        if access_info.get("expires_at", 0) < time.time():
            # Clean up expired access
            self._revoke_access(access_token)
            return None
        
        # Check if temporary file exists
        temp_path = access_info.get("temp_path")
        if not temp_path or not os.path.exists(temp_path):
            self._revoke_access(access_token)
            return None
        
        return access_info
    
    def revoke_access(self, access_token: str) -> bool:
        """Explicitly revoke access.
        
        Args:
            access_token: Access token to revoke
            
        Returns:
            True if access was revoked, False otherwise
        """
        return self._revoke_access(access_token)
    
    def _revoke_access(self, access_token: str) -> bool:
        """Internal method to revoke access and clean up files.
        
        Args:
            access_token: Access token
            
        Returns:
            True if access was revoked, False otherwise
        """
        access_file = os.path.join(self.temp_dir, f"{access_token}.json")
        if not os.path.exists(access_file):
            return False
        
        # Load access info to get temporary file path
        with open(access_file, 'r') as f:
            access_info = json.load(f)
        
        # Delete temporary file
        temp_path = access_info.get("temp_path")
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        
        # Delete access file
        try:
            os.remove(access_file)
        except Exception:
            return False
        
        return True
    
    def _cleanup_temp_files(self, max_age_hours: int = 24) -> None:
        """Clean up old temporary files.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        
        # Clean up access files and their associated temp files
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            
            # Process access records
            if filename.endswith('.json'):
                try:
                    with open(file_path, 'r') as f:
                        access_info = json.load(f)
                    
                    # Check if expired
                    if access_info.get("expires_at", 0) < current_time:
                        self._revoke_access(access_info.get("access_token"))
                except Exception:
                    # If we can't read the file, just delete it
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
            
            # Process orphaned temp files (fallback cleanup)
            elif filename.startswith('temp_'):
                # Check file age
                file_age = current_time - os.path.getctime(file_path)
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass