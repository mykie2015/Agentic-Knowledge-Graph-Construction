"""
File Suggestion Agent for the Agentic Knowledge Graph Construction system.
Analyzes user goals and recommends relevant data files for processing.
"""

from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import ToolContext

from core.agent_base import BaseAgent, AgentValidationError
from utils.neo4j_for_adk import tool_success, tool_error
from utils.tools import (
    get_approved_user_goal, 
    list_available_files, 
    suggest_files_for_goal,
    validate_file_for_import,
    approve_file_selection,
    sample_file
)


class FileSuggestionAgent(BaseAgent):
    """
    Agent that suggests and validates data files for knowledge graph construction.
    
    Responsibilities:
    - Analyze available data files
    - Suggest files based on user goals
    - Validate file formats and content
    - Help users select appropriate files
    - Approve final file selection
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the File Suggestion Agent."""
        super().__init__("file_suggestion", config)
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent."""
        self.agent = Agent(
            name=self.agent_name,
            model=self.llm,
            instruction=self.get_system_prompt(),
            tools=self.get_tools()
        )
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for the File Suggestion Agent."""
        return """You are a File Suggestion Agent specialized in analyzing data files for knowledge graph construction.

Your primary responsibilities:
1. Understand the user's approved goals for their knowledge graph
2. Analyze available data files in the system
3. Suggest relevant files based on the user's objectives
4. Validate file formats and content quality
5. Help users understand what each file contains
6. Guide users through file selection process
7. Approve the final file selection for processing

Guidelines:
- Always start by checking the approved user goal to understand requirements
- List available files and analyze their content
- Suggest files that align with the user's graph type and objectives
- Provide clear reasoning for your suggestions
- Sample files to show users what data they contain
- Validate file quality and warn about potential issues
- Only approve files that are valid and relevant to the goals
- Be helpful in explaining file relationships and dependencies

Available tools:
- get_approved_user_goal: Get the user's approved goals
- list_available_files: See all available data files
- suggest_files_for_goal: Get AI-powered file suggestions
- sample_file: Show file content previews
- validate_file_for_import: Check file validity
- approve_file_selection: Finalize file selection

File types you'll work with:
- CSV files: Structured data (products, suppliers, parts, assemblies)
- Markdown files: Unstructured data (reviews, descriptions)
- Other formats: Configuration files, schemas

Always explain your reasoning and help users make informed decisions about their data."""
    
    def get_tools(self) -> List:
        """Return list of tools available to the File Suggestion Agent."""
        return [
            self.get_approved_user_goal_tool,
            self.list_available_files_tool,
            self.suggest_files_for_goal_tool,
            self.sample_file_tool,
            self.validate_file_for_import_tool,
            self.approve_file_selection_tool
        ]
    
    def get_required_input_fields(self) -> List[str]:
        """File Suggestion Agent requires an approved user goal."""
        return ["approved_user_goal"]
    
    def get_approved_user_goal_tool(self, tool_context: ToolContext):
        """Tool wrapper for getting approved user goal."""
        try:
            return get_approved_user_goal(tool_context)
        except Exception as e:
            return self.process_error(e, "getting approved user goal")
    
    def list_available_files_tool(self, tool_context: ToolContext):
        """Tool wrapper for listing available files."""
        try:
            result = list_available_files()
            
            # Store the file list in context for reference
            if result['status'] == 'success':
                tool_context.state["available_files"] = result['available_files']
            
            return result
        except Exception as e:
            return self.process_error(e, "listing available files")
    
    def suggest_files_for_goal_tool(self, tool_context: ToolContext):
        """Tool wrapper for suggesting files based on goals."""
        try:
            # Get the approved goal first
            goal_result = get_approved_user_goal(tool_context)
            if goal_result['status'] != 'success':
                return goal_result
            
            goal_data = goal_result['approved_user_goal']
            
            # Generate suggestions
            suggestions = suggest_files_for_goal(
                goal_data['description'], 
                goal_data['graph_type']
            )
            
            # Store suggestions in context
            if suggestions['status'] == 'success':
                tool_context.state["file_suggestions"] = suggestions['file_suggestions']
            
            return suggestions
        except Exception as e:
            return self.process_error(e, "suggesting files for goal")
    
    def sample_file_tool(self, tool_context: ToolContext, file_path: str):
        """Tool wrapper for sampling file content."""
        try:
            result = sample_file(file_path)
            
            # Store sample in context for reference
            if result['status'] == 'success':
                if "sampled_files" not in tool_context.state:
                    tool_context.state["sampled_files"] = {}
                tool_context.state["sampled_files"][file_path] = result['content']
            
            return result
        except Exception as e:
            return self.process_error(e, f"sampling file {file_path}")
    
    def validate_file_for_import_tool(self, tool_context: ToolContext, file_path: str, file_type: str = "auto"):
        """Tool wrapper for validating files."""
        try:
            result = validate_file_for_import(file_path, file_type)
            
            # Store validation results
            if result['status'] == 'success':
                if "file_validations" not in tool_context.state:
                    tool_context.state["file_validations"] = {}
                tool_context.state["file_validations"][file_path] = result['validation_result']
            
            return result
        except Exception as e:
            return self.process_error(e, f"validating file {file_path}")
    
    def approve_file_selection_tool(self, tool_context: ToolContext, selected_files: List[str]):
        """Tool wrapper for approving file selection."""
        try:
            # Validate the selection
            if not selected_files:
                return tool_error("No files selected. Please select at least one file.")
            
            # Check that files were previously validated or validate them now
            for file_path in selected_files:
                if "file_validations" not in tool_context.state or file_path not in tool_context.state["file_validations"]:
                    # Validate the file now
                    validation_result = validate_file_for_import(file_path)
                    if validation_result['status'] != 'success':
                        return validation_result
                    
                    validation_data = validation_result['validation_result']
                    if not validation_data['valid']:
                        return tool_error(f"File {file_path} failed validation: {validation_data['errors']}")
            
            # Approve the selection
            result = approve_file_selection(tool_context, selected_files)
            
            if result['status'] == 'success':
                self.logger.info(f"Approved file selection: {selected_files}")
                self.update_state("approved_files", result['approved_files'])
            
            return result
        except Exception as e:
            return self.process_error(e, "approving file selection")
    
    def analyze_file_relationships(self, files: List[str]) -> Dict[str, Any]:
        """Analyze relationships between selected files."""
        relationships = {
            'connected_files': [],
            'standalone_files': [],
            'potential_joins': [],
            'recommendations': []
        }
        
        # Simple relationship analysis based on file names and common patterns
        csv_files = [f for f in files if f.endswith('.csv')]
        
        # Look for common ID patterns
        id_patterns = {}
        for file in csv_files:
            if 'product' in file.lower():
                id_patterns[file] = 'product_id'
            elif 'supplier' in file.lower():
                id_patterns[file] = 'supplier_id'
            elif 'part' in file.lower():
                id_patterns[file] = ['part_id', 'assembly_id']
            elif 'assembly' in file.lower():
                id_patterns[file] = ['assembly_id', 'product_id']
        
        # Identify potential relationships
        if len(csv_files) > 1:
            relationships['recommendations'].append("Consider how these CSV files might connect through common ID fields")
            relationships['potential_joins'] = list(id_patterns.items())
        
        return relationships
    
    def health_check(self) -> Dict[str, Any]:
        """Perform File Suggestion Agent health check."""
        base_health = super().health_check()
        
        if base_health["status"] == "healthy":
            try:
                # Check if we can access file system
                from pathlib import Path
                data_dir = self.config_manager.get('data.input_dir', './data/input')
                if not Path(data_dir).exists():
                    base_health["status"] = "degraded"
                    base_health["reason"] = f"Input directory not accessible: {data_dir}"
                
                # Check available tools
                tools = self.get_tools()
                if len(tools) < 6:
                    base_health["status"] = "degraded"
                    base_health["reason"] = "Some tools missing"
                
            except Exception as e:
                base_health["status"] = "unhealthy"
                base_health["reason"] = f"Health check failed: {str(e)}"
        
        return base_health
