"""
Monitoring Service for handling metrics collection, alerting, and logging.
"""

import os
import json
import yaml
import logging
import time
import uuid
import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from app.services.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringManager:
    """
    Monitoring Manager for handling metrics collection, alerting, and logging.
    Now supports business metrics: user satisfaction and cost monitoring (task 2.2).
    """
    
    def __init__(self, db_manager: DatabaseManager, config_path: str = "config"):
        """
        Initialize the monitoring manager.
        
        Args:
            db_manager: Database manager instance
            config_path: Path to configuration files
        """
        self.db_manager = db_manager
        self.config_path = config_path
        
        # Create config directory if it doesn't exist
        os.makedirs(config_path, exist_ok=True)
        
        # Initialize monitoring database
        self._init_db()
        
        # Load monitoring configuration
        self.config = self._load_config()
    
    def _init_db(self):
        """
        Initialize monitoring database.
        """
        # Create metrics tables
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    tags TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    metric_name TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    severity TEXT NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id TEXT PRIMARY KEY,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load monitoring configuration.
        
        Returns:
            Dict containing monitoring configuration
        """
        # Initialize configuration
        config = {
            "metrics": {
                "collection_interval": 60,
                "retention_period": 30,
                "aggregation_functions": ["min", "max", "avg", "sum"]
            },
            "alerts": {
                "check_interval": 60,
                "notification_channels": ["email", "slack", "webhook"],
                "default_severity": "warning"
            },
            "logging": {
                "level": "INFO",
                "retention_period": 30,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
        # Load YAML configuration
        yaml_path = os.path.join(self.config_path, "monitoring.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                config.update(yaml.safe_load(f))
        
        # Load JSON configuration
        json_path = os.path.join(self.config_path, "monitoring.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                config.update(json.load(f))
        
        return config
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """
        Record metric.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Metric tags
        """
        # Generate ID
        metric_id = str(uuid.uuid4())
        
        # Add metric
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO metrics (id, name, value, tags) VALUES (?, ?, ?, ?)",
                [metric_id, name, value, json.dumps(tags) if tags else None]
            )
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "record_metric", {
            "metric_id": metric_id,
            "name": name,
            "value": value,
            "tags": tags
        })
    
    def get_metrics(self, name: str = None, start_time: datetime.datetime = None, end_time: datetime.datetime = None) -> List[Dict[str, Any]]:
        """
        Get metrics.
        
        Args:
            name: Filter by name
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of metrics
        """
        # Initialize query
        query = "SELECT * FROM metrics"
        params = []
        
        # Check if name, start_time, or end_time is provided
        if name or start_time or end_time:
            query += " WHERE"
            
            # Check if name is provided
            if name:
                query += " name = ?"
                params.append(name)
            
            # Check if start_time is provided
            if start_time:
                if name:
                    query += " AND"
                query += " timestamp >= ?"
                params.append(start_time)
            
            # Check if end_time is provided
            if end_time:
                if name or start_time:
                    query += " AND"
                query += " timestamp <= ?"
                params.append(end_time)
        
        # Execute query
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Get metrics
            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    "id": row[0],
                    "name": row[1],
                    "value": row[2],
                    "tags": json.loads(row[3]) if row[3] else None,
                    "timestamp": row[4]
                })
            
            return metrics
    
    def get_alerts(self, status: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """
        Get alerts.
        
        Args:
            status: Filter by status
            severity: Filter by severity
            
        Returns:
            List of alerts
        """
        # Initialize query
        query = "SELECT * FROM alerts"
        params = []
        
        # Check if status or severity is provided
        if status or severity:
            query += " WHERE"
            
            # Check if status is provided
            if status:
                query += " status = ?"
                params.append(status)
            
            # Check if severity is provided
            if severity:
                if status:
                    query += " AND"
                query += " severity = ?"
                params.append(severity)
        
        # Execute query
        cursor = this.db_manager.execute(query, params)
        
        # Get alerts
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "severity": row[3],
                "status": row[4],
                "created_at": row[5],
                "resolved_at": row[6]
            })
        
        return alerts
    
    def get_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Get alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert
        """
        # Execute query
        cursor = this.db_manager.execute(
            "SELECT * FROM alerts WHERE id = ?",
            [alert_id]
        )
        
        # Get alert
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "severity": row[3],
                "status": row[4],
                "created_at": row[5],
                "resolved_at": row[6]
            }
        
        return None
    
    def create_alert(self, name: str, description: str, severity: str) -> str:
        """
        Create alert.
        
        Args:
            name: Alert name
            description: Alert description
            severity: Alert severity
            
        Returns:
            Alert ID
        """
        # Generate ID
        alert_id = str(uuid.uuid4())
        
        # Add alert
        this.db_manager.execute(
            "INSERT INTO alerts (id, name, description, severity, status) VALUES (?, ?, ?, ?, 'open')",
            [alert_id, name, description, severity]
        )
        
        # Log action
        this.db_manager.log_action(None, "create_alert", {
            "alert_id": alert_id,
            "name": name,
            "description": description,
            "severity": severity
        })
        
        return alert_id
    
    def resolve_alert(self, alert_id: str):
        """
        Resolve alert.
        
        Args:
            alert_id: Alert ID
        """
        # Check if alert exists
        alert = this.get_alert(alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} does not exist")
        
        # Check if alert is already resolved
        if alert["status"] == "resolved":
            raise ValueError(f"Alert {alert_id} is already resolved")
        
        # Update alert
        this.db_manager.execute(
            "UPDATE alerts SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
            [alert_id]
        )
        
        # Log action
        this.db_manager.log_action(None, "resolve_alert", {
            "alert_id": alert_id,
            "name": alert["name"]
        })
    
    def get_alert_rules(self, enabled: bool = None) -> List[Dict[str, Any]]:
        """
        Get alert rules.
        
        Args:
            enabled: Filter by enabled
            
        Returns:
            List of alert rules
        """
        # Initialize query
        query = "SELECT * FROM alert_rules"
        params = []
        
        # Check if enabled is provided
        if enabled is not None:
            query += " WHERE enabled = ?"
            params.append(enabled)
        
        # Execute query
        cursor = this.db_manager.execute(query, params)
        
        # Get alert rules
        alert_rules = []
        for row in cursor.fetchall():
            alert_rules.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "metric_name": row[3],
                "condition": row[4],
                "threshold": row[5],
                "severity": row[6],
                "enabled": row[7],
                "created_at": row[8],
                "updated_at": row[9]
            })
        
        return alert_rules
    
    def get_alert_rule(self, alert_rule_id: str) -> Dict[str, Any]:
        """
        Get alert rule.
        
        Args:
            alert_rule_id: Alert rule ID
            
        Returns:
            Alert rule
        """
        # Execute query
        cursor = this.db_manager.execute(
            "SELECT * FROM alert_rules WHERE id = ?",
            [alert_rule_id]
        )
        
        # Get alert rule
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "metric_name": row[3],
                "condition": row[4],
                "threshold": row[5],
                "severity": row[6],
                "enabled": row[7],
                "created_at": row[8],
                "updated_at": row[9]
            }
        
        return None
    
    def add_alert_rule(self, name: str, description: str, metric_name: str, condition: str, threshold: float, severity: str, enabled: bool = True) -> str:
        """
        Add alert rule.
        
        Args:
            name: Alert rule name
            description: Alert rule description
            metric_name: Metric name
            condition: Alert condition
            threshold: Alert threshold
            severity: Alert severity
            enabled: Alert rule enabled
            
        Returns:
            Alert rule ID
        """
        # Generate ID
        alert_rule_id = str(uuid.uuid4())
        
        # Add alert rule
        this.db_manager.execute(
            "INSERT INTO alert_rules (id, name, description, metric_name, condition, threshold, severity, enabled) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [alert_rule_id, name, description, metric_name, condition, threshold, severity, enabled]
        )
        
        # Log action
        this.db_manager.log_action(None, "add_alert_rule", {
            "alert_rule_id": alert_rule_id,
            "name": name,
            "description": description,
            "metric_name": metric_name,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
            "enabled": enabled
        })
        
        return alert_rule_id
    
    def update_alert_rule(self, alert_rule_id: str, enabled: bool = None, threshold: float = None, severity: str = None):
        """
        Update alert rule.
        
        Args:
            alert_rule_id: Alert rule ID
            enabled: Alert rule enabled
            threshold: Alert threshold
            severity: Alert severity
        """
        # Check if alert rule exists
        alert_rule = this.get_alert_rule(alert_rule_id)
        if not alert_rule:
            raise ValueError(f"Alert rule {alert_rule_id} does not exist")
        
        # Initialize query
        query = "UPDATE alert_rules SET updated_at = CURRENT_TIMESTAMP"
        params = []
        
        # Check if enabled is provided
        if enabled is not None:
            query += ", enabled = ?"
            params.append(enabled)
        
        # Check if threshold is provided
        if threshold is not None:
            query += ", threshold = ?"
            params.append(threshold)
        
        # Check if severity is provided
        if severity is not None:
            query += ", severity = ?"
            params.append(severity)
        
        # Add WHERE clause
        query += " WHERE id = ?"
        params.append(alert_rule_id)
        
        # Execute query
        this.db_manager.execute(query, params)
        
        # Log action
        this.db_manager.log_action(None, "update_alert_rule", {
            "alert_rule_id": alert_rule_id,
            "enabled": enabled,
            "threshold": threshold,
            "severity": severity
        })
    
    def delete_alert_rule(self, alert_rule_id: str):
        """
        Delete alert rule.
        
        Args:
            alert_rule_id: Alert rule ID
        """
        # Check if alert rule exists
        alert_rule = this.get_alert_rule(alert_rule_id)
        if not alert_rule:
            raise ValueError(f"Alert rule {alert_rule_id} does not exist")
        
        # Delete alert rule
        this.db_manager.execute(
            "DELETE FROM alert_rules WHERE id = ?",
            [alert_rule_id]
        )
        
        # Log action
        this.db_manager.log_action(None, "delete_alert_rule", {
            "alert_rule_id": alert_rule_id,
            "name": alert_rule["name"]
        })
    
    def check_alert_rules(self):
        """
        Check alert rules.
        """
        # Get enabled alert rules
        alert_rules = this.get_alert_rules(enabled=True)
        
        # Check alert rules
        for alert_rule in alert_rules:
            # Get latest metric
            metrics = this.get_metrics(
                name=alert_rule["metric_name"],
                start_time=datetime.datetime.now() - datetime.timedelta(minutes=5)
            )
            
            if not metrics:
                continue
            
            # Get latest metric
            latest_metric = metrics[-1]
            
            # Check condition
            if alert_rule["condition"] == ">":
                if latest_metric["value"] > alert_rule["threshold"]:
                    this.create_alert(
                        name=alert_rule["name"],
                        description=alert_rule["description"],
                        severity=alert_rule["severity"]
                    )
            elif alert_rule["condition"] == "<":
                if latest_metric["value"] < alert_rule["threshold"]:
                    this.create_alert(
                        name=alert_rule["name"],
                        description=alert_rule["description"],
                        severity=alert_rule["severity"]
                    )
            elif alert_rule["condition"] == ">=":
                if latest_metric["value"] >= alert_rule["threshold"]:
                    this.create_alert(
                        name=alert_rule["name"],
                        description=alert_rule["description"],
                        severity=alert_rule["severity"]
                    )
            elif alert_rule["condition"] == "<=":
                if latest_metric["value"] <= alert_rule["threshold"]:
                    this.create_alert(
                        name=alert_rule["name"],
                        description=alert_rule["description"],
                        severity=alert_rule["severity"]
                    )
            elif alert_rule["condition"] == "==":
                if latest_metric["value"] == alert_rule["threshold"]:
                    this.create_alert(
                        name=alert_rule["name"],
                        description=alert_rule["description"],
                        severity=alert_rule["severity"]
                    )
    
    def log(self, level: str, message: str, source: str = None):
        """
        Log message.
        
        Args:
            level: Log level
            message: Log message
            source: Log source
        """
        # Generate ID
        log_id = str(uuid.uuid4())
        
        # Add log
        this.db_manager.execute(
            "INSERT INTO logs (id, level, message, source) VALUES (?, ?, ?, ?)",
            [log_id, level, message, source]
        )
        
        # Log action
        this.db_manager.log_action(None, "log", {
            "log_id": log_id,
            "level": level,
            "message": message,
            "source": source
        })
    
    def get_logs(self, level: str = None, source: str = None, start_time: datetime.datetime = None, end_time: datetime.datetime = None) -> List[Dict[str, Any]]:
        """
        Get logs.
        
        Args:
            level: Filter by level
            source: Filter by source
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of logs
        """
        # Initialize query
        query = "SELECT * FROM logs"
        params = []
        
        # Check if level, source, start_time, or end_time is provided
        if level or source or start_time or end_time:
            query += " WHERE"
            
            # Check if level is provided
            if level:
                query += " level = ?"
                params.append(level)
            
            # Check if source is provided
            if source:
                if level:
                    query += " AND"
                query += " source = ?"
                params.append(source)
            
            # Check if start_time is provided
            if start_time:
                if level or source:
                    query += " AND"
                query += " timestamp >= ?"
                params.append(start_time)
            
            # Check if end_time is provided
            if end_time:
                if level or source or start_time:
                    query += " AND"
                query += " timestamp <= ?"
                params.append(end_time)
        
        # Execute query
        cursor = this.db_manager.execute(query, params)
        
        # Get logs
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "id": row[0],
                "level": row[1],
                "message": row[2],
                "source": row[3],
                "timestamp": row[4]
            })
        
        return logs
    
    def save_config(self):
        """
        Save monitoring configuration.
        """
        # Save YAML configuration
        yaml_path = os.path.join(this.config_path, "monitoring.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(this.config, f, default_flow_style=False)
        
        # Save JSON configuration
        json_path = os.path.join(this.config_path, "monitoring.json")
        with open(json_path, "w") as f:
            json.dump(this.config, f, indent=2)
        
        # Log action
        this.db_manager.log_action(None, "save_config", this.config)

    def record_user_satisfaction(self, value: float, tags: Dict[str, str] = None):
        """Record a user satisfaction metric (e.g., from feedback ratings)."""
        self.record_metric("user_satisfaction", value, tags)

    def get_user_satisfaction(self, start_time: datetime.datetime = None, end_time: datetime.datetime = None) -> List[Dict[str, Any]]:
        """Retrieve user satisfaction metrics."""
        return self.get_metrics(name="user_satisfaction", start_time=start_time, end_time=end_time)

    def record_cost_metric(self, value: float, tags: Dict[str, str] = None):
        """Record a cost metric (e.g., resource usage, cloud spend)."""
        self.record_metric("cost", value, tags)

    def get_cost_metrics(self, start_time: datetime.datetime = None, end_time: datetime.datetime = None) -> List[Dict[str, Any]]:
        """Retrieve cost metrics."""
        return self.get_metrics(name="cost", start_time=start_time, end_time=end_time) 