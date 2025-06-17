#!/usr/bin/env python3
"""
Quick validation script for LangSmith tracing setup.

This script validates the tracing infrastructure without making actual LLM calls,
allowing you to verify the setup is correct before running full tests.

Usage: python validate_tracing_setup.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_environment():
    """Check environment variables and configuration."""
    print("🔍 Checking Environment Configuration")
    print("=" * 50)
    
    # Check required environment variables
    env_vars = {
        "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2"),
        "LANGCHAIN_API_KEY": os.getenv("LANGCHAIN_API_KEY"),
        "LANGCHAIN_PROJECT": os.getenv("LANGCHAIN_PROJECT"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }
    
    print("\n📋 Environment Variables:")
    for var, value in env_vars.items():
        if value:
            display_value = value if var != "LANGCHAIN_API_KEY" and var != "OPENAI_API_KEY" else f"{value[:8]}..."
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: Not set")
    
    # Check critical variables
    critical_missing = []
    if not env_vars["LANGCHAIN_TRACING_V2"]:
        critical_missing.append("LANGCHAIN_TRACING_V2")
    elif env_vars["LANGCHAIN_TRACING_V2"].lower() != "true":
        print(f"   ⚠️  LANGCHAIN_TRACING_V2 should be 'true', got '{env_vars['LANGCHAIN_TRACING_V2']}'")
    
    if not env_vars["LANGCHAIN_API_KEY"]:
        critical_missing.append("LANGCHAIN_API_KEY")
    
    return len(critical_missing) == 0, critical_missing

def check_imports():
    """Check if all required modules can be imported."""
    print("\n🔧 Checking Module Imports")
    print("=" * 50)
    
    imports_to_test = [
        ("langsmith", "LangSmith tracing library"),
        ("src.utils.tracing", "Custom tracing utilities"),
        ("src.utils.llm", "LLM utilities with tracing"),
        ("src.graph.state", "Agent state management")
    ]
    
    import_errors = []
    
    for module_name, description in imports_to_test:
        try:
            if module_name == "langsmith":
                from langsmith import Client, traceable
                print(f"   ✅ {module_name}: {description}")
            elif module_name == "src.utils.tracing":
                from src.utils.tracing import setup_langsmith_tracing, get_tracing_enabled
                print(f"   ✅ {module_name}: {description}")
            elif module_name == "src.utils.llm":
                from src.utils.llm import call_llm
                print(f"   ✅ {module_name}: {description}")
            elif module_name == "src.graph.state":
                from src.graph.state import AgentState
                print(f"   ✅ {module_name}: {description}")
        except ImportError as e:
            print(f"   ❌ {module_name}: Failed to import - {e}")
            import_errors.append(module_name)
        except Exception as e:
            print(f"   ⚠️  {module_name}: Import warning - {e}")
    
    return len(import_errors) == 0, import_errors

def test_tracing_setup():
    """Test the tracing setup without making LLM calls."""
    print("\n🚀 Testing Tracing Setup")
    print("=" * 50)
    
    try:
        from src.utils.tracing import setup_langsmith_tracing, get_tracing_enabled
        
        # Setup tracing
        print("\n1. Setting up LangSmith tracing...")
        client = setup_langsmith_tracing(environment="development")
        
        # Check if tracing is enabled
        tracing_enabled = get_tracing_enabled()
        print(f"   Tracing Enabled: {'✅ Yes' if tracing_enabled else '❌ No'}")
        
        if client:
            print("   ✅ LangSmith client initialized successfully")
        else:
            print("   ⚠️  LangSmith client not initialized (may be due to missing API key)")
        
        # Test creating session metadata
        print("\n2. Testing session metadata creation...")
        try:
            from src.utils.tracing import create_agent_session_metadata
            
            metadata = create_agent_session_metadata(
                session_id="test_session_123",
                agent_name="test_agent",
                tickers=["AAPL", "MSFT"],
                model_name="gpt-4o-mini",
                model_provider="OpenAI"
            )
            
            print("   ✅ Session metadata created successfully")
            print(f"   📊 Sample metadata: {list(metadata.keys())}")
            
        except Exception as e:
            print(f"   ❌ Session metadata creation failed: {e}")
        
        # Test traceable decorator (without actual function call)
        print("\n3. Testing @traceable decorator...")
        try:
            from langsmith import traceable
            
            @traceable(name="test_function", tags=["test"])
            def dummy_test_function(x: int) -> int:
                return x * 2
            
            print("   ✅ @traceable decorator applied successfully")
            
        except Exception as e:
            print(f"   ❌ @traceable decorator failed: {e}")
        
        return True, None
        
    except Exception as e:
        return False, str(e)

def check_agent_files():
    """Check if agent files exist and have tracing decorators."""
    print("\n📁 Checking Agent Files")
    print("=" * 50)
    
    agent_files = [
        "src/agents/warren_buffett.py",
        "src/agents/charlie_munger.py", 
        "src/agents/ben_graham.py",
        "src/agents/michael_burry.py",
        "src/agents/peter_lynch.py",
        "src/agents/phil_fisher.py",
        "src/agents/cathie_wood.py",
        "src/agents/bill_ackman.py",
        "src/agents/stanley_druckenmiller.py",
        "src/agents/aswath_damodaran.py"
    ]
    
    missing_files = []
    files_without_tracing = []
    
    for agent_file in agent_files:
        if not os.path.exists(agent_file):
            missing_files.append(agent_file)
            print(f"   ❌ {agent_file}: File not found")
        else:
            # Check if file has @traceable decorators
            try:
                with open(agent_file, 'r') as f:
                    content = f.read()
                
                if "@traceable" in content:
                    traceable_count = content.count("@traceable")
                    print(f"   ✅ {agent_file}: {traceable_count} @traceable decorators found")
                else:
                    files_without_tracing.append(agent_file)
                    print(f"   ⚠️  {agent_file}: No @traceable decorators found")
                    
            except Exception as e:
                print(f"   ❌ {agent_file}: Error reading file - {e}")
    
    return len(missing_files) == 0 and len(files_without_tracing) == 0, missing_files + files_without_tracing

def main():
    """Main validation function."""
    print("🔍 LANGSMITH TRACING SETUP VALIDATION")
    print("=" * 80)
    print("Validating tracing infrastructure without making API calls...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_checks_passed = True
    issues = []
    
    # Check environment
    env_ok, env_issues = check_environment()
    if not env_ok:
        all_checks_passed = False
        issues.extend(env_issues)
    
    # Check imports
    imports_ok, import_issues = check_imports()
    if not imports_ok:
        all_checks_passed = False
        issues.extend(import_issues)
    
    # Test tracing setup (only if imports worked)
    if imports_ok:
        tracing_ok, tracing_error = test_tracing_setup()
        if not tracing_ok:
            all_checks_passed = False
            issues.append(f"Tracing setup failed: {tracing_error}")
    
    # Check agent files
    files_ok, file_issues = check_agent_files()
    if not files_ok:
        all_checks_passed = False
        issues.extend(file_issues)
    
    # Print summary
    print("\n" + "="*80)
    print("🎯 VALIDATION SUMMARY")
    print("="*80)
    
    if all_checks_passed:
        print("✅ All validation checks passed!")
        print("🚀 Your tracing setup is ready for testing.")
        print("\nNext steps:")
        print("   1. Run individual tests: python test_warren_buffett_tracing.py")
        print("   2. Run all tests: python test_all_tracing.py")
        print("   3. Check LangSmith dashboard: https://smith.langchain.com/")
    else:
        print("❌ Some validation checks failed:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Please fix these issues before running full tests.")
    
    print(f"\nValidation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 