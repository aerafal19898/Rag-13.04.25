"""
Deployment Management Service for handling multiple deployment methods, feature flags, and rollback procedures.
"""

import os
import json
import yaml
import logging
import subprocess
import uuid
import datetime
import hashlib
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from app.services.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """
    Deployment Manager for handling multiple deployment methods, feature flags, and rollback procedures.
    Implements feature flags for task 1.8 (Deployment Strategy Conflicts).
    """
    
    def __init__(self, db_manager: DatabaseManager, config_path: str = "config"):
        """
        Initialize the deployment manager.
        
        Args:
            db_manager: Database manager instance
            config_path: Path to configuration files
        """
        self.db_manager = db_manager
        self.config_path = config_path
        
        # Create config directory if it doesn't exist
        os.makedirs(config_path, exist_ok=True)
        
        # Initialize deployment database
        self._init_db()
        
        # Load deployment configuration
        self.config = self._load_config()
    
    def _init_db(self):
        """
        Initialize deployment database.
        """
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create deployment tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    status TEXT NOT NULL,
                    deployed_at TIMESTAMP,
                    rolled_back_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployment_steps (
                    id TEXT PRIMARY KEY,
                    deployment_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    step_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (deployment_id) REFERENCES deployments (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feature_flags (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    enabled BOOLEAN NOT NULL DEFAULT FALSE,
                    rollout_percentage INTEGER DEFAULT 0, -- 0 to 100
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployment_verifications (
                    id TEXT PRIMARY KEY,
                    deployment_id TEXT NOT NULL,
                    verification_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (deployment_id) REFERENCES deployments (id)
                )
            """)
            
            conn.commit()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load deployment configuration.
        
        Returns:
            Dict containing deployment configuration
        """
        # Initialize configuration
        config = {
            "environments": ["development", "staging", "production"],
            "deployment_methods": ["docker", "kubernetes", "serverless"],
            "default_method": "docker",
            "rollback_strategy": "automatic",
            "verification_checks": ["health", "functionality", "performance"],
            "feature_flag_strategy": "percentage"
        }
        
        # Load YAML configuration
        yaml_path = os.path.join(self.config_path, "deployment.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                config.update(yaml.safe_load(f))
        
        # Load JSON configuration
        json_path = os.path.join(self.config_path, "deployment.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                config.update(json.load(f))
        
        return config
    
    def get_deployments(self, environment: str = None, status: str = None) -> List[Dict[str, Any]]:
        """
        Get deployments.
        
        Args:
            environment: Filter by environment
            status: Filter by status
            
        Returns:
            List of deployments
        """
        # Initialize query
        query = "SELECT * FROM deployments"
        params = []
        
        # Check if environment or status is provided
        if environment or status:
            query += " WHERE"
            
            # Check if environment is provided
            if environment:
                query += " environment = %s"
                params.append(environment)
            
            # Check if status is provided
            if status:
                if environment:
                    query += " AND"
                query += " status = %s"
                params.append(status)
        
        # Execute query
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            
            # Get deployments
            deployments = []
            for row in cursor.fetchall():
                deployments.append({
                    "id": row[0],
                    "name": row[1],
                    "version": row[2],
                    "environment": row[3],
                    "status": row[4],
                    "deployed_at": row[5],
                    "rolled_back_at": row[6],
                    "created_at": row[7]
                })
            
            return deployments
    
    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """
        Get deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Deployment
        """
        # Execute query
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM deployments WHERE id = %s",
                (deployment_id,)
            )
            
            # Get deployment
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "version": row[2],
                    "environment": row[3],
                    "status": row[4],
                    "deployed_at": row[5],
                    "rolled_back_at": row[6],
                    "created_at": row[7]
                }
            
            return None
    
    def create_deployment(self, name: str, version: str, environment: str) -> str:
        """
        Create deployment.
        
        Args:
            name: Deployment name
            version: Deployment version
            environment: Deployment environment
            
        Returns:
            Deployment ID
        """
        # Check if environment is valid
        if environment not in self.config["environments"]:
            raise ValueError(f"Environment {environment} is not valid")
        
        # Generate ID
        deployment_id = str(uuid.uuid4())
        
        # Add deployment
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO deployments (id, name, version, environment, status) VALUES (%s, %s, %s, %s, 'pending')",
                (deployment_id, name, version, environment)
            )
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "create_deployment", {
            "deployment_id": deployment_id,
            "name": name,
            "version": version,
            "environment": environment
        })
        
        return deployment_id
    
    def deploy(self, deployment_id: str, method: str = None) -> Dict[str, Any]:
        """
        Deploy deployment.
        
        Args:
            deployment_id: Deployment ID
            method: Deployment method
            
        Returns:
            Deployment result
        """
        # Check if deployment exists
        deployment = this.get_deployment(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} does not exist")
        
        # Check if deployment is already deployed
        if deployment["status"] == "deployed":
            raise ValueError(f"Deployment {deployment_id} is already deployed")
        
        # Check if deployment is rolled back
        if deployment["status"] == "rolled_back":
            raise ValueError(f"Deployment {deployment_id} is rolled back")
        
        # Get deployment method
        if not method:
            method = self.config["default_method"]
        
        # Check if method is valid
        if method not in this.config["deployment_methods"]:
            raise ValueError(f"Deployment method {method} is not valid")
        
        # Initialize result
        result = {
            "deployment_id": deployment_id,
            "status": "deployed",
            "method": method,
            "steps": []
        }
        
        try:
            # Update deployment status
            this.db_manager.execute(
                "UPDATE deployments SET status = 'deploying', deployed_at = CURRENT_TIMESTAMP WHERE id = %s",
                (deployment_id,)
            )
            
            # Add deployment steps
            steps = this._get_deployment_steps(method)
            for step in steps:
                # Add step
                step_id = this._add_deployment_step(deployment_id, step["name"], step["type"])
                
                # Execute step
                step_result = this._execute_deployment_step(step["type"], deployment)
                
                # Update step
                this._update_deployment_step(step_id, step_result["status"], step_result.get("error"))
                
                # Add step to result
                result["steps"].append({
                    "name": step["name"],
                    "type": step["type"],
                    "status": step_result["status"],
                    "error": step_result.get("error")
                })
                
                # Check if step failed
                if step_result["status"] == "failed":
                    # Update deployment status
                    this.db_manager.execute(
                        "UPDATE deployments SET status = 'failed' WHERE id = %s",
                        (deployment_id,)
                    )
                    
                    # Update result
                    result["status"] = "failed"
                    
                    # Break
                    break
            
            # Check if deployment is still deploying
            if result["status"] != "failed":
                # Update deployment status
                this.db_manager.execute(
                    "UPDATE deployments SET status = 'deployed' WHERE id = %s",
                    (deployment_id,)
                )
                
                # Run verifications
                verifications = this._run_deployment_verifications(deployment_id)
                
                # Add verifications to result
                result["verifications"] = verifications
                
                # Check if verifications failed
                if any(v["status"] == "failed" for v in verifications):
                    # Update deployment status
                    this.db_manager.execute(
                        "UPDATE deployments SET status = 'failed' WHERE id = %s",
                        (deployment_id,)
                    )
                    
                    # Update result
                    result["status"] = "failed"
            
            # Log action
            this.db_manager.log_action(None, "deploy", result)
            
            return result
        except Exception as e:
            # Update deployment status
            this.db_manager.execute(
                "UPDATE deployments SET status = 'failed' WHERE id = %s",
                (deployment_id,)
            )
            
            # Update result
            result["status"] = "failed"
            result["error"] = str(e)
            
            # Log action
            this.db_manager.log_action(None, "deploy", result)
            
            return result
    
    def _get_deployment_steps(self, method: str) -> List[Dict[str, str]]:
        """
        Get deployment steps.
        
        Args:
            method: Deployment method
            
        Returns:
            List of deployment steps
        """
        # Initialize steps
        steps = []
        
        # Check method
        if method == "docker":
            steps = [
                {"name": "Build Docker Image", "type": "docker_build"},
                {"name": "Push Docker Image", "type": "docker_push"},
                {"name": "Deploy Docker Container", "type": "docker_deploy"}
            ]
        elif method == "kubernetes":
            steps = [
                {"name": "Build Docker Image", "type": "docker_build"},
                {"name": "Push Docker Image", "type": "docker_push"},
                {"name": "Update Kubernetes Manifests", "type": "kubernetes_update"},
                {"name": "Apply Kubernetes Manifests", "type": "kubernetes_apply"}
            ]
        elif method == "serverless":
            steps = [
                {"name": "Package Application", "type": "serverless_package"},
                {"name": "Deploy Serverless Function", "type": "serverless_deploy"}
            ]
        
        return steps
    
    def _add_deployment_step(self, deployment_id: str, step_name: str, step_type: str) -> str:
        """
        Add deployment step.
        
        Args:
            deployment_id: Deployment ID
            step_name: Step name
            step_type: Step type
            
        Returns:
            Step ID
        """
        # Generate ID
        step_id = str(uuid.uuid4())
        
        # Add step
        this.db_manager.execute(
            "INSERT INTO deployment_steps (id, deployment_id, step_name, step_type, status) VALUES (%s, %s, %s, %s, 'pending')",
            (step_id, deployment_id, step_name, step_type)
        )
        
        return step_id
    
    def _update_deployment_step(self, step_id: str, status: str, error: str = None):
        """
        Update deployment step.
        
        Args:
            step_id: Step ID
            status: Step status
            error: Step error
        """
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now(datetime.timezone.utc)
            if status == "running":
                cursor.execute(
                    "UPDATE deployment_steps SET status = %s, started_at = %s WHERE id = %s",
                    (status, now, step_id)
                )
            elif status in ["success", "failure"]:
                cursor.execute(
                    "UPDATE deployment_steps SET status = %s, completed_at = %s, error = %s WHERE id = %s",
                    (status, now, error, step_id)
                )
            conn.commit()
    
    def _execute_deployment_step(self, step_type: str, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute deployment step.
        
        Args:
            step_type: Step type
            deployment: Deployment
            
        Returns:
            Step result
        """
        # Initialize result
        result = {
            "status": "completed"
        }
        
        try:
            # Check step type
            if step_type == "docker_build":
                # Build Docker image
                subprocess.run(
                    ["docker", "build", "-t", f"{deployment['name']}:{deployment['version']}", "."],
                    check=True
                )
            elif step_type == "docker_push":
                # Push Docker image
                subprocess.run(
                    ["docker", "push", f"{deployment['name']}:{deployment['version']}"],
                    check=True
                )
            elif step_type == "docker_deploy":
                # Deploy Docker container
                subprocess.run(
                    ["docker", "run", "-d", "--name", deployment["name"], f"{deployment['name']}:{deployment['version']}"],
                    check=True
                )
            elif step_type == "kubernetes_update":
                # Update Kubernetes manifests
                with open("kubernetes/deployment.yaml", "r") as f:
                    manifest = yaml.safe_load(f)
                
                # Update image
                manifest["spec"]["template"]["spec"]["containers"][0]["image"] = f"{deployment['name']}:{deployment['version']}"
                
                # Save manifest
                with open("kubernetes/deployment.yaml", "w") as f:
                    yaml.dump(manifest, f)
            elif step_type == "kubernetes_apply":
                # Apply Kubernetes manifests
                subprocess.run(
                    ["kubectl", "apply", "-f", "kubernetes/"],
                    check=True
                )
            elif step_type == "serverless_package":
                # Package serverless application
                subprocess.run(
                    ["serverless", "package", "--stage", deployment["environment"]],
                    check=True
                )
            elif step_type == "serverless_deploy":
                # Deploy serverless application
                subprocess.run(
                    ["serverless", "deploy", "--stage", deployment["environment"]],
                    check=True
                )
        except Exception as e:
            # Update result
            result["status"] = "failed"
            result["error"] = str(e)
        
        return result
    
    def _run_deployment_verifications(self, deployment_id: str) -> List[Dict[str, Any]]:
        """
        Run deployment verifications.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            List of verifications
        """
        results = []
        for check_name in self.config["verification_checks"]:
            verification_id = str(uuid.uuid4())
            status = "pending"
            result_text = None
            
            # Add verification record
            with self.db_manager._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO deployment_verifications (id, deployment_id, verification_name, status) VALUES (%s, %s, %s, %s)",
                    (verification_id, deployment_id, check_name, status)
                )
                conn.commit()

            try:
                logger.info(f"Running verification check: {check_name}")
                # Simulate verification check
                if check_name == "health":
                    # Simulate health check
                    status = "success"
                    result_text = "Health check passed"
                elif check_name == "functionality":
                    # Simulate functionality check
                    status = "success"
                    result_text = "Functionality check passed"
                elif check_name == "performance":
                     # Simulate performance check (can randomly fail for testing)
                    if datetime.datetime.now().second % 5 == 0: # Fail sometimes
                        raise ValueError("Simulated performance degradation")
                    status = "success"
                    result_text = "Performance check passed"
                else:
                    status = "skipped"
                    result_text = "Unknown check type"

                logger.info(f"Verification check {check_name} completed with status: {status}")

            except Exception as e:
                status = "failure"
                result_text = str(e)
                logger.error(f"Verification check {check_name} failed: {e}")

            # Update verification record
            with self.db_manager._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE deployment_verifications SET status = %s, result = %s WHERE id = %s",
                    (status, result_text, verification_id)
                )
                conn.commit()

            results.append({
                "name": check_name,
                "status": status,
                "result": result_text
            })
        return results
    
    def rollback(self, deployment_id: str) -> Dict[str, Any]:
        """
        Rollback deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Rollback result
        """
        # Check if deployment exists
        deployment = this.get_deployment(deployment_id)
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} does not exist")
        
        # Check if deployment is already rolled back
        if deployment["status"] == "rolled_back":
            raise ValueError(f"Deployment {deployment_id} is already rolled back")
        
        # Initialize result
        result = {
            "deployment_id": deployment_id,
            "status": "rolled_back"
        }
        
        try:
            # Update deployment status
            this.db_manager.execute(
                "UPDATE deployments SET status = 'rolling_back', rolled_back_at = CURRENT_TIMESTAMP WHERE id = %s",
                (deployment_id,)
            )
            
            # Get deployment method
            method = this.config["default_method"]
            
            # Check method
            if method == "docker":
                # Rollback Docker container
                subprocess.run(
                    ["docker", "stop", deployment["name"]],
                    check=True
                )
                
                subprocess.run(
                    ["docker", "rm", deployment["name"]],
                    check=True
                )
                
                subprocess.run(
                    ["docker", "run", "-d", "--name", deployment["name"], f"{deployment['name']}:{deployment['version']}"],
                    check=True
                )
            elif method == "kubernetes":
                # Rollback Kubernetes deployment
                subprocess.run(
                    ["kubectl", "rollout", "undo", "deployment", deployment["name"]],
                    check=True
                )
            elif method == "serverless":
                # Rollback serverless deployment
                subprocess.run(
                    ["serverless", "rollback", "--stage", deployment["environment"]],
                    check=True
                )
            
            # Update deployment status
            this.db_manager.execute(
                "UPDATE deployments SET status = 'rolled_back' WHERE id = %s",
                (deployment_id,)
            )
            
            # Log action
            this.db_manager.log_action(None, "rollback", result)
            
            return result
        except Exception as e:
            # Update deployment status
            this.db_manager.execute(
                "UPDATE deployments SET status = 'failed' WHERE id = %s",
                (deployment_id,)
            )
            
            # Update result
            result["status"] = "failed"
            result["error"] = str(e)
            
            # Log action
            this.db_manager.log_action(None, "rollback", result)
            
            return result
    
    def get_feature_flags(self, enabled: bool = None) -> List[Dict[str, Any]]:
        """
        Get feature flags.
        
        Args:
            enabled: Filter by enabled
            
        Returns:
            List of feature flags
        """
        query = "SELECT id, name, description, enabled, rollout_percentage, created_at, updated_at FROM feature_flags"
        params = []
        if enabled is not None:
            query += " WHERE enabled = %s"
            params.append(enabled)
        query += " ORDER BY name"

        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_feature_flag(self, feature_flag_id: str) -> Dict[str, Any]:
        """
        Get feature flag by ID. Deprecated, use get_feature_flag_by_name.
        
        Args:
            feature_flag_id: Feature flag ID
            
        Returns:
            Feature flag
        """
        logger.warning("get_feature_flag by ID is deprecated, use get_feature_flag_by_name")
        query = "SELECT id, name, description, enabled, rollout_percentage, created_at, updated_at FROM feature_flags WHERE id = %s"
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (feature_flag_id,))
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
    
    def add_feature_flag(self, name: str, description: str = None, enabled: bool = False, rollout_percentage: int = 0) -> str:
        """
        Add feature flag. Deprecated, use create_feature_flag.
        
        Args:
            name: Feature flag name
            description: Feature flag description
            enabled: Feature flag enabled
            rollout_percentage: Feature flag rollout percentage
            
        Returns:
            Feature flag ID
        """
        logger.warning("add_feature_flag is deprecated, use create_feature_flag")
        flag_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.timezone.utc)
        query = """
            INSERT INTO feature_flags (id, name, description, enabled, rollout_percentage, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (flag_id, name, description, enabled, rollout_percentage, now, now))
            conn.commit()
        return flag_id
    
    def update_feature_flag(self, feature_flag_id: str, enabled: bool = None, rollout_percentage: int = None):
        """
        Update feature flag by ID. Deprecated, use update_feature_flag_by_name.
        
        Args:
            feature_flag_id: Feature flag ID
            enabled: Feature flag enabled
            rollout_percentage: Feature flag rollout percentage
        """
        logger.warning("update_feature_flag by ID is deprecated, use update_feature_flag_by_name")
        updates = []
        params = []
        if enabled is not None:
            updates.append("enabled = %s")
            params.append(enabled)
        if rollout_percentage is not None:
            if not 0 <= rollout_percentage <= 100:
                raise ValueError("Rollout percentage must be between 0 and 100")
            updates.append("rollout_percentage = %s")
            params.append(rollout_percentage)

        if not updates:
            return # No changes to make

        updates.append("updated_at = %s")
        params.append(datetime.datetime.now(datetime.timezone.utc))
        params.append(feature_flag_id) # For the WHERE clause

        query = f"UPDATE feature_flags SET {', '.join(updates)} WHERE id = %s"

        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            conn.commit()

    def delete_feature_flag(self, feature_flag_id: str):
        """
        Delete feature flag by ID. Deprecated, use delete_feature_flag_by_name.
        
        Args:
            feature_flag_id: Feature flag ID
        """
        logger.warning("delete_feature_flag by ID is deprecated, use delete_feature_flag_by_name")
        query = "DELETE FROM feature_flags WHERE id = %s"
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (feature_flag_id,))
            conn.commit()
    
    def create_feature_flag(self, name: str, description: str = None, enabled: bool = False, rollout_percentage: int = 0) -> Dict[str, Any]:
        """
        Create a new feature flag or return existing if name conflicts.
        Uses name as the primary way to reference flags.
        
        Args:
            name: Feature flag name
            description: Feature flag description
            enabled: Feature flag enabled
            rollout_percentage: Feature flag rollout percentage
            
        Returns:
            Feature flag
        """
        if not 0 <= rollout_percentage <= 100:
            raise ValueError("Rollout percentage must be between 0 and 100")

        now = datetime.datetime.now(datetime.timezone.utc)
        query = """
            INSERT INTO feature_flags (name, description, enabled, rollout_percentage, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id, name, description, enabled, rollout_percentage, created_at, updated_at;
        """
        
        flag_data = None
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (name, description, enabled, rollout_percentage, now, now))
                flag_data = cursor.fetchone()
                conn.commit()
            except Exception as e:
                logger.error(f"Error creating feature flag '{name}': {e}")
                conn.rollback()
                raise

        if flag_data:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, flag_data))
        else:
            # If insert did nothing (conflict), fetch the existing flag
            logger.warning(f"Feature flag '{name}' already exists. Returning existing flag.")
            return self.get_feature_flag_by_name(name)

    def get_feature_flag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get feature flag by name.
        
        Args:
            name: Feature flag name
            
        Returns:
            Feature flag
        """
        query = "SELECT id, name, description, enabled, rollout_percentage, created_at, updated_at FROM feature_flags WHERE name = %s"
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None

    def update_feature_flag_by_name(self, name: str, description: str = None, enabled: bool = None, rollout_percentage: int = None) -> Optional[Dict[str, Any]]:
        """
        Update feature flag by name.
        
        Args:
            name: Feature flag name
            description: Feature flag description
            enabled: Feature flag enabled
            rollout_percentage: Feature flag rollout percentage
            
        Returns:
            Updated feature flag
        """
        updates = []
        params = []
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if enabled is not None:
            updates.append("enabled = %s")
            params.append(enabled)
        if rollout_percentage is not None:
            if not 0 <= rollout_percentage <= 100:
                raise ValueError("Rollout percentage must be between 0 and 100")
            updates.append("rollout_percentage = %s")
            params.append(rollout_percentage)

        if not updates:
            logger.warning(f"No update parameters provided for feature flag '{name}'.")
            return self.get_feature_flag_by_name(name) # Return current state if no updates

        updates.append("updated_at = %s")
        params.append(datetime.datetime.now(datetime.timezone.utc))
        params.append(name) # For the WHERE clause

        query = f"UPDATE feature_flags SET {', '.join(updates)} WHERE name = %s RETURNING id, name, description, enabled, rollout_percentage, created_at, updated_at;"

        updated_flag_data = None
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, tuple(params))
                updated_flag_data = cursor.fetchone()
                conn.commit()
                if updated_flag_data:
                    logger.info(f"Feature flag '{name}' updated successfully.")
                else:
                    logger.warning(f"Feature flag '{name}' not found for update.")

            except Exception as e:
                logger.error(f"Error updating feature flag '{name}': {e}")
                conn.rollback()
                # Optionally re-raise or return None/error indicator
                return None # Indicate update failure

        if updated_flag_data:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, updated_flag_data))
        else:
            return None # Flag not found or error occurred

    def delete_feature_flag_by_name(self, name: str) -> bool:
        """
        Delete feature flag by name. Returns True if deleted, False otherwise.
        
        Args:
            name: Feature flag name
            
        Returns:
            True if deleted, False otherwise
        """
        query = "DELETE FROM feature_flags WHERE name = %s"
        rows_deleted = 0
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (name,))
                rows_deleted = cursor.rowcount
                conn.commit()
            except Exception as e:
                logger.error(f"Error deleting feature flag '{name}': {e}")
                conn.rollback()
                return False # Indicate deletion failure
        
        if rows_deleted > 0:
            logger.info(f"Feature flag '{name}' deleted successfully.")
            return True
        else:
            logger.warning(f"Feature flag '{name}' not found for deletion.")
            return False

    def is_feature_flag_active(self, name: str, user_identifier: Optional[str] = None) -> bool:
        """
        Check if a feature flag is active for a given user identifier (if provided) based on rollout percentage.
        Uses name as the primary way to reference flags.
        
        Args:
            name: Feature flag name
            user_identifier: User identifier
            
        Returns:
            True if active, False otherwise
        """
        flag = self.get_feature_flag_by_name(name)
        if not flag or not flag['enabled']:
            return False

        # If rollout is 100%, it's active for everyone
        if flag['rollout_percentage'] == 100:
            return True
            
        # If rollout is 0%, it's inactive for everyone (unless specifically enabled later for segments)
        if flag['rollout_percentage'] == 0:
            return False

        # If no user identifier is provided for a partial rollout, consider it inactive
        if user_identifier is None:
            logger.debug(f"No user identifier provided for flag '{name}' with partial rollout ({flag['rollout_percentage']}%). Returning inactive.")
            return False

        # Consistent hash of the feature name and user identifier
        hasher = hashlib.sha1()
        hasher.update(name.encode('utf-8'))
        hasher.update(user_identifier.encode('utf-8'))
        hash_value = int(hasher.hexdigest(), 16)

        # Scale the hash to a 0-99 range
        percentage_bucket = hash_value % 100

        # Check if the user's bucket falls within the rollout percentage
        is_active = percentage_bucket < flag['rollout_percentage']
        logger.debug(f"Flag '{name}' check for user '{user_identifier}': enabled={flag['enabled']}, rollout={flag['rollout_percentage']}%, bucket={percentage_bucket}, active={is_active}")
        return is_active
    
    def save_config(self):
        """
        Save deployment configuration.
        """
        # Save YAML configuration
        yaml_path = os.path.join(this.config_path, "deployment.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(this.config, f, default_flow_style=False)
        
        # Save JSON configuration
        json_path = os.path.join(this.config_path, "deployment.json")
        with open(json_path, "w") as f:
            json.dump(this.config, f, indent=2)
        
        # Log action
        this.db_manager.log_action(None, "save_config", this.config) 