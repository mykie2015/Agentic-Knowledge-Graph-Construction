#!/usr/bin/env python3
"""
Test script to verify User Intent Agent configuration loading.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_user_intent_config():
    """Test User Intent Agent configuration loading."""
    print("🧪 Testing User Intent Agent Configuration Loading")
    print("=" * 60)
    
    try:
        from agents.user_intent_agent import UserIntentAgent
        
        # Test default initialization
        print("1. Testing default initialization...")
        agent = UserIntentAgent()
        
        # Check configuration summary
        config_summary = agent.get_configuration_summary()
        print("   Configuration Summary:")
        for key, value in config_summary.items():
            print(f"     {key}: {value}")
        
        # Test health check with configuration
        print("\n2. Testing health check with configuration...")
        health = agent.health_check()
        print(f"   Health Status: {health['status']}")
        if 'configuration' in health:
            print("   Configuration in health check: ✅")
        else:
            print("   Configuration in health check: ❌")
        
        # Test system prompt customization
        print("\n3. Testing system prompt...")
        system_prompt = agent.get_system_prompt()
        if "Valid graph types are:" in system_prompt:
            print("   System prompt includes valid graph types: ✅")
        else:
            print("   System prompt includes valid graph types: ❌")
        
        # Test configuration updates
        print("\n4. Testing runtime configuration updates...")
        original_style = agent.get_config_value('conversation_style', 'unknown')
        print(f"   Original conversation style: {original_style}")
        
        agent.update_config({
            'conversation_style': 'formal',
            'domain_specialization': 'business'
        })
        
        new_style = agent.get_config_value('conversation_style', 'unknown')
        print(f"   Updated conversation style: {new_style}")
        
        # Test validation with different strictness
        print("\n5. Testing goal validation...")
        test_goal = {
            "description": "Build a simple graph",
            "graph_type": "domain"
        }
        
        errors = agent.validate_goal(test_goal)
        print(f"   Validation errors for '{test_goal['description']}': {len(errors)}")
        if errors:
            for error in errors:
                print(f"     - {error}")
        
        # Test with strict validation
        agent.update_config({'validation_strictness': 'strict'})
        strict_errors = agent.validate_goal(test_goal)
        print(f"   Strict validation errors: {len(strict_errors)}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_file_parsing():
    """Test configuration file parsing specifically."""
    print("\n🧪 Testing Configuration File Parsing")
    print("=" * 60)
    
    try:
        config_file = Path(__file__).parent / "config" / "user-intent.md"
        
        if not config_file.exists():
            print(f"❌ Configuration file not found: {config_file}")
            return False
        
        print(f"✅ Configuration file found: {config_file}")
        
        # Check file content
        with open(config_file, 'r') as f:
            content = f.read()
        
        print(f"   File size: {len(content)} characters")
        
        # Check for key sections
        sections = [
            "Valid Graph Types",
            "System Prompt Configuration",
            "Goal Validation Rules",
            "Conversation Flow"
        ]
        
        for section in sections:
            if section in content:
                print(f"   ✅ Found section: {section}")
            else:
                print(f"   ❌ Missing section: {section}")
        
        # Check for system prompt
        import re
        prompt_match = re.search(r'```markdown(.*?)```', content, re.DOTALL)
        if prompt_match:
            print(f"   ✅ Found system prompt ({len(prompt_match.group(1))} characters)")
        else:
            print(f"   ❌ System prompt not found in expected format")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration file test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing User Intent Agent Configuration System")
    print("=" * 70)
    
    config_test = test_config_file_parsing()
    agent_test = test_user_intent_config()
    
    print("\n" + "=" * 70)
    if config_test and agent_test:
        print("🎉 All configuration tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)
