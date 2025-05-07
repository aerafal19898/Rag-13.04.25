"""
Feedback system for collecting and processing user feedback.
"""

import os
import json
import time
import uuid
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime

class FeedbackManager:
    """Manage user feedback and suggestions. Now supports aggregation of user satisfaction metrics (task 2.2)."""
    
    def __init__(
        self, 
        storage_dir: Optional[str] = None,
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        recipient_email: Optional[str] = None,
        use_tls: bool = True
    ):
        """Initialize the feedback manager.
        
        Args:
            storage_dir: Directory for storing feedback
            smtp_server: SMTP server for sending email
            smtp_port: SMTP port
            smtp_username: SMTP username
            smtp_password: SMTP password
            sender_email: Sender email address
            recipient_email: Recipient email address for feedback notifications
            use_tls: Whether to use TLS for SMTP connection
        """
        # Set up storage directory
        if storage_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            storage_dir = os.path.join(base_dir, "data", "feedback")
        
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Set up email configuration
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.sender_email = sender_email
        self.recipient_email = recipient_email
        self.use_tls = use_tls
        
        # Set up logger
        self.logger = logging.getLogger("feedback")
        handler = logging.FileHandler(os.path.join(self.storage_dir, "feedback.log"))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def submit_feedback(
        self,
        user_id: Optional[str],
        feedback_type: str,
        content: str,
        rating: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        send_notification: bool = True
    ) -> str:
        """Submit feedback.
        
        Args:
            user_id: ID of the user submitting feedback
            feedback_type: Type of feedback (bug, feature, general, etc.)
            content: Feedback text content
            rating: Optional numerical rating (e.g., 1-5)
            metadata: Additional metadata about the feedback
            send_notification: Whether to send an email notification
            
        Returns:
            Feedback ID
        """
        # Generate feedback ID
        feedback_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Create feedback data
        feedback = {
            "id": feedback_id,
            "user_id": user_id,
            "feedback_type": feedback_type,
            "content": content,
            "rating": rating,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "status": "new"
        }
        
        # Save feedback
        feedback_file = os.path.join(self.storage_dir, f"{feedback_id}.json")
        with open(feedback_file, 'w') as f:
            json.dump(feedback, f, indent=2)
        
        # Log feedback submission
        self.logger.info(f"Feedback submitted: {feedback_id} - Type: {feedback_type} - User: {user_id}")
        
        # Send email notification if configured
        if send_notification and self.smtp_server and self.recipient_email:
            try:
                self._send_notification(feedback)
            except Exception as e:
                self.logger.error(f"Failed to send feedback notification: {e}")
        
        return feedback_id
    
    def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback by ID.
        
        Args:
            feedback_id: Feedback ID
            
        Returns:
            Feedback data or None if not found
        """
        feedback_file = os.path.join(self.storage_dir, f"{feedback_id}.json")
        
        if not os.path.exists(feedback_file):
            return None
        
        with open(feedback_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
    
    def update_feedback_status(
        self,
        feedback_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update the status of feedback.
        
        Args:
            feedback_id: Feedback ID
            status: New status (new, in_progress, resolved, closed)
            notes: Optional notes about the status change
            
        Returns:
            Whether the update was successful
        """
        feedback = self.get_feedback(feedback_id)
        
        if not feedback:
            return False
        
        # Update status
        feedback["status"] = status
        feedback["updated_at"] = time.time()
        
        # Add status history if it doesn't exist
        if "status_history" not in feedback:
            feedback["status_history"] = []
        
        # Add status change to history
        feedback["status_history"].append({
            "status": status,
            "timestamp": time.time(),
            "datetime": datetime.fromtimestamp(time.time()).isoformat(),
            "notes": notes
        })
        
        # Save updated feedback
        feedback_file = os.path.join(self.storage_dir, f"{feedback_id}.json")
        with open(feedback_file, 'w') as f:
            json.dump(feedback, f, indent=2)
        
        # Log status change
        self.logger.info(f"Feedback status updated: {feedback_id} - Status: {status}")
        
        return True
    
    def list_feedback(
        self,
        status: Optional[str] = None,
        feedback_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List feedback entries with optional filters.
        
        Args:
            status: Filter by status
            feedback_type: Filter by feedback type
            user_id: Filter by user ID
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of entries to return
            
        Returns:
            List of feedback entries
        """
        feedback_list = []
        
        # Default time range
        if start_time is None:
            start_time = 0
        
        if end_time is None:
            end_time = time.time()
        
        # Get all feedback files
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith(".json") or filename == "feedback.log":
                continue
            
            feedback_file = os.path.join(self.storage_dir, filename)
            
            with open(feedback_file, 'r') as f:
                try:
                    feedback = json.load(f)
                    
                    # Apply filters
                    if status and feedback.get("status") != status:
                        continue
                    
                    if feedback_type and feedback.get("feedback_type") != feedback_type:
                        continue
                    
                    if user_id and feedback.get("user_id") != user_id:
                        continue
                    
                    if feedback.get("timestamp", 0) < start_time:
                        continue
                    
                    if feedback.get("timestamp", 0) > end_time:
                        continue
                    
                    feedback_list.append(feedback)
                    
                    if len(feedback_list) >= limit:
                        break
                except json.JSONDecodeError:
                    continue
        
        # Sort by timestamp in descending order (newest first)
        feedback_list.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return feedback_list[:limit]
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get a summary of feedback statistics.
        
        Returns:
            Summary statistics
        """
        summary = {
            "total": 0,
            "by_status": {},
            "by_type": {},
            "by_rating": {},
            "recent": []
        }
        
        # Process all feedback
        for filename in os.listdir(self.storage_dir):
            if not filename.endswith(".json") or filename == "feedback.log":
                continue
            
            feedback_file = os.path.join(self.storage_dir, filename)
            
            with open(feedback_file, 'r') as f:
                try:
                    feedback = json.load(f)
                    
                    # Increment total
                    summary["total"] += 1
                    
                    # Count by status
                    status = feedback.get("status", "unknown")
                    if status not in summary["by_status"]:
                        summary["by_status"][status] = 0
                    summary["by_status"][status] += 1
                    
                    # Count by type
                    feedback_type = feedback.get("feedback_type", "unknown")
                    if feedback_type not in summary["by_type"]:
                        summary["by_type"][feedback_type] = 0
                    summary["by_type"][feedback_type] += 1
                    
                    # Count by rating
                    rating = feedback.get("rating")
                    if rating is not None:
                        rating_str = str(rating)
                        if rating_str not in summary["by_rating"]:
                            summary["by_rating"][rating_str] = 0
                        summary["by_rating"][rating_str] += 1
                    
                    # Add to recent list if newly submitted
                    if feedback.get("timestamp", 0) > time.time() - 86400:  # Within last 24 hours
                        summary["recent"].append({
                            "id": feedback.get("id"),
                            "feedback_type": feedback_type,
                            "rating": rating,
                            "status": status,
                            "datetime": feedback.get("datetime"),
                            "user_id": feedback.get("user_id")
                        })
                except json.JSONDecodeError:
                    continue
        
        # Sort recent feedback by timestamp
        summary["recent"].sort(key=lambda x: x.get("datetime", ""), reverse=True)
        
        return summary
    
    def export_feedback(
        self,
        output_file: str,
        status: Optional[str] = None,
        feedback_type: Optional[str] = None,
        format: str = "csv"
    ) -> int:
        """Export feedback to a file.
        
        Args:
            output_file: Path to output file
            status: Filter by status
            feedback_type: Filter by feedback type
            format: Output format (csv or jsonl)
            
        Returns:
            Number of feedback entries exported
        """
        # Get all feedback with filters
        feedback_list = self.list_feedback(
            status=status,
            feedback_type=feedback_type,
            limit=1000000  # High limit for export
        )
        
        if not feedback_list:
            return 0
        
        # Export to file
        if format.lower() == "csv":
            import csv
            
            # Determine fields from first feedback
            fields = ["id", "user_id", "feedback_type", "content", "rating", "status", "datetime"]
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                
                for feedback in feedback_list:
                    # Create a simplified row with selected fields
                    row = {field: feedback.get(field, "") for field in fields}
                    writer.writerow(row)
        elif format.lower() == "jsonl":
            with open(output_file, 'w') as f:
                for feedback in feedback_list:
                    f.write(json.dumps(feedback) + "\n")
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return len(feedback_list)
    
    def delete_feedback(self, feedback_id: str) -> bool:
        """Delete feedback by ID.
        
        Args:
            feedback_id: Feedback ID
            
        Returns:
            Whether the deletion was successful
        """
        feedback_file = os.path.join(self.storage_dir, f"{feedback_id}.json")
        
        if not os.path.exists(feedback_file):
            return False
        
        # Delete the file
        os.remove(feedback_file)
        
        # Log deletion
        self.logger.info(f"Feedback deleted: {feedback_id}")
        
        return True
    
    def _send_notification(self, feedback: Dict[str, Any]) -> bool:
        """Send an email notification about new feedback.
        
        Args:
            feedback: Feedback data
            
        Returns:
            Whether the email was sent successfully
        """
        if not self.smtp_server or not self.recipient_email:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email
            msg["Subject"] = f"New Feedback: {feedback.get('feedback_type')} - ID: {feedback.get('id')}"
            
            # Create email body
            body = f"""
            <h2>New Feedback Submission</h2>
            
            <p><strong>ID:</strong> {feedback.get('id')}</p>
            <p><strong>Type:</strong> {feedback.get('feedback_type')}</p>
            <p><strong>User:</strong> {feedback.get('user_id', 'Anonymous')}</p>
            <p><strong>Rating:</strong> {feedback.get('rating', 'N/A')}</p>
            <p><strong>Date:</strong> {feedback.get('datetime')}</p>
            
            <h3>Content:</h3>
            <p>{feedback.get('content')}</p>
            
            <h3>Additional Information:</h3>
            <pre>{json.dumps(feedback.get('metadata', {}), indent=2)}</pre>
            """
            
            # Attach body
            msg.attach(MIMEText(body, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            return True
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")
            return False
    
    def sanitize_feedback(self, content: str) -> str:
        """Sanitize feedback content to prevent spam and malicious content.
        
        Args:
            content: Raw feedback content
            
        Returns:
            Sanitized content
        """
        # Basic sanitization
        sanitized = content.strip()
        
        # Remove excessive whitespace and line breaks
        import re
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Limit length
        if len(sanitized) > 5000:
            sanitized = sanitized[:5000]
        
        # Check for suspicious patterns
        spam_patterns = [
            r'https?://',  # URLs
            r'www\.',
            r'\b(?:viagra|cialis|casino|lottery|winner)\b',  # Common spam words
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email addresses
        ]
        
        # Flag content as potentially spam
        is_potential_spam = False
        for pattern in spam_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                is_potential_spam = True
                break
        
        # Add spam warning if detected
        if is_potential_spam:
            sanitized = "[POTENTIAL SPAM] " + sanitized
        
        return sanitized
    
    def validate_feedback(
        self,
        content: str,
        feedback_type: str,
        rating: Optional[int] = None
    ) -> Tuple[bool, str]:
        """Validate feedback before submission.
        
        Args:
            content: Feedback content
            feedback_type: Feedback type
            rating: Optional numerical rating
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for empty content
        if not content or len(content.strip()) < 5:
            return False, "Feedback content must be at least 5 characters."
        
        # Check content length
        if len(content) > 5000:
            return False, "Feedback content must be less than 5000 characters."
        
        # Validate feedback type
        valid_types = ["bug", "feature", "general", "suggestion", "other"]
        if feedback_type not in valid_types:
            return False, f"Invalid feedback type. Must be one of: {', '.join(valid_types)}."
        
        # Validate rating if provided
        if rating is not None:
            try:
                rating_val = int(rating)
                if rating_val < 1 or rating_val > 5:
                    return False, "Rating must be between 1 and 5."
            except (ValueError, TypeError):
                return False, "Rating must be a number between 1 and 5."
        
        # Check for potential spam
        sanitized = self.sanitize_feedback(content)
        if sanitized.startswith("[POTENTIAL SPAM]"):
            return False, "Feedback appears to contain spam or prohibited content."
        
        return True, ""
    
    def get_satisfaction_summary(self) -> Dict[str, Any]:
        """Aggregate user satisfaction metrics (average rating, count, etc.)."""
        feedback_list = self.list_feedback(feedback_type=None)
        ratings = [f["rating"] for f in feedback_list if f.get("rating") is not None]
        if not ratings:
            return {"count": 0, "average": None, "min": None, "max": None}
        return {
            "count": len(ratings),
            "average": sum(ratings) / len(ratings),
            "min": min(ratings),
            "max": max(ratings)
        }