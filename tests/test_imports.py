#!/usr/bin/env python3
"""
Test script to verify all imports work correctly in the restructured system.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        print("  Testing utils imports...")
        from utils.config_manager import get_config
        from utils.logging_config import setup_logging
        from utils.neo4j_for_adk import graphdb, tool_success, tool_error
        from utils.helper import load_env, get_openai_api_key
        from utils.tools import neo4j_is_ready
        print("  ✅ Utils imports successful")
        
        print("  Testing core imports...")
        from core.agent_base import BaseAgent
        from core.session_manager import SessionManager
        print("  ✅ Core imports successful")
        
        print("  Testing agent imports...")
        from agents.user_intent_agent import UserIntentAgent
        from agents.file_suggestion_agent import FileSuggestionAgent
        from agents.kg_constructor_agent import KnowledgeGraphConstructorAgent
        print("  ✅ Agent imports successful")
        
        print("  Testing main module...")
        import main
        print("  ✅ Main module imports successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Other error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test configuration
        from utils.config_manager import get_config
        config = get_config()
        print("  ✅ Configuration manager working")
        
        # Test Neo4j connection (if available)
        from utils.tools import neo4j_is_ready
        neo4j_result = neo4j_is_ready()
        if neo4j_result['status'] == 'success':
            print("  ✅ Neo4j connection working")
        else:
            print(f"  ⚠️ Neo4j connection: {neo4j_result.get('error_message', 'Not available')}")
        
        # Test agent creation
        from agents.user_intent_agent import UserIntentAgent
        agent = UserIntentAgent()
        health = agent.health_check()
        print(f"  ✅ User Intent Agent: {health['status']}")
        
        print("\n🎉 Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Restructured Agentic Knowledge Graph Construction System")
    print("=" * 70)
    
    import_success = test_imports()
    if import_success:
        functionality_success = test_basic_functionality()
    else:
        functionality_success = False
    
    print("\n" + "=" * 70)
    if import_success and functionality_success:
        print("✅ All tests passed! System is ready for use.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above for details.")
        sys.exit(1)
