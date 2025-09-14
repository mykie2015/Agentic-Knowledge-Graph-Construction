"""
Base agent class for the Agentic Knowledge Graph Construction system.
Provides common functionality and interfaces for all agents.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from utils.logging_config import get_agent_logger
from utils.config_manager import get_config


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Provides common functionality and enforces agent interface.
    """
    
    def __init__(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Unique name for the agent
            config: Agent-specific configuration (optional)
        """
        self.agent_name = agent_name
        self.logger = get_agent_logger(agent_name)
        self.config_manager = get_config()
        
        # Get agent-specific configuration
        self.agent_config = config or self.config_manager.get_agent_config(agent_name)
        
        # Initialize LLM
        llm_config = self.config_manager.get_llm_config()
        model = self.agent_config.get('model', llm_config.get('default_model'))
        self.llm = LiteLlm(model=model)
        
        # Initialize state tracking
        self.state = {}
        self.session_id = None
        self.task_id = None
        
        # Initialize the ADK agent
        self.agent = None
        self._initialize_agent()
        
        self.logger.info(f"Agent {agent_name} initialized with model {model}")
    
    @abstractmethod
    def _initialize_agent(self):
        """Initialize the Google ADK agent. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_tools(self) -> List:
        """Return list of tools available to this agent. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent. Must be implemented by subclasses."""
        pass
    
    def set_session_context(self, session_id: str, task_id: Optional[str] = None):
        """
        Set session context for the agent.
        
        Args:
            session_id: Unique session identifier
            task_id: Optional task identifier for this session
        """
        self.session_id = session_id
        self.task_id = task_id
        
        # Update logger context
        if hasattr(self.logger, 'extra'):
            self.logger.extra.update({
                'session_id': session_id,
                'task_id': task_id
            })
        
        self.logger.info(f"Session context set: session_id={session_id}, task_id={task_id}")
    
    def update_state(self, key: str, value: Any):
        """
        Update agent state.
        
        Args:
            key: State key
            value: State value
        """
        self.state[key] = value
        self.logger.debug(f"State updated: {key} = {value}")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get value from agent state.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        return self.state.get(key, default)
    
    def clear_state(self):
        """Clear all agent state."""
        self.state.clear()
        self.logger.info("Agent state cleared")
    
    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Validate input data for the agent.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        required_fields = self.get_required_input_fields()
        
        for field in required_fields:
            if field not in input_data:
                errors.append(f"Required field missing: {field}")
            elif input_data[field] is None:
                errors.append(f"Required field is None: {field}")
        
        return errors
    
    def get_required_input_fields(self) -> List[str]:
        """
        Return list of required input fields for this agent.
        Can be overridden by subclasses.
        
        Returns:
            List of required field names
        """
        return []
    
    def process_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Process and log errors consistently.
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
            
        Returns:
            Error response dictionary
        """
        error_msg = f"Error in {self.agent_name}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"
        
        self.logger.error(error_msg, exc_info=True)
        
        return {
            'status': 'error',
            'error_message': error_msg,
            'agent': self.agent_name,
            'session_id': self.session_id,
            'task_id': self.task_id
        }
    
    def create_success_response(self, data: Any, message: str = "") -> Dict[str, Any]:
        """
        Create a standardized success response.
        
        Args:
            data: Response data
            message: Optional success message
            
        Returns:
            Success response dictionary
        """
        response = {
            'status': 'success',
            'data': data,
            'agent': self.agent_name,
            'session_id': self.session_id,
            'task_id': self.task_id
        }
        
        if message:
            response['message'] = message
        
        self.logger.info(f"Success response created: {message or 'Operation completed'}")
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            'agent_name': self.agent_name,
            'state_size': len(self.state),
            'session_id': self.session_id,
            'task_id': self.task_id,
            'config': self.agent_config
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform agent health check.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check if agent is properly initialized
            if not self.agent:
                return {'status': 'unhealthy', 'reason': 'Agent not initialized'}
            
            # Check if LLM is accessible (simple check)
            if not self.llm:
                return {'status': 'unhealthy', 'reason': 'LLM not available'}
            
            # Check configuration
            if not self.agent_config:
                return {'status': 'unhealthy', 'reason': 'Agent configuration missing'}
            
            return {
                'status': 'healthy',
                'agent': self.agent_name,
                'model': self.agent_config.get('model'),
                'enabled': self.agent_config.get('enabled', True)
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'reason': f'Health check failed: {str(e)}'
            }
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name={self.agent_name}, session={self.session_id})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (f"{self.__class__.__name__}("
                f"name={self.agent_name}, "
                f"model={self.agent_config.get('model')}, "
                f"session={self.session_id}, "
                f"task={self.task_id})")


class AgentError(Exception):
    """Custom exception for agent-related errors."""
    
    def __init__(self, message: str, agent_name: str = None, error_code: str = None):
        """
        Initialize agent error.
        
        Args:
            message: Error message
            agent_name: Name of the agent that generated the error
            error_code: Optional error code for categorization
        """
        super().__init__(message)
        self.agent_name = agent_name
        self.error_code = error_code
        self.message = message


class AgentTimeoutError(AgentError):
    """Exception for agent timeout errors."""
    pass


class AgentValidationError(AgentError):
    """Exception for agent input validation errors."""
    pass
