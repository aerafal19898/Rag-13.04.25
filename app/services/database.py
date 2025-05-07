# Override system sqlite3 with pysqlite3-binary for ChromaDB
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

"""
Database abstraction layer for handling both ChromaDB and PostgreSQL database operations.
"""

import chromadb
from chromadb.config import Settings
import psycopg2 # Added for PostgreSQL
import psycopg2.extras # For dict cursors
import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import hashlib
import uuid
import contextlib
import shutil
from unittest.mock import MagicMock # Keep for placeholder AuditLogger
# Assuming AuditLogger implementation exists or is handled elsewhere
# from app.utils.audit_logger import AuditLogger
# ConfigManager might not be needed directly here if connection details come from ENV
# from app.services.config import ConfigManager
# VectorStoreManager might be refactored later
from app.services.vector_store import VectorStoreManager
# BackupManager placeholder is likely unused now
# from app.utils.backup_manager import BackupManager
import sqlite3  # Add at top for fallback
import bcrypt  # for verifying passwords

# Configure logging level globally based on env var (e.g., in main app setup or ConfigManager)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages PostgreSQL and ChromaDB connections and operations.
    """

    def __init__(self,
                 db_host: Optional[str] = None,
                 db_port: Optional[int] = None,
                 db_user: Optional[str] = None,
                 db_password: Optional[str] = None,
                 db_name: Optional[str] = None,
                 chroma_host: Optional[str] = None,
                 chroma_port: Optional[int] = None
                 ):
        """
        Initialize the database manager using environment variables primarily.
        Args allow overriding for testing or alternative configurations.
        """
        # PostgreSQL Connection Details from ENV (falling back to test credentials)
        self.db_host = db_host or os.getenv("DB_HOST", "localhost")
        self.db_port = db_port or int(os.getenv("DB_PORT", 5432))
        self.db_user = db_user or os.getenv("DB_USER", "testuser")
        self.db_password = db_password or os.getenv("DB_PASSWORD", "testpassword")
        self.db_name = db_name or os.getenv("DB_NAME", "testdb")
        # Always use PostgreSQL by default
        self.use_sqlite = False

        # ChromaDB Connection Details from Env Vars
        self.chroma_host = chroma_host or os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = chroma_port or int(os.getenv("CHROMA_PORT", 8000))

        logger.info(f"Initializing DatabaseManager for PGSQL: {self.db_host}:{self.db_port}, Chroma: {self.chroma_host}:{self.chroma_port}")

        # Initialize ChromaDB HTTP Client
        try:
            # Settings like allow_reset are generally for PersistentClient, not HttpClient
            self.chroma_client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port,
            )
            self.chroma_client.heartbeat() # Raises exception on failure
            logger.info("ChromaDB HttpClient connected successfully.")
        except Exception as e:
            logger.critical(f"Failed to connect to ChromaDB at {self.chroma_host}:{self.chroma_port}: {e}")
            self.chroma_client = None # Ensure client is None if connection fails

        # Initialize Audit Logger (Replace mock with real logger if/when available)
        self.audit_logger = MagicMock()

        # Database schema initialization (table creation) is now handled by migrations (Alembic).

    @contextlib.contextmanager
    def _get_db_connection(self):
        """
        Context manager for PostgreSQL database connections.

        Yields:
            psycopg2.connection: Database connection object.
        """
        # Always connect to PostgreSQL
        conn = None
        try:
            conn = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            logger.debug("PostgreSQL connection established.")
            yield conn
        except psycopg2.OperationalError as e:
            logger.error(f"PostgreSQL OperationalError connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"PostgreSQL general connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("PostgreSQL connection closed.")

    # --- Transaction Management --- #

    def begin_transaction(self, details: Dict[str, Any]) -> str:
        """Begin a transaction record in the database."""
        transaction_id = str(uuid.uuid4())
        sql = """
            INSERT INTO transactions (id, status, details)
            VALUES (%s, %s, %s)
            """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (transaction_id, "started", json.dumps(details)))
                    conn.commit()
            logger.info(f"Started transaction {transaction_id}")
            return transaction_id
        except Exception as e:
            logger.error(f"Error beginning transaction: {e}")
            raise

    def commit_transaction(self, transaction_id: str):
        """Commit a transaction record in the database."""
        sql = """
            UPDATE transactions
            SET status = %s, completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, ("completed", transaction_id))
                    conn.commit()
            logger.info(f"Committed transaction {transaction_id}")
        except Exception as e:
            logger.error(f"Error committing transaction {transaction_id}: {e}")
            raise

    def rollback_transaction(self, transaction_id: str):
        """Rollback a transaction record in the database."""
        # Note: Actual DB rollback happens implicitly if connection context exits with error.
        # This method updates the tracking table.
        sql = """
            UPDATE transactions
            SET status = %s, completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, ("rolled_back", transaction_id))
                    conn.commit()
            logger.warning(f"Rolled back transaction {transaction_id}")
        except Exception as e:
            logger.error(f"Error rolling back transaction {transaction_id}: {e}")
            # Don't re-raise here, as this is often called during exception handling

    # --- User operations --- #

    def create_user(self, user_id: str, username: str, password_hash: str, email: str) -> Optional[Dict[str, Any]]:
        """Create a new user. Expects hashed password."""
        sql = """
            INSERT INTO users (id, username, password_hash, email, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, username, email, created_at, last_login;
            """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (user_id, username, password_hash, email))
                    new_user = cursor.fetchone()
                    conn.commit()
                    logger.info(f"User created: {username} (ID: {user_id})")
                    return dict(new_user) if new_user else None
        except psycopg2.Error as e:
            logger.error(f"Error creating user {username}: {e}")
            conn.rollback() # Rollback on error
            # Re-raise specific DB errors if needed by caller (e.g., duplicate username/email)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error creating user {username}: {e}")
            raise

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        sql = "SELECT id, username, email, password_hash, created_at, last_login FROM users WHERE id = %s;"
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (user_id,))
                    user = cursor.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        sql = "SELECT id, username, email, password_hash, created_at, last_login FROM users WHERE username = %s;"
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (username,))
                    user = cursor.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None

    def update_last_login(self, user_id: str):
        """Updates the last_login timestamp for a user."""
        sql = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s;"
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (user_id,))
                    conn.commit()
                    logger.debug(f"Updated last_login for user {user_id}")
        except Exception as e:
             logger.error(f"Error updating last_login for user {user_id}: {e}")
             # Decide if this error should be propagated

    # --- Chat Operations (Example - Adapt schema as needed) --- #

    def create_chat(self, user_id: str, title: str) -> Optional[Dict[str, Any]]:
        """Creates a new chat record."""
        chat_id = str(uuid.uuid4())
        sql = """
            INSERT INTO chats (id, user_id, title, created_at, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, user_id, title, created_at, updated_at;
            """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (chat_id, user_id, title))
                    new_chat = cursor.fetchone()
                    conn.commit()
                    logger.info(f"Chat created: {title} (ID: {chat_id}) for user {user_id}")
                    return dict(new_chat) if new_chat else None
        except Exception as e:
            logger.error(f"Error creating chat '{title}' for user {user_id}: {e}")
            raise

    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a specific chat."""
        sql = "SELECT id, user_id, title, created_at, updated_at FROM chats WHERE id = %s;"
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (chat_id,))
                    chat = cursor.fetchone()
                    return dict(chat) if chat else None
        except Exception as e:
            logger.error(f"Error retrieving chat {chat_id}: {e}")
            return None

    def get_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieves all chats for a given user."""
        sql = "SELECT id, user_id, title, created_at, updated_at FROM chats WHERE user_id = %s ORDER BY updated_at DESC;"
        chats = []
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (user_id,))
                    for row in cursor.fetchall():
                        chats.append(dict(row))
            return chats
        except Exception as e:
            logger.error(f"Error retrieving chats for user {user_id}: {e}")
            return []

    def delete_chat(self, chat_id: str):
        """Deletes a chat and its associated messages."""
        # Note: Consider transaction or cascade delete in DB schema
        sql_delete_messages = "DELETE FROM messages WHERE chat_id = %s;"
        sql_delete_chat = "DELETE FROM chats WHERE id = %s;"
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Delete messages first
                    cursor.execute(sql_delete_messages, (chat_id,))
                    # Delete chat
                    cursor.execute(sql_delete_chat, (chat_id,))
                    conn.commit()
                    logger.info(f"Deleted chat {chat_id} and its messages.")
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            raise

    # --- Message Operations (Example - Adapt schema as needed) --- #

    def add_message(self, chat_id: str, role: str, content: str) -> Optional[Dict[str, Any]]:
         """Adds a message to a chat."""
         message_id = str(uuid.uuid4())
         sql = """
             INSERT INTO messages (id, chat_id, role, content, created_at)
             VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
             RETURNING id, chat_id, role, content, created_at;
             """
         sql_update_chat = "UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = %s;"
         try:
             with self._get_db_connection() as conn:
                 with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                     cursor.execute(sql, (message_id, chat_id, role, content))
                     new_message = cursor.fetchone()
                     # Update chat timestamp
                     cursor.execute(sql_update_chat, (chat_id,))
                     conn.commit()
                     logger.info(f"Added message {message_id} to chat {chat_id}")
                     return dict(new_message) if new_message else None
         except Exception as e:
             logger.error(f"Error adding message to chat {chat_id}: {e}")
             raise

    def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Retrieves all messages for a specific chat."""
        sql = "SELECT id, chat_id, role, content, created_at FROM messages WHERE chat_id = %s ORDER BY created_at ASC;"
        messages = []
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (chat_id,))
                    for row in cursor.fetchall():
                        messages.append(dict(row))
            return messages
        except Exception as e:
            logger.error(f"Error retrieving messages for chat {chat_id}: {e}")
            return []

    # --- Document Operations (Example - Adapt schema as needed) --- #

    def add_document(self, user_id: str, filename: str, content_type: str, size: int) -> Optional[Dict[str, Any]]:
        """Adds a document metadata record."""
        doc_id = str(uuid.uuid4())
        sql = """
            INSERT INTO documents (id, user_id, filename, content_type, size, created_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, user_id, filename, content_type, size, created_at;
            """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (doc_id, user_id, filename, content_type, size))
                    new_doc = cursor.fetchone()
                    conn.commit()
                    logger.info(f"Added document record: {filename} (ID: {doc_id}) for user {user_id}")
                    return dict(new_doc) if new_doc else None
        except Exception as e:
            logger.error(f"Error adding document record '{filename}' for user {user_id}: {e}")
            raise

    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieves all document records for a user."""
        sql = "SELECT id, user_id, filename, content_type, size, created_at FROM documents WHERE user_id = %s ORDER BY created_at DESC;"
        documents = []
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, (user_id,))
                    for row in cursor.fetchall():
                        documents.append(dict(row))
            return documents
        except Exception as e:
            logger.error(f"Error retrieving documents for user {user_id}: {e}")
            return []

    def delete_document(self, document_id: str):
        """Deletes a document metadata record."""
        # Note: This only deletes the DB record. Actual file deletion is handled elsewhere.
        sql = "DELETE FROM documents WHERE id = %s;"
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (document_id,))
                    conn.commit()
                    logger.info(f"Deleted document record {document_id}.")
        except Exception as e:
            logger.error(f"Error deleting document record {document_id}: {e}")
            raise

    # --- Audit Log Operations --- #

    def log_action(self, user_id: Optional[str], action: str, details: dict):
        """Log an action to the audit log table."""
        log_id = str(uuid.uuid4())
        # Ensure details are always stored as JSON string
        try:
            details_json = json.dumps(details)
        except TypeError as e:
            logger.error(f"Could not serialize details for audit log action '{action}': {e}")
            details_json = json.dumps({"error": "Serialization failed", "original_details": str(details)})

        sql = """
            INSERT INTO audit_logs (id, user_id, action, details, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
        try:
            with self._get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (log_id, user_id, action, details_json))
                    conn.commit()
            # Avoid logging the log action itself recursively if logger used db
            # logger.info(f"Logged action: {action} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log action '{action}' for user {user_id}: {e}")
            # Decide if this error needs propagation

    def get_audit_logs(self, user_id: Optional[str] = None, action: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve audit logs, optionally filtered by user_id and/or action."""
        base_sql = "SELECT id, user_id, action, details, created_at FROM audit_logs"
        filters = []
        params = []

        if user_id:
            # Use %s for PostgreSQL
            filters.append("user_id = %s")
            params.append(user_id)
        if action:
            # Use %s for PostgreSQL
            filters.append("action = %s")
            params.append(action)

        if filters:
            sql = f"{base_sql} WHERE {' AND '.join(filters)} ORDER BY created_at DESC LIMIT %s;"
        else:
            sql = f"{base_sql} ORDER BY created_at DESC LIMIT %s;"
        params.append(limit) # Add limit parameter

        logs = []
        try:
            with self._get_db_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(sql, tuple(params))
                    for row in cursor.fetchall():
                        log_entry = dict(row)
                        try:
                            # Details are stored as JSON string, attempt to parse
                            log_entry['details'] = json.loads(log_entry['details'])
                        except (json.JSONDecodeError, TypeError):
                             logger.warning(f"Could not decode JSON details for audit log {log_entry['id']}")
                             # Keep raw string or set to error indicator
                        logs.append(log_entry)
            return logs
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return [] # Return empty list on error

    # --- ChromaDB Operations --- #
    # These methods interact with the ChromaDB HttpClient

    def create_collection(self, name: str, metadata: Optional[Dict] = None):
        """Creates a collection in ChromaDB."""
        if not self.chroma_client:
            logger.error("ChromaDB client not available.")
            raise ConnectionError("ChromaDB client not initialized")
        try:
            self.chroma_client.create_collection(name=name, metadata=metadata)
            logger.info(f"ChromaDB collection '{name}' created.")
        except Exception as e:
            # Catch potential exceptions, e.g., collection already exists
            logger.warning(f"Issue creating ChromaDB collection '{name}': {e}")
            # Decide if specific exceptions should be handled differently or re-raised
            # raise # Re-raise if creation failure is critical

    def delete_collection(self, name: str):
        """Deletes a collection from ChromaDB."""
        if not self.chroma_client:
            logger.error("ChromaDB client not available.")
            raise ConnectionError("ChromaDB client not initialized")
        try:
            self.chroma_client.delete_collection(name=name)
            logger.info(f"ChromaDB collection '{name}' deleted.")
        except Exception as e:
            logger.error(f"Failed to delete ChromaDB collection '{name}': {e}")
            raise # Re-raise if deletion failure is critical

    def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None):
        """Gets a collection or creates it if it doesn't exist."""
        if not self.chroma_client:
            logger.error("ChromaDB client not available.")
            raise ConnectionError("ChromaDB client not initialized")
        try:
            collection = self.chroma_client.get_or_create_collection(name=name, metadata=metadata)
            logger.info(f"Ensured ChromaDB collection '{name}' exists.")
            return collection
        except Exception as e:
            logger.error(f"Failed to get or create ChromaDB collection '{name}': {e}")
            raise

    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Adds documents (embeddings) to a ChromaDB collection."""
        if not self.chroma_client:
            logger.error("ChromaDB client not available.")
            raise ConnectionError("ChromaDB client not initialized")
        try:
            # HttpClient interacts directly with collections by name
            collection = self.chroma_client.get_collection(name=collection_name)
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(ids)} documents to ChromaDB collection '{collection_name}'.")
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB collection '{collection_name}': {e}")
            raise

    def query_documents(self, collection_name: str, query_texts: List[str], n_results: int = 5, where: Optional[Dict] = None, where_document: Optional[Dict] = None, include: Optional[List[str]] = ["metadatas", "documents", "distances"]) -> Optional[Dict[str, Any]]:
        """Queries a ChromaDB collection."""
        if not self.chroma_client:
            logger.error("ChromaDB client not available.")
            raise ConnectionError("ChromaDB client not initialized")
        try:
            # HttpClient interacts directly with collections by name
            collection = self.chroma_client.get_collection(name=collection_name)
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=include
            )
            logger.debug(f"Query returned {len(results.get('ids', [[]])[0])} results from '{collection_name}'.")
            return results
        except Exception as e:
            logger.error(f"Failed to query ChromaDB collection '{collection_name}': {e}")
            return None # Return None or empty dict on error

    # --- Deprecated Backup Methods --- #

    def backup_sqlite_db(self, backup_dir: str):
        """DEPRECATED: Backup SQLite database to a specified directory."""
        logger.warning("backup_sqlite_db is deprecated. Use PostgreSQL backup tools (e.g., pg_dump).")
        if not self.db_type == DatabaseType.SQLITE:
            logger.error("Backup function is only for SQLite.")
            return None

        if not self.sqlite_db_path or not os.path.exists(self.sqlite_db_path):
            logger.error("SQLite database path not configured or file does not exist.")
            return None

        # This method is deprecated and should ideally do nothing or just log.
        # Returning None to satisfy the modified test expectation.
        return None

    def restore_sqlite_db(self, backup_path: str):
        """DEPRECATED: Restore SQLite database from a backup file."""
        logger.warning("restore_sqlite_db is deprecated. Use PostgreSQL restore tools (e.g., pg_restore).")
        if not self.db_type == DatabaseType.SQLITE:
            logger.error("Restore function is only for SQLite.")
            return False

        if not os.path.exists(backup_path):
            logger.error(f"Backup file does not exist: {backup_path}")
            return False

        # This method is deprecated.
        return False # Indicate failure or no action taken

    def backup_chroma_db(self, backup_dir: str) -> str:
        logger.error("backup_chroma_db using file copy is deprecated for production ChromaDB.")
        # Backup for production ChromaDB involves backing up its persistent volume
        # or using potential future API-based backup features provided by ChromaDB.
        return ""

    def verify_user(self, username: str, password: str) -> Dict[str, Any]:
        """Verify a user's password and return user data on success."""
        user = self.get_user_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found")
        stored_hash = user.get('password_hash')
        # bcrypt hash stored as string; ensure bytes
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            raise ValueError("Invalid credentials")
        # Remove hash before returning
        user.pop('password_hash', None)
        return user
