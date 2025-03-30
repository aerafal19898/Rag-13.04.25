"""
Audit logging system for security and compliance.
"""

import os
import json
import time
import uuid
import socket
import logging
import traceback
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime

class AuditLogger:
    """Audit logging for security and compliance tracking."""
    
    def __init__(self, log_dir: Optional[str] = None, enabled: bool = True):
        """Initialize the audit logger.
        
        Args:
            log_dir: Directory for storing audit logs
            enabled: Whether audit logging is enabled
        """
        # Set up log directory
        if log_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            log_dir = os.path.join(base_dir, "data", "audit_logs")
        
        self.log_dir = log_dir
        self.enabled = enabled
        self.hostname = socket.gethostname()
        
        # Create log directory if it doesn't exist
        if self.enabled:
            os.makedirs(self.log_dir, exist_ok=True)
        
        # Set up logger
        self.logger = logging.getLogger("audit")
        handler = logging.FileHandler(os.path.join(self.log_dir, "audit.log"))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Log an audit event.
        
        Args:
            event_type: Type of event (e.g., authentication, access, data)
            user_id: ID of the user performing the action
            resource_id: ID of the resource being accessed
            resource_type: Type of resource being accessed
            action: Action being performed
            status: Status of the action (success, failure, error)
            details: Additional details about the event
            ip_address: IP address of the user
            session_id: Session ID of the user
            
        Returns:
            ID of the logged event
        """
        if not self.enabled:
            return ""
        
        event_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Create event data
        event_data = {
            "id": event_id,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "action": action,
            "status": status,
            "details": details or {},
            "ip_address": ip_address,
            "session_id": session_id,
            "hostname": self.hostname
        }
        
        # Log to structured log file
        self._write_log_entry(event_data)
        
        # Also log a simple message to the logger
        message = f"{event_type}.{action} - User: {user_id} - Resource: {resource_id} - Status: {status}"
        if status == "success":
            self.logger.info(message)
        elif status == "failure":
            self.logger.warning(message)
        else:
            self.logger.error(message)
        
        return event_id
    
    def log_authentication(
        self,
        user_id: Optional[str],
        action: str,
        status: str,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an authentication event.
        
        Args:
            user_id: ID of the user
            action: Action being performed (login, logout, etc.)
            status: Status of the action (success, failure, error)
            ip_address: IP address of the user
            session_id: Session ID of the user
            details: Additional details about the event
            
        Returns:
            ID of the logged event
        """
        return self.log_event(
            event_type="authentication",
            user_id=user_id,
            action=action,
            status=status,
            ip_address=ip_address,
            session_id=session_id,
            details=details
        )
    
    def log_access(
        self,
        user_id: Optional[str],
        resource_id: str,
        resource_type: str,
        action: str,
        status: str,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an access event.
        
        Args:
            user_id: ID of the user
            resource_id: ID of the resource being accessed
            resource_type: Type of resource being accessed
            action: Action being performed (read, write, delete)
            status: Status of the action (success, failure, error)
            ip_address: IP address of the user
            session_id: Session ID of the user
            details: Additional details about the event
            
        Returns:
            ID of the logged event
        """
        return self.log_event(
            event_type="access",
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            status=status,
            ip_address=ip_address,
            session_id=session_id,
            details=details
        )
    
    def log_data_event(
        self,
        user_id: Optional[str],
        resource_id: str,
        resource_type: str,
        action: str,
        status: str,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a data event.
        
        Args:
            user_id: ID of the user
            resource_id: ID of the resource being accessed
            resource_type: Type of resource being accessed
            action: Action being performed (create, update, delete)
            status: Status of the action (success, failure, error)
            ip_address: IP address of the user
            session_id: Session ID of the user
            details: Additional details about the event
            
        Returns:
            ID of the logged event
        """
        return self.log_event(
            event_type="data",
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            status=status,
            ip_address=ip_address,
            session_id=session_id,
            details=details
        )
    
    def log_exception(
        self,
        exception: Exception,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Log an exception.
        
        Args:
            exception: Exception object
            user_id: ID of the user
            resource_id: ID of the resource being accessed
            resource_type: Type of resource being accessed
            action: Action being performed
            ip_address: IP address of the user
            session_id: Session ID of the user
            
        Returns:
            ID of the logged event
        """
        tb = traceback.format_exc()
        
        return self.log_event(
            event_type="exception",
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            status="error",
            ip_address=ip_address,
            session_id=session_id,
            details={
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "traceback": tb
            }
        )
    
    def get_events(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        event_type: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit events within a time range.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            user_id: Filter by user ID
            resource_id: Filter by resource ID
            event_type: Filter by event type
            action: Filter by action
            status: Filter by status
            limit: Maximum number of events to return
            
        Returns:
            List of audit events
        """
        if not self.enabled:
            return []
        
        events = []
        
        # Default to last 24 hours if no time range specified
        if start_time is None:
            start_time = time.time() - 86400  # Last 24 hours
        
        if end_time is None:
            end_time = time.time()
        
        # Convert timestamps to dates for file lookup
        start_date = datetime.fromtimestamp(start_time).strftime("%Y%m%d")
        end_date = datetime.fromtimestamp(end_time).strftime("%Y%m%d")
        
        # Get all dates between start and end
        current_date = start_date
        date_range = []
        
        while current_date <= end_date:
            date_range.append(current_date)
            year = int(current_date[:4])
            month = int(current_date[4:6])
            day = int(current_date[6:8])
            
            # Increment date by one day
            dt = datetime(year, month, day)
            next_dt = dt.replace(day=dt.day + 1)
            current_date = next_dt.strftime("%Y%m%d")
        
        # Look for log files for each date
        for date in date_range:
            log_file = os.path.join(self.log_dir, f"{date}.jsonl")
            
            if not os.path.exists(log_file):
                continue
            
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        
                        # Apply filters
                        if start_time and event.get("timestamp", 0) < start_time:
                            continue
                        
                        if end_time and event.get("timestamp", 0) > end_time:
                            continue
                        
                        if user_id and event.get("user_id") != user_id:
                            continue
                        
                        if resource_id and event.get("resource_id") != resource_id:
                            continue
                        
                        if event_type and event.get("event_type") != event_type:
                            continue
                        
                        if action and event.get("action") != action:
                            continue
                        
                        if status and event.get("status") != status:
                            continue
                        
                        events.append(event)
                        
                        if len(events) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
            
            if len(events) >= limit:
                break
        
        # Sort by timestamp in descending order (newest first)
        events.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return events[:limit]
    
    def _write_log_entry(self, event_data: Dict[str, Any]) -> None:
        """Write an event to the appropriate log file.
        
        Args:
            event_data: Event data to write
        """
        # Get the date for the log file
        date = datetime.fromtimestamp(event_data["timestamp"]).strftime("%Y%m%d")
        log_file = os.path.join(self.log_dir, f"{date}.jsonl")
        
        # Append to log file
        with open(log_file, 'a') as f:
            f.write(json.dumps(event_data) + "\n")
    
    def export_events(
        self,
        output_file: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        event_type: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        format: str = "jsonl"
    ) -> int:
        """Export audit events to a file.
        
        Args:
            output_file: Path to output file
            start_time: Start timestamp
            end_time: End timestamp
            user_id: Filter by user ID
            resource_id: Filter by resource ID
            event_type: Filter by event type
            action: Filter by action
            status: Filter by status
            format: Output format (jsonl or csv)
            
        Returns:
            Number of events exported
        """
        if not self.enabled:
            return 0
        
        # Get events with filters
        events = self.get_events(
            start_time=start_time,
            end_time=end_time,
            user_id=user_id,
            resource_id=resource_id,
            event_type=event_type,
            action=action,
            status=status,
            limit=1000000  # High limit for export
        )
        
        if not events:
            return 0
        
        # Export to file
        if format.lower() == "jsonl":
            with open(output_file, 'w') as f:
                for event in events:
                    f.write(json.dumps(event) + "\n")
        elif format.lower() == "csv":
            import csv
            
            # Determine fields from first event
            fields = list(events[0].keys())
            
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                
                for event in events:
                    # Handle nested dictionaries for CSV export
                    if "details" in event and isinstance(event["details"], dict):
                        # Convert details dict to string representation
                        event["details"] = json.dumps(event["details"])
                    
                    writer.writerow(event)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return len(events)
    
    def purge_old_logs(self, days_to_keep: int = 365) -> int:
        """Delete old audit logs beyond a certain age.
        
        Args:
            days_to_keep: Number of days of logs to keep
            
        Returns:
            Number of log files deleted
        """
        if not self.enabled:
            return 0
        
        # Calculate cutoff date
        cutoff_time = time.time() - (days_to_keep * 86400)
        cutoff_date = datetime.fromtimestamp(cutoff_time).strftime("%Y%m%d")
        
        deleted_count = 0
        
        # Loop through all log files
        for filename in os.listdir(self.log_dir):
            if filename.endswith(".jsonl") and filename[:8].isdigit():
                file_date = filename[:8]
                
                # Delete if older than cutoff
                if file_date < cutoff_date:
                    try:
                        os.remove(os.path.join(self.log_dir, filename))
                        deleted_count += 1
                    except Exception:
                        pass
        
        return deleted_count