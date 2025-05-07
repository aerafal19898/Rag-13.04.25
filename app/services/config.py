"""
Environment Configuration Service for handling environment variables, configuration files, and secrets management.
"""

import os
import json
import yaml
import logging
import secrets
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pathlib import Path
from cryptography.fernet import Fernet

# Type hint import
if TYPE_CHECKING:
    from app.services.database import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration Manager for handling environment variables, configuration files, and secrets management.
    """
    
    def __init__(self, db_manager: 'DatabaseManager', config_path: str = "config"):
        """
        Initialize the configuration manager.
        
        Args:
            db_manager: Database manager instance
            config_path: Path to configuration files
        """
        self.db_manager = db_manager
        self.config_path = config_path
        
        # Create config directory if it doesn't exist
        # os.makedirs(config_path, exist_ok=True) # Less relevant if not saving files
        
        # Load environment variables
        # self._load_env() # .env loading is primarily for local dev
        
        # Initialize encryption key - Keep for potential use, but consider env var for key?
        # For production, the .key file needs to exist or be mounted, or key comes from ENV
        self._init_encryption()
        
        # Load configuration
        self.config = self._load_config()
    
    def _init_encryption(self):
        """
        Initialize encryption key for secrets management.
        Tries ENV var first, then falls back to file.
        """
        # Try loading key from environment variable first
        env_key = os.getenv('ENCRYPTION_KEY')
        if env_key:
            self.key = env_key.encode()
            logger.info("Loaded encryption key from ENCRYPTION_KEY environment variable.")
        else:
            # Fallback to loading from file
            key_path = os.path.join(self.config_path, ".key")
            if os.path.exists(key_path):
                with open(key_path, "rb") as f:
                    self.key = f.read()
                logger.info(f"Loaded encryption key from file: {key_path}")
            else:
                # Generate and save only if file AND env var are missing (dev fallback)
                # In production, key MUST be provided via ENV or mounted file.
                self.key = Fernet.generate_key()
                os.makedirs(self.config_path, exist_ok=True) # Ensure dir exists before write
                try:
                    with open(key_path, "wb") as f:
                        f.write(self.key)
                    logger.warning(f"Generated new encryption key and saved to {key_path}. Ensure this key is managed securely for production!")
                except OSError as e:
                     logger.error(f"Failed to save generated encryption key to {key_path}: {e}. Secrets requiring encryption may fail.")
                     # Set cipher to None or handle error appropriately if key is mandatory
                     self.cipher = None
                     return

        # Initialize Fernet cipher
        try:
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.error(f"Failed to initialize Fernet cipher with the provided key: {e}")
            self.cipher = None # Ensure cipher is None if key is invalid
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration primarily from environment variables for production.
        Falls back to config files (config.yaml, config.json) if they exist.
        Environment variables take precedence.
        """
        config = {}
        
        # Load config files first (if they exist) as base
        yaml_path = os.path.join(self.config_path, "config.yaml")
        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, "r") as f:
                    config.update(yaml.safe_load(f))
            except Exception as e:
                logger.warning(f"Failed to load config.yaml: {e}")
        
        json_path = os.path.join(self.config_path, "config.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    config.update(json.load(f))
            except Exception as e:
                logger.warning(f"Failed to load config.json: {e}")
        
        # --- Override/Set values from Environment Variables --- #
        # Database (PostgreSQL Connection Info)
        db_config = config.get('db', {})
        db_config['type'] = os.getenv("DB_TYPE", db_config.get('type', 'postgresql')) # Default to postgresql
        db_config['host'] = os.getenv("DB_HOST", db_config.get('host', 'localhost'))
        db_config['port'] = int(os.getenv("DB_PORT", db_config.get('port', 5432)))
        db_config['user'] = os.getenv("DB_USER", db_config.get('user', None))
        db_config['password'] = os.getenv("DB_PASSWORD", db_config.get('password', None))
        db_config['name'] = os.getenv("DB_NAME", db_config.get('name', None))
        # Remove placeholder DB_PATH
        db_config.pop('path', None)
        config['db'] = db_config
        
        # API
        api_config = config.get('api', {})
        api_config['host'] = os.getenv("API_HOST", api_config.get('host', "0.0.0.0")) # Default to 0.0.0.0 for container
        api_config['port'] = int(os.getenv("API_PORT", api_config.get('port', 8000)))
        # Determine debug mode from APP_ENV, default to False (production)
        api_config['debug'] = os.getenv("APP_ENV", "production").lower() != "production"
        config['api'] = api_config
        
        # Authentication (JWT)
        auth_config = config.get('auth', {})
        # JWT_SECRET_KEY MUST come from ENV in production
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if not jwt_secret:
            logger.critical("FATAL: JWT_SECRET_KEY environment variable not set!")
            # Potentially raise an exception or exit? For now, use fallback but log critical.
            jwt_secret = auth_config.get('jwt_secret_key', "fallback-insecure-secret-key")
        auth_config['jwt_secret_key'] = jwt_secret
        auth_config['jwt_algorithm'] = os.getenv("JWT_ALGORITHM", auth_config.get('jwt_algorithm', "HS256"))
        auth_config['jwt_access_token_expire_minutes'] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", auth_config.get('jwt_access_token_expire_minutes', 30)))
        config['auth'] = auth_config
        
        # Model (Path/Type/Version can still be useful from files/env)
        model_config = config.get('model', {})
        model_config['path'] = os.getenv("MODEL_PATH", model_config.get('path', "models"))
        model_config['type'] = os.getenv("MODEL_TYPE", model_config.get('type', "deepseek"))
        model_config['version'] = os.getenv("MODEL_VERSION", model_config.get('version', "1.0"))
        config['model'] = model_config
        
        # Redis
        redis_config = config.get('redis', {})
        redis_config['host'] = os.getenv("REDIS_HOST", redis_config.get('host', 'localhost'))
        redis_config['port'] = int(os.getenv("REDIS_PORT", redis_config.get('port', 6379)))
        redis_config['password'] = os.getenv("REDIS_PASSWORD", redis_config.get('password', None))
        config['redis'] = redis_config
        
        # ChromaDB
        chroma_config = config.get('chroma', {})
        chroma_config['host'] = os.getenv("CHROMA_HOST", chroma_config.get('host', 'localhost'))
        chroma_config['port'] = int(os.getenv("CHROMA_PORT", chroma_config.get('port', 8000)))
        config['chroma'] = chroma_config
        
        # External API Keys (Example: DeepSeek)
        ext_apis_config = config.get('external_apis', {})
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", ext_apis_config.get('deepseek_api_key', None))
        if not deepseek_key:
            logger.warning("DEEPSEEK_API_KEY environment variable not set.")
        ext_apis_config['deepseek_api_key'] = deepseek_key
        # Add other external API keys here (e.g., OPENROUTER_API_KEY)
        config['external_apis'] = ext_apis_config
        
        # Logging Level
        log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        config['logging'] = {'level': log_level_name}
        # Apply log level (consider doing this more centrally at app startup)
        logging.getLogger().setLevel(getattr(logging, log_level_name, logging.INFO))
        
        logger.info(f"Configuration loaded. Debug mode: {config['api']['debug']}")
        logger.debug(f"Full configuration (secrets redacted where possible): {self._get_redacted_config(config)}")
        
        return config
    
    def get_config(self, section: str = None, key: str = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            
        Returns:
            Configuration value
        """
        # Check if section is provided
        if section:
            # Check if key is provided
            if key:
                return self.config.get(section, {}).get(key)
            return self.config.get(section, {})
        return self.config
    
    def set_config(self, section: str, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        # Runtime import needed here
        from app.services.database import DatabaseManager

        # Check if section exists
        if section not in self.config:
            self.config[section] = {}
        
        # Set configuration value
        self.config[section][key] = value
        
        # Save configuration
        self._save_config()
        
        # Log action
        # Ensure db_manager is actually a DatabaseManager instance before calling methods
        if isinstance(self.db_manager, DatabaseManager):
            self.db_manager.log_action(None, "set_config", {
                "section": section,
                "key": key,
                "value": value
            })
        else:
            # Maybe log a warning or raise an error if the type is unexpected
            logger.warning("db_manager provided to ConfigManager is not an instance of DatabaseManager.")
    
    def _save_config(self):
        """
        Save configuration to files.
        """
        # In production, saving config derived from ENV back to files is likely undesirable.
        # Consider disabling this or making it conditional.
        logger.warning("_save_config called. In a production environment sourced from ENV vars, saving back to files might be disabled or unintended.")
        # Temporarily disable saving to files in production if APP_ENV is production
        if os.getenv("APP_ENV", "production").lower() == "production":
            logger.info("Skipping saving config to files in production environment.")
            return

        # Original saving logic (for dev/local use)
        # Save YAML configuration
        yaml_path = os.path.join(self.config_path, "config.yaml")
        with open(yaml_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        # Save JSON configuration
        json_path = os.path.join(self.config_path, "config.json")
        with open(json_path, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def encrypt_secret(self, secret: str) -> str:
        """
        Encrypt a secret.
        
        Args:
            secret: Secret to encrypt
            
        Returns:
            Encrypted secret
        """
        # Encrypt secret
        encrypted_secret = self.cipher.encrypt(secret.encode())
        
        # Return encrypted secret
        return encrypted_secret.decode()
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """
        Decrypt a secret.
        
        Args:
            encrypted_secret: Encrypted secret
            
        Returns:
            Decrypted secret
        """
        # Decrypt secret
        decrypted_secret = self.cipher.decrypt(encrypted_secret.encode())
        
        # Return decrypted secret
        return decrypted_secret.decode()
    
    def generate_secret(self, length: int = 32) -> str:
        """
        Generate a random secret.
        
        Args:
            length: Secret length
            
        Returns:
            Generated secret
        """
        # Generate secret
        secret = secrets.token_urlsafe(length)
        
        # Return secret
        return secret
    
    def get_env_vars(self) -> Dict[str, str]:
        """
        Get all environment variables.
        
        Returns:
            Dict containing environment variables
        """
        return dict(os.environ)
    
    def set_env_var(self, key: str, value: str):
        """
        Set environment variable.
        
        Args:
            key: Environment variable key
            value: Environment variable value
        """
        # Set environment variable
        os.environ[key] = value
        
        # Update .env file
        env_path = os.path.join(self.config_path, ".env")
        with open(env_path, "a") as f:
            f.write(f"{key}={value}\n")
        
        # Log action
        # Ensure db_manager is actually a DatabaseManager instance before calling methods
        if isinstance(self.db_manager, DatabaseManager):
            self.db_manager.log_action(None, "set_env_var", {
                "key": key,
                "value": value
            })
        else:
            # Maybe log a warning or raise an error if the type is unexpected
            logger.warning("db_manager provided to ConfigManager is not an instance of DatabaseManager.")
    
    def get_config_files(self) -> List[str]:
        """
        Get all configuration files.
        
        Returns:
            List of configuration file paths
        """
        # Get configuration files
        config_files = []
        for file in os.listdir(self.config_path):
            if file.endswith((".yaml", ".json", ".env")):
                config_files.append(os.path.join(self.config_path, file))
        
        return config_files
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration.
        
        Returns:
            List of validation errors
        """
        # Initialize errors
        errors = []
        
        # Validate database configuration
        if "db" not in self.config:
            errors.append("Database configuration is missing")
        else:
            if "type" not in self.config["db"]:
                errors.append("Database type is missing")
            if "path" not in self.config["db"]:
                errors.append("Database path is missing")
        
        # Validate API configuration
        if "api" not in self.config:
            errors.append("API configuration is missing")
        else:
            if "host" not in self.config["api"]:
                errors.append("API host is missing")
            if "port" not in self.config["api"]:
                errors.append("API port is missing")
            if "debug" not in self.config["api"]:
                errors.append("API debug is missing")
        
        # Validate authentication configuration
        if "auth" not in self.config:
            errors.append("Authentication configuration is missing")
        else:
            if "jwt_secret_key" not in self.config["auth"]:
                errors.append("JWT secret key is missing")
            if "jwt_algorithm" not in self.config["auth"]:
                errors.append("JWT algorithm is missing")
            if "jwt_access_token_expire_minutes" not in self.config["auth"]:
                errors.append("JWT access token expire minutes is missing")
        
        # Validate model configuration
        if "model" not in self.config:
            errors.append("Model configuration is missing")
        else:
            if "path" not in self.config["model"]:
                errors.append("Model path is missing")
            if "type" not in self.config["model"]:
                errors.append("Model type is missing")
            if "version" not in self.config["model"]:
                errors.append("Model version is missing")
        
        return errors
    
    def backup_config(self, backup_path: str = None) -> str:
        """
        Backup configuration.
        
        Args:
            backup_path: Backup path
            
        Returns:
            Backup path
        """
        # Check if backup path is provided
        if not backup_path:
            # Generate backup path
            backup_path = os.path.join(self.config_path, "backup")
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_path, exist_ok=True)
        
        # Backup configuration files
        for file in self.get_config_files():
            # Get file name
            file_name = os.path.basename(file)
            
            # Copy file
            with open(file, "r") as src:
                with open(os.path.join(backup_path, file_name), "w") as dst:
                    dst.write(src.read())
        
        # Log action
        # Ensure db_manager is actually a DatabaseManager instance before calling methods
        if isinstance(self.db_manager, DatabaseManager):
            self.db_manager.log_action(None, "backup_config", {
                "backup_path": backup_path
            })
        else:
            # Maybe log a warning or raise an error if the type is unexpected
            logger.warning("db_manager provided to ConfigManager is not an instance of DatabaseManager.")
        
        return backup_path
    
    def restore_config(self, backup_path: str):
        """
        Restore configuration from backup.
        
        Args:
            backup_path: Backup path
        """
        # Check if backup path exists
        if not os.path.exists(backup_path):
            raise ValueError("Backup path does not exist")
        
        # Restore configuration files
        for file in os.listdir(backup_path):
            if file.endswith((".yaml", ".json", ".env")):
                # Copy file
                with open(os.path.join(backup_path, file), "r") as src:
                    with open(os.path.join(self.config_path, file), "w") as dst:
                        dst.write(src.read())
        
        # Reload configuration
        self.config = self._load_config()
        
        # Log action
        # Ensure db_manager is actually a DatabaseManager instance before calling methods
        if isinstance(self.db_manager, DatabaseManager):
            self.db_manager.log_action(None, "restore_config", {
                "backup_path": backup_path
            })
        else:
            # Maybe log a warning or raise an error if the type is unexpected
            logger.warning("db_manager provided to ConfigManager is not an instance of DatabaseManager.")
    
    # --- Add Helper for Debug Logging --- #
    def _get_redacted_config(self, config_dict: Dict) -> Dict:
        """Return a copy of the config with sensitive values redacted."""
        redacted_config = json.loads(json.dumps(config_dict)) # Deep copy
        sensitive_keys = ['password', 'jwt_secret_key', 'encryption_key', 'api_key']
        try:
            if 'db' in redacted_config and 'password' in redacted_config['db']:
                redacted_config['db']['password'] = "********"
            if 'redis' in redacted_config and 'password' in redacted_config['redis']:
                redacted_config['redis']['password'] = "********"
            if 'auth' in redacted_config and 'jwt_secret_key' in redacted_config['auth']:
                redacted_config['auth']['jwt_secret_key'] = "********"
            if 'external_apis' in redacted_config:
                for key in redacted_config['external_apis']:
                    if any(sk in key for sk in sensitive_keys):
                         redacted_config['external_apis'][key] = "********"
            # Redact the actual self.key if shown elsewhere
        except Exception as e:
            logger.warning(f"Error redacting config for logging: {e}")
        return redacted_config 