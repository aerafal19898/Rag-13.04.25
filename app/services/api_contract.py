"""
API Contract Management Service for handling OpenAPI/Swagger documentation, API versioning, and contract testing.
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
import yaml
import jsonschema
from app.services.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIContractManager:
    """
    API Contract Manager for handling OpenAPI/Swagger documentation, API versioning, and contract testing.
    """
    
    def __init__(self, db_manager: DatabaseManager, contract_path: str = "data/api_contracts"):
        """
        Initialize the API contract manager.
        
        Args:
            db_manager: Database manager instance
            contract_path: Path to store API contract data
        """
        self.db_manager = db_manager
        self.contract_path = contract_path
        
        # Create contract directory if it doesn't exist
        os.makedirs(contract_path, exist_ok=True)
        
        # Initialize contract database
        self._init_contract_db()
    
    def _init_contract_db(self):
        """
        Initialize the API contract database.
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create api_versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_versions (
                    id TEXT PRIMARY KEY,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create api_endpoints table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_endpoints (
                    id TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL,
                    path TEXT NOT NULL,
                    method TEXT NOT NULL,
                    description TEXT,
                    parameters TEXT,
                    request_body TEXT,
                    responses TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES api_versions (id)
                )
            """)
            
            # Create breaking_changes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS breaking_changes (
                    id TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    migration_guide TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES api_versions (id)
                )
            """)
            
            # Create contract_tests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contract_tests (
                    id TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    test_data TEXT,
                    expected_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (version_id) REFERENCES api_versions (id)
                )
            """)
            
            # Create test_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id TEXT PRIMARY KEY,
                    test_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    actual_response TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES contract_tests (id)
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
        conn = sqlite3.connect(os.path.join(self.contract_path, "contracts.db"))
        try:
            yield conn
        finally:
            conn.close()
    
    def create_api_version(self, version: str, status: str = "draft") -> Dict[str, Any]:
        """
        Create a new API version.
        
        Args:
            version: API version string
            status: API version status (draft, active, deprecated)
            
        Returns:
            Dict containing API version information
        """
        # Generate version ID
        version_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert API version
            cursor.execute(
                """
                INSERT INTO api_versions (id, version, status)
                VALUES (?, ?, ?)
                """,
                (version_id, version, status)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "create_api_version", {
            "version_id": version_id,
            "version": version,
            "status": status
        })
        
        # Return API version information
        return {
            "id": version_id,
            "version": version,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def update_api_version_status(self, version_id: str, status: str) -> Dict[str, Any]:
        """
        Update the status of an API version.
        
        Args:
            version_id: API version ID
            status: New API version status
            
        Returns:
            Dict containing API version information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get API version
            cursor.execute(
                """
                SELECT id, version, status
                FROM api_versions
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if API version exists
            if not result:
                raise ValueError("API version not found")
            
            # Update API version
            cursor.execute(
                """
                UPDATE api_versions
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, version_id)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "update_api_version_status", {
            "version_id": version_id,
            "version": result[1],
            "old_status": result[2],
            "new_status": status
        })
        
        # Return API version information
        return {
            "id": result[0],
            "version": result[1],
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
    
    def add_api_endpoint(self, version_id: str, path: str, method: str, 
                        description: str = None, parameters: Dict[str, Any] = None,
                        request_body: Dict[str, Any] = None, responses: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a new API endpoint to an API version.
        
        Args:
            version_id: API version ID
            path: API endpoint path
            method: HTTP method
            description: Endpoint description
            parameters: Endpoint parameters
            request_body: Request body schema
            responses: Response schemas
            
        Returns:
            Dict containing API endpoint information
        """
        # Generate endpoint ID
        endpoint_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get API version
            cursor.execute(
                """
                SELECT id, version
                FROM api_versions
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if API version exists
            if not result:
                raise ValueError("API version not found")
            
            # Insert API endpoint
            cursor.execute(
                """
                INSERT INTO api_endpoints (id, version_id, path, method, description, parameters, request_body, responses)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (endpoint_id, version_id, path, method, description,
                 json.dumps(parameters) if parameters else None,
                 json.dumps(request_body) if request_body else None,
                 json.dumps(responses) if responses else None)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "add_api_endpoint", {
            "endpoint_id": endpoint_id,
            "version_id": version_id,
            "version": result[1],
            "path": path,
            "method": method
        })
        
        # Return API endpoint information
        return {
            "id": endpoint_id,
            "version_id": version_id,
            "path": path,
            "method": method,
            "description": description,
            "parameters": parameters,
            "request_body": request_body,
            "responses": responses,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def add_breaking_change(self, version_id: str, description: str, migration_guide: str = None) -> Dict[str, Any]:
        """
        Add a breaking change to an API version.
        
        Args:
            version_id: API version ID
            description: Breaking change description
            migration_guide: Migration guide
            
        Returns:
            Dict containing breaking change information
        """
        # Generate breaking change ID
        breaking_change_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get API version
            cursor.execute(
                """
                SELECT id, version
                FROM api_versions
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if API version exists
            if not result:
                raise ValueError("API version not found")
            
            # Insert breaking change
            cursor.execute(
                """
                INSERT INTO breaking_changes (id, version_id, description, migration_guide)
                VALUES (?, ?, ?, ?)
                """,
                (breaking_change_id, version_id, description, migration_guide)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "add_breaking_change", {
            "breaking_change_id": breaking_change_id,
            "version_id": version_id,
            "version": result[1],
            "description": description
        })
        
        # Return breaking change information
        return {
            "id": breaking_change_id,
            "version_id": version_id,
            "description": description,
            "migration_guide": migration_guide,
            "created_at": datetime.now().isoformat()
        }
    
    def create_contract_test(self, version_id: str, name: str, 
                           test_data: Dict[str, Any] = None, 
                           expected_response: Dict[str, Any] = None,
                           description: str = None) -> Dict[str, Any]:
        """
        Create a new contract test for an API version.
        
        Args:
            version_id: API version ID
            name: Test name
            test_data: Test data
            expected_response: Expected response
            description: Test description
            
        Returns:
            Dict containing contract test information
        """
        # Generate test ID
        test_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get API version
            cursor.execute(
                """
                SELECT id, version
                FROM api_versions
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if API version exists
            if not result:
                raise ValueError("API version not found")
            
            # Insert contract test
            cursor.execute(
                """
                INSERT INTO contract_tests (id, version_id, name, description, test_data, expected_response)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (test_id, version_id, name, description,
                 json.dumps(test_data) if test_data else None,
                 json.dumps(expected_response) if expected_response else None)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "create_contract_test", {
            "test_id": test_id,
            "version_id": version_id,
            "version": result[1],
            "name": name
        })
        
        # Return contract test information
        return {
            "id": test_id,
            "version_id": version_id,
            "name": name,
            "description": description,
            "test_data": test_data,
            "expected_response": expected_response,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def run_contract_test(self, test_id: str, actual_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a contract test and record the result.
        
        Args:
            test_id: Test ID
            actual_response: Actual response
            
        Returns:
            Dict containing test result information
        """
        # Generate result ID
        result_id = str(uuid.uuid4())
        
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get contract test
            cursor.execute(
                """
                SELECT id, version_id, name, expected_response
                FROM contract_tests
                WHERE id = ?
                """,
                (test_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if contract test exists
            if not result:
                raise ValueError("Contract test not found")
            
            # Validate response against expected response
            expected_response = json.loads(result[3]) if result[3] else None
            
            # Check if response matches expected response
            if expected_response:
                try:
                    jsonschema.validate(actual_response, expected_response)
                    status = "passed"
                    error_message = None
                except jsonschema.exceptions.ValidationError as e:
                    status = "failed"
                    error_message = str(e)
            else:
                status = "passed"
                error_message = None
            
            # Insert test result
            cursor.execute(
                """
                INSERT INTO test_results (id, test_id, status, actual_response, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (result_id, test_id, status,
                 json.dumps(actual_response) if actual_response else None,
                 error_message)
            )
            
            # Commit changes
            conn.commit()
        
        # Log action
        self.db_manager.log_action(None, "run_contract_test", {
            "result_id": result_id,
            "test_id": test_id,
            "version_id": result[1],
            "name": result[2],
            "status": status
        })
        
        # Return test result information
        return {
            "id": result_id,
            "test_id": test_id,
            "status": status,
            "actual_response": actual_response,
            "error_message": error_message,
            "created_at": datetime.now().isoformat()
        }
    
    def generate_openapi_spec(self, version_id: str) -> Dict[str, Any]:
        """
        Generate OpenAPI specification for an API version.
        
        Args:
            version_id: API version ID
            
        Returns:
            Dict containing OpenAPI specification
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get API version
            cursor.execute(
                """
                SELECT id, version, status
                FROM api_versions
                WHERE id = ?
                """,
                (version_id,)
            )
            
            # Get result
            result = cursor.fetchone()
            
            # Check if API version exists
            if not result:
                raise ValueError("API version not found")
            
            # Get API endpoints
            cursor.execute(
                """
                SELECT path, method, description, parameters, request_body, responses
                FROM api_endpoints
                WHERE version_id = ?
                """,
                (version_id,)
            )
            
            # Get results
            endpoints = cursor.fetchall()
            
            # Generate OpenAPI specification
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "Legal Sanctions RAG API",
                    "version": result[1],
                    "description": f"API for Legal Sanctions RAG System (Version {result[1]})"
                },
                "servers": [
                    {
                        "url": "http://localhost:8000",
                        "description": "Local development server"
                    }
                ],
                "paths": {}
            }
            
            # Add endpoints to OpenAPI specification
            for endpoint in endpoints:
                path = endpoint[0]
                method = endpoint[1].lower()
                description = endpoint[2]
                parameters = json.loads(endpoint[3]) if endpoint[3] else []
                request_body = json.loads(endpoint[4]) if endpoint[4] else None
                responses = json.loads(endpoint[5]) if endpoint[5] else {}
                
                # Add path if it doesn't exist
                if path not in openapi_spec["paths"]:
                    openapi_spec["paths"][path] = {}
                
                # Add method
                openapi_spec["paths"][path][method] = {
                    "summary": description,
                    "description": description,
                    "operationId": f"{method}_{path.replace('/', '_')}",
                    "responses": responses
                }
                
                # Add parameters
                if parameters:
                    openapi_spec["paths"][path][method]["parameters"] = parameters
                
                # Add request body
                if request_body:
                    openapi_spec["paths"][path][method]["requestBody"] = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": request_body
                            }
                        }
                    }
            
            # Save OpenAPI specification to file
            spec_path = os.path.join(self.contract_path, f"openapi_{result[1]}.json")
            with open(spec_path, "w") as f:
                json.dump(openapi_spec, f, indent=2)
            
            # Log action
            self.db_manager.log_action(None, "generate_openapi_spec", {
                "version_id": version_id,
                "version": result[1],
                "spec_path": spec_path
            })
            
            # Return OpenAPI specification
            return openapi_spec
    
    def get_api_versions(self, status: str = None) -> List[Dict[str, Any]]:
        """
        Get all API versions.
        
        Args:
            status: API version status filter (optional)
            
        Returns:
            List of dicts containing API version information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build query
            query = """
                SELECT id, version, status, created_at, updated_at
                FROM api_versions
            """
            params = []
            
            # Add status filter
            if status:
                query += " WHERE status = ?"
                params.append(status)
            
            # Add order by
            query += " ORDER BY created_at DESC"
            
            # Get API versions
            cursor.execute(query, params)
            
            # Get results
            results = cursor.fetchall()
            
            # Return API version information
            return [
                {
                    "id": result[0],
                    "version": result[1],
                    "status": result[2],
                    "created_at": result[3],
                    "updated_at": result[4]
                }
                for result in results
            ]
    
    def get_api_endpoints(self, version_id: str) -> List[Dict[str, Any]]:
        """
        Get all API endpoints for an API version.
        
        Args:
            version_id: API version ID
            
        Returns:
            List of dicts containing API endpoint information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get API endpoints
            cursor.execute(
                """
                SELECT id, version_id, path, method, description, parameters, request_body, responses, created_at, updated_at
                FROM api_endpoints
                WHERE version_id = ?
                ORDER BY path, method
                """,
                (version_id,)
            )
            
            # Get results
            results = cursor.fetchall()
            
            # Return API endpoint information
            return [
                {
                    "id": result[0],
                    "version_id": result[1],
                    "path": result[2],
                    "method": result[3],
                    "description": result[4],
                    "parameters": json.loads(result[5]) if result[5] else None,
                    "request_body": json.loads(result[6]) if result[6] else None,
                    "responses": json.loads(result[7]) if result[7] else None,
                    "created_at": result[8],
                    "updated_at": result[9]
                }
                for result in results
            ]
    
    def get_breaking_changes(self, version_id: str) -> List[Dict[str, Any]]:
        """
        Get all breaking changes for an API version.
        
        Args:
            version_id: API version ID
            
        Returns:
            List of dicts containing breaking change information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get breaking changes
            cursor.execute(
                """
                SELECT id, version_id, description, migration_guide, created_at
                FROM breaking_changes
                WHERE version_id = ?
                ORDER BY created_at DESC
                """,
                (version_id,)
            )
            
            # Get results
            results = cursor.fetchall()
            
            # Return breaking change information
            return [
                {
                    "id": result[0],
                    "version_id": result[1],
                    "description": result[2],
                    "migration_guide": result[3],
                    "created_at": result[4]
                }
                for result in results
            ]
    
    def get_contract_tests(self, version_id: str) -> List[Dict[str, Any]]:
        """
        Get all contract tests for an API version.
        
        Args:
            version_id: API version ID
            
        Returns:
            List of dicts containing contract test information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get contract tests
            cursor.execute(
                """
                SELECT id, version_id, name, description, test_data, expected_response, created_at, updated_at
                FROM contract_tests
                WHERE version_id = ?
                ORDER BY name
                """,
                (version_id,)
            )
            
            # Get results
            results = cursor.fetchall()
            
            # Return contract test information
            return [
                {
                    "id": result[0],
                    "version_id": result[1],
                    "name": result[2],
                    "description": result[3],
                    "test_data": json.loads(result[4]) if result[4] else None,
                    "expected_response": json.loads(result[5]) if result[5] else None,
                    "created_at": result[6],
                    "updated_at": result[7]
                }
                for result in results
            ]
    
    def get_test_results(self, test_id: str) -> List[Dict[str, Any]]:
        """
        Get all test results for a contract test.
        
        Args:
            test_id: Test ID
            
        Returns:
            List of dicts containing test result information
        """
        # Connect to SQLite database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get test results
            cursor.execute(
                """
                SELECT id, test_id, status, actual_response, error_message, created_at
                FROM test_results
                WHERE test_id = ?
                ORDER BY created_at DESC
                """,
                (test_id,)
            )
            
            # Get results
            results = cursor.fetchall()
            
            # Return test result information
            return [
                {
                    "id": result[0],
                    "test_id": result[1],
                    "status": result[2],
                    "actual_response": json.loads(result[3]) if result[3] else None,
                    "error_message": result[4],
                    "created_at": result[5]
                }
                for result in results
            ] 