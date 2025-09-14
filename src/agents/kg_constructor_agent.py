"""
Knowledge Graph Constructor Agent for the Agentic Knowledge Graph Construction system.
Builds knowledge graphs from approved files and construction plans.
"""

from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import ToolContext
import json

from core.agent_base import BaseAgent, AgentValidationError
from utils.neo4j_for_adk import tool_success, tool_error, graphdb
from utils.tools import (
    get_approved_user_goal,
    get_approved_files,
    create_uniqueness_constraint,
    load_nodes_from_csv,
    clear_neo4j_data,
    neo4j_is_ready
)


class KnowledgeGraphConstructorAgent(BaseAgent):
    """
    Agent that constructs knowledge graphs from approved data files.
    
    Responsibilities:
    - Validate system readiness for graph construction
    - Create database constraints for data integrity
    - Import nodes from CSV files
    - Create relationships between nodes
    - Verify constructed graph quality
    - Report construction statistics and results
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Knowledge Graph Constructor Agent."""
        super().__init__("kg_constructor", config)
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent."""
        self.agent = Agent(
            name=self.agent_name,
            model=self.llm,
            instruction=self.get_system_prompt(),
            tools=self.get_tools()
        )
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for the Knowledge Graph Constructor Agent."""
        return """You are a Knowledge Graph Constructor Agent specialized in building Neo4j knowledge graphs.

Your primary responsibilities:
1. Validate that the system is ready for graph construction
2. Check that Neo4j database is accessible and properly configured
3. Create database constraints to ensure data integrity
4. Import nodes from approved CSV files using proper schemas
5. Create relationships between nodes based on data relationships
6. Verify the constructed graph for completeness and quality
7. Provide detailed statistics and reports on the construction process

Guidelines:
- Always verify system readiness before starting construction
- Use the approved user goal and files to guide construction
- Create constraints before importing data to prevent duplicates
- Import data in logical order (foundational entities first)
- Create relationships after all nodes are imported
- Validate graph structure and report any issues
- Provide clear progress updates during construction
- Generate comprehensive construction reports

Available tools:
- get_approved_user_goal: Get the user's objectives
- get_approved_files: Get the validated file list
- check_neo4j_ready: Verify database connectivity
- clear_database: Reset database if needed (with confirmation)
- create_constraint: Create uniqueness constraints
- import_csv_nodes: Import nodes from CSV files
- create_relationships: Build relationships between nodes
- verify_graph: Check graph completeness and quality
- get_construction_stats: Generate construction statistics

Construction process:
1. Validate prerequisites (goal, files, database)
2. Optionally clear existing data (with user confirmation)
3. Create constraints for data integrity
4. Import nodes in dependency order
5. Create relationships between imported nodes
6. Verify and validate the constructed graph
7. Generate final construction report

Always be thorough, provide clear status updates, and ensure data quality."""
    
    def get_tools(self) -> List:
        """Return list of tools available to the Knowledge Graph Constructor Agent."""
        return [
            self.get_approved_user_goal_tool,
            self.get_approved_files_tool,
            self.check_neo4j_ready_tool,
            self.clear_database_tool,
            self.create_constraint_tool,
            self.import_csv_nodes_tool,
            self.create_relationships_tool,
            self.verify_graph_tool,
            self.get_construction_stats_tool
        ]
    
    def get_required_input_fields(self) -> List[str]:
        """Constructor Agent requires approved goal and files."""
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
    
    def check_neo4j_ready_tool(self, tool_context: ToolContext):
        """Tool wrapper for checking Neo4j readiness."""
        try:
            result = neo4j_is_ready()
            
            # Store readiness status
            tool_context.state["neo4j_ready"] = result['status'] == 'success'
            
            return result
        except Exception as e:
            return self.process_error(e, "checking Neo4j readiness")
    
    def clear_database_tool(self, tool_context: ToolContext, confirm: bool = False):
        """Tool wrapper for clearing database."""
        try:
            if not confirm:
                return tool_error("Database clear requires explicit confirmation. This will delete all existing data!")
            
            result = clear_neo4j_data()
            
            if result['status'] == 'success':
                tool_context.state["database_cleared"] = True
                self.logger.warning("Database cleared by user request")
            
            return result
        except Exception as e:
            return self.process_error(e, "clearing database")
    
    def create_constraint_tool(self, tool_context: ToolContext, label: str, property_key: str):
        """Tool wrapper for creating constraints."""
        try:
            result = create_uniqueness_constraint(label, property_key)
            
            # Track created constraints
            if result['status'] == 'success':
                if "constraints_created" not in tool_context.state:
                    tool_context.state["constraints_created"] = []
                tool_context.state["constraints_created"].append(f"{label}.{property_key}")
                self.logger.info(f"Created constraint for {label}.{property_key}")
            
            return result
        except Exception as e:
            return self.process_error(e, f"creating constraint for {label}.{property_key}")
    
    def import_csv_nodes_tool(self, tool_context: ToolContext, csv_file: str, label: str, 
                             unique_property: str, properties: List[str]):
        """Tool wrapper for importing CSV nodes."""
        try:
            # Create constraint first
            constraint_result = create_uniqueness_constraint(label, unique_property)
            if constraint_result['status'] != 'success':
                self.logger.warning(f"Constraint creation failed for {label}, continuing: {constraint_result}")
            
            # Import the nodes
            result = load_nodes_from_csv(csv_file, label, unique_property, properties)
            
            # Track imported nodes
            if result['status'] == 'success':
                if "nodes_imported" not in tool_context.state:
                    tool_context.state["nodes_imported"] = {}
                tool_context.state["nodes_imported"][label] = {
                    'file': csv_file,
                    'properties': properties,
                    'unique_property': unique_property
                }
                self.logger.info(f"Imported {label} nodes from {csv_file}")
            
            return result
        except Exception as e:
            return self.process_error(e, f"importing {label} nodes from {csv_file}")
    
    def create_relationships_tool(self, tool_context: ToolContext, relationship_configs: List[Dict[str, str]]):
        """Tool wrapper for creating relationships."""
        try:
            results = []
            relationships_created = {}
            
            for config in relationship_configs:
                from_label = config['from_label']
                to_label = config['to_label']
                relationship_type = config['relationship_type']
                match_property = config['match_property']
                
                # Create the relationship using Cypher
                query = f"""
                MATCH (from:`{from_label}`), (to:`{to_label}`)
                WHERE from.{match_property} = to.{match_property}
                MERGE (from)-[r:`{relationship_type}`]->(to)
                SET r.created_at = datetime()
                RETURN count(r) as relationships_created
                """
                
                result = graphdb.send_query(query)
                
                if result['status'] == 'success':
                    count = result['query_result'][0]['relationships_created'] if result['query_result'] else 0
                    relationships_created[relationship_type] = count
                    results.append({
                        'relationship': relationship_type,
                        'from': from_label,
                        'to': to_label,
                        'count': count,
                        'status': 'success'
                    })
                    self.logger.info(f"Created {count} {relationship_type} relationships")
                else:
                    results.append({
                        'relationship': relationship_type,
                        'status': 'error',
                        'error': result.get('error_message', 'Unknown error')
                    })
            
            # Store relationship creation results
            tool_context.state["relationships_created"] = relationships_created
            
            return tool_success("relationship_results", results)
            
        except Exception as e:
            return self.process_error(e, "creating relationships")
    
    def verify_graph_tool(self, tool_context: ToolContext):
        """Tool wrapper for verifying constructed graph."""
        try:
            verification_results = {}
            
            # Get node counts
            node_query = """
            MATCH (n) 
            RETURN labels(n)[0] as label, count(n) as count 
            ORDER BY count DESC
            """
            node_result = graphdb.send_query(node_query)
            
            if node_result['status'] == 'success':
                verification_results['nodes'] = node_result['query_result']
                total_nodes = sum(item['count'] for item in node_result['query_result'])
                verification_results['total_nodes'] = total_nodes
            else:
                verification_results['nodes'] = []
                verification_results['total_nodes'] = 0
            
            # Get relationship counts
            rel_query = """
            MATCH ()-[r]->() 
            RETURN type(r) as type, count(r) as count 
            ORDER BY count DESC
            """
            rel_result = graphdb.send_query(rel_query)
            
            if rel_result['status'] == 'success':
                verification_results['relationships'] = rel_result['query_result']
                total_rels = sum(item['count'] for item in rel_result['query_result'])
                verification_results['total_relationships'] = total_rels
            else:
                verification_results['relationships'] = []
                verification_results['total_relationships'] = 0
            
            # Check for connected components
            connected_query = """
            MATCH path = (a)-[*1..3]-(b)
            WHERE labels(a) <> labels(b)
            RETURN labels(a)[0] as from_label, labels(b)[0] as to_label, length(path) as path_length
            LIMIT 10
            """
            connected_result = graphdb.send_query(connected_query)
            
            if connected_result['status'] == 'success':
                verification_results['connected_paths'] = connected_result['query_result']
            else:
                verification_results['connected_paths'] = []
            
            # Determine graph health
            health_score = 0
            issues = []
            
            if verification_results['total_nodes'] > 0:
                health_score += 40
            else:
                issues.append("No nodes found in graph")
            
            if verification_results['total_relationships'] > 0:
                health_score += 40
            else:
                issues.append("No relationships found in graph")
            
            if len(verification_results['connected_paths']) > 0:
                health_score += 20
            else:
                issues.append("No connected paths found")
            
            verification_results['health_score'] = health_score
            verification_results['issues'] = issues
            verification_results['status'] = 'healthy' if health_score >= 80 else 'degraded' if health_score >= 40 else 'unhealthy'
            
            # Store verification results
            tool_context.state["graph_verification"] = verification_results
            
            return tool_success("verification_results", verification_results)
            
        except Exception as e:
            return self.process_error(e, "verifying graph")
    
    def get_construction_stats_tool(self, tool_context: ToolContext):
        """Tool wrapper for getting construction statistics."""
        try:
            stats = {
                'constraints_created': tool_context.state.get("constraints_created", []),
                'nodes_imported': tool_context.state.get("nodes_imported", {}),
                'relationships_created': tool_context.state.get("relationships_created", {}),
                'database_cleared': tool_context.state.get("database_cleared", False),
                'neo4j_ready': tool_context.state.get("neo4j_ready", False),
                'graph_verification': tool_context.state.get("graph_verification", {})
            }
            
            # Calculate totals
            total_node_types = len(stats['nodes_imported'])
            total_relationship_types = len(stats['relationships_created'])
            total_relationships = sum(stats['relationships_created'].values())
            
            summary = {
                'construction_successful': stats['neo4j_ready'] and total_node_types > 0,
                'total_node_types': total_node_types,
                'total_relationship_types': total_relationship_types,
                'total_relationships': total_relationships,
                'graph_health': stats['graph_verification'].get('status', 'unknown'),
                'detailed_stats': stats
            }
            
            return tool_success("construction_stats", summary)
            
        except Exception as e:
            return self.process_error(e, "getting construction statistics")
    
    def get_default_construction_plan(self) -> List[Dict[str, Any]]:
        """Get default construction plan for the furniture domain."""
        return [
            {
                'label': 'Product',
                'csv_file': 'products.csv',
                'unique_property': 'product_id',
                'properties': ['product_name', 'price', 'description']
            },
            {
                'label': 'Supplier',
                'csv_file': 'suppliers.csv',
                'unique_property': 'supplier_id',
                'properties': ['name', 'specialty', 'city', 'country', 'website', 'contact_email']
            },
            {
                'label': 'Part',
                'csv_file': 'parts.csv',
                'unique_property': 'part_id',
                'properties': ['part_name', 'quantity', 'assembly_id']
            },
            {
                'label': 'Assembly',
                'csv_file': 'assemblies.csv',
                'unique_property': 'assembly_id',
                'properties': ['assembly_name', 'quantity', 'product_id']
            }
        ]
    
    def get_default_relationship_configs(self) -> List[Dict[str, str]]:
        """Get default relationship configurations."""
        return [
            {
                'from_label': 'Product',
                'to_label': 'Assembly',
                'relationship_type': 'CONTAINS',
                'match_property': 'product_id'
            },
            {
                'from_label': 'Assembly',
                'to_label': 'Part',
                'relationship_type': 'IS_PART_OF',
                'match_property': 'assembly_id'
            },
            {
                'from_label': 'Part',
                'to_label': 'Supplier',
                'relationship_type': 'SUPPLIED_BY',
                'match_property': 'supplier_id'  # This would need mapping data
            }
        ]
    
    def health_check(self) -> Dict[str, Any]:
        """Perform Knowledge Graph Constructor Agent health check."""
        base_health = super().health_check()
        
        if base_health["status"] == "healthy":
            try:
                # Check Neo4j connectivity
                neo4j_result = neo4j_is_ready()
                if neo4j_result['status'] != 'success':
                    base_health["status"] = "unhealthy"
                    base_health["reason"] = "Neo4j database not accessible"
                
                # Check available tools
                tools = self.get_tools()
                if len(tools) < 9:
                    base_health["status"] = "degraded"
                    base_health["reason"] = "Some tools missing"
                
            except Exception as e:
                base_health["status"] = "unhealthy"
                base_health["reason"] = f"Health check failed: {str(e)}"
        
        return base_health
