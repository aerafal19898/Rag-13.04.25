"""
Unified Testing Service for handling unit testing, integration testing, and end-to-end testing.
"""

import os
import json
import yaml
import logging
import time
import uuid
import datetime
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path
from app.services.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestingManager:
    """
    Testing Manager for handling unit testing, integration testing, and end-to-end testing.
    Adds load and scalability testing for system scalability risk mitigation (task 2.1).
    Scaling thresholds are stored in the config.
    """
    
    def __init__(self, db_manager: DatabaseManager, config_path: str = "config"):
        """
        Initialize the testing manager.
        
        Args:
            db_manager: Database manager instance
            config_path: Path to configuration files
        """
        self.db_manager = db_manager
        self.config_path = config_path
        
        # Create config directory if it doesn't exist
        os.makedirs(config_path, exist_ok=True)
        
        # Initialize testing database
        self._init_db()
        
        # Load testing configuration
        self.config = self._load_config()
    
    def _init_db(self):
        """
        Initialize testing database.
        """
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create test suites table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_suites (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create test cases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    id TEXT PRIMARY KEY,
                    suite_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (suite_id) REFERENCES test_suites (id)
                )
            """)
            
            # Create test runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id TEXT PRIMARY KEY,
                    suite_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    result TEXT,
                    FOREIGN KEY (suite_id) REFERENCES test_suites (id)
                )
            """)
            
            # Create test results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    result TEXT,
                    FOREIGN KEY (run_id) REFERENCES test_runs (id),
                    FOREIGN KEY (case_id) REFERENCES test_cases (id)
                )
            """)
            
            # Create test environments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_environments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    config TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create test coverage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_coverage (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_coverage REAL NOT NULL,
                    branch_coverage REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (run_id) REFERENCES test_runs (id)
                )
            """)
            
            conn.commit()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load testing configuration.
        
        Returns:
            Dict containing testing configuration
        """
        # Initialize configuration
        config = {
            "unit_testing": {
                "framework": "pytest",
                "test_dir": "tests/unit",
                "coverage_threshold": 80,
                "parallel": True
            },
            "integration_testing": {
                "framework": "pytest",
                "test_dir": "tests/integration",
                "coverage_threshold": 70,
                "parallel": False
            },
            "end_to_end_testing": {
                "framework": "selenium",
                "test_dir": "tests/e2e",
                "browser": "chrome",
                "headless": True
            },
            "environments": {
                "development": {
                    "database": "sqlite:///dev.db",
                    "api_url": "http://localhost:5000",
                    "timeout": 30
                },
                "staging": {
                    "database": "sqlite:///staging.db",
                    "api_url": "http://staging-api.example.com",
                    "timeout": 60
                },
                "production": {
                    "database": "sqlite:///prod.db",
                    "api_url": "http://api.example.com",
                    "timeout": 120
                }
            }
        }
        
        # Load YAML configuration
        yaml_path = os.path.join(self.config_path, "testing.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                config.update(yaml.safe_load(f))
        
        # Load JSON configuration
        json_path = os.path.join(self.config_path, "testing.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                config.update(json.load(f))
        
        return config
    
    def get_test_suites(self, test_type: str = None) -> List[Dict[str, Any]]:
        """
        Get test suites.
        
        Args:
            test_type: Filter by test type
            
        Returns:
            List of test suites
        """
        # Initialize query
        query = "SELECT * FROM test_suites"
        params = []
        
        # Check if test_type is provided
        if test_type:
            query += " WHERE type = ?"
            params.append(test_type)
        
        # Execute query
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Get test suites
            test_suites = []
            for row in cursor.fetchall():
                test_suites.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "created_at": row[4],
                    "updated_at": row[5]
                })
            
            return test_suites
    
    def get_test_suite(self, suite_id: str) -> Dict[str, Any]:
        """
        Get test suite.
        
        Args:
            suite_id: Test suite ID
            
        Returns:
            Test suite
        """
        # Execute query
        with self.db_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM test_suites WHERE id = ?",
                [suite_id]
            )
            
            # Get test suite
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "created_at": row[4],
                    "updated_at": row[5]
                }
            return None
    
    def create_test_suite(self, name: str, description: str, test_type: str) -> str:
        """
        Create test suite.
        
        Args:
            name: Test suite name
            description: Test suite description
            test_type: Test type (unit, integration, e2e)
            
        Returns:
            Test suite ID
        """
        # Generate ID
        suite_id = str(uuid.uuid4())
        
        # Add test suite
        self.db_manager.execute(
            "INSERT INTO test_suites (id, name, description, type) VALUES (?, ?, ?, ?)",
            [suite_id, name, description, test_type]
        )
        
        # Log action
        self.db_manager.log_action(None, "create_test_suite", {
            "suite_id": suite_id,
            "name": name,
            "description": description,
            "test_type": test_type
        })
        
        return suite_id
    
    def update_test_suite(self, suite_id: str, name: str = None, description: str = None):
        """
        Update test suite.
        
        Args:
            suite_id: Test suite ID
            name: Test suite name
            description: Test suite description
        """
        # Check if test suite exists
        test_suite = self.get_test_suite(suite_id)
        if not test_suite:
            raise ValueError(f"Test suite {suite_id} does not exist")
        
        # Initialize query
        query = "UPDATE test_suites SET updated_at = CURRENT_TIMESTAMP"
        params = []
        
        # Check if name is provided
        if name:
            query += ", name = ?"
            params.append(name)
        
        # Check if description is provided
        if description:
            query += ", description = ?"
            params.append(description)
        
        # Add WHERE clause
        query += " WHERE id = ?"
        params.append(suite_id)
        
        # Execute query
        self.db_manager.execute(query, params)
        
        # Log action
        self.db_manager.log_action(None, "update_test_suite", {
            "suite_id": suite_id,
            "name": name,
            "description": description
        })
    
    def delete_test_suite(self, suite_id: str):
        """
        Delete test suite.
        
        Args:
            suite_id: Test suite ID
        """
        # Check if test suite exists
        test_suite = self.get_test_suite(suite_id)
        if not test_suite:
            raise ValueError(f"Test suite {suite_id} does not exist")
        
        # Delete test suite
        self.db_manager.execute(
            "DELETE FROM test_suites WHERE id = ?",
            [suite_id]
        )
        
        # Log action
        self.db_manager.log_action(None, "delete_test_suite", {
            "suite_id": suite_id,
            "name": test_suite["name"]
        })
    
    def get_test_cases(self, suite_id: str) -> List[Dict[str, Any]]:
        """
        Get test cases.
        
        Args:
            suite_id: Test suite ID
            
        Returns:
            List of test cases
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM test_cases WHERE suite_id = ?",
            [suite_id]
        )
        
        # Get test cases
        test_cases = []
        for row in cursor.fetchall():
            test_cases.append({
                "id": row[0],
                "suite_id": row[1],
                "name": row[2],
                "description": row[3],
                "code": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            })
        
        return test_cases
    
    def get_test_case(self, case_id: str) -> Dict[str, Any]:
        """
        Get test case.
        
        Args:
            case_id: Test case ID
            
        Returns:
            Test case
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM test_cases WHERE id = ?",
            [case_id]
        )
        
        # Get test case
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "suite_id": row[1],
                "name": row[2],
                "description": row[3],
                "code": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        
        return None
    
    def add_test_case(self, suite_id: str, name: str, description: str, code: str) -> str:
        """
        Add test case.
        
        Args:
            suite_id: Test suite ID
            name: Test case name
            description: Test case description
            code: Test case code
            
        Returns:
            Test case ID
        """
        # Check if test suite exists
        test_suite = self.get_test_suite(suite_id)
        if not test_suite:
            raise ValueError(f"Test suite {suite_id} does not exist")
        
        # Generate ID
        case_id = str(uuid.uuid4())
        
        # Add test case
        self.db_manager.execute(
            "INSERT INTO test_cases (id, suite_id, name, description, code) VALUES (?, ?, ?, ?, ?)",
            [case_id, suite_id, name, description, code]
        )
        
        # Log action
        self.db_manager.log_action(None, "add_test_case", {
            "case_id": case_id,
            "suite_id": suite_id,
            "name": name,
            "description": description
        })
        
        return case_id
    
    def update_test_case(self, case_id: str, name: str = None, description: str = None, code: str = None):
        """
        Update test case.
        
        Args:
            case_id: Test case ID
            name: Test case name
            description: Test case description
            code: Test case code
        """
        # Check if test case exists
        test_case = self.get_test_case(case_id)
        if not test_case:
            raise ValueError(f"Test case {case_id} does not exist")
        
        # Initialize query
        query = "UPDATE test_cases SET updated_at = CURRENT_TIMESTAMP"
        params = []
        
        # Check if name is provided
        if name:
            query += ", name = ?"
            params.append(name)
        
        # Check if description is provided
        if description:
            query += ", description = ?"
            params.append(description)
        
        # Check if code is provided
        if code:
            query += ", code = ?"
            params.append(code)
        
        # Add WHERE clause
        query += " WHERE id = ?"
        params.append(case_id)
        
        # Execute query
        self.db_manager.execute(query, params)
        
        # Log action
        self.db_manager.log_action(None, "update_test_case", {
            "case_id": case_id,
            "name": name,
            "description": description
        })
    
    def delete_test_case(self, case_id: str):
        """
        Delete test case.
        
        Args:
            case_id: Test case ID
        """
        # Check if test case exists
        test_case = self.get_test_case(case_id)
        if not test_case:
            raise ValueError(f"Test case {case_id} does not exist")
        
        # Delete test case
        self.db_manager.execute(
            "DELETE FROM test_cases WHERE id = ?",
            [case_id]
        )
        
        # Log action
        self.db_manager.log_action(None, "delete_test_case", {
            "case_id": case_id,
            "name": test_case["name"]
        })
    
    def get_test_runs(self, suite_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """
        Get test runs.
        
        Args:
            suite_id: Filter by test suite ID
            status: Filter by status
            
        Returns:
            List of test runs
        """
        # Initialize query
        query = "SELECT * FROM test_runs"
        params = []
        
        # Check if suite_id or status is provided
        if suite_id or status:
            query += " WHERE"
            
            # Check if suite_id is provided
            if suite_id:
                query += " suite_id = ?"
                params.append(suite_id)
            
            # Check if status is provided
            if status:
                if suite_id:
                    query += " AND"
                query += " status = ?"
                params.append(status)
        
        # Execute query
        cursor = self.db_manager.execute(query, params)
        
        # Get test runs
        test_runs = []
        for row in cursor.fetchall():
            test_runs.append({
                "id": row[0],
                "suite_id": row[1],
                "status": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "result": row[5]
            })
        
        return test_runs
    
    def get_test_run(self, run_id: str) -> Dict[str, Any]:
        """
        Get test run.
        
        Args:
            run_id: Test run ID
            
        Returns:
            Test run
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM test_runs WHERE id = ?",
            [run_id]
        )
        
        # Get test run
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "suite_id": row[1],
                "status": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "result": row[5]
            }
        
        return None
    
    def run_test_suite(self, suite_id: str, environment: str = "development") -> str:
        """
        Run test suite.
        
        Args:
            suite_id: Test suite ID
            environment: Test environment
            
        Returns:
            Test run ID
        """
        # Check if test suite exists
        test_suite = self.get_test_suite(suite_id)
        if not test_suite:
            raise ValueError(f"Test suite {suite_id} does not exist")
        
        # Check if environment exists
        if environment not in self.config["environments"]:
            raise ValueError(f"Environment {environment} does not exist")
        
        # Generate ID
        run_id = str(uuid.uuid4())
        
        # Add test run
        self.db_manager.execute(
            "INSERT INTO test_runs (id, suite_id, status) VALUES (?, ?, 'running')",
            [run_id, suite_id]
        )
        
        # Log action
        self.db_manager.log_action(None, "run_test_suite", {
            "run_id": run_id,
            "suite_id": suite_id,
            "environment": environment
        })
        
        # Run test suite in a separate thread
        import threading
        thread = threading.Thread(
            target=self._run_test_suite_thread,
            args=(run_id, suite_id, environment)
        )
        thread.daemon = True
        thread.start()
        
        return run_id
    
    def _run_test_suite_thread(self, run_id: str, suite_id: str, environment: str):
        """
        Run test suite in a separate thread.
        
        Args:
            run_id: Test run ID
            suite_id: Test suite ID
            environment: Test environment
        """
        try:
            # Get test suite
            test_suite = self.get_test_suite(suite_id)
            
            # Get test cases
            test_cases = self.get_test_cases(suite_id)
            
            # Get environment config
            env_config = self.config["environments"][environment]
            
            # Get test type config
            test_type_config = self.config[f"{test_suite['type']}_testing"]
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create test files
                for test_case in test_cases:
                    # Create test file
                    test_file = os.path.join(temp_dir, f"{test_case['id']}.py")
                    with open(test_file, "w") as f:
                        f.write(test_case["code"])
                
                # Run tests
                if test_suite["type"] == "unit":
                    # Run unit tests
                    result = self._run_unit_tests(temp_dir, env_config, test_type_config)
                elif test_suite["type"] == "integration":
                    # Run integration tests
                    result = self._run_integration_tests(temp_dir, env_config, test_type_config)
                elif test_suite["type"] == "e2e":
                    # Run end-to-end tests
                    result = self._run_e2e_tests(temp_dir, env_config, test_type_config)
                else:
                    # Unknown test type
                    result = {
                        "status": "failed",
                        "result": f"Unknown test type: {test_suite['type']}"
                    }
                
                # Update test run
                self.db_manager.execute(
                    "UPDATE test_runs SET status = ?, end_time = CURRENT_TIMESTAMP, result = ? WHERE id = ?",
                    [result["status"], json.dumps(result), run_id]
                )
                
                # Log action
                self.db_manager.log_action(None, "test_suite_completed", {
                    "run_id": run_id,
                    "suite_id": suite_id,
                    "status": result["status"]
                })
        except Exception as e:
            # Update test run
            self.db_manager.execute(
                "UPDATE test_runs SET status = 'failed', end_time = CURRENT_TIMESTAMP, result = ? WHERE id = ?",
                [str(e), run_id]
            )
            
            # Log action
            self.db_manager.log_action(None, "test_suite_failed", {
                "run_id": run_id,
                "suite_id": suite_id,
                "error": str(e)
            })
    
    def _run_unit_tests(self, test_dir: str, env_config: Dict[str, Any], test_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run unit tests.
        
        Args:
            test_dir: Test directory
            env_config: Environment configuration
            test_config: Test configuration
            
        Returns:
            Test result
        """
        # Set environment variables
        os.environ["TEST_DATABASE"] = env_config["database"]
        os.environ["TEST_API_URL"] = env_config["api_url"]
        os.environ["TEST_TIMEOUT"] = str(env_config["timeout"])
        
        # Run pytest
        cmd = [
            "pytest",
            test_dir,
            "--cov=app",
            "--cov-report=json",
            "--cov-report=term-missing"
        ]
        
        if test_config["parallel"]:
            cmd.append("-n auto")
        
        # Run command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output
        stdout, stderr = process.communicate()
        
        # Check result
        if process.returncode == 0:
            # Parse coverage
            coverage_file = os.path.join(os.getcwd(), "coverage.json")
            if os.path.exists(coverage_file):
                with open(coverage_file, "r") as f:
                    coverage = json.load(f)
                
                # Calculate coverage
                total_lines = 0
                covered_lines = 0
                for file_path, file_data in coverage.items():
                    if file_path.startswith("app/"):
                        for line_num, line_data in file_data["executed_lines"].items():
                            total_lines += 1
                            if line_data:
                                covered_lines += 1
                
                # Calculate coverage percentage
                coverage_percentage = (covered_lines / total_lines) * 100 if total_lines > 0 else 0
                
                # Check if coverage meets threshold
                if coverage_percentage < test_config["coverage_threshold"]:
                    return {
                        "status": "failed",
                        "result": f"Coverage {coverage_percentage:.2f}% is below threshold {test_config['coverage_threshold']}%"
                    }
            
            return {
                "status": "passed",
                "result": stdout
            }
        else:
            return {
                "status": "failed",
                "result": stderr
            }
    
    def _run_integration_tests(self, test_dir: str, env_config: Dict[str, Any], test_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run integration tests.
        
        Args:
            test_dir: Test directory
            env_config: Environment configuration
            test_config: Test configuration
            
        Returns:
            Test result
        """
        # Set environment variables
        os.environ["TEST_DATABASE"] = env_config["database"]
        os.environ["TEST_API_URL"] = env_config["api_url"]
        os.environ["TEST_TIMEOUT"] = str(env_config["timeout"])
        
        # Run pytest
        cmd = [
            "pytest",
            test_dir,
            "--cov=app",
            "--cov-report=json",
            "--cov-report=term-missing"
        ]
        
        if test_config["parallel"]:
            cmd.append("-n auto")
        
        # Run command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output
        stdout, stderr = process.communicate()
        
        # Check result
        if process.returncode == 0:
            # Parse coverage
            coverage_file = os.path.join(os.getcwd(), "coverage.json")
            if os.path.exists(coverage_file):
                with open(coverage_file, "r") as f:
                    coverage = json.load(f)
                
                # Calculate coverage
                total_lines = 0
                covered_lines = 0
                for file_path, file_data in coverage.items():
                    if file_path.startswith("app/"):
                        for line_num, line_data in file_data["executed_lines"].items():
                            total_lines += 1
                            if line_data:
                                covered_lines += 1
                
                # Calculate coverage percentage
                coverage_percentage = (covered_lines / total_lines) * 100 if total_lines > 0 else 0
                
                # Check if coverage meets threshold
                if coverage_percentage < test_config["coverage_threshold"]:
                    return {
                        "status": "failed",
                        "result": f"Coverage {coverage_percentage:.2f}% is below threshold {test_config['coverage_threshold']}%"
                    }
            
            return {
                "status": "passed",
                "result": stdout
            }
        else:
            return {
                "status": "failed",
                "result": stderr
            }
    
    def _run_e2e_tests(self, test_dir: str, env_config: Dict[str, Any], test_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run end-to-end tests.
        
        Args:
            test_dir: Test directory
            env_config: Environment configuration
            test_config: Test configuration
            
        Returns:
            Test result
        """
        # Set environment variables
        os.environ["TEST_API_URL"] = env_config["api_url"]
        os.environ["TEST_TIMEOUT"] = str(env_config["timeout"])
        os.environ["TEST_BROWSER"] = test_config["browser"]
        os.environ["TEST_HEADLESS"] = str(test_config["headless"]).lower()
        
        # Run pytest
        cmd = [
            "pytest",
            test_dir
        ]
        
        # Run command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output
        stdout, stderr = process.communicate()
        
        # Check result
        if process.returncode == 0:
            return {
                "status": "passed",
                "result": stdout
            }
        else:
            return {
                "status": "failed",
                "result": stderr
            }
    
    def get_test_results(self, run_id: str) -> List[Dict[str, Any]]:
        """
        Get test results.
        
        Args:
            run_id: Test run ID
            
        Returns:
            List of test results
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM test_results WHERE run_id = ?",
            [run_id]
        )
        
        # Get test results
        test_results = []
        for row in cursor.fetchall():
            test_results.append({
                "id": row[0],
                "run_id": row[1],
                "case_id": row[2],
                "status": row[3],
                "start_time": row[4],
                "end_time": row[5],
                "result": row[6]
            })
        
        return test_results
    
    def get_test_result(self, result_id: str) -> Dict[str, Any]:
        """
        Get test result.
        
        Args:
            result_id: Test result ID
            
        Returns:
            Test result
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM test_results WHERE id = ?",
            [result_id]
        )
        
        # Get test result
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "run_id": row[1],
                "case_id": row[2],
                "status": row[3],
                "start_time": row[4],
                "end_time": row[5],
                "result": row[6]
            }
        
        return None
    
    def get_test_environments(self) -> List[Dict[str, Any]]:
        """
        Get test environments.
        
        Returns:
            List of test environments
        """
        # Execute query
        cursor = self.db_manager.execute("SELECT * FROM test_environments")
        
        # Get test environments
        test_environments = []
        for row in cursor.fetchall():
            test_environments.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "config": json.loads(row[3]),
                "created_at": row[4],
                "updated_at": row[5]
            })
        
        return test_environments
    
    def get_test_environment(self, env_id: str) -> Dict[str, Any]:
        """
        Get test environment.
        
        Args:
            env_id: Test environment ID
            
        Returns:
            Test environment
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM test_environments WHERE id = ?",
            [env_id]
        )
        
        # Get test environment
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "config": json.loads(row[3]),
                "created_at": row[4],
                "updated_at": row[5]
            }
        
        return None
    
    def add_test_environment(self, name: str, description: str, config: Dict[str, Any]) -> str:
        """
        Add test environment.
        
        Args:
            name: Test environment name
            description: Test environment description
            config: Test environment configuration
            
        Returns:
            Test environment ID
        """
        # Generate ID
        env_id = str(uuid.uuid4())
        
        # Add test environment
        self.db_manager.execute(
            "INSERT INTO test_environments (id, name, description, config) VALUES (?, ?, ?, ?)",
            [env_id, name, description, json.dumps(config)]
        )
        
        # Log action
        self.db_manager.log_action(None, "add_test_environment", {
            "env_id": env_id,
            "name": name,
            "description": description
        })
        
        return env_id
    
    def update_test_environment(self, env_id: str, name: str = None, description: str = None, config: Dict[str, Any] = None):
        """
        Update test environment.
        
        Args:
            env_id: Test environment ID
            name: Test environment name
            description: Test environment description
            config: Test environment configuration
        """
        # Check if test environment exists
        test_environment = self.get_test_environment(env_id)
        if not test_environment:
            raise ValueError(f"Test environment {env_id} does not exist")
        
        # Initialize query
        query = "UPDATE test_environments SET updated_at = CURRENT_TIMESTAMP"
        params = []
        
        # Check if name is provided
        if name:
            query += ", name = ?"
            params.append(name)
        
        # Check if description is provided
        if description:
            query += ", description = ?"
            params.append(description)
        
        # Check if config is provided
        if config:
            query += ", config = ?"
            params.append(json.dumps(config))
        
        # Add WHERE clause
        query += " WHERE id = ?"
        params.append(env_id)
        
        # Execute query
        self.db_manager.execute(query, params)
        
        # Log action
        self.db_manager.log_action(None, "update_test_environment", {
            "env_id": env_id,
            "name": name,
            "description": description
        })
    
    def delete_test_environment(self, env_id: str):
        """
        Delete test environment.
        
        Args:
            env_id: Test environment ID
        """
        # Check if test environment exists
        test_environment = self.get_test_environment(env_id)
        if not test_environment:
            raise ValueError(f"Test environment {env_id} does not exist")
        
        # Delete test environment
        self.db_manager.execute(
            "DELETE FROM test_environments WHERE id = ?",
            [env_id]
        )
        
        # Log action
        self.db_manager.log_action(None, "delete_test_environment", {
            "env_id": env_id,
            "name": test_environment["name"]
        })
    
    def get_test_coverage(self, run_id: str) -> List[Dict[str, Any]]:
        """
        Get test coverage.
        
        Args:
            run_id: Test run ID
            
        Returns:
            List of test coverage
        """
        # Execute query
        cursor = self.db_manager.execute(
            "SELECT * FROM test_coverage WHERE run_id = ?",
            [run_id]
        )
        
        # Get test coverage
        test_coverage = []
        for row in cursor.fetchall():
            test_coverage.append({
                "id": row[0],
                "run_id": row[1],
                "file_path": row[2],
                "line_coverage": row[3],
                "branch_coverage": row[4],
                "created_at": row[5]
            })
        
        return test_coverage
    
    def save_config(self):
        """
        Save testing configuration.
        """
        # Save YAML configuration
        yaml_path = os.path.join(self.config_path, "testing.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        # Save JSON configuration
        json_path = os.path.join(self.config_path, "testing.json")
        with open(json_path, "w") as f:
            json.dump(self.config, f, indent=2)
        
        # Log action
        self.db_manager.log_action(None, "save_config", self.config)

    def run_load_test(self, endpoint: str, num_requests: int = 100, concurrency: int = 10, threshold_ms: int = 1000) -> dict:
        """Run a simple load test against an endpoint."""
        import httpx, asyncio
        results = []
        async def worker():
            async with httpx.AsyncClient() as client:
                for _ in range(num_requests // concurrency):
                    start = time.time()
                    try:
                        resp = await client.get(endpoint)
                        elapsed = (time.time() - start) * 1000
                        results.append(elapsed)
                    except Exception:
                        results.append(float('inf'))
        async def main():
            await asyncio.gather(*(worker() for _ in range(concurrency)))
        asyncio.run(main())
        avg = sum(results) / len(results) if results else float('inf')
        passed = avg < threshold_ms
        self.db_manager.log_action(None, "run_load_test", {"endpoint": endpoint, "avg_ms": avg, "threshold_ms": threshold_ms, "passed": passed})
        return {"average_ms": avg, "threshold_ms": threshold_ms, "passed": passed, "results": results}

    def run_scalability_test(self, endpoint: str, scale_steps: int = 3, base_concurrency: int = 10, threshold_ms: int = 1000) -> dict:
        """Run a scalability test by increasing concurrency and measuring response times."""
        results = []
        for step in range(1, scale_steps + 1):
            concurrency = base_concurrency * step
            res = self.run_load_test(endpoint, num_requests=concurrency*10, concurrency=concurrency, threshold_ms=threshold_ms)
            results.append({"concurrency": concurrency, **res})
        self.db_manager.log_action(None, "run_scalability_test", {"endpoint": endpoint, "results": results})
        return {"endpoint": endpoint, "results": results} 