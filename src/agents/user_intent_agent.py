"""
User Intent Agent for the Agentic Knowledge Graph Construction system.
Helps users ideate on the kind of graph to build and understands their goals.
"""

from typing import Dict, Any, List
from pathlib import Path
import re
from google.adk.agents import Agent
from google.adk.tools import ToolContext

from core.agent_base import BaseAgent, AgentValidationError
from utils.neo4j_for_adk import tool_success, tool_error


class UserIntentAgent(BaseAgent):
    """
    Agent that understands user intent and helps define graph construction goals.
    
    Responsibilities:
    - Engage with users to understand their graph requirements
    - Help users clarify their goals and use cases
    - Validate and approve user goals
    - Set the foundation for subsequent agent work
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the User Intent Agent."""
        super().__init__("user_intent", config)
        
        # Load agent configuration from markdown file
        self.agent_config_data = self._load_agent_config()
        
        # Extract configuration values
        self.valid_graph_types = self.agent_config_data.get('valid_graph_types', 
            ['domain', 'semantic', 'knowledge', 'lexical', 'subject'])
        self.conversation_style = self.agent_config.get('conversation_style', 'casual')
        self.domain_specialization = self.agent_config.get('domain_specialization', 'general')
        self.validation_strictness = self.agent_config.get('validation_strictness', 'moderate')
    
    def _load_agent_config(self) -> Dict[str, Any]:
        """Load agent configuration from the user-intent.md file."""
        try:
            # Get the config file path
            config_dir = Path(__file__).parent.parent.parent / "config"
            config_file = config_dir / "user-intent.md"
            
            if not config_file.exists():
                self.logger.warning(f"Configuration file not found: {config_file}")
                return {}
            
            # Read the markdown file
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse configuration from markdown
            config_data = {}
            
            # Extract valid graph types
            graph_types_match = re.search(r'Valid Graph Types.*?-\s*\*\*(.*?)\*\*:', content, re.DOTALL)
            if graph_types_match:
                # Extract all graph types from the bullet points
                graph_section = re.findall(r'-\s*\*\*(.*?)\*\*:', content[graph_types_match.start():])
                config_data['valid_graph_types'] = graph_section
            
            # Extract system prompt
            prompt_match = re.search(r'```markdown(.*?)```', content, re.DOTALL)
            if prompt_match:
                config_data['system_prompt'] = prompt_match.group(1).strip()
            
            self.logger.info(f"Loaded agent configuration from {config_file}")
            return config_data
            
        except Exception as e:
            self.logger.error(f"Error loading agent configuration: {e}")
            return {}
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent."""
        self.agent = Agent(
            name=self.agent_name,
            model=self.llm,
            instruction=self.get_system_prompt(),
            tools=self.get_tools()
        )
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for the User Intent Agent."""
        # Use system prompt from configuration file if available
        if hasattr(self, 'agent_config_data') and 'system_prompt' in self.agent_config_data:
            base_prompt = self.agent_config_data['system_prompt']
        else:
            # Fallback to default prompt
            base_prompt = """You are a User Intent Agent specialized in understanding user goals for knowledge graph construction.

Your primary responsibilities:
1. Engage with users to understand what kind of knowledge graph they want to build
2. Help users clarify their specific use cases and requirements
3. Gather information about the purpose and scope of their graph
4. Validate that the user's goals are clear and achievable
5. Save approved user goals for other agents to use

Guidelines:
- Ask clarifying questions to understand the user's domain and objectives
- Help users think through different types of knowledge graphs (domain, semantic, etc.)
- Ensure goals are specific enough for technical implementation
- Be conversational but focused on gathering requirements
- Validate that goals align with available data sources
- Only approve goals that are clear, specific, and technically feasible

Available tools:
- set_perceived_user_goal: Save your understanding of the user's goal
- approve_perceived_user_goal: Mark a goal as approved after user confirmation
- get_perceived_user_goal: Retrieve previously set goals

Always be helpful, ask good questions, and ensure the user's vision is clearly captured."""
        
        # Customize prompt based on configuration
        customizations = []
        
        if hasattr(self, 'conversation_style'):
            if self.conversation_style == 'formal':
                customizations.append("Use a professional and structured communication style.")
            elif self.conversation_style == 'educational':
                customizations.append("Provide educational explanations and teach users about knowledge graphs.")
            elif self.conversation_style == 'efficient':
                customizations.append("Be direct and goal-focused, minimizing conversation length.")
        
        if hasattr(self, 'domain_specialization'):
            if self.domain_specialization == 'business':
                customizations.append("Focus on business processes, KPIs, and commercial applications.")
            elif self.domain_specialization == 'research':
                customizations.append("Emphasize academic and research-oriented knowledge graph applications.")
            elif self.domain_specialization == 'technical':
                customizations.append("Focus on system architecture and technical infrastructure graphs.")
        
        if hasattr(self, 'valid_graph_types'):
            valid_types = ", ".join(self.valid_graph_types)
            customizations.append(f"Valid graph types are: {valid_types}")
        
        if customizations:
            base_prompt += "\n\nAdditional Guidelines:\n" + "\n".join(f"- {c}" for c in customizations)
        
        return base_prompt
    
    def get_tools(self) -> List:
        """Return list of tools available to the User Intent Agent."""
        return [
            self.set_perceived_user_goal,
            self.approve_perceived_user_goal,
            self.get_perceived_user_goal
        ]
    
    def get_required_input_fields(self) -> List[str]:
        """User Intent Agent typically starts conversations, so no required inputs."""
        return []
    
    def set_perceived_user_goal(self, tool_context: ToolContext, goal_description: str, graph_type: str):
        """
        Set the perceived user goal based on conversation analysis.
        
        Args:
            tool_context: ADK tool context
            goal_description: Description of what the user wants to achieve
            graph_type: Type of graph (e.g., "domain", "semantic", "knowledge")
        """
        try:
            # Validate inputs
            if not goal_description or not goal_description.strip():
                return tool_error("Goal description cannot be empty")
            
            if not graph_type or not graph_type.strip():
                return tool_error("Graph type cannot be empty")
            
            # Create goal structure
            user_goal = {
                "description": goal_description.strip(),
                "graph_type": graph_type.strip().lower(),
                "status": "perceived",
                "agent": self.agent_name,
                "session_id": self.session_id
            }
            
            # Save to tool context state
            tool_context.state["perceived_user_goal"] = user_goal
            
            # Update agent state
            self.update_state("perceived_user_goal", user_goal)
            
            self.logger.info(f"User goal set: {graph_type} - {goal_description}")
            
            return tool_success("user_goal", user_goal)
            
        except Exception as e:
            return self.process_error(e, "setting perceived user goal")
    
    def approve_perceived_user_goal(self, tool_context: ToolContext):
        """
        Approve the currently perceived user goal.
        
        Args:
            tool_context: ADK tool context
        """
        try:
            # Check if there's a perceived goal
            if "perceived_user_goal" not in tool_context.state:
                return tool_error("No perceived user goal found. Please set a goal first.")
            
            # Get the perceived goal
            perceived_goal = tool_context.state["perceived_user_goal"]
            
            # Update status to approved
            approved_goal = perceived_goal.copy()
            approved_goal["status"] = "approved"
            approved_goal["approved_by"] = self.agent_name
            
            # Save as approved goal
            tool_context.state["approved_user_goal"] = approved_goal
            
            # Update agent state
            self.update_state("approved_user_goal", approved_goal)
            
            self.logger.info(f"User goal approved: {approved_goal['graph_type']} - {approved_goal['description']}")
            
            return tool_success("approved_user_goal", approved_goal)
            
        except Exception as e:
            return self.process_error(e, "approving user goal")
    
    def get_perceived_user_goal(self, tool_context: ToolContext):
        """
        Retrieve the currently perceived user goal.
        
        Args:
            tool_context: ADK tool context
        """
        try:
            if "perceived_user_goal" not in tool_context.state:
                return tool_error("No perceived user goal found")
            
            goal = tool_context.state["perceived_user_goal"]
            return tool_success("perceived_user_goal", goal)
            
        except Exception as e:
            return self.process_error(e, "retrieving perceived user goal")
    
    def get_approved_user_goal(self, tool_context: ToolContext):
        """
        Retrieve the approved user goal.
        
        Args:
            tool_context: ADK tool context
        """
        try:
            if "approved_user_goal" not in tool_context.state:
                return tool_error("No approved user goal found. Goal must be approved first.")
            
            goal = tool_context.state["approved_user_goal"]
            return tool_success("approved_user_goal", goal)
            
        except Exception as e:
            return self.process_error(e, "retrieving approved user goal")
    
    def validate_goal(self, goal_data: Dict[str, Any]) -> List[str]:
        """
        Validate a user goal for completeness and feasibility.
        
        Args:
            goal_data: Goal data to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        required_fields = ["description", "graph_type"]
        for field in required_fields:
            if field not in goal_data:
                errors.append(f"Missing required field: {field}")
            elif not goal_data[field] or not str(goal_data[field]).strip():
                errors.append(f"Field cannot be empty: {field}")
        
        # Validate graph type using configuration
        if "graph_type" in goal_data:
            graph_type = goal_data["graph_type"].lower()
            if graph_type not in self.valid_graph_types:
                errors.append(f"Invalid graph type: {graph_type}. Must be one of: {self.valid_graph_types}")
        
        # Validate description length based on strictness
        if "description" in goal_data:
            description = goal_data["description"]
            min_length = 10 if self.validation_strictness == 'strict' else 5
            max_length = 1000 if self.validation_strictness != 'permissive' else 2000
            
            if len(description) < min_length:
                errors.append(f"Goal description is too short. Please provide at least {min_length} characters.")
            elif len(description) > max_length:
                errors.append(f"Goal description is too long. Please keep it under {max_length} characters.")
        
        return errors
    
    def suggest_goal_improvements(self, goal_data: Dict[str, Any]) -> List[str]:
        """
        Suggest improvements for a user goal.
        
        Args:
            goal_data: Goal data to analyze
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        if "description" in goal_data:
            description = goal_data["description"].lower()
            
            # Check for specificity
            vague_terms = ["good", "better", "nice", "useful", "helpful"]
            if any(term in description for term in vague_terms):
                suggestions.append("Try to be more specific about what you want to achieve")
            
            # Check for use case
            if "use case" not in description and "purpose" not in description:
                suggestions.append("Consider mentioning the intended use case or purpose")
            
            # Check for domain context
            if "domain" not in description and "business" not in description:
                suggestions.append("Adding domain or business context would be helpful")
        
        return suggestions
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with fallback to default."""
        return getattr(self, key, default)
    
    def update_config(self, config_updates: Dict[str, Any]):
        """Update agent configuration at runtime."""
        for key, value in config_updates.items():
            if key in ['conversation_style', 'domain_specialization', 'validation_strictness']:
                setattr(self, key, value)
                self.logger.info(f"Updated {key} to {value}")
            elif key == 'valid_graph_types' and isinstance(value, list):
                self.valid_graph_types = value
                self.logger.info(f"Updated valid graph types to {value}")
            else:
                self.logger.warning(f"Ignoring unknown configuration key: {key}")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get current agent configuration summary."""
        return {
            'agent_name': self.agent_name,
            'conversation_style': getattr(self, 'conversation_style', 'casual'),
            'domain_specialization': getattr(self, 'domain_specialization', 'general'),
            'validation_strictness': getattr(self, 'validation_strictness', 'moderate'),
            'valid_graph_types': getattr(self, 'valid_graph_types', []),
            'config_file_loaded': hasattr(self, 'agent_config_data'),
            'config_file_path': str(Path(__file__).parent.parent.parent / "config" / "user-intent.md")
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform User Intent Agent health check."""
        base_health = super().health_check()
        
        if base_health["status"] == "healthy":
            # Add agent-specific health checks
            try:
                # Check if tools are properly initialized
                tools = self.get_tools()
                if len(tools) < 3:
                    base_health["status"] = "degraded"
                    base_health["reason"] = "Some tools missing"
                
                # Check state management
                if not hasattr(self, 'state'):
                    base_health["status"] = "unhealthy"
                    base_health["reason"] = "State management not initialized"
                
                # Check configuration loading
                if not hasattr(self, 'valid_graph_types') or not self.valid_graph_types:
                    base_health["status"] = "degraded"
                    base_health["reason"] = "Configuration not properly loaded"
                
                # Add configuration info to health report
                base_health["configuration"] = self.get_configuration_summary()
                
            except Exception as e:
                base_health["status"] = "unhealthy"
                base_health["reason"] = f"Health check failed: {str(e)}"
        
        return base_health
