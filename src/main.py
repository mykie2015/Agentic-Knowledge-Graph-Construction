"""
Main entry point for the Agentic Knowledge Graph Construction system.
Provides CLI interface and system orchestration.
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Import system components
from utils.config_manager import init_config, get_config
from utils.logging_config import setup_logging, get_system_logger
from utils.neo4j_for_adk import graphdb
from utils.tools import neo4j_is_ready
from utils.helper import make_agent_caller
from core.session_manager import SessionManager
from agents.user_intent_agent import UserIntentAgent
from agents.file_suggestion_agent import FileSuggestionAgent
from agents.schema_proposal_agent import SchemaProposalAgent
from agents.kg_constructor_agent import KnowledgeGraphConstructorAgent


def setup_system(config_file: Optional[str] = None, debug: bool = False) -> bool:
    """
    Initialize the system with configuration and logging.
    
    Args:
        config_file: Path to configuration file
        debug: Enable debug logging
        
    Returns:
        True if setup successful, False otherwise
    """
    try:
        # Initialize configuration
        config = init_config(config_file)
        
        # Setup logging
        log_level = "DEBUG" if debug else config.get('logging.level', 'INFO')
        setup_logging(
            log_dir=config.get('logging.log_dir', './log'),
            level=log_level
        )
        
        logger = get_system_logger('main')
        logger.info("System initialization started")
        
        # Validate configuration
        errors = config.validate_config()
        if errors:
            logger.error(f"Configuration validation failed: {errors}")
            for error in errors:
                print(f"❌ {error}")
            return False
        
        # Test Neo4j connection
        logger.info("Testing Neo4j connection...")
        neo4j_result = neo4j_is_ready()
        if neo4j_result['status'] != 'success':
            logger.error(f"Neo4j connection failed: {neo4j_result}")
            print(f"❌ Neo4j connection failed: {neo4j_result.get('error_message', 'Unknown error')}")
            return False
        
        logger.info("System initialization completed successfully")
        print("✅ System initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return False


async def run_interactive_session():
    """Run an interactive session with the user intent agent."""
    logger = get_system_logger('interactive')
    logger.info("Starting interactive session")
    
    try:
        # Initialize session manager
        session_manager = SessionManager()
        session_id = await session_manager.create_session("interactive_user")
        
        # Create user intent agent
        user_agent = UserIntentAgent()
        user_agent.set_session_context(session_id, "user_intent_task")
        
        # Create agent caller for ADK integration
        agent_caller = await make_agent_caller(user_agent.agent)
        
        print("\n🤖 Welcome to the Agentic Knowledge Graph Construction system!")
        print("I'm here to help you build a knowledge graph. Let's start by understanding your goals.\n")
        
        # Interactive session loop with actual agent
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Thank you for using the system.")
                break
            
            if not user_input:
                continue
            
            try:
                # Use the actual agent caller
                response = await agent_caller.call(user_input, verbose=False)
                
                # Check session state for any approvals or progress
                session = agent_caller.get_session()
                if session.state.get("approved_user_goal"):
                    goal = session.state["approved_user_goal"]
                    print(f"\n✅ Goal approved: {goal['description']} (Type: {goal['graph_type']})")
                    print("🤖 Great! Now let's move to file selection...")
                    # Here we could transition to the next agent
                    
            except Exception as e:
                logger.error(f"Agent interaction error: {e}")
                print(f"🤖 I encountered an error: {e}")
                print("🤖 Let's try again. What would you like to accomplish?")
        
        await session_manager.close_session(session_id)
        logger.info("Interactive session completed")
        
    except Exception as e:
        logger.error(f"Interactive session error: {e}")
        print(f"❌ Session error: {e}")


async def run_batch_processing(input_dir: str, output_dir: str):
    """
    Run batch processing on input data.
    
    Args:
        input_dir: Input data directory
        output_dir: Output results directory
    """
    logger = get_system_logger('batch')
    logger.info(f"Starting batch processing: {input_dir} -> {output_dir}")
    
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize session
        session_manager = SessionManager()
        session_id = await session_manager.create_session("batch_user")
        
        print(f"📂 Processing data from: {input_path}")
        print(f"📁 Results will be saved to: {output_path}")
        
        # List available data files
        csv_files = list(input_path.glob("**/*.csv"))
        md_files = list(input_path.glob("**/*.md"))
        
        print(f"📊 Found {len(csv_files)} CSV files and {len(md_files)} Markdown files")
        
        # Implement basic batch processing workflow
        try:
            # Create agents
            user_agent = UserIntentAgent()
            file_agent = FileSuggestionAgent()
            schema_agent = SchemaProposalAgent()
            constructor_agent = KnowledgeGraphConstructorAgent()
            
            print("\n📋 Starting batch processing workflow...")
            
            # Step 1: Set default goal for batch processing
            print("1. Setting default knowledge graph goal...")
            # This would typically come from user input or config
            default_goal = {
                "description": "Build a comprehensive knowledge graph from the available furniture product data",
                "graph_type": "domain",
                "status": "approved"
            }
            
            # Step 2: Auto-suggest files
            print("2. Analyzing available files...")
            from utils.tools import list_available_files
            files_result = list_available_files(str(input_path))
            if files_result['status'] == 'success':
                available_files = files_result['available_files']
                csv_count = len(available_files['csv_files'])
                md_count = len(available_files['markdown_files'])
                print(f"   Found {csv_count} CSV files and {md_count} Markdown files")
                
                # Auto-select core CSV files for basic domain graph
                selected_files = []
                for csv_file in ['products.csv', 'suppliers.csv', 'parts.csv', 'assemblies.csv']:
                    if csv_file in available_files['csv_files']:
                        selected_files.append(f'csv/{csv_file}')
                
                print(f"   Selected {len(selected_files)} files for processing")
            
            # Step 3: Validate Neo4j connection
            print("3. Validating Neo4j connection...")
            neo4j_result = neo4j_is_ready()
            if neo4j_result['status'] != 'success':
                print(f"❌ Neo4j not ready: {neo4j_result.get('error_message')}")
                return
            
            print("✅ Batch processing setup complete")
            print(f"📊 Would process {len(selected_files)} files to build domain knowledge graph")
            print("🚧 Full automated construction coming in next implementation phase")
            
        except Exception as e:
            logger.error(f"Batch processing setup error: {e}")
            print(f"❌ Batch processing setup failed: {e}")
        
        await session_manager.close_session(session_id)
        logger.info("Batch processing completed")
        
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        print(f"❌ Batch processing failed: {e}")


def show_system_status():
    """Display current system status and health."""
    print("\n🔍 System Status Check")
    print("=" * 50)
    
    try:
        # Configuration status
        config = get_config()
        print("✅ Configuration loaded")
        
        # Neo4j status
        neo4j_result = neo4j_is_ready()
        if neo4j_result['status'] == 'success':
            print("✅ Neo4j connection working")
        else:
            print(f"❌ Neo4j connection failed: {neo4j_result.get('error_message')}")
        
        # Agent status
        agents_to_check = [
            ("User Intent Agent", UserIntentAgent),
            ("File Suggestion Agent", FileSuggestionAgent),
            ("Schema Proposal Agent", SchemaProposalAgent),
            ("KG Constructor Agent", KnowledgeGraphConstructorAgent)
        ]
        
        for agent_name, agent_class in agents_to_check:
            try:
                agent = agent_class()
                health = agent.health_check()
                if health['status'] == 'healthy':
                    print(f"✅ {agent_name} healthy")
                else:
                    print(f"⚠️ {agent_name}: {health.get('reason', 'Unknown issue')}")
            except Exception as e:
                print(f"❌ {agent_name} initialization failed: {e}")
        
        # Data directories
        data_config = config.get_data_config()
        input_dir = Path(data_config.get('input_dir', './data/input'))
        output_dir = Path(data_config.get('output_dir', './data/output'))
        
        if input_dir.exists():
            print(f"✅ Input directory accessible: {input_dir}")
        else:
            print(f"❌ Input directory missing: {input_dir}")
        
        if output_dir.exists():
            print(f"✅ Output directory accessible: {output_dir}")
        else:
            print(f"⚠️ Output directory will be created: {output_dir}")
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
    
    print("=" * 50)


def main():
    """Main entry point with command line interface."""
    parser = argparse.ArgumentParser(
        description="Agentic Knowledge Graph Construction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s interactive                    # Start interactive session
  %(prog)s batch data/input data/output   # Process data in batch mode
  %(prog)s status                         # Show system status
        """
    )
    
    parser.add_argument(
        'command',
        choices=['interactive', 'batch', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'input_dir',
        nargs='?',
        help='Input directory (required for batch mode)'
    )
    
    parser.add_argument(
        'output_dir',
        nargs='?',
        help='Output directory (required for batch mode)'
    )
    
    parser.add_argument(
        '--config',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Validate batch mode arguments
    if args.command == 'batch':
        if not args.input_dir or not args.output_dir:
            parser.error("batch mode requires input_dir and output_dir arguments")
    
    # Initialize system
    if not setup_system(args.config, args.debug):
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'interactive':
            asyncio.run(run_interactive_session())
        elif args.command == 'batch':
            asyncio.run(run_batch_processing(args.input_dir, args.output_dir))
        elif args.command == 'status':
            show_system_status()
    
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
