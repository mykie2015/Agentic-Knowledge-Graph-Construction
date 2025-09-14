"""
Logging configuration for the Agentic Knowledge Graph Construction system.
Provides structured logging with proper formatting and file outputs.
"""

import logging
import logging.config
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'agent_name'):
            log_entry['agent_name'] = record.agent_name
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'task_id'):
            log_entry['task_id'] = record.task_id
        
        return json.dumps(log_entry)


def setup_logging(log_dir: Optional[str] = None, level: str = "INFO"):
    """
    Set up logging configuration for the entire system.
    
    Args:
        log_dir: Directory to store log files. Defaults to ./log
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'log')
    
    # Ensure log directories exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    (log_path / 'agents').mkdir(exist_ok=True)
    (log_path / 'system').mkdir(exist_ok=True)
    (log_path / 'errors').mkdir(exist_ok=True)
    
    # Define logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d: %(message)s'
            },
            'json': {
                '()': JSONFormatter
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'system_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': level,
                'formatter': 'json',
                'filename': os.path.join(log_dir, 'system', 'system.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'agent_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': level,
                'formatter': 'json',
                'filename': os.path.join(log_dir, 'agents', 'agents.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'errors', 'errors.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'system_file', 'error_file'],
                'level': level,
                'propagate': False
            },
            'agents': {
                'handlers': ['console', 'agent_file', 'error_file'],
                'level': level,
                'propagate': False
            },
            'neo4j': {
                'handlers': ['system_file'],
                'level': 'WARNING',
                'propagate': False
            },
            'litellm': {
                'handlers': ['system_file'],
                'level': 'WARNING',
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(config)
    
    # Log the initialization
    logger = logging.getLogger(__name__)
    logger.info(f"Logging system initialized with level {level}")
    logger.info(f"Log directory: {log_dir}")


def get_agent_logger(agent_name: str):
    """
    Get a logger specifically configured for an agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        logging.Logger: Configured logger for the agent
    """
    logger = logging.getLogger(f'agents.{agent_name}')
    
    # Add agent context to all log records
    class AgentAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return msg, kwargs
        
        def _log(self, level, msg, args, **kwargs):
            if not kwargs.get('extra'):
                kwargs['extra'] = {}
            kwargs['extra']['agent_name'] = self.extra['agent_name']
            return self.logger._log(level, msg, args, **kwargs)
    
    return AgentAdapter(logger, {'agent_name': agent_name})


def get_system_logger(component: str):
    """
    Get a logger for system components.
    
    Args:
        component: Name of the system component
        
    Returns:
        logging.Logger: Configured logger for the component
    """
    return logging.getLogger(f'system.{component}')


# Convenience function for quick setup
def quick_setup(debug: bool = False):
    """Quick logging setup with sensible defaults."""
    level = "DEBUG" if debug else "INFO"
    setup_logging(level=level)
