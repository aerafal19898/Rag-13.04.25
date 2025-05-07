"""
Unified authentication service for handling multiple authentication methods.
"""

import jwt
import bcrypt
import uuid
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import os
from functools import wraps
import json
from app.services.database import DatabaseManager
from app.utils.cache_manager import CacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication service for handling multiple authentication methods.
    Uses Redis caching for sessions and user data (task 3.3).
    """
    
    def __init__(self, db_manager: DatabaseManager, secret_key: str = None, token_expiry: int = 3600):
        """
        Initialize the authentication service.
        
        Args:
            db_manager: Database manager instance
            secret_key: Secret key for JWT tokens
            token_expiry: Token expiry time in seconds
        """
        self.db_manager = db_manager
        # Require JWT secret key from environment or passed in explicitly
        self.secret_key = secret_key or os.environ.get("JWT_SECRET_KEY")
        if not self.secret_key:
            logger.critical("JWT_SECRET_KEY environment variable not set!")
            raise ValueError("JWT_SECRET_KEY is required for authentication service")
        self.token_expiry = token_expiry
        self.cache_manager = CacheManager()
        
        # Authentication methods
        self.auth_methods = {
            "password": self._authenticate_password,
            "token": self._authenticate_token,
            "api_key": self._authenticate_api_key
        }
    
    def _authenticate_password(self, username: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Tuple of (success, user_data)
        """
        try:
            # Get user from database
            user = self.db_manager.verify_user(username, password)
            
            # Return success and user data
            return True, user
        
        except ValueError as e:
            # Log error
            logger.error(f"Password authentication failed: {str(e)}")
            
            # Return failure
            return False, {"error": str(e)}
    
    def _authenticate_token(self, token: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Authenticate user with JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Tuple of (success, user_data)
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check if token is expired
            if payload["exp"] < time.time():
                raise jwt.ExpiredSignatureError("Token has expired")
            
            # Get user from database
            user = self.db_manager.get_user(payload["user_id"])
            
            # Return success and user data
            return True, user
        
        except jwt.InvalidTokenError as e:
            # Log error
            logger.error(f"Token authentication failed: {str(e)}")
            
            # Return failure
            return False, {"error": "Invalid token"}
        
        except ValueError as e:
            # Log error
            logger.error(f"Token authentication failed: {str(e)}")
            
            # Return failure
            return False, {"error": str(e)}
    
    def _authenticate_api_key(self, api_key: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Authenticate user with API key.
        
        Args:
            api_key: API key
            
        Returns:
            Tuple of (success, user_data)
        """
        # This is a placeholder for API key authentication
        # In a real implementation, you would check the API key against a database
        
        # For now, we'll just return failure
        return False, {"error": "API key authentication not implemented"}
    
    def authenticate(self, method: str, **kwargs) -> Dict[str, Any]:
        """
        Authenticate user with the specified method.
        
        Args:
            method: Authentication method
            **kwargs: Authentication parameters
            
        Returns:
            Dict containing authentication result
        """
        # Check if method is supported
        if method not in self.auth_methods:
            return {"success": False, "error": f"Unsupported authentication method: {method}"}
        
        # Get authentication function
        auth_func = self.auth_methods[method]
        
        # Authenticate user
        success, user_data = auth_func(**kwargs)
        
        # Check if authentication was successful
        if not success:
            return {"success": False, "error": user_data.get("error", "Authentication failed")}
        
        # Generate session ID
        session_id = self.create_session(user_data["id"])
        
        # Generate token
        token = self.generate_token(user_data["id"])
        
        # Log action
        self.db_manager.log_action(user_data["id"], "login", {
            "method": method,
            "session_id": session_id
        })
        
        # Return success and session data
        return {
            "success": True,
            "session_id": session_id,
            "token": token,
            "user": user_data
        }
    
    def generate_token(self, user_id: str) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            JWT token
        """
        # Create token payload
        payload = {
            "user_id": user_id,
            "exp": time.time() + self.token_expiry,
            "iat": time.time()
        }
        
        # Generate token
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # Return token
        return token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Dict containing token payload
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check if token is expired
            if payload["exp"] < time.time():
                raise jwt.ExpiredSignatureError("Token has expired")
            
            # Return payload
            return payload
        
        except jwt.InvalidTokenError as e:
            # Log error
            logger.error(f"Token verification failed: {str(e)}")
            
            # Raise exception
            raise ValueError("Invalid token")
    
    def logout(self, session_id: str) -> Dict[str, Any]:
        """
        Logout a user.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict containing logout result
        """
        # Check if session exists
        if not self.invalidate_session(session_id):
            return {"success": False, "error": "Session not found"}
        
        # Log action
        self.db_manager.log_action(self.get_session_user(session_id), "logout", {
            "session_id": session_id
        })
        
        # Remove session
        return {"success": True}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session information.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict containing session information
        """
        # Check if session exists
        if not self.invalidate_session(session_id):
            return {"success": False, "error": "Session not found"}
        
        # Get session
        session_user_id = self.get_session_user(session_id)
        
        # Check if session is expired
        if not session_user_id:
            return {"success": False, "error": "Session expired"}
        
        # Get user data
        user_data = self.db_manager.get_user(session_user_id)
        
        # Check if session is valid
        if not user_data:
            return {"success": False, "error": "User not found"}
        
        # Return session
        return {"success": True, "session": {
            "user_id": session_user_id,
            "token": self.generate_token(session_user_id),
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=self.token_expiry)).isoformat()
        }}
    
    def refresh_session(self, session_id: str) -> Dict[str, Any]:
        """
        Refresh a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict containing session information
        """
        # Check if session exists
        if not self.invalidate_session(session_id):
            return {"success": False, "error": "Session not found"}
        
        # Get session
        session = self.get_session(session_id)
        
        # Generate new token
        token = self.generate_token(session["session"]["user_id"])
        
        # Update session
        session["session"]["token"] = token
        session["session"]["expires_at"] = (datetime.now() + timedelta(seconds=self.token_expiry)).isoformat()
        
        # Log action
        self.db_manager.log_action(session["session"]["user_id"], "refresh_session", {
            "session_id": session_id
        })
        
        # Return session
        return {"success": True, "session": session["session"]}
    
    def require_auth(self, f):
        """
        Decorator for requiring authentication.
        
        Args:
            f: Function to decorate
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get token from request
            token = kwargs.get("token")
            
            # Check if token is provided
            if not token:
                return {"success": False, "error": "Token not provided"}
            
            try:
                # Verify token
                payload = self.verify_token(token)
                
                # Add user ID to kwargs
                kwargs["user_id"] = payload["user_id"]
                
                # Call function
                return f(*args, **kwargs)
            
            except ValueError as e:
                # Return error
                return {"success": False, "error": str(e)}
        
        return decorated
    
    def require_session(self, f):
        """
        Decorator for requiring a valid session.
        
        Args:
            f: Function to decorate
            
        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get session ID from request
            session_id = kwargs.get("session_id")
            
            # Check if session ID is provided
            if not session_id:
                return {"success": False, "error": "Session ID not provided"}
            
            # Get session
            session_result = self.get_session(session_id)
            
            # Check if session is valid
            if not session_result["success"]:
                return session_result
            
            # Add session to kwargs
            kwargs["session"] = session_result["session"]
            
            # Call function
            return f(*args, **kwargs)
        
        return decorated
    
    def create_session(self, user_id: str) -> str:
        """Create a new session for a user and store it in Redis."""
        if not self.cache_manager.is_connected():
            logger.error("Cannot create session: Redis not connected.")
            return None
        session_id = str(uuid.uuid4())
        # Store session ID with user ID, expire after a reasonable time (e.g., 1 day)
        success = self.cache_manager.set(f"session:{session_id}", user_id, expire_seconds=86400)
        if success:
            return session_id
        else:
            logger.error(f"Failed to store session {session_id} in Redis.")
            return None

    def get_session_user(self, session_id: str) -> Optional[str]:
        """Get user ID from session ID stored in Redis."""
        if not self.cache_manager.is_connected():
            logger.warning("Cannot get session user: Redis not connected.")
            return None
        return self.cache_manager.get(f"session:{session_id}")

    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session by deleting it from Redis."""
        if not self.cache_manager.is_connected():
            logger.warning("Cannot invalidate session: Redis not connected.")
            return False
        return self.cache_manager.delete(f"session:{session_id}")

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username, checking cache first."""
        cache_key = f"user_username:{username}"
        if self.cache_manager.is_connected():
            cached_user = self.cache_manager.get(cache_key)
            if cached_user:
                logger.debug(f"Cache hit for username: {username}")
                # Ensure the cached value is parsed correctly if stored as JSON
                if isinstance(cached_user, str):
                    try:
                        return json.loads(cached_user)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode cached user data for {username}. Fetching from DB.")
                elif isinstance(cached_user, dict):
                     return cached_user # Already a dict
                else:
                     logger.warning(f"Unexpected data type in cache for {username}. Fetching from DB.")

        logger.debug(f"Cache miss for username: {username}. Querying database.")
        query = "SELECT id, username, email, password_hash, last_login, created_at FROM users WHERE username = %s"
        try:
            with self.db_manager._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (username,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    user = dict(zip(columns, row))
                    # Convert datetime objects to ISO format string if necessary for caching/consistency
                    user['last_login'] = user['last_login'].isoformat() if user.get('last_login') else None
                    user['created_at'] = user['created_at'].isoformat() if user.get('created_at') else None

                    if self.cache_manager.is_connected():
                        # Cache for 1 hour (3600 seconds)
                        self.cache_manager.set(cache_key, user, expire_seconds=3600)
                        logger.debug(f"User {username} cached.")
                    return user
                else:
                    return None
        except Exception as e:
            logger.error(f"Database error fetching user by username '{username}': {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID, checking cache first."""
        cache_key = f"user_id:{user_id}"
        if self.cache_manager.is_connected():
            cached_user = self.cache_manager.get(cache_key)
            if cached_user:
                logger.debug(f"Cache hit for user ID: {user_id}")
                if isinstance(cached_user, str):
                    try:
                        return json.loads(cached_user)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode cached user data for ID {user_id}. Fetching from DB.")
                elif isinstance(cached_user, dict):
                    return cached_user
                else:
                    logger.warning(f"Unexpected data type in cache for ID {user_id}. Fetching from DB.")

        logger.debug(f"Cache miss for user ID: {user_id}. Querying database.")
        query = "SELECT id, username, email, password_hash, last_login, created_at FROM users WHERE id = %s"
        try:
            with self.db_manager._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    user = dict(zip(columns, row))
                    # Convert datetime objects to ISO format string
                    user['last_login'] = user['last_login'].isoformat() if user.get('last_login') else None
                    user['created_at'] = user['created_at'].isoformat() if user.get('created_at') else None

                    if self.cache_manager.is_connected():
                        self.cache_manager.set(cache_key, user, expire_seconds=3600)
                        logger.debug(f"User ID {user_id} cached.")
                    return user
                else:
                    return None
        except Exception as e:
            logger.error(f"Database error fetching user by ID '{user_id}': {e}")
            return None

    def update_user(self, user_id: str, username: str = None, email: str = None):
        """Update user details."""
        # ... (existing update logic) ...
        
        # Invalidate cache after update
        if self.cache_manager.is_connected():
            if username: self.cache_manager.delete(f"user:username:{username}") # Need old username if changed
            self.cache_manager.delete(f"user:id:{user_id}")
            # Also need to fetch old username if it was updated to delete that key too
            # This part needs careful handling depending on update logic

        # ... (rest of existing method) ...

    def delete_user(self, user_id: str):
        """Delete user."""
        # Fetch user first to get username for cache invalidation
        user = self.get_user_by_id(user_id) 
        if not user: return # Or raise error

        # ... (existing delete logic) ...

        # Invalidate cache after delete
        if self.cache_manager.is_connected():
            self.cache_manager.delete(f"user:username:{user['username']}")
            self.cache_manager.delete(f"user:id:{user_id}")

        # ... (rest of existing method) ... 