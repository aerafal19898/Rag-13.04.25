"""
User model and authentication functionality.
"""

import os
import json
import time
import datetime
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

from app.config import BASE_DIR, BCRYPT_ROUNDS, USER_ROLES, DEFAULT_CREDITS

class User:
    """User model for authentication and authorization."""
    
    def __init__(self, storage_dir: str = None):
        """Initialize with the storage directory."""
        if storage_dir is None:
            self.storage_dir = os.path.join(BASE_DIR, "data", "users")
        else:
            self.storage_dir = storage_dir
            
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # User index file for quick lookups
        self.index_file = os.path.join(self.storage_dir, "user_index.json")
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w') as f:
                json.dump({"users": {}}, f, indent=2)
    
    def create_user(self, username: str, email: str, password: str, 
                   role: str = USER_ROLES["USER"], 
                   is_active: bool = True,
                   requires_mfa: bool = False) -> Optional[str]:
        """
        Create a new user.
        
        Args:
            username: Unique username
            email: User's email
            password: Plain text password (will be hashed)
            role: User role (admin, user, guest)
            is_active: Whether the account is active
            requires_mfa: Whether MFA is required
            
        Returns:
            User ID if successful, None if username/email already exists
        """
        # Check if username or email already exists
        if self._get_user_by_username_or_email(username, email):
            return None
            
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), 
                                      bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
        
        # Create a new user ID
        user_id = str(uuid.uuid4())
        
        # Create user data structure
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash.decode('utf-8'),  # Store as string
            "role": role,
            "is_active": is_active,
            "requires_mfa": requires_mfa,
            "mfa_secret": None,  # For TOTP setup
            "credits": DEFAULT_CREDITS,
            "created_at": time.time(),
            "last_login": None,
            "profile": {
                "first_name": "",
                "last_name": "",
                "company": "",
                "job_title": ""
            }
        }
        
        # Save user file
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)
            
        # Update index
        self._update_user_index(user_id, username, email)
        
        return user_id
    
    def authenticate(self, username_or_email: str, password: str) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        Authenticate a user with username/email and password.
        
        Args:
            username_or_email: Username or email
            password: Plain text password
            
        Returns:
            Tuple of (success, user_data, error_message)
        """
        user = self._get_user_by_username_or_email(username_or_email, username_or_email)
        
        if not user:
            return False, None, "Invalid username or password"
            
        # Check if user is active
        if not user.get("is_active", True):
            return False, None, "Account is inactive"
            
        # Verify password
        stored_hash = user.get("password_hash", "").encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            # Update last login
            user["last_login"] = time.time()
            user_file = os.path.join(self.storage_dir, f"{user['id']}.json")
            with open(user_file, 'w') as f:
                json.dump(user, f, indent=2)
                
            # Check if MFA is required
            if user.get("requires_mfa", False):
                return True, user, "MFA required"
                
            return True, user, None
        
        return False, None, "Invalid username or password"
    
    def verify_mfa(self, user_id: str, mfa_code: str) -> bool:
        """
        Verify MFA code for a user.
        
        Args:
            user_id: User ID
            mfa_code: MFA code provided by user
            
        Returns:
            Whether code is valid
        """
        user = self.get_user(user_id)
        if not user or not user.get("requires_mfa") or not user.get("mfa_secret"):
            return False
            
        # TODO: Implement TOTP verification
        # This is a placeholder - implement proper TOTP
        return mfa_code == "123456"
    
    def generate_tokens(self, user_id: str) -> Dict[str, str]:
        """
        Generate JWT tokens for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with access and refresh tokens
        """
        user = self.get_user(user_id)
        if not user:
            return {"error": "User not found"}
            
        # Create tokens with custom claims
        additional_claims = {
            "username": user["username"],
            "role": user["role"]
        }
        
        access_token = create_access_token(
            identity=user_id, 
            additional_claims=additional_claims
        )
        
        refresh_token = create_refresh_token(
            identity=user_id
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        if not os.path.exists(user_file):
            return None
            
        with open(user_file, 'r') as f:
            return json.load(f)
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Update user data.
        
        Args:
            user_id: User ID
            data: Dict of fields to update
            
        Returns:
            Success flag
        """
        user = self.get_user(user_id)
        if not user:
            return False
            
        # Don't allow updating critical fields directly
        forbidden_keys = ["id", "password_hash", "role", "created_at"]
        
        # Update fields
        for key, value in data.items():
            if key not in forbidden_keys:
                # Handle nested profile updates
                if key == "profile" and isinstance(value, dict):
                    if "profile" not in user:
                        user["profile"] = {}
                    for profile_key, profile_value in value.items():
                        user["profile"][profile_key] = profile_value
                else:
                    user[key] = value
        
        # Save user file
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
            
        # If username or email changed, update index
        if "username" in data or "email" in data:
            self._update_user_index(user_id, user.get("username"), user.get("email"))
            
        return True
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success, error_message)
        """
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
            
        # Verify current password
        stored_hash = user.get("password_hash", "").encode('utf-8')
        if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash):
            return False, "Current password is incorrect"
            
        # Hash the new password
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), 
                               bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
        
        user["password_hash"] = new_hash.decode('utf-8')
        
        # Save user file
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
            
        return True, None
    
    def reset_password(self, user_id: str, new_password: str) -> bool:
        """
        Reset user password (admin function).
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            Success flag
        """
        user = self.get_user(user_id)
        if not user:
            return False
            
        # Hash the new password
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), 
                               bcrypt.gensalt(rounds=BCRYPT_ROUNDS))
        
        user["password_hash"] = new_hash.decode('utf-8')
        
        # Save user file
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
            
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID."""
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        if not os.path.exists(user_file):
            return False
            
        # Get user info for index update
        with open(user_file, 'r') as f:
            user_data = json.load(f)
            
        # Remove from index
        self._remove_from_index(user_id)
        
        # Delete user file
        os.remove(user_file)
        
        return True
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users (admin function)."""
        users = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json') and filename != "user_index.json":
                user_file = os.path.join(self.storage_dir, filename)
                with open(user_file, 'r') as f:
                    user = json.load(f)
                    
                    # Don't expose password hash
                    if "password_hash" in user:
                        del user["password_hash"]
                        
                    users.append(user)
        
        return users
    
    def update_credits(self, user_id: str, amount: float, 
                      transaction_type: str, description: str = None) -> bool:
        """
        Update user credits with a transaction.
        
        Args:
            user_id: User ID
            amount: Credit amount (positive for additions, negative for deductions)
            transaction_type: Type of transaction (purchase, usage, refund, bonus, etc.)
            description: Optional transaction description
            
        Returns:
            Success flag
        """
        user = self.get_user(user_id)
        if not user:
            return False
            
        # Don't allow negative credits
        if user.get("credits", 0) + amount < 0:
            return False
            
        # Update credits
        user["credits"] = user.get("credits", 0) + amount
        
        # Save user file
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(user_file, 'w') as f:
            json.dump(user, f, indent=2)
            
        # Record transaction
        transaction = CreditTransaction()
        transaction.record_transaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description
        )
        
        return True
    
    def get_credits(self, user_id: str) -> float:
        """Get current credit balance for a user."""
        user = self.get_user(user_id)
        if not user:
            return 0
            
        return user.get("credits", 0)
    
    def _get_user_by_username_or_email(self, username: str = None, email: str = None) -> Optional[Dict[str, Any]]:
        """
        Get user by username or email.
        
        Returns:
            User data or None if not found
        """
        if not username and not email:
            return None
            
        # Load index
        with open(self.index_file, 'r') as f:
            index = json.load(f)
            
        user_id = None
        
        if username and username in index["users"]:
            user_id = index["users"][username]
        elif email and email in index["users"]:
            user_id = index["users"][email]
            
        if user_id:
            return self.get_user(user_id)
            
        return None
    
    def _update_user_index(self, user_id: str, username: str = None, email: str = None) -> None:
        """Update the user index with username and email."""
        with open(self.index_file, 'r') as f:
            index = json.load(f)
            
        # Add username to index
        if username:
            index["users"][username] = user_id
            
        # Add email to index
        if email:
            index["users"][email] = user_id
            
        # Save index
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _remove_from_index(self, user_id: str) -> None:
        """Remove user from index."""
        with open(self.index_file, 'r') as f:
            index = json.load(f)
            
        # Find and remove user entries
        keys_to_remove = []
        for key, val in index["users"].items():
            if val == user_id:
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            if key in index["users"]:
                del index["users"][key]
                
        # Save index
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)


class CreditTransaction:
    """Manages credit transactions and history."""
    
    def __init__(self, storage_dir: str = None):
        """Initialize with the storage directory."""
        if storage_dir is None:
            self.storage_dir = os.path.join(BASE_DIR, "data", "transactions")
        else:
            self.storage_dir = storage_dir
            
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def record_transaction(self, user_id: str, amount: float, 
                          transaction_type: str, description: str = None) -> str:
        """
        Record a credit transaction.
        
        Args:
            user_id: User ID
            amount: Transaction amount (positive for credits added, negative for used)
            transaction_type: Type of transaction
            description: Optional description
            
        Returns:
            Transaction ID
        """
        transaction_id = str(uuid.uuid4())
        timestamp = time.time()
        
        transaction_data = {
            "id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "transaction_type": transaction_type,
            "description": description,
            "created_at": timestamp
        }
        
        # Use year/month directories for better organization
        date = datetime.datetime.fromtimestamp(timestamp)
        year_month = date.strftime("%Y-%m")
        
        # Create directory if it doesn't exist
        transaction_dir = os.path.join(self.storage_dir, year_month)
        os.makedirs(transaction_dir, exist_ok=True)
        
        # Save transaction file
        transaction_file = os.path.join(transaction_dir, f"{transaction_id}.json")
        with open(transaction_file, 'w') as f:
            json.dump(transaction_data, f, indent=2)
            
        return transaction_id
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID."""
        # Need to search through year/month directories
        for year_month in os.listdir(self.storage_dir):
            if os.path.isdir(os.path.join(self.storage_dir, year_month)):
                transaction_file = os.path.join(self.storage_dir, year_month, f"{transaction_id}.json")
                if os.path.exists(transaction_file):
                    with open(transaction_file, 'r') as f:
                        return json.load(f)
        
        return None
    
    def get_user_transactions(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get transactions for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions, most recent first
        """
        transactions = []
        
        # Search through year/month directories
        for year_month in sorted(os.listdir(self.storage_dir), reverse=True):
            if os.path.isdir(os.path.join(self.storage_dir, year_month)):
                month_dir = os.path.join(self.storage_dir, year_month)
                
                for filename in os.listdir(month_dir):
                    if filename.endswith('.json'):
                        transaction_file = os.path.join(month_dir, filename)
                        with open(transaction_file, 'r') as f:
                            transaction = json.load(f)
                            
                            if transaction.get("user_id") == user_id:
                                transactions.append(transaction)
                                
                                if len(transactions) >= limit:
                                    return sorted(transactions, 
                                                 key=lambda x: x.get("created_at", 0), 
                                                 reverse=True)
        
        return sorted(transactions, 
                     key=lambda x: x.get("created_at", 0), 
                     reverse=True)