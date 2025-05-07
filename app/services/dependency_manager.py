"""
Dependency Management Service for handling library version conflicts, dependency updates, and compatibility matrices.
"""

import os
import json
import yaml
import logging
import subprocess
import pkg_resources
import semver
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from app.services.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyManager:
    """
    Dependency Manager for handling library version conflicts, dependency updates, and compatibility matrices.
    Now supports security scanning and compliance checks (task 2.3).
    Fulfills requirements for task 1.7 (Dependency Conflicts) through existing methods for scanning, compatibility checks, update scheduling (via config), and matrix documentation.
    """
    
    def __init__(self, db_manager: DatabaseManager, config_path: str = "config"):
        """
        Initialize the dependency manager.
        
        Args:
            db_manager: Database manager instance
            config_path: Path to configuration files
        """
        self.db_manager = db_manager
        self.config_path = config_path
        
        # Create config directory if it doesn't exist
        os.makedirs(config_path, exist_ok=True)
        
        # Initialize dependency database
        self._init_db()
        
        # Load dependency configuration
        self.config = self._load_config()
        
        # Load installed packages
        self.installed_packages = self._load_installed_packages()
    
    def _init_db(self):
        """
        Initialize dependency database.
        """
        # Create dependency tables
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT NOT NULL,
                last_checked TIMESTAMP,
                last_updated TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS dependency_updates (
                id TEXT PRIMARY KEY,
                dependency_id TEXT NOT NULL,
                old_version TEXT NOT NULL,
                new_version TEXT NOT NULL,
                status TEXT NOT NULL,
                scheduled_date TIMESTAMP,
                applied_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dependency_id) REFERENCES dependencies (id)
            )
        """)
        
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS compatibility_matrices (
                id TEXT PRIMARY KEY,
                dependency_id TEXT NOT NULL,
                compatible_with TEXT NOT NULL,
                version_range TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dependency_id) REFERENCES dependencies (id)
            )
        """)
        
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS dependency_scans (
                id TEXT PRIMARY KEY,
                scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_dependencies INTEGER,
                outdated_dependencies INTEGER,
                conflicting_dependencies INTEGER,
                security_issues INTEGER,
                status TEXT NOT NULL
            )
        """)
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load dependency configuration.
        
        Returns:
            Dict containing dependency configuration
        """
        # Initialize configuration
        config = {
            "update_schedule": "weekly",
            "auto_update": False,
            "security_scan": True,
            "compatibility_check": True,
            "excluded_packages": [],
            "version_constraints": {}
        }
        
        # Load YAML configuration
        yaml_path = os.path.join(self.config_path, "dependencies.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                config.update(yaml.safe_load(f))
        
        # Load JSON configuration
        json_path = os.path.join(self.config_path, "dependencies.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                config.update(json.load(f))
        
        return config
    
    def _load_installed_packages(self) -> Dict[str, str]:
        """
        Load installed packages.
        
        Returns:
            Dict containing installed packages and their versions
        """
        # Initialize packages
        packages = {}
        
        # Get installed packages
        for package in pkg_resources.working_set:
            packages[package.key] = package.version
        
        return packages
    
    def get_dependencies(self, status: str = None) -> List[Dict[str, Any]]:
        """
        Get dependencies.
        
        Args:
            status: Filter by status
            
        Returns:
            List of dependencies
        """
        # Initialize query
        query = "SELECT * FROM dependencies"
        params = []
        
        # Check if status is provided
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        
        # Get dependencies
        dependencies = []
        for row in cursor.fetchall():
            dependencies.append({
                "id": row[0],
                "name": row[1],
                "version": row[2],
                "status": row[3],
                "last_checked": row[4],
                "last_updated": row[5],
                "created_at": row[6]
            })
        
        return dependencies
    
    def get_dependency(self, dependency_id: str) -> Dict[str, Any]:
        """
        Get dependency.
        
        Args:
            dependency_id: Dependency ID
            
        Returns:
            Dependency
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM dependencies WHERE id = ?",
            [dependency_id]
        )
        
        # Get dependency
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "version": row[2],
                "status": row[3],
                "last_checked": row[4],
                "last_updated": row[5],
                "created_at": row[6]
            }
        
        return None
    
    def add_dependency(self, name: str, version: str, status: str = "active"):
        """
        Add dependency.
        
        Args:
            name: Dependency name
            version: Dependency version
            status: Dependency status
        """
        # Generate ID
        dependency_id = f"{name}-{version}"
        
        # Check if dependency exists
        if self.get_dependency(dependency_id):
            # Update dependency
            self.db_manager.execute(
                "UPDATE dependencies SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?",
                [status, dependency_id]
            )
        else:
            # Add dependency
            self.db_manager.execute(
                "INSERT INTO dependencies (id, name, version, status, last_checked, last_updated) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                [dependency_id, name, version, status]
            )
        
        # Log action
        self.db_manager.log_action(None, "add_dependency", {
            "name": name,
            "version": version,
            "status": status
        })
    
    def update_dependency(self, dependency_id: str, version: str, status: str = None):
        """
        Update dependency.
        
        Args:
            dependency_id: Dependency ID
            version: Dependency version
            status: Dependency status
        """
        # Check if dependency exists
        dependency = self.get_dependency(dependency_id)
        if not dependency:
            raise ValueError(f"Dependency {dependency_id} does not exist")
        
        # Initialize query
        query = "UPDATE dependencies SET version = ?, last_updated = CURRENT_TIMESTAMP"
        params = [version]
        
        # Check if status is provided
        if status:
            query += ", status = ?"
            params.append(status)
        
        # Add WHERE clause
        query += " WHERE id = ?"
        params.append(dependency_id)
        
        # Execute query
        self.db_manager.execute(query, params)
        
        # Log action
        self.db_manager.log_action(None, "update_dependency", {
            "dependency_id": dependency_id,
            "old_version": dependency["version"],
            "new_version": version,
            "status": status
        })
    
    def delete_dependency(self, dependency_id: str):
        """
        Delete dependency.
        
        Args:
            dependency_id: Dependency ID
        """
        # Check if dependency exists
        dependency = self.get_dependency(dependency_id)
        if not dependency:
            raise ValueError(f"Dependency {dependency_id} does not exist")
        
        # Delete dependency
        self.db_manager.execute(
            "DELETE FROM dependencies WHERE id = ?",
            [dependency_id]
        )
        
        # Log action
        self.db_manager.log_action(None, "delete_dependency", {
            "dependency_id": dependency_id,
            "name": dependency["name"],
            "version": dependency["version"]
        })
    
    def get_updates(self, dependency_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """
        Get dependency updates.
        
        Args:
            dependency_id: Filter by dependency ID
            status: Filter by status
            
        Returns:
            List of dependency updates
        """
        # Initialize query
        query = "SELECT * FROM dependency_updates"
        params = []
        
        # Check if dependency_id or status is provided
        if dependency_id or status:
            query += " WHERE"
            
            # Check if dependency_id is provided
            if dependency_id:
                query += " dependency_id = ?"
                params.append(dependency_id)
            
            # Check if status is provided
            if status:
                if dependency_id:
                    query += " AND"
                query += " status = ?"
                params.append(status)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        
        # Get updates
        updates = []
        for row in cursor.fetchall():
            updates.append({
                "id": row[0],
                "dependency_id": row[1],
                "old_version": row[2],
                "new_version": row[3],
                "status": row[4],
                "scheduled_date": row[5],
                "applied_date": row[6],
                "created_at": row[7]
            })
        
        return updates
    
    def schedule_update(self, dependency_id: str, new_version: str, scheduled_date: str = None):
        """
        Schedule dependency update.
        
        Args:
            dependency_id: Dependency ID
            new_version: New version
            scheduled_date: Scheduled date
        """
        # Check if dependency exists
        dependency = self.get_dependency(dependency_id)
        if not dependency:
            raise ValueError(f"Dependency {dependency_id} does not exist")
        
        # Generate ID
        update_id = f"{dependency_id}-{new_version}"
        
        # Check if update exists
        cursor = self.db_manager.execute(
            "SELECT * FROM dependency_updates WHERE id = ?",
            [update_id]
        )
        
        if cursor.fetchone():
            # Update update
            self.db_manager.execute(
                "UPDATE dependency_updates SET scheduled_date = ?, status = 'scheduled' WHERE id = ?",
                [scheduled_date, update_id]
            )
        else:
            # Add update
            self.db_manager.execute(
                "INSERT INTO dependency_updates (id, dependency_id, old_version, new_version, status, scheduled_date) VALUES (?, ?, ?, ?, 'scheduled', ?)",
                [update_id, dependency_id, dependency["version"], new_version, scheduled_date]
            )
        
        # Log action
        self.db_manager.log_action(None, "schedule_update", {
            "dependency_id": dependency_id,
            "old_version": dependency["version"],
            "new_version": new_version,
            "scheduled_date": scheduled_date
        })
    
    def apply_update(self, update_id: str):
        """
        Apply dependency update.
        
        Args:
            update_id: Update ID
        """
        # Get update
        cursor = self.db_manager.execute(
            "SELECT * FROM dependency_updates WHERE id = ?",
            [update_id]
        )
        
        update = cursor.fetchone()
        if not update:
            raise ValueError(f"Update {update_id} does not exist")
        
        # Check if update is scheduled
        if update[4] != "scheduled":
            raise ValueError(f"Update {update_id} is not scheduled")
        
        # Get dependency
        dependency = self.get_dependency(update[1])
        if not dependency:
            raise ValueError(f"Dependency {update[1]} does not exist")
        
        # Update dependency
        self.update_dependency(update[1], update[3], "active")
        
        # Update update
        self.db_manager.execute(
            "UPDATE dependency_updates SET status = 'applied', applied_date = CURRENT_TIMESTAMP WHERE id = ?",
            [update_id]
        )
        
        # Log action
        self.db_manager.log_action(None, "apply_update", {
            "update_id": update_id,
            "dependency_id": update[1],
            "old_version": update[2],
            "new_version": update[3]
        })
    
    def get_compatibility_matrices(self, dependency_id: str = None) -> List[Dict[str, Any]]:
        """
        Get compatibility matrices.
        
        Args:
            dependency_id: Filter by dependency ID
            
        Returns:
            List of compatibility matrices
        """
        # Initialize query
        query = "SELECT * FROM compatibility_matrices"
        params = []
        
        # Check if dependency_id is provided
        if dependency_id:
            query += " WHERE dependency_id = ?"
            params.append(dependency_id)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        
        # Get matrices
        matrices = []
        for row in cursor.fetchall():
            matrices.append({
                "id": row[0],
                "dependency_id": row[1],
                "compatible_with": row[2],
                "version_range": row[3],
                "notes": row[4],
                "created_at": row[5]
            })
        
        return matrices
    
    def add_compatibility_matrix(self, dependency_id: str, compatible_with: str, version_range: str, notes: str = None):
        """
        Add compatibility matrix.
        
        Args:
            dependency_id: Dependency ID
            compatible_with: Compatible with
            version_range: Version range
            notes: Notes
        """
        # Check if dependency exists
        dependency = self.get_dependency(dependency_id)
        if not dependency:
            raise ValueError(f"Dependency {dependency_id} does not exist")
        
        # Generate ID
        matrix_id = f"{dependency_id}-{compatible_with}"
        
        # Check if matrix exists
        cursor = self.db_manager.execute(
            "SELECT * FROM compatibility_matrices WHERE id = ?",
            [matrix_id]
        )
        
        if cursor.fetchone():
            # Update matrix
            self.db_manager.execute(
                "UPDATE compatibility_matrices SET version_range = ?, notes = ? WHERE id = ?",
                [version_range, notes, matrix_id]
            )
        else:
            # Add matrix
            self.db_manager.execute(
                "INSERT INTO compatibility_matrices (id, dependency_id, compatible_with, version_range, notes) VALUES (?, ?, ?, ?, ?)",
                [matrix_id, dependency_id, compatible_with, version_range, notes]
            )
        
        # Log action
        self.db_manager.log_action(None, "add_compatibility_matrix", {
            "dependency_id": dependency_id,
            "compatible_with": compatible_with,
            "version_range": version_range,
            "notes": notes
        })
    
    def check_compatibility(self, dependency_id: str, version: str) -> List[Dict[str, Any]]:
        """
        Check dependency compatibility.
        
        Args:
            dependency_id: Dependency ID
            version: Version
            
        Returns:
            List of compatibility issues
        """
        # Check if dependency exists
        dependency = self.get_dependency(dependency_id)
        if not dependency:
            raise ValueError(f"Dependency {dependency_id} does not exist")
        
        # Get compatibility matrices
        matrices = self.get_compatibility_matrices(dependency_id)
        
        # Initialize issues
        issues = []
        
        # Check compatibility
        for matrix in matrices:
            # Parse version range
            version_range = matrix["version_range"]
            
            # Check if version is compatible
            if not self._is_version_compatible(version, version_range):
                issues.append({
                    "dependency_id": dependency_id,
                    "version": version,
                    "compatible_with": matrix["compatible_with"],
                    "version_range": version_range,
                    "notes": matrix["notes"]
                })
        
        return issues
    
    def _is_version_compatible(self, version: str, version_range: str) -> bool:
        """
        Check if version is compatible with version range.
        
        Args:
            version: Version
            version_range: Version range
            
        Returns:
            True if compatible, False otherwise
        """
        # Parse version range
        if version_range.startswith(">="):
            min_version = version_range[2:]
            return semver.compare(version, min_version) >= 0
        elif version_range.startswith("<="):
            max_version = version_range[2:]
            return semver.compare(version, max_version) <= 0
        elif version_range.startswith("=="):
            exact_version = version_range[2:]
            return version == exact_version
        elif " - " in version_range:
            min_version, max_version = version_range.split(" - ")
            return semver.compare(version, min_version) >= 0 and semver.compare(version, max_version) <= 0
        else:
            return version == version_range
    
    def scan_dependencies(self) -> Dict[str, Any]:
        """
        Scan dependencies.
        
        Returns:
            Scan results
        """
        # Initialize results
        results = {
            "total_dependencies": len(self.installed_packages),
            "outdated_dependencies": 0,
            "conflicting_dependencies": 0,
            "security_issues": 0,
            "status": "completed"
        }
        
        # Scan dependencies
        for name, version in self.installed_packages.items():
            # Add dependency
            self.add_dependency(name, version)
            
            # Check for updates
            try:
                # Get latest version
                latest_version = self._get_latest_version(name)
                
                # Check if update is available
                if latest_version and semver.compare(latest_version, version) > 0:
                    results["outdated_dependencies"] += 1
                    
                    # Schedule update
                    self.schedule_update(f"{name}-{version}", latest_version)
            except Exception as e:
                logger.error(f"Error checking for updates for {name}: {e}")
            
            # Check compatibility
            try:
                # Get compatibility issues
                issues = self.check_compatibility(f"{name}-{version}", version)
                
                # Check if issues exist
                if issues:
                    results["conflicting_dependencies"] += 1
            except Exception as e:
                logger.error(f"Error checking compatibility for {name}: {e}")
            
            # Check security
            try:
                # Check for security issues
                if self._check_security_issues(name, version):
                    results["security_issues"] += 1
            except Exception as e:
                logger.error(f"Error checking security for {name}: {e}")
        
        # Add scan to database
        self.db_manager.execute(
            "INSERT INTO dependency_scans (total_dependencies, outdated_dependencies, conflicting_dependencies, security_issues, status) VALUES (?, ?, ?, ?, ?)",
            [
                results["total_dependencies"],
                results["outdated_dependencies"],
                results["conflicting_dependencies"],
                results["security_issues"],
                results["status"]
            ]
        )
        
        # Log action
        self.db_manager.log_action(None, "scan_dependencies", results)
        
        return results
    
    def _get_latest_version(self, package_name: str) -> str:
        """
        Get latest version of package.
        
        Args:
            package_name: Package name
            
        Returns:
            Latest version
        """
        try:
            # Run pip index versions
            result = subprocess.run(
                ["pip", "index", "versions", package_name],
                capture_output=True,
                text=True
            )
            
            # Parse output
            for line in result.stdout.split("\n"):
                if line.startswith("Available versions:"):
                    versions = line.split("Available versions:")[1].strip().split(", ")
                    if versions:
                        return versions[0]
        except Exception as e:
            logger.error(f"Error getting latest version for {package_name}: {e}")
        
        return None
    
    def _check_security_issues(self, package_name: str, version: str) -> bool:
        """
        Check for security issues.
        
        Args:
            package_name: Package name
            version: Package version
            
        Returns:
            True if security issues exist, False otherwise
        """
        try:
            # Run safety check
            result = subprocess.run(
                ["safety", "check", f"{package_name}=={version}"],
                capture_output=True,
                text=True
            )
            
            # Check if issues exist
            return "Vulnerability found" in result.stdout
        except Exception as e:
            logger.error(f"Error checking security for {package_name}: {e}")
        
        return False
    
    def get_scan_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get scan history.
        
        Args:
            limit: Limit
            
        Returns:
            List of scans
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM dependency_scans ORDER BY scan_date DESC LIMIT ?",
            [limit]
        )
        
        # Get scans
        scans = []
        for row in cursor.fetchall():
            scans.append({
                "id": row[0],
                "scan_date": row[1],
                "total_dependencies": row[2],
                "outdated_dependencies": row[3],
                "conflicting_dependencies": row[4],
                "security_issues": row[5],
                "status": row[6]
            })
        
        return scans
    
    def save_config(self):
        """
        Save dependency configuration.
        """
        # Save YAML configuration
        yaml_path = os.path.join(self.config_path, "dependencies.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        # Save JSON configuration
        json_path = os.path.join(self.config_path, "dependencies.json")
        with open(json_path, "w") as f:
            json.dump(self.config, f, indent=2)
        
        # Log action
        self.db_manager.log_action(None, "save_config", self.config) 