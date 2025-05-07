"""
Model Registry Service for managing AI model versions, tracking, and A/B testing.
"""

import os
import json
import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import sqlite3
import contextlib
from app.services.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelRegistry:
    """
    Model Registry for managing AI model versions, tracking, and A/B testing.
    Implements continuous model evaluation, baseline monitoring, and retraining triggers (task 2.1).
    Performance degradation thresholds are stored in the registry config.
    A/B testing can be used for UI changes as part of user adoption risk mitigation (task 2.2).
    """
    
    def __init__(self, db_manager: DatabaseManager, registry_path: str = "data/model_registry"):
        """
        Initialize the model registry.
        
        Args:
            db_manager: Database manager instance
            registry_path: Path to store model registry data
        """
        self.db_manager = db_manager
        self.registry_path = registry_path
        
        # Create registry directory if it doesn't exist
        os.makedirs(registry_path, exist_ok=True)
        
        # Initialize registry database
        self._init_registry_db()
    
    def _init_registry_db(self):
        """
        Initialize the model registry database.
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create models table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS models (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    framework TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create model_versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_versions (
                    id TEXT PRIMARY KEY,
                    model_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    path TEXT NOT NULL,
                    parameters TEXT,
                    metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (model_id) REFERENCES models (id)
                )
            """)
            
            # Create deployments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id TEXT PRIMARY KEY,
                    model_version_id TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_version_id) REFERENCES model_versions (id)
                )
            """)
            
            # Create ab_tests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ab_tests (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    model_a_id TEXT NOT NULL,
                    model_b_id TEXT NOT NULL,
                    traffic_split REAL NOT NULL,
                    metrics TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_a_id) REFERENCES model_versions (id),
                    FOREIGN KEY (model_b_id) REFERENCES model_versions (id)
                )
            """)
            
            # Create performance_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    model_version_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_version_id) REFERENCES model_versions (id)
                )
            """)
            
            # Commit changes
            conn.commit()
    
    @contextlib.contextmanager
    def _get_db_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(os.path.join(self.registry_path, "registry.db"))
        try:
            yield conn
        finally:
            conn.close()
    
    def register_model(self, name: str, framework: str, description: str = None) -> Dict[str, Any]:
        """
        Register a new model.
        
        Args:
            name: Model name
            framework: Model framework (e.g., PyTorch, TensorFlow)
            description: Model description
            
        Returns:
            Dict containing model information
        """
        # Generate model ID
        model_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert model
            cursor.execute(
                """
                INSERT INTO models (id, name, description, framework)
                VALUES (?, ?, ?, ?)
                """,
                (model_id, name, description, framework)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "register_model", {
            "model_id": model_id,
            "name": name,
            "framework": framework
        })
        
        # Return model information
        return {
            "id": model_id,
            "name": name,
            "description": description,
            "framework": framework,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def add_model_version(self, model_id: str, version: str, path: str, 
                         parameters: Dict[str, Any] = None, metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a new model version.
        
        Args:
            model_id: Model ID
            version: Version string
            path: Path to model files
            parameters: Model parameters
            metrics: Model metrics
            
        Returns:
            Dict containing model version information
        """
        # Generate version ID
        version_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert model version
            cursor.execute(
                """
                INSERT INTO model_versions (id, model_id, version, path, parameters, metrics)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (version_id, model_id, version, path, 
                 json.dumps(parameters) if parameters else None,
                 json.dumps(metrics) if metrics else None)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "add_model_version", {
            "model_id": model_id,
            "version_id": version_id,
            "version": version
        })
        
        # Return model version information
        return {
            "id": version_id,
            "model_id": model_id,
            "version": version,
            "path": path,
            "parameters": parameters,
            "metrics": metrics,
            "created_at": datetime.now().isoformat(),
            "is_active": False
        }
    
    def activate_model_version(self, version_id: str) -> Dict[str, Any]:
        """
        Activate a model version.
        
        Args:
            version_id: Model version ID
            
        Returns:
            Dict containing model version information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get model version
            cursor.execute(
                """
                SELECT id, model_id, version, path, parameters, metrics, created_at
                FROM model_versions
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if model version exists
            if not result:
                raise ValueError("Model version not found")
            
            # Deactivate all versions of the same model
            cursor.execute(
                """
                UPDATE model_versions
                SET is_active = FALSE
                WHERE model_id = ?
                """,
                (result[1],)
            )
            
            # Activate model version
            cursor.execute(
                """
                UPDATE model_versions
                SET is_active = TRUE
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "activate_model_version", {
            "version_id": version_id,
            "model_id": result[1],
            "version": result[2]
        })
        
        # Return model version information
        return {
            "id": result[0],
            "model_id": result[1],
            "version": result[2],
            "path": result[3],
            "parameters": json.loads(result[4]) if result[4] else None,
            "metrics": json.loads(result[5]) if result[5] else None,
            "created_at": result[6],
            "is_active": True
        }
    
    def deploy_model(self, version_id: str, environment: str) -> Dict[str, Any]:
        """
        Deploy a model version to an environment.
        
        Args:
            version_id: Model version ID
            environment: Deployment environment
            
        Returns:
            Dict containing deployment information
        """
        # Generate deployment ID
        deployment_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get model version
            cursor.execute(
                """
                SELECT id, model_id, version
                FROM model_versions
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if model version exists
            if not result:
                raise ValueError("Model version not found")
            
            # Insert deployment
            cursor.execute(
                """
                INSERT INTO deployments (id, model_version_id, environment, status)
                VALUES (?, ?, ?, ?)
                """,
                (deployment_id, version_id, environment, "deployed")
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "deploy_model", {
            "deployment_id": deployment_id,
            "version_id": version_id,
            "model_id": result[1],
            "version": result[2],
            "environment": environment
        })
        
        # Return deployment information
        return {
            "id": deployment_id,
            "model_version_id": version_id,
            "environment": environment,
            "status": "deployed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def create_ab_test(self, name: str, model_a_id: str, model_b_id: str, 
                      traffic_split: float = 0.5, description: str = None) -> Dict[str, Any]:
        """
        Create an A/B test between two model versions.
        
        Args:
            name: Test name
            model_a_id: Model version A ID
            model_b_id: Model version B ID
            traffic_split: Traffic split ratio (0.0 to 1.0)
            description: Test description
            
        Returns:
            Dict containing A/B test information
        """
        # Generate test ID
        test_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get model versions
            cursor.execute(
                """
                SELECT id, model_id, version
                FROM model_versions
                WHERE id IN (?, ?)
                """,
                (model_a_id, model_b_id)
            )
            
            # Get results
            results = cursor.fetchall()
            
            # Check if model versions exist
            if len(results) != 2:
                raise ValueError("One or both model versions not found")
            
            # Insert A/B test
            cursor.execute(
                """
                INSERT INTO ab_tests (id, name, description, model_a_id, model_b_id, traffic_split, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (test_id, name, description, model_a_id, model_b_id, traffic_split, "active")
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "create_ab_test", {
            "test_id": test_id,
            "name": name,
            "model_a_id": model_a_id,
            "model_b_id": model_b_id,
            "traffic_split": traffic_split
        })
        
        # Return A/B test information
        return {
            "id": test_id,
            "name": name,
            "description": description,
            "model_a_id": model_a_id,
            "model_b_id": model_b_id,
            "traffic_split": traffic_split,
            "metrics": None,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def update_ab_test_metrics(self, test_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update A/B test metrics.
        
        Args:
            test_id: Test ID
            metrics: Test metrics
            
        Returns:
            Dict containing A/B test information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get A/B test
            cursor.execute(
                """
                SELECT id, name, model_a_id, model_b_id, traffic_split, status
                FROM ab_tests
                WHERE id = ?
                """,
                (test_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if A/B test exists
            if not result:
                raise ValueError("A/B test not found")
            
            # Update A/B test
            cursor.execute(
                """
                UPDATE ab_tests
                SET metrics = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (json.dumps(metrics), test_id)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "update_ab_test_metrics", {
            "test_id": test_id,
            "metrics": metrics
        })
        
        # Return A/B test information
        return {
            "id": result[0],
            "name": result[1],
            "model_a_id": result[2],
            "model_b_id": result[3],
            "traffic_split": result[4],
            "metrics": metrics,
            "status": result[5],
            "updated_at": datetime.now().isoformat()
        }
    
    def end_ab_test(self, test_id: str, winner_id: str = None) -> Dict[str, Any]:
        """
        End an A/B test and optionally declare a winner.
        
        Args:
            test_id: Test ID
            winner_id: Winner model version ID (optional)
            
        Returns:
            Dict containing A/B test information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get A/B test
            cursor.execute(
                """
                SELECT id, name, model_a_id, model_b_id, traffic_split, metrics, status
                FROM ab_tests
                WHERE id = ?
                """,
                (test_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if A/B test exists
            if not result:
                raise ValueError("A/B test not found")
            
            # Update A/B test
            cursor.execute(
                """
                UPDATE ab_tests
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                ("completed", test_id)
            )
            
            # If winner is specified, activate the winning model version
            if winner_id:
                # Check if winner is one of the test models
                if winner_id not in [result[2], result[3]]:
                    raise ValueError("Winner must be one of the test models")
                
                # Activate winning model version
                cursor.execute(
                    """
                    UPDATE model_versions
                    SET is_active = TRUE
                    WHERE id = ?
                    """,
                    (winner_id,)
                )
                
                # Deactivate other model version
                other_id = result[3] if winner_id == result[2] else result[2]
                cursor.execute(
                    """
                    UPDATE model_versions
                    SET is_active = FALSE
                    WHERE id = ?
                    """,
                    (other_id,)
                )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "end_ab_test", {
            "test_id": test_id,
            "winner_id": winner_id
        })
        
        # Return A/B test information
        return {
            "id": result[0],
            "name": result[1],
            "model_a_id": result[2],
            "model_b_id": result[3],
            "traffic_split": result[4],
            "metrics": json.loads(result[5]) if result[5] else None,
            "status": "completed",
            "winner_id": winner_id,
            "updated_at": datetime.now().isoformat()
        }
    
    def record_performance_metric(self, version_id: str, metric_name: str, metric_value: float) -> Dict[str, Any]:
        """
        Record a performance metric for a model version.
        
        Args:
            version_id: Model version ID
            metric_name: Metric name
            metric_value: Metric value
            
        Returns:
            Dict containing performance metric information
        """
        # Generate metric ID
        metric_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get model version
            cursor.execute(
                """
                SELECT id, model_id, version
                FROM model_versions
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if model version exists
            if not result:
                raise ValueError("Model version not found")
            
            # Insert performance metric
            cursor.execute(
                """
                INSERT INTO performance_metrics (id, model_version_id, metric_name, metric_value)
                VALUES (?, ?, ?, ?)
                """,
                (metric_id, version_id, metric_name, metric_value)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "record_performance_metric", {
            "metric_id": metric_id,
            "version_id": version_id,
            "model_id": result[1],
            "version": result[2],
            "metric_name": metric_name,
            "metric_value": metric_value
        })
        
        # Return performance metric information
        return {
            "id": metric_id,
            "model_version_id": version_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_model_versions(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a model.
        
        Args:
            model_id: Model ID
            
        Returns:
            List of dicts containing model version information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get model versions
            cursor.execute(
                """
                SELECT id, model_id, version, path, parameters, metrics, created_at, is_active
                FROM model_versions
                WHERE model_id = ?
                ORDER BY created_at DESC
                """,
                (model_id,)
            )
            
            # Get results
            results = cursor.fetchall()
            
            # Return model version information
            return [
                {
                    "id": result[0],
                    "model_id": result[1],
                    "version": result[2],
                    "path": result[3],
                    "parameters": json.loads(result[4]) if result[4] else None,
                    "metrics": json.loads(result[5]) if result[5] else None,
                    "created_at": result[6],
                    "is_active": bool(result[7])
                }
                for result in results
            ]
    
    def get_active_model_version(self, model_id: str) -> Dict[str, Any]:
        """
        Get the active version of a model.
        
        Args:
            model_id: Model ID
            
        Returns:
            Dict containing model version information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get active model version
            cursor.execute(
                """
                SELECT id, model_id, version, path, parameters, metrics, created_at, is_active
                FROM model_versions
                WHERE model_id = ? AND is_active = TRUE
                """,
                (model_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if active model version exists
            if not result:
                return None
            
            # Return model version information
            return {
                "id": result[0],
                "model_id": result[1],
                "version": result[2],
                "path": result[3],
                "parameters": json.loads(result[4]) if result[4] else None,
                "metrics": json.loads(result[5]) if result[5] else None,
                "created_at": result[6],
                "is_active": bool(result[7])
            }
    
    def get_ab_tests(self, status: str = None) -> List[Dict[str, Any]]:
        """
        Get all A/B tests.
        
        Args:
            status: Test status filter (optional)
            
        Returns:
            List of dicts containing A/B test information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build query
            query = """
                SELECT id, name, description, model_a_id, model_b_id, traffic_split, metrics, status, created_at, updated_at
                FROM ab_tests
            """
            params = []
            
            # Add status filter
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            # Add order by
            query += " ORDER BY created_at DESC"
            
            # Get A/B tests
            cursor.execute(query, params)
            
            # Get results
            results = cursor.fetchall()
            
            # Return A/B test information
            return [
                {
                    "id": result[0],
                    "name": result[1],
                    "description": result[2],
                    "model_a_id": result[3],
                    "model_b_id": result[4],
                    "traffic_split": result[5],
                    "metrics": json.loads(result[6]) if result[6] else None,
                    "status": result[7],
                    "created_at": result[8],
                    "updated_at": result[9]
                }
                for result in results
            ]
    
    def get_performance_metrics(self, version_id: str, metric_name: str = None) -> List[Dict[str, Any]]:
        """
        Get performance metrics for a model version.
        
        Args:
            version_id: Model version ID
            metric_name: Metric name filter (optional)
            
        Returns:
            List of dicts containing performance metric information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build query
            query = """
                SELECT id, model_version_id, metric_name, metric_value, timestamp
                FROM performance_metrics
                WHERE model_version_id = ?
            """
            params = [version_id]
            
            # Add metric name filter
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            # Add order by
            query += " ORDER BY timestamp DESC"
            
            # Get performance metrics
            cursor.execute(query, params)
            
            # Get results
            results = cursor.fetchall()
            
            # Return performance metric information
            return [
                {
                    "id": result[0],
                    "model_version_id": result[1],
                    "metric_name": result[2],
                    "metric_value": result[3],
                    "timestamp": result[4]
                }
                for result in results
            ]
    
    def set_performance_baseline(self, version_id: str, metrics: dict):
        """Set baseline metrics for a model version."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE model_versions SET metrics = ? WHERE id = ?",
                (json.dumps(metrics), version_id)
            )
            conn.commit()
        self.db_manager.log_action(None, "set_performance_baseline", {"version_id": version_id, "metrics": metrics})

    def get_performance_baseline(self, version_id: str) -> dict:
        """Get baseline metrics for a model version."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT metrics FROM model_versions WHERE id = ?",
                (version_id,)
            )
            result = cursor.fetchone()
            return json.loads(result[0]) if result and result[0] else {}

    def evaluate_active_models(self, thresholds: dict = None):
        """Evaluate all active models, compare to baseline, and trigger retraining if below threshold."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, model_id, metrics FROM model_versions WHERE is_active = TRUE")
            for row in cursor.fetchall():
                version_id, model_id, metrics_json = row
                current_metrics = json.loads(metrics_json) if metrics_json else {}
                baseline = self.get_performance_baseline(version_id)
                if not baseline:
                    continue
                for metric, baseline_value in baseline.items():
                    current_value = current_metrics.get(metric)
                    threshold = (thresholds or {}).get(metric, 0.9)  # Default: 90% of baseline
                    if current_value is not None and current_value < baseline_value * threshold:
                        self.trigger_retraining(model_id, version_id, metric, current_value, baseline_value)
                        self.db_manager.log_action(None, "performance_degradation_detected", {
                            "model_id": model_id,
                            "version_id": version_id,
                            "metric": metric,
                            "current_value": current_value,
                            "baseline_value": baseline_value,
                            "threshold": threshold
                        })

    def trigger_retraining(self, model_id: str, version_id: str, metric: str, current_value: float, baseline_value: float):
        """Stub for automated retraining trigger."""
        # In production, this would enqueue a retraining job or call an external pipeline
        self.db_manager.log_action(None, "trigger_retraining", {
            "model_id": model_id,
            "version_id": version_id,
            "metric": metric,
            "current_value": current_value,
            "baseline_value": baseline_value
        })
        # For now, just log the action
        print(f"Retraining triggered for model {model_id} version {version_id} due to {metric} drop: {current_value} < {baseline_value}") 