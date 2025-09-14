"""
Schema Proposal Agent for the Agentic Knowledge Graph Construction system.
Analyzes approved files and user goals to propose knowledge graph schemas.
"""

from typing import Dict, Any, List
from pathlib import Path
import json
from google.adk.agents import Agent
from google.adk.tools import ToolContext

from core.agent_base import BaseAgent, AgentValidationError
from utils.neo4j_for_adk import tool_success, tool_error
from utils.tools import (
    get_approved_user_goal,
    get_approved_files,
    sample_file,
    validate_file_for_import
)


class SchemaProposalAgent(BaseAgent):
    """
    Agent that proposes knowledge graph schemas based on user goals and approved files.
    
    Responsibilities:
    - Analyze approved files to understand data structure
    - Consider user goals to determine relevant entities and relationships
    - Propose comprehensive graph schema with nodes, relationships, and properties
    - Handle both structured (CSV) and unstructured (Markdown) data
    - Create construction plans for the Knowledge Graph Constructor Agent
    - Support iterative schema refinement based on user feedback
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Schema Proposal Agent."""
        super().__init__("schema_proposal", config)
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent."""
        self.agent = Agent(
            name=self.agent_name,
            model=self.llm,
            instruction=self.get_system_prompt(),
            tools=self.get_tools()
        )
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for the Schema Proposal Agent."""
        return """You are a Schema Proposal Agent specialized in designing knowledge graph schemas.

Your primary responsibilities:
1. Analyze the approved user goal to understand what kind of graph they want to build
2. Examine approved files to understand the available data structure
3. Propose a comprehensive graph schema with nodes, relationships, and properties
4. Create construction plans that can be executed by the Knowledge Graph Constructor Agent
5. Handle both structured data (CSV files) and unstructured data (Markdown files)
6. Support iterative refinement based on user feedback

Schema Design Guidelines:
- Start with the user's goal to determine the most important entities and relationships
- Analyze CSV files to identify potential nodes (entities) and their properties
- Look for foreign key relationships in CSV data to propose edges
- For unstructured data, propose named entity recognition and relationship extraction
- Ensure schema supports the user's intended use cases and queries
- Propose constraints for data integrity (uniqueness, required properties)
- Design for scalability and future data additions

Construction Plan Output:
- Node definitions with labels and property schemas
- Relationship definitions with types and direction
- Constraints for data integrity
- Data import order and dependencies
- Validation rules and quality checks

Available tools:
- get_approved_user_goal: Get the user's objectives and requirements
- get_approved_files: Get the validated file list for analysis
- sample_file: Preview file contents to understand structure
- validate_file: Check file format and content quality
- propose_schema: Create schema proposal based on analysis
- save_construction_plan: Save the final construction plan
- get_schema_feedback: Get user feedback on proposed schema

Schema Types:
- Domain schemas: Business entities and their relationships
- Semantic schemas: Meaning and context extraction from text
- Hybrid schemas: Combination of structured and unstructured data

Always explain your schema design decisions and how they support the user's goals."""
    
    def get_tools(self) -> List:
        """Return list of tools available to the Schema Proposal Agent."""
        return [
            self.get_approved_user_goal_tool,
            self.get_approved_files_tool,
            self.sample_file_tool,
            self.validate_file_tool,
            self.analyze_structured_data_tool,
            self.analyze_unstructured_data_tool,
            self.propose_schema_tool,
            self.save_construction_plan_tool,
            self.get_schema_feedback_tool
        ]
    
    def get_required_input_fields(self) -> List[str]:
        """Schema Proposal Agent requires approved goal and files."""
        return ["approved_user_goal", "approved_files"]
    
    def get_approved_user_goal_tool(self, tool_context: ToolContext):
        """Tool wrapper for getting approved user goal."""
        try:
            return get_approved_user_goal(tool_context)
        except Exception as e:
            return self.process_error(e, "getting approved user goal")
    
    def get_approved_files_tool(self, tool_context: ToolContext):
        """Tool wrapper for getting approved files."""
        try:
            return get_approved_files(tool_context)
        except Exception as e:
            return self.process_error(e, "getting approved files")
    
    def sample_file_tool(self, tool_context: ToolContext, filename: str, num_rows: int = 5):
        """Tool wrapper for sampling file content."""
        try:
            return sample_file(tool_context, filename, num_rows)
        except Exception as e:
            return self.process_error(e, f"sampling file {filename}")
    
    def validate_file_tool(self, tool_context: ToolContext, filename: str):
        """Tool wrapper for file validation."""
        try:
            return validate_file_for_import(tool_context, filename)
        except Exception as e:
            return self.process_error(e, f"validating file {filename}")
    
    def analyze_structured_data_tool(self, tool_context: ToolContext, files: List[str]):
        """Analyze structured data files (CSV) to propose schema."""
        try:
            schema_proposal = {
                "analysis_type": "structured",
                "files_analyzed": files,
                "nodes": [],
                "relationships": [],
                "constraints": [],
                "import_order": []
            }
            
            # Analyze each CSV file
            for filename in files:
                if not filename.endswith('.csv'):
                    continue
                
                # Get file sample to understand structure
                sample_result = sample_file(tool_context, filename, 3)
                if sample_result['status'] != 'success':
                    continue
                
                # Extract node information from filename and content
                node_label = self._infer_node_label(filename)
                properties = self._extract_properties_from_sample(sample_result['data'])
                
                node_info = {
                    "label": node_label,
                    "source_file": filename,
                    "properties": properties,
                    "primary_key": self._infer_primary_key(properties)
                }
                schema_proposal["nodes"].append(node_info)
                
                # Infer constraints
                if node_info["primary_key"]:
                    constraint = {
                        "type": "uniqueness",
                        "label": node_label,
                        "property": node_info["primary_key"]
                    }
                    schema_proposal["constraints"].append(constraint)
            
            # Analyze relationships between files
            relationships = self._infer_relationships(schema_proposal["nodes"])
            schema_proposal["relationships"] = relationships
            
            # Determine import order based on dependencies
            import_order = self._calculate_import_order(schema_proposal["nodes"], relationships)
            schema_proposal["import_order"] = import_order
            
            # Store in tool context for later use
            tool_context.state["structured_schema_proposal"] = schema_proposal
            
            return tool_success("structured_data_analysis", schema_proposal)
            
        except Exception as e:
            return self.process_error(e, "analyzing structured data")
    
    def analyze_unstructured_data_tool(self, tool_context: ToolContext, files: List[str]):
        """Analyze unstructured data files (Markdown) to propose entity extraction."""
        try:
            analysis = {
                "analysis_type": "unstructured",
                "files_analyzed": files,
                "named_entities": [],
                "relationships": [],
                "extraction_rules": []
            }
            
            # Analyze each Markdown file
            for filename in files:
                if not filename.endswith('.md'):
                    continue
                
                # Get file sample to understand content
                sample_result = sample_file(tool_context, filename, 10)
                if sample_result['status'] != 'success':
                    continue
                
                # Analyze content for entities and relationships
                content_analysis = self._analyze_text_content(sample_result['data'], filename)
                
                analysis["named_entities"].extend(content_analysis["entities"])
                analysis["relationships"].extend(content_analysis["relationships"])
                analysis["extraction_rules"].extend(content_analysis["rules"])
            
            # Store in tool context
            tool_context.state["unstructured_analysis"] = analysis
            
            return tool_success("unstructured_data_analysis", analysis)
            
        except Exception as e:
            return self.process_error(e, "analyzing unstructured data")
    
    def propose_schema_tool(self, tool_context: ToolContext):
        """Create comprehensive schema proposal combining structured and unstructured analysis."""
        try:
            user_goal = tool_context.state.get("approved_user_goal", {})
            structured_analysis = tool_context.state.get("structured_schema_proposal", {})
            unstructured_analysis = tool_context.state.get("unstructured_analysis", {})
            
            # Create unified schema proposal
            schema_proposal = {
                "user_goal": user_goal,
                "schema_type": self._determine_schema_type(user_goal),
                "nodes": structured_analysis.get("nodes", []),
                "relationships": structured_analysis.get("relationships", []),
                "constraints": structured_analysis.get("constraints", []),
                "import_order": structured_analysis.get("import_order", []),
                "entity_extraction": {
                    "named_entities": unstructured_analysis.get("named_entities", []),
                    "text_relationships": unstructured_analysis.get("relationships", []),
                    "extraction_rules": unstructured_analysis.get("extraction_rules", [])
                },
                "reasoning": self._generate_schema_reasoning(user_goal, structured_analysis, unstructured_analysis)
            }
            
            # Store proposed schema
            tool_context.state["proposed_schema"] = schema_proposal
            
            return tool_success("schema_proposal", schema_proposal)
            
        except Exception as e:
            return self.process_error(e, "proposing schema")
    
    def save_construction_plan_tool(self, tool_context: ToolContext, approved: bool = False):
        """Save the construction plan to data/output directory."""
        try:
            if not approved:
                return tool_error("Schema must be approved before saving construction plan")
            
            proposed_schema = tool_context.state.get("proposed_schema")
            if not proposed_schema:
                return tool_error("No schema proposal found to save")
            
            # Create construction plan
            construction_plan = {
                "metadata": {
                    "created_by": "schema_proposal_agent",
                    "user_goal": proposed_schema["user_goal"],
                    "schema_type": proposed_schema["schema_type"],
                    "timestamp": self._get_timestamp()
                },
                "database_setup": {
                    "constraints": proposed_schema["constraints"],
                    "indexes": self._suggest_indexes(proposed_schema)
                },
                "data_import": {
                    "import_order": proposed_schema["import_order"],
                    "node_imports": self._create_import_instructions(proposed_schema["nodes"]),
                    "relationship_imports": self._create_relationship_instructions(proposed_schema["relationships"])
                },
                "entity_extraction": proposed_schema.get("entity_extraction", {}),
                "validation": {
                    "quality_checks": self._create_quality_checks(proposed_schema),
                    "completeness_checks": self._create_completeness_checks(proposed_schema)
                }
            }
            
            # Save to data/output directory
            output_dir = Path("data/output")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / "construction_plan.json"
            with open(output_file, 'w') as f:
                json.dump(construction_plan, f, indent=2)
            
            # Also save to tool context
            tool_context.state["approved_construction_plan"] = construction_plan
            
            # Log the save operation
            self.logger.info(f"Construction plan saved to {output_file}")
            
            return tool_success("construction_plan_saved", {
                "file_path": str(output_file),
                "plan": construction_plan
            })
            
        except Exception as e:
            return self.process_error(e, "saving construction plan")
    
    def get_schema_feedback_tool(self, tool_context: ToolContext):
        """Get user feedback on the proposed schema."""
        try:
            proposed_schema = tool_context.state.get("proposed_schema")
            if not proposed_schema:
                return tool_error("No schema proposal found")
            
            # This would typically interact with the user interface
            # For now, we'll return the schema for review
            feedback_request = {
                "schema_summary": self._create_schema_summary(proposed_schema),
                "key_decisions": proposed_schema.get("reasoning", {}),
                "review_points": [
                    "Are the proposed node types appropriate for your use case?",
                    "Do the relationships capture the connections you need?",
                    "Are there missing entities or relationships?",
                    "Do the property schemas make sense for your data?",
                    "Is the import order logical and efficient?"
                ]
            }
            
            return tool_success("schema_feedback_request", feedback_request)
            
        except Exception as e:
            return self.process_error(e, "requesting schema feedback")
    
    def _infer_node_label(self, filename: str) -> str:
        """Infer node label from filename."""
        # Remove extension and convert to title case
        name = Path(filename).stem
        # Handle common patterns
        if name.endswith('_mapping'):
            return name.replace('_mapping', '').title() + 'Mapping'
        return name.replace('_', '').title()
    
    def _extract_properties_from_sample(self, sample_data: Dict) -> List[Dict]:
        """Extract property schema from sample data."""
        if not sample_data or 'headers' not in sample_data:
            return []
        
        properties = []
        for header in sample_data['headers']:
            prop_info = {
                "name": header,
                "type": "string",  # Default type, could be improved with type inference
                "required": header.lower() in ['id', 'name', 'title'],
                "description": f"Property {header} extracted from data"
            }
            properties.append(prop_info)
        
        return properties
    
    def _infer_primary_key(self, properties: List[Dict]) -> str:
        """Infer the primary key property."""
        for prop in properties:
            if prop['name'].lower() in ['id', 'uuid', 'key']:
                return prop['name']
        return None
    
    def _infer_relationships(self, nodes: List[Dict]) -> List[Dict]:
        """Infer relationships between nodes based on foreign key patterns."""
        relationships = []
        
        for node in nodes:
            for prop in node.get('properties', []):
                prop_name = prop['name'].lower()
                
                # Look for foreign key patterns
                for other_node in nodes:
                    if node == other_node:
                        continue
                    
                    other_label = other_node['label'].lower()
                    
                    # Check if property name suggests relationship
                    if prop_name == f"{other_label}_id" or prop_name == f"{other_label}id":
                        relationship = {
                            "type": f"BELONGS_TO_{other_node['label'].upper()}",
                            "from_label": node['label'],
                            "to_label": other_node['label'],
                            "property": prop['name'],
                            "description": f"{node['label']} belongs to {other_node['label']}"
                        }
                        relationships.append(relationship)
        
        return relationships
    
    def _calculate_import_order(self, nodes: List[Dict], relationships: List[Dict]) -> List[str]:
        """Calculate optimal import order based on dependencies."""
        # Simple dependency resolution - nodes without foreign keys first
        independent_nodes = []
        dependent_nodes = []
        
        for node in nodes:
            has_foreign_key = any(
                rel['from_label'] == node['label'] for rel in relationships
            )
            
            if has_foreign_key:
                dependent_nodes.append(node['source_file'])
            else:
                independent_nodes.append(node['source_file'])
        
        return independent_nodes + dependent_nodes
    
    def _analyze_text_content(self, sample_data: Dict, filename: str) -> Dict:
        """Analyze text content for entities and relationships."""
        # This is a simplified analysis - in practice would use NLP libraries
        content = sample_data.get('content', '')
        
        analysis = {
            "entities": [
                {
                    "type": "Review",
                    "description": "Customer review entity",
                    "source_file": filename,
                    "extraction_pattern": "Review content structure"
                },
                {
                    "type": "Reviewer",
                    "description": "Person who wrote the review",
                    "source_file": filename,
                    "extraction_pattern": "Author identification"
                }
            ],
            "relationships": [
                {
                    "type": "REVIEWED_BY",
                    "from_entity": "Review",
                    "to_entity": "Reviewer",
                    "description": "Review was written by reviewer"
                }
            ],
            "rules": [
                {
                    "rule_type": "entity_extraction",
                    "pattern": "Extract review metadata and content",
                    "target_file": filename
                }
            ]
        }
        
        return analysis
    
    def _determine_schema_type(self, user_goal: Dict) -> str:
        """Determine schema type based on user goal."""
        goal_type = user_goal.get('graph_type', 'domain').lower()
        
        type_mapping = {
            'domain': 'domain_schema',
            'semantic': 'semantic_schema',
            'knowledge': 'hybrid_schema',
            'lexical': 'lexical_schema',
            'subject': 'subject_schema'
        }
        
        return type_mapping.get(goal_type, 'hybrid_schema')
    
    def _generate_schema_reasoning(self, user_goal: Dict, structured: Dict, unstructured: Dict) -> Dict:
        """Generate reasoning for schema design decisions."""
        return {
            "goal_alignment": f"Schema designed to support {user_goal.get('description', 'user objectives')}",
            "data_coverage": f"Covers {len(structured.get('nodes', []))} structured entities and {len(unstructured.get('named_entities', []))} unstructured entities",
            "relationship_strategy": "Relationships inferred from foreign key patterns and text analysis",
            "scalability": "Schema designed for extensibility and future data additions"
        }
    
    def _suggest_indexes(self, schema: Dict) -> List[Dict]:
        """Suggest database indexes for performance."""
        indexes = []
        
        for node in schema.get('nodes', []):
            # Index on primary key
            if node.get('primary_key'):
                indexes.append({
                    "type": "btree",
                    "label": node['label'],
                    "property": node['primary_key'],
                    "reason": "Primary key lookup performance"
                })
        
        return indexes
    
    def _create_import_instructions(self, nodes: List[Dict]) -> List[Dict]:
        """Create detailed import instructions for nodes."""
        instructions = []
        
        for node in nodes:
            instruction = {
                "source_file": node['source_file'],
                "target_label": node['label'],
                "property_mapping": {prop['name']: prop['name'] for prop in node.get('properties', [])},
                "transformations": [],
                "validation_rules": []
            }
            instructions.append(instruction)
        
        return instructions
    
    def _create_relationship_instructions(self, relationships: List[Dict]) -> List[Dict]:
        """Create detailed relationship import instructions."""
        instructions = []
        
        for rel in relationships:
            instruction = {
                "relationship_type": rel['type'],
                "from_label": rel['from_label'],
                "to_label": rel['to_label'],
                "match_property": rel.get('property'),
                "cypher_template": f"MATCH (a:{rel['from_label']}), (b:{rel['to_label']}) WHERE a.{rel.get('property', 'id')} = b.id CREATE (a)-[:{rel['type']}]->(b)"
            }
            instructions.append(instruction)
        
        return instructions
    
    def _create_quality_checks(self, schema: Dict) -> List[Dict]:
        """Create data quality validation checks."""
        checks = []
        
        for node in schema.get('nodes', []):
            check = {
                "check_type": "node_completeness",
                "label": node['label'],
                "required_properties": [prop['name'] for prop in node.get('properties', []) if prop.get('required', False)],
                "validation_query": f"MATCH (n:{node['label']}) WHERE n.{node.get('primary_key', 'id')} IS NULL RETURN count(n) as incomplete_nodes"
            }
            checks.append(check)
        
        return checks
    
    def _create_completeness_checks(self, schema: Dict) -> List[Dict]:
        """Create completeness validation checks."""
        checks = []
        
        for relationship in schema.get('relationships', []):
            check = {
                "check_type": "relationship_completeness",
                "relationship_type": relationship['type'],
                "validation_query": f"MATCH (a:{relationship['from_label']}) WHERE NOT (a)-[:{relationship['type']}]->() RETURN count(a) as unconnected_nodes"
            }
            checks.append(check)
        
        return checks
    
    def _create_schema_summary(self, schema: Dict) -> Dict:
        """Create a human-readable schema summary."""
        return {
            "total_nodes": len(schema.get('nodes', [])),
            "total_relationships": len(schema.get('relationships', [])),
            "node_types": [node['label'] for node in schema.get('nodes', [])],
            "relationship_types": [rel['type'] for rel in schema.get('relationships', [])],
            "data_sources": list(set(node['source_file'] for node in schema.get('nodes', [])))
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check for the Schema Proposal Agent."""
        base_health = super().health_check()
        
        if base_health["status"] == "healthy":
            try:
                # Check if output directory is writable
                output_dir = Path("data/output")
                if not output_dir.exists() or not output_dir.is_dir():
                    base_health["status"] = "degraded"
                    base_health["reason"] = "Output directory not accessible"
                
                # Check available tools
                tools = self.get_tools()
                if len(tools) < 8:
                    base_health["status"] = "degraded"
                    base_health["reason"] = "Some tools missing"
                
            except Exception as e:
                base_health["status"] = "unhealthy"
                base_health["reason"] = f"Health check failed: {str(e)}"
        
        return base_health
