"""
Credit system for managing and tracking usage.
"""

import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime

class CreditSystem:
    """Credit system for tracking and managing user usage."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize the credit system.
        
        Args:
            storage_dir: Directory for storing credit transactions
        """
        # Set up storage directory
        if storage_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            storage_dir = os.path.join(base_dir, "data", "credits")
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize transaction directory
        self.transaction_dir = os.path.join(self.storage_dir, "transactions")
        os.makedirs(self.transaction_dir, exist_ok=True)
    
    def get_user_balance(self, user_id: str) -> int:
        """Get a user's current credit balance.
        
        Args:
            user_id: User ID
            
        Returns:
            Current credit balance
        """
        # Get user balance file
        balance_file = os.path.join(self.storage_dir, f"{user_id}.json")
        
        if not os.path.exists(balance_file):
            return 0
        
        with open(balance_file, 'r') as f:
            try:
                data = json.load(f)
                return data.get("balance", 0)
            except json.JSONDecodeError:
                return 0
    
    def adjust_balance(
        self,
        user_id: str,
        amount: int,
        transaction_type: str,
        description: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Tuple[bool, int]:
        """Adjust a user's credit balance.
        
        Args:
            user_id: User ID
            amount: Amount to adjust (positive for addition, negative for deduction)
            transaction_type: Type of transaction (purchase, usage, refund, etc.)
            description: Optional description of the transaction
            reference_id: Optional reference ID (e.g. order ID for purchases)
            
        Returns:
            Tuple of (success, new balance)
        """
        # Get current balance
        current_balance = self.get_user_balance(user_id)
        
        # Check if deduction would result in negative balance
        if amount < 0 and current_balance + amount < 0:
            return False, current_balance
        
        # Calculate new balance
        new_balance = current_balance + amount
        
        # Update balance file
        balance_file = os.path.join(self.storage_dir, f"{user_id}.json")
        with open(balance_file, 'w') as f:
            json.dump({
                "user_id": user_id,
                "balance": new_balance,
                "updated_at": time.time()
            }, f)
        
        # Record transaction
        self._record_transaction(
            user_id=user_id, 
            amount=amount,
            balance=new_balance,
            transaction_type=transaction_type,
            description=description,
            reference_id=reference_id
        )
        
        return True, new_balance
    
    def check_can_afford(self, user_id: str, amount: int) -> bool:
        """Check if a user can afford a deduction.
        
        Args:
            user_id: User ID
            amount: Amount to check (positive number)
            
        Returns:
            Whether the user has sufficient credits
        """
        if amount <= 0:
            return True
        
        current_balance = self.get_user_balance(user_id)
        return current_balance >= amount
    
    def deduct_usage(
        self,
        user_id: str,
        amount: int,
        feature: str,
        description: Optional[str] = None
    ) -> Tuple[bool, int]:
        """Deduct credits for feature usage.
        
        Args:
            user_id: User ID
            amount: Amount to deduct (positive number)
            feature: Feature being used
            description: Optional description
            
        Returns:
            Tuple of (success, new balance)
        """
        if amount <= 0:
            return True, self.get_user_balance(user_id)
        
        return self.adjust_balance(
            user_id=user_id,
            amount=-amount,  # Negative for deduction
            transaction_type="usage",
            description=f"Usage: {feature}" + (f" - {description}" if description else ""),
            reference_id=None
        )
    
    def add_credits(
        self,
        user_id: str,
        amount: int,
        transaction_type: str = "purchase",
        description: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Tuple[bool, int]:
        """Add credits to a user's balance.
        
        Args:
            user_id: User ID
            amount: Amount to add (positive number)
            transaction_type: Type of transaction (purchase, bonus, etc.)
            description: Optional description
            reference_id: Optional reference ID
            
        Returns:
            Tuple of (success, new balance)
        """
        if amount <= 0:
            return False, self.get_user_balance(user_id)
        
        return self.adjust_balance(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            reference_id=reference_id
        )
    
    def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50,
        transaction_type: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get transaction history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of transactions to return
            transaction_type: Filter by transaction type
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of transaction records
        """
        # Get user transaction directory
        user_transaction_dir = os.path.join(self.transaction_dir, user_id)
        
        if not os.path.exists(user_transaction_dir):
            return []
        
        transactions = []
        
        # Get all transaction files and sort by modification time (newest first)
        transaction_files = sorted(
            [os.path.join(user_transaction_dir, f) for f in os.listdir(user_transaction_dir)],
            key=os.path.getmtime,
            reverse=True
        )
        
        # Get transactions
        for file_path in transaction_files:
            if len(transactions) >= limit:
                break
            
            with open(file_path, 'r') as f:
                try:
                    transaction = json.load(f)
                    
                    # Apply filters
                    if transaction_type and transaction.get("transaction_type") != transaction_type:
                        continue
                    
                    if start_time and transaction.get("timestamp", 0) < start_time:
                        continue
                    
                    if end_time and transaction.get("timestamp", 0) > end_time:
                        continue
                    
                    transactions.append(transaction)
                except json.JSONDecodeError:
                    continue
        
        return transactions[:limit]
    
    def get_usage_summary(
        self,
        user_id: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get usage summary for a user.
        
        Args:
            user_id: User ID
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            Usage summary dictionary
        """
        # Default to last 30 days if no time range specified
        if start_time is None:
            start_time = time.time() - (30 * 86400)  # 30 days ago
        
        if end_time is None:
            end_time = time.time()
        
        # Get all transactions in the time range
        transactions = self.get_transaction_history(
            user_id=user_id,
            limit=1000,  # High limit to get all transactions
            start_time=start_time,
            end_time=end_time
        )
        
        # Calculate usage statistics
        total_usage = 0
        usage_by_feature = {}
        purchases = 0
        refunds = 0
        
        for transaction in transactions:
            transaction_type = transaction.get("transaction_type", "")
            amount = transaction.get("amount", 0)
            
            if transaction_type == "usage":
                total_usage += abs(amount)
                
                # Extract feature from description
                description = transaction.get("description", "")
                feature = "unknown"
                
                if description.startswith("Usage: "):
                    feature_part = description[7:]
                    # Get everything before the first dash if it exists
                    if " - " in feature_part:
                        feature = feature_part.split(" - ")[0].strip()
                    else:
                        feature = feature_part.strip()
                
                if feature not in usage_by_feature:
                    usage_by_feature[feature] = 0
                
                usage_by_feature[feature] += abs(amount)
            
            elif transaction_type == "purchase":
                purchases += amount
            
            elif transaction_type == "refund":
                refunds += abs(amount)
        
        # Calculate current balance
        current_balance = self.get_user_balance(user_id)
        
        # Calculate usage periods
        time_periods = [
            {
                "name": "Last 24 hours",
                "start_time": time.time() - 86400,
                "usage": 0
            },
            {
                "name": "Last 7 days",
                "start_time": time.time() - (7 * 86400),
                "usage": 0
            },
            {
                "name": "Last 30 days",
                "start_time": time.time() - (30 * 86400),
                "usage": 0
            }
        ]
        
        for transaction in transactions:
            transaction_type = transaction.get("transaction_type", "")
            amount = transaction.get("amount", 0)
            timestamp = transaction.get("timestamp", 0)
            
            if transaction_type == "usage":
                for period in time_periods:
                    if timestamp >= period["start_time"]:
                        period["usage"] += abs(amount)
        
        return {
            "user_id": user_id,
            "current_balance": current_balance,
            "total_usage": total_usage,
            "usage_by_feature": usage_by_feature,
            "time_periods": time_periods,
            "purchases": purchases,
            "refunds": refunds,
            "start_time": start_time,
            "end_time": end_time
        }
    
    def transfer_credits(
        self,
        from_user_id: str,
        to_user_id: str,
        amount: int,
        description: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Transfer credits from one user to another.
        
        Args:
            from_user_id: User ID to transfer from
            to_user_id: User ID to transfer to
            amount: Amount to transfer (positive number)
            description: Optional description
            
        Returns:
            Tuple of (success, message)
        """
        if amount <= 0:
            return False, "Amount must be positive"
        
        # Check if source user can afford the transfer
        if not self.check_can_afford(from_user_id, amount):
            return False, "Insufficient credits"
        
        # Generate a transfer ID to link the transactions
        transfer_id = str(uuid.uuid4())
        
        # Deduct from source user
        success, _ = self.adjust_balance(
            user_id=from_user_id,
            amount=-amount,
            transaction_type="transfer_out",
            description=f"Transfer to user {to_user_id}" + (f" - {description}" if description else ""),
            reference_id=transfer_id
        )
        
        if not success:
            return False, "Failed to deduct credits from source user"
        
        # Add to destination user
        success, _ = self.adjust_balance(
            user_id=to_user_id,
            amount=amount,
            transaction_type="transfer_in",
            description=f"Transfer from user {from_user_id}" + (f" - {description}" if description else ""),
            reference_id=transfer_id
        )
        
        if not success:
            # Rollback the source user deduction
            self.adjust_balance(
                user_id=from_user_id,
                amount=amount,
                transaction_type="transfer_rollback",
                description=f"Rollback failed transfer to user {to_user_id}",
                reference_id=transfer_id
            )
            return False, "Failed to add credits to destination user"
        
        return True, f"Successfully transferred {amount} credits"
    
    def _record_transaction(
        self,
        user_id: str,
        amount: int,
        balance: int,
        transaction_type: str,
        description: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> str:
        """Record a transaction.
        
        Args:
            user_id: User ID
            amount: Amount adjusted
            balance: New balance after adjustment
            transaction_type: Type of transaction
            description: Optional description
            reference_id: Optional reference ID
            
        Returns:
            Transaction ID
        """
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Create transaction data
        transaction = {
            "id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "balance": balance,
            "transaction_type": transaction_type,
            "description": description,
            "reference_id": reference_id,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat()
        }
        
        # Create user transaction directory if it doesn't exist
        user_transaction_dir = os.path.join(self.transaction_dir, user_id)
        os.makedirs(user_transaction_dir, exist_ok=True)
        
        # Save transaction
        transaction_file = os.path.join(user_transaction_dir, f"{transaction_id}.json")
        with open(transaction_file, 'w') as f:
            json.dump(transaction, f, indent=2)
        
        return transaction_id
    
    def create_credit_package(
        self,
        name: str,
        credits: int,
        price: float,
        is_active: bool = True,
        description: Optional[str] = None
    ) -> str:
        """Create a credit package for users to purchase.
        
        Args:
            name: Package name
            credits: Number of credits in the package
            price: Price of the package
            is_active: Whether the package is active
            description: Optional description
            
        Returns:
            Package ID
        """
        # Generate package ID
        package_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Create package data
        package = {
            "id": package_id,
            "name": name,
            "credits": credits,
            "price": price,
            "is_active": is_active,
            "description": description,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Save package
        packages_dir = os.path.join(self.storage_dir, "packages")
        os.makedirs(packages_dir, exist_ok=True)
        
        package_file = os.path.join(packages_dir, f"{package_id}.json")
        with open(package_file, 'w') as f:
            json.dump(package, f, indent=2)
        
        return package_id
    
    def get_credit_packages(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get all credit packages.
        
        Args:
            include_inactive: Whether to include inactive packages
            
        Returns:
            List of credit packages
        """
        packages = []
        packages_dir = os.path.join(self.storage_dir, "packages")
        
        if not os.path.exists(packages_dir):
            return []
        
        for filename in os.listdir(packages_dir):
            if not filename.endswith(".json"):
                continue
            
            package_file = os.path.join(packages_dir, filename)
            
            with open(package_file, 'r') as f:
                try:
                    package = json.load(f)
                    
                    # Skip inactive packages if not requested
                    if not include_inactive and not package.get("is_active", True):
                        continue
                    
                    packages.append(package)
                except json.JSONDecodeError:
                    continue
        
        # Sort by price ascending
        return sorted(packages, key=lambda x: x.get("price", 0))
    
    def purchase_credit_package(
        self,
        user_id: str,
        package_id: str,
        payment_ref: Optional[str] = None
    ) -> Tuple[bool, str, int]:
        """Purchase a credit package for a user.
        
        Args:
            user_id: User ID
            package_id: Package ID
            payment_ref: Optional payment reference
            
        Returns:
            Tuple of (success, message, credits_added)
        """
        # Get package
        packages_dir = os.path.join(self.storage_dir, "packages")
        package_file = os.path.join(packages_dir, f"{package_id}.json")
        
        if not os.path.exists(package_file):
            return False, "Package not found", 0
        
        with open(package_file, 'r') as f:
            try:
                package = json.load(f)
            except json.JSONDecodeError:
                return False, "Invalid package data", 0
        
        # Check if package is active
        if not package.get("is_active", True):
            return False, "Package is not available for purchase", 0
        
        # Add credits to user
        credits = package.get("credits", 0)
        success, _ = self.add_credits(
            user_id=user_id,
            amount=credits,
            transaction_type="purchase",
            description=f"Purchase of {package.get('name')} package",
            reference_id=payment_ref or package_id
        )
        
        if not success:
            return False, "Failed to add credits", 0
        
        return True, f"Successfully purchased {credits} credits", credits