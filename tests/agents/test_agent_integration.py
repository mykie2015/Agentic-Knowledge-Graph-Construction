#!/usr/bin/env python3
"""
Integration test for all agent implementations.
Tests agent initialization, health checks, and basic functionality.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
test_dir = Path(__file__).parent.parent  # tests directory
project_root = test_dir.parent  # project root
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def test_agent_imports():
    """Test that all agents can be imported successfully."""
    print("🧪 Testing agent imports...")
    
    try:
        from agents.user_intent_agent import UserIntentAgent
        print("  ✅ UserIntentAgent imported")
        
        from agents.file_suggestion_agent import FileSuggestionAgent
        print("  ✅ FileSuggestionAgent imported")
        
        from agents.schema_proposal_agent import SchemaProposalAgent
        print("  ✅ SchemaProposalAgent imported")
        
        from agents.kg_constructor_agent import KnowledgeGraphConstructorAgent
        print("  ✅ KnowledgeGraphConstructorAgent imported")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_agent_initialization():
    """Test that all agents can be initialized."""
    print("\n🧪 Testing agent initialization...")
    
    try:
        from agents.user_intent_agent import UserIntentAgent
        from agents.file_suggestion_agent import FileSuggestionAgent
        from agents.schema_proposal_agent import SchemaProposalAgent
        from agents.kg_constructor_agent import KnowledgeGraphConstructorAgent
        
        # Test initialization
        user_agent = UserIntentAgent()
        print("  ✅ UserIntentAgent initialized")
        
        file_agent = FileSuggestionAgent()
        print("  ✅ FileSuggestionAgent initialized")
        
        schema_agent = SchemaProposalAgent()
        print("  ✅ SchemaProposalAgent initialized")
        
        kg_agent = KnowledgeGraphConstructorAgent()
        print("  ✅ KnowledgeGraphConstructorAgent initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Initialization error: {e}")
        return False

def test_agent_health_checks():
    """Test agent health check functionality."""
    print("\n🧪 Testing agent health checks...")
    
    try:
        from agents.user_intent_agent import UserIntentAgent
        from agents.file_suggestion_agent import FileSuggestionAgent
        from agents.schema_proposal_agent import SchemaProposalAgent
        from agents.kg_constructor_agent import KnowledgeGraphConstructorAgent
        
        agents = [
            ("UserIntentAgent", UserIntentAgent()),
            ("FileSuggestionAgent", FileSuggestionAgent()),
            ("SchemaProposalAgent", SchemaProposalAgent()),
            ("KnowledgeGraphConstructorAgent", KnowledgeGraphConstructorAgent())
        ]
        
        all_healthy = True
        
        for name, agent in agents:
            health = agent.health_check()
            status = health.get('status', 'unknown')
            
            if status == 'healthy':
                print(f"  ✅ {name}: {status}")
            elif status == 'degraded':
                print(f"  ⚠️ {name}: {status} - {health.get('reason', 'No reason given')}")
            else:
                print(f"  ❌ {name}: {status} - {health.get('reason', 'No reason given')}")
                all_healthy = False
        
        return all_healthy
        
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist and are accessible."""
    print("\n🧪 Testing directory structure...")
    
    try:
        # Check data directories
        data_input = Path("data/input")
        data_output = Path("data/output")
        log_dir = Path("log")
        
        # Check input directory
        if data_input.exists():
            print("  ✅ data/input directory exists")
        else:
            print("  ⚠️ data/input directory missing")
        
        # Check output directory (should be created if missing)
        data_output.mkdir(exist_ok=True)
        if data_output.exists():
            print("  ✅ data/output directory exists")
        else:
            print("  ❌ data/output directory could not be created")
            return False
        
        # Check log directory (should be created if missing)
        log_dir.mkdir(exist_ok=True)
        if log_dir.exists():
            print("  ✅ log directory exists")
        else:
            print("  ❌ log directory could not be created")
            return False
        
        # Test write access to output directory
        test_file = data_output / "test_write.txt"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("  ✅ data/output directory is writable")
        except Exception as e:
            print(f"  ❌ data/output directory not writable: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Directory structure test failed: {e}")
        return False

def test_configuration_system():
    """Test the configuration management system."""
    print("\n🧪 Testing configuration system...")
    
    try:
        from utils.config_manager import get_config
        
        config = get_config()
        if config:
            print("  ✅ Configuration loaded successfully")
            
            # Check key configuration sections
            data_config = config.get('data')
            if data_config:
                print("  ✅ Data configuration present")
            else:
                print("  ⚠️ Data configuration missing")
            
            logging_config = config.get('logging')
            if logging_config:
                print("  ✅ Logging configuration present")
            else:
                print("  ⚠️ Logging configuration missing")
            
            return True
        else:
            print("  ❌ Configuration could not be loaded")
            return False
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_logging_system():
    """Test the logging system."""
    print("\n🧪 Testing logging system...")
    
    try:
        from utils.logging_config import setup_logging, get_system_logger
        
        # Setup logging
        setup_logging()
        print("  ✅ Logging system initialized")
        
        # Test logger creation
        logger = get_system_logger("test")
        logger.info("Test log message")
        print("  ✅ Logger created and test message logged")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Logging test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Running Agent Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Agent Imports", test_agent_imports),
        ("Agent Initialization", test_agent_initialization),
        ("Agent Health Checks", test_agent_health_checks),
        ("Directory Structure", test_directory_structure),
        ("Configuration System", test_configuration_system),
        ("Logging System", test_logging_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent integration is working correctly.")
        return 0
    else:
        print(f"⚠️ {total - passed} test(s) failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
