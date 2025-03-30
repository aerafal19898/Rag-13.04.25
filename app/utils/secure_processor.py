"""
Secure document processor module for handling sensitive information.
"""

import os
import io
import json
import shutil
import tempfile
import logging
from typing import List, Dict, Any, Optional, BinaryIO, Union
from pathlib import Path

from app.utils.encryption import DocumentEncryption, SecureTemporaryAccess
from app.utils.document_processor import LegalDocumentProcessor

class SecureDocumentProcessor:
    """Process documents securely in memory with encryption."""
    
    def __init__(
        self,
        encryption_handler: Optional[DocumentEncryption] = None,
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        chroma_path: Optional[str] = None,
        device: str = "cpu"
    ):
        """Initialize the secure document processor.
        
        Args:
            encryption_handler: Optional encryption handler
            embedding_model: Name of the embedding model
            chroma_path: Path to ChromaDB
            device: Device to use for embeddings
        """
        # Set up encryption handler
        if encryption_handler is None:
            self.encryption = DocumentEncryption()
        else:
            self.encryption = encryption_handler
        
        # Initialize secure temporary access
        self.temp_access = SecureTemporaryAccess(self.encryption)
        
        # Set up base directory and ChromaDB path
        base_dir = Path(__file__).resolve().parent.parent.parent
        if chroma_path is None:
            chroma_path = os.path.join(base_dir, "data", "chroma")
        
        # Initialize document processor with provided settings
        self.doc_processor = LegalDocumentProcessor(
            embedding_model=embedding_model,
            chroma_path=chroma_path,
            device=device
        )
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SecureDocumentProcessor")
    
    def process_document_securely(
        self,
        file_path: str,
        dataset_name: str,
        user_id: Optional[str] = None,
        delete_original: bool = False
    ) -> Dict[str, Any]:
        """Process a document securely and add to vector database.
        
        Args:
            file_path: Path to the document file
            dataset_name: Name of the dataset to add document to
            user_id: Optional user ID for access control
            delete_original: Whether to delete the original file after processing
            
        Returns:
            Dictionary with processing results
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Step 1: Encrypt the original document
            encrypt_result = self.encryption.encrypt_file(file_path, user_id)
            encrypted_id = encrypt_result["id"]
            
            # Step 2: Process in-memory to avoid writing unencrypted data to disk
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a temporary decrypted copy for processing
                temp_file = os.path.join(temp_dir, os.path.basename(file_path))
                temp_access = self.temp_access.get_temporary_access(encrypted_id, max_age_seconds=600)
                
                # Use the temporary file for processing
                processing_path = temp_access["temp_path"]
                
                # Process the document
                chunks = self.doc_processor.process_document(processing_path)
                
                # Add to vector database
                doc_count, chunk_count = self._add_to_dataset(
                    dataset_name=dataset_name,
                    chunks=chunks,
                    metadata={
                        "source": os.path.basename(file_path),
                        "encrypted_id": encrypted_id,
                        "user_id": user_id
                    }
                )
                
                # Revoke temporary access to clean up
                self.temp_access.revoke_access(temp_access["access_token"])
                
            # Delete original if requested
            if delete_original:
                try:
                    os.remove(file_path)
                except Exception as e:
                    self.logger.warning(f"Failed to delete original file: {e}")
            
            # Return processing result
            return {
                "status": "success",
                "encrypted_id": encrypted_id,
                "dataset": dataset_name,
                "chunk_count": chunk_count,
                "file_name": os.path.basename(file_path)
            }
        
        except Exception as e:
            self.logger.error(f"Error in secure document processing: {str(e)}")
            # Clean up any partial processing
            try:
                if 'encrypted_id' in locals():
                    self.encryption.delete_encrypted_file(encrypted_id)
            except Exception:
                pass
                
            raise
    
    def process_batch_securely(
        self,
        file_paths: List[str],
        dataset_name: str,
        user_id: Optional[str] = None,
        delete_originals: bool = False
    ) -> Dict[str, Any]:
        """Process multiple documents securely.
        
        Args:
            file_paths: List of file paths to process
            dataset_name: Name of the dataset to add documents to
            user_id: Optional user ID for access control
            delete_originals: Whether to delete original files after processing
            
        Returns:
            Dictionary with batch processing results
        """
        results = {
            "successful": [],
            "failed": []
        }
        
        for file_path in file_paths:
            try:
                result = self.process_document_securely(
                    file_path=file_path,
                    dataset_name=dataset_name,
                    user_id=user_id,
                    delete_original=delete_originals
                )
                results["successful"].append({
                    "file_name": os.path.basename(file_path),
                    **result
                })
            except Exception as e:
                results["failed"].append({
                    "file_name": os.path.basename(file_path),
                    "error": str(e)
                })
        
        # Add summary statistics
        results["summary"] = {
            "total": len(file_paths),
            "successful": len(results["successful"]),
            "failed": len(results["failed"])
        }
        
        return results
    
    def _add_to_dataset(
        self,
        dataset_name: str,
        chunks: List[str],
        metadata: Dict[str, Any]
    ) -> tuple:
        """Add document chunks to a dataset.
        
        Args:
            dataset_name: Name of the dataset
            chunks: List of text chunks
            metadata: Metadata to attach to chunks
            
        Returns:
            Tuple of (doc_count, chunk_count)
        """
        import uuid
        
        # Create documents with metadata
        documents = []
        metadatas = []
        ids = []
        
        # Base metadata for all chunks
        base_metadata = {
            "source": metadata.get("source", "Unknown"),
            "encrypted_id": metadata.get("encrypted_id", None),
            "user_id": metadata.get("user_id", None)
        }
        
        # Process each chunk
        for i, chunk in enumerate(chunks):
            if len(chunk) < 100:  # Skip very short chunks
                continue
                
            chunk_id = f"{base_metadata['source']}_{i}_{uuid.uuid4()}"
            chunk_metadata = {
                **base_metadata,
                "chunk_index": i,
                "page": i  # For compatibility with existing code
            }
            
            documents.append(chunk)
            metadatas.append(chunk_metadata)
            ids.append(chunk_id)
        
        # Get ChromaDB collection
        collection = self.doc_processor.chroma_client.get_or_create_collection(name=dataset_name)
        
        # Add chunks in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            batch_docs = documents[i:end_idx]
            batch_meta = metadatas[i:end_idx]
            batch_ids = ids[i:end_idx]
            
            collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
        
        return 1, len(documents)  # One document, multiple chunks
    
    def secure_search(
        self,
        dataset_name: str,
        query: str,
        user_id: Optional[str] = None,
        n_results: int = 5,
        filter_user: bool = True
    ) -> Dict[str, Any]:
        """Search a dataset with user-based access control.
        
        Args:
            dataset_name: Name of the dataset to search
            query: Search query
            user_id: User ID for access control
            n_results: Number of results to return
            filter_user: Whether to filter results by user_id
            
        Returns:
            Dictionary with search results
        """
        # Configure user filtering if needed
        where_filter = None
        if filter_user and user_id:
            # Filter to show only this user's documents or public documents
            where_filter = {"$or": [
                {"user_id": user_id},
                {"user_id": None}  # Public documents have null user_id
            ]}
        
        # Search with document processor
        results = self.doc_processor.query_dataset(
            dataset_name=dataset_name,
            query=query,
            n_results=n_results,
            use_hybrid_search=True,
            use_reranking=True,
            where=where_filter
        )
        
        # Process results for security: clear full document content
        # Only return the specific chunks that matched, not entire documents
        secure_results = {
            "documents": results["documents"],
            "metadatas": results["metadatas"],
            "ids": results["ids"] if "ids" in results else None,
            "distances": results["distances"] if "distances" in results else None
        }
        
        return secure_results
    
    def get_document_securely(
        self,
        encrypted_id: str,
        user_id: Optional[str] = None,
        max_age_seconds: int = 300
    ) -> Dict[str, Any]:
        """Get temporary secure access to a document.
        
        Args:
            encrypted_id: ID of the encrypted document
            user_id: User ID for access control
            max_age_seconds: How long the access should last
            
        Returns:
            Dictionary with access information
        """
        # Check if user has access to this document
        metadata = self.encryption.get_file_metadata(encrypted_id)
        if not metadata:
            raise FileNotFoundError(f"Document not found: {encrypted_id}")
        
        # Check user access
        if user_id and metadata.get("user_id") and metadata.get("user_id") != user_id:
            raise PermissionError("You don't have access to this document")
        
        # Get temporary access
        access_info = self.temp_access.get_temporary_access(
            encrypted_id=encrypted_id,
            max_age_seconds=max_age_seconds
        )
        
        # Return secure access info with original filename
        return {
            "access_token": access_info["access_token"],
            "original_name": access_info["original_name"],
            "mime_type": access_info["mime_type"],
            "expires_at": access_info["expires_at"]
        }
    
    def stream_document_securely(
        self,
        access_token: str
    ) -> tuple:
        """Stream a document securely using an access token.
        
        Args:
            access_token: Access token from get_document_securely
            
        Returns:
            Tuple of (file-like object, filename, mimetype)
        """
        # Verify token is valid
        access_info = self.temp_access.verify_access(access_token)
        if not access_info:
            raise PermissionError("Invalid or expired access token")
        
        # Open file for streaming
        file = open(access_info["temp_path"], "rb")
        
        return (
            file,
            access_info["original_name"],
            access_info["mime_type"]
        )
    
    def delete_document_securely(
        self,
        encrypted_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete an encrypted document.
        
        Args:
            encrypted_id: ID of the encrypted document
            user_id: User ID for access control
            
        Returns:
            Whether deletion was successful
        """
        # Check if user has access to this document
        metadata = self.encryption.get_file_metadata(encrypted_id)
        if not metadata:
            return False
        
        # Check user access
        if user_id and metadata.get("user_id") and metadata.get("user_id") != user_id:
            raise PermissionError("You don't have permission to delete this document")
        
        # Delete the document
        return self.encryption.delete_encrypted_file(encrypted_id)
    
    def memoryless_processing(
        self,
        file_obj: BinaryIO,
        dataset_name: str,
        original_filename: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a document in-memory without writing to disk.
        
        Args:
            file_obj: File-like object containing document data
            dataset_name: Name of the dataset to add document to
            original_filename: Original filename for metadata
            user_id: Optional user ID for access control
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Read file data into memory
            file_data = file_obj.read()
            
            # Encrypt data directly
            encrypted_id = f"enc_{int(time.time())}_{secrets.token_hex(8)}"
            encrypted_data = self.encryption.fernet.encrypt(file_data)
            
            # Save encrypted file
            encrypted_file_path = os.path.join(self.encryption.encrypted_dir, f"{encrypted_id}.enc")
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Get file extension
            _, file_extension = os.path.splitext(original_filename)
            
            # Create metadata
            metadata = {
                "id": encrypted_id,
                "original_name": original_filename,
                "encrypted_path": encrypted_file_path,
                "original_size": len(file_data),
                "encrypted_size": len(encrypted_data),
                "extension": file_extension.lower(),
                "mime_type": self.encryption._get_mime_type(file_extension),
                "encrypted_at": time.time(),
                "user_id": user_id,
                "checksum": self.encryption._generate_checksum(file_data)
            }
            
            # Save metadata
            metadata_file = os.path.join(self.encryption.storage_dir, f"{encrypted_id}.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Process in memory using a temporary buffer
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(file_data)
            
            try:
                # Process the document
                chunks = self.doc_processor.process_document(temp_path)
                
                # Delete temporary file immediately
                os.unlink(temp_path)
                
                # Add to vector database
                doc_count, chunk_count = self._add_to_dataset(
                    dataset_name=dataset_name,
                    chunks=chunks,
                    metadata={
                        "source": original_filename,
                        "encrypted_id": encrypted_id,
                        "user_id": user_id
                    }
                )
                
                # Return processing result
                return {
                    "status": "success",
                    "encrypted_id": encrypted_id,
                    "dataset": dataset_name,
                    "chunk_count": chunk_count,
                    "file_name": original_filename
                }
            finally:
                # Ensure temp file is deleted
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except Exception as e:
            self.logger.error(f"Error in memoryless document processing: {str(e)}")
            # Clean up any partial processing
            try:
                if 'encrypted_id' in locals():
                    self.encryption.delete_encrypted_file(encrypted_id)
            except Exception:
                pass
                
            raise