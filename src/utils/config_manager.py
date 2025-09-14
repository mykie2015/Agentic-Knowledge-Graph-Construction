"""
Configuration management for the Agentic Knowledge Graph Construction system.
Handles environment variables, configuration files, and system settings.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv


class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (JSON or YAML)
        """
        # Load environment variables
        self._load_env()
        
        # Default configuration
        self._config = {
            'agents': {
                'user_intent': {
                    'enabled': True,
                    'model': 'openai/gpt-4o',
                    'max_retries': 3
                },
                'file_suggestion': {
                    'enabled': True,
                    'model': 'openai/gpt-4o',
                    'max_retries': 3
                },
                'schema_proposal_structured': {
                    'enabled': True,
                    'model': 'openai/gpt-4o',
                    'max_retries': 3
                },
                'schema_proposal_unstructured': {
                    'enabled': True,
                    'model': 'openai/gpt-4o',
                    'max_retries': 3
                },
                'kg_constructor': {
                    'enabled': True,
                    'batch_size': 1000,
                    'max_retries': 3
                }
            },
            'neo4j': {
                'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
                'username': os.getenv('NEO4J_USERNAME', 'neo4j'),
                'password': os.getenv('NEO4J_PASSWORD', 'password'),
                'database': os.getenv('NEO4J_DATABASE', 'neo4j')
            },
            'llm': {
                'provider': os.getenv('LLM_PROVIDER', 'openai'),
                'api_key': os.getenv('OPENAI_API_KEY'),
                'base_url': os.getenv('OPENAI_BASE_URL'),
                'default_model': os.getenv('DEFAULT_MODEL', 'openai/gpt-4o'),
                'timeout': int(os.getenv('LLM_TIMEOUT', '60')),
                'max_tokens': int(os.getenv('LLM_MAX_TOKENS', '4000'))
            },
            'data': {
                'input_dir': os.getenv('INPUT_DIR', './data/input'),
                'output_dir': os.getenv('OUTPUT_DIR', './data/output'),
                'neo4j_import_dir': os.getenv('NEO4J_IMPORT_DIR', './data/input')
            },
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'log_dir': os.getenv('LOG_DIR', './log'),
                'enable_json': os.getenv('ENABLE_JSON_LOGGING', 'true').lower() == 'true'
            },
            'system': {
                'max_concurrent_agents': int(os.getenv('MAX_CONCURRENT_AGENTS', '3')),
                'session_timeout': int(os.getenv('SESSION_TIMEOUT', '3600')),
                'enable_monitoring': os.getenv('ENABLE_MONITORING', 'true').lower() == 'true'
            }
        }
        
        # Load configuration file if provided
        if config_file:
            self._load_config_file(config_file)
    
    def _load_env(self):
        """Load environment variables from .env file."""
        env_file = find_dotenv()
        if env_file:
            load_dotenv(env_file)
    
    def _load_config_file(self, config_file: str):
        """Load configuration from JSON or YAML file."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yml', '.yaml']:
                    file_config = yaml.safe_load(f)
                else:
                    file_config = json.load(f)
            
            # Merge with default configuration
            if isinstance(file_config, dict):
                self._deep_merge(self._config, file_config)
            else:
                raise ValueError(f"Configuration file must contain a dictionary, got {type(file_config)}")
            
        except Exception as e:
            raise ValueError(f"Error loading configuration file {config_file}: {e}")
    
    def _deep_merge(self, base_dict: Dict, update_dict: Dict):
        """Recursively merge two dictionaries."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration value (e.g., 'neo4j.uri')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration value
            value: Value to set
        """
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            if isinstance(config[key], dict):
                config = config[key]
            else:
                raise ValueError(f"Cannot set nested key {key_path}: {key} is not a dictionary")
        
        # Set the value
        config[keys[-1]] = value
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return self.get(f'agents.{agent_name}', {})
    
    def get_neo4j_config(self) -> Dict[str, Any]:
        """Get Neo4j connection configuration."""
        return self.get('neo4j', {})
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.get('llm', {})
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data directories configuration."""
        return self.get('data', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def validate_config(self) -> list:
        """
        Validate configuration and return list of errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate Neo4j configuration
        neo4j_config = self.get_neo4j_config()
        if not neo4j_config.get('uri'):
            errors.append("Neo4j URI is required")
        if not neo4j_config.get('username'):
            errors.append("Neo4j username is required")
        if not neo4j_config.get('password'):
            errors.append("Neo4j password is required")
        
        # Validate LLM configuration
        llm_config = self.get_llm_config()
        if not llm_config.get('api_key'):
            errors.append("LLM API key is required")
        
        # Validate data directories
        data_config = self.get_data_config()
        input_dir = Path(data_config.get('input_dir', ''))
        if not input_dir.exists():
            errors.append(f"Input directory does not exist: {input_dir}")
        
        output_dir = Path(data_config.get('output_dir', ''))
        if not output_dir.exists():
            errors.append(f"Output directory does not exist: {output_dir}")
        
        return errors
    
    def save_config(self, file_path: str):
        """Save current configuration to file."""
        config_path = Path(file_path)
        
        with open(config_path, 'w') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(self._config, f, default_flow_style=False)
            else:
                json.dump(self._config, f, indent=2)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get the complete configuration dictionary."""
        return self._config.copy()


# Global configuration instance
_config_manager = None


def get_config(config_file: Optional[str] = None) -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Args:
        config_file: Path to configuration file (used only on first call)
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    
    return _config_manager


def init_config(config_file: Optional[str] = None) -> ConfigManager:
    """
    Initialize the global configuration manager.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    _config_manager = ConfigManager(config_file)
    return _config_manager
