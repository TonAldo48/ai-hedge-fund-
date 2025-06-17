#!/usr/bin/env python3
"""
Comprehensive test runner for all LangSmith tracing implementations.

This script runs all individual agent tracing tests and provides a summary
of results to ensure complete tracing coverage across the hedge fund system.

Usage: python test_all_tracing.py
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.tracing import setup_langsmith_tracing, get_tracing_enabled

# List of all agent tracing tests
AGENT_TESTS = [
    {
        "name": "Warren Buffett",
        "file": "test_warren_buffett_tracing.py",
        "style": "value_investing",
        "description": "Classic value investing with moats and owner earnings"
    },
    {
        "name": "Charlie Munger", 
        "file": "test_charlie_munger_tracing.py",
        "style": "value_investing",
        "description": "Mental models and concentrated value investing"
    },
    {
        "name": "Ben Graham",
        "file": "test_ben_graham_tracing.py", 
        "style": "classic_value_investing",
        "description": "Deep value with margin of safety"
    },
    {
        "name": "Michael Burry",
        "file": "test_michael_burry_tracing.py",
        "style": "deep_value_contrarian", 
        "description": "Contrarian deep value with distressed opportunities"
    },
    {
        "name": "Peter Lynch",
        "file": "test_peter_lynch_tracing.py",
        "style": "growth_at_reasonable_price",
        "description": "GARP strategy with PEG ratio focus"
    },
    {
        "name": "Phil Fisher",
        "file": "test_phil_fisher_tracing.py",
        "style": "quality_growth_investing",
        "description": "Quality growth with R&D and management focus"
    },
    {
        "name": "Cathie Wood",
        "file": "test_cathie_wood_tracing.py",
        "style": "disruptive_innovation",
        "description": "Disruptive innovation and exponential growth"
    },
    {
        "name": "Bill Ackman", 
        "file": "test_bill_ackman_tracing.py",
        "style": "activist_value_investing",
        "description": "Activist investing with brand focus"
    },
    {
        "name": "Stanley Druckenmiller",
        "file": "test_stanley_druckenmiller_tracing.py",
        "style": "macro_momentum_trading",
        "description": "Macro momentum with trend following"
    },
    {
        "name": "Aswath Damodaran",
        "file": "test_aswath_damodaran_tracing.py", 
        "style": "academic_valuation",
        "description": "Rigorous DCF and academic valuation"
    }
]

def check_prerequisites() -> Tuple[bool, List[str]]:
    """Check if all prerequisites for tracing are met."""
    issues = []
    
    print("🔍 Checking prerequisites...")
    
    # Check environment variables
    required_vars = [
        ("LANGCHAIN_TRACING_V2", "true"),
        ("LANGCHAIN_API_KEY", None),
        ("OPENAI_API_KEY", None)
    ]
    
    for var, expected_value in required_vars:
        value = os.getenv(var)
        if not value:
            issues.append(f"Missing environment variable: {var}")
        elif expected_value and value != expected_value:
            issues.append(f"Wrong value for {var}: expected '{expected_value}', got '{value}'")
    
    # Check if test files exist
    for test in AGENT_TESTS:
        if not os.path.exists(test["file"]):
            issues.append(f"Missing test file: {test['file']}")
    
    # Check if source files exist
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
    
    for agent_file in agent_files:
        if not os.path.exists(agent_file):
            issues.append(f"Missing agent file: {agent_file}")
    
    return len(issues) == 0, issues

def run_single_test(test_file: str) -> Tuple[bool, str, float]:
    """Run a single tracing test and return success status, output, and execution time."""
    start_time = time.time()
    
    try:
        # Run the test as a subprocess
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        execution_time = time.time() - start_time
        
        # Check if test passed
        success = result.returncode == 0 and "✅" in result.stdout
        
        # Get output (prefer stdout, fallback to stderr)
        output = result.stdout if result.stdout else result.stderr
        
        return success, output, execution_time
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return False, "Test timed out after 2 minutes", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return False, f"Error running test: {str(e)}", execution_time

def print_summary(results: List[Dict]) -> None:
    """Print a comprehensive summary of all test results."""
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE TRACING TEST SUMMARY")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"\n📊 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Group by investment style
    styles = {}
    for result in results:
        style = result["style"]
        if style not in styles:
            styles[style] = {"passed": 0, "failed": 0, "agents": []}
        
        if result["success"]:
            styles[style]["passed"] += 1
        else:
            styles[style]["failed"] += 1
        styles[style]["agents"].append(result)
    
    print(f"\n📈 Results by Investment Style:")
    for style, data in styles.items():
        total = data["passed"] + data["failed"]
        success_rate = (data["passed"] / total) * 100 if total > 0 else 0
        print(f"   {style.replace('_', ' ').title()}: {data['passed']}/{total} ({success_rate:.1f}%)")
    
    # Show detailed results
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} {result['name']} ({result['execution_time']:.1f}s)")
        if not result["success"]:
            error_lines = result["output"].split('\n')
            error_msg = next((line for line in error_lines if "❌" in line or "Error" in line), "Unknown error")
            print(f"        Error: {error_msg}")
    
    # Tracing status
    print(f"\n🔍 Tracing Status:")
    print(f"   LangSmith Enabled: {'✅ Yes' if get_tracing_enabled() else '❌ No'}")
    print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'Not set')}")
    print(f"   API Key: {'✅ Configured' if os.getenv('LANGCHAIN_API_KEY') else '❌ Missing'}")
    
    if get_tracing_enabled():
        print(f"\n🌐 View traces at: https://smith.langchain.com/")
        print(f"   Look for project: {os.getenv('LANGCHAIN_PROJECT', 'ai-hedge-fund-dev')}")

def main():
    """Main test runner function."""
    print("🚀 COMPREHENSIVE LANGSMITH TRACING TEST SUITE")
    print("="*80)
    print("Testing all investment agent tracing implementations...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    prereq_ok, issues = check_prerequisites()
    
    if not prereq_ok:
        print("\n❌ Prerequisites check failed:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Please fix these issues before running the tests.")
        return 1
    
    print("✅ Prerequisites check passed!")
    
    # Setup tracing
    print("\n🔧 Setting up LangSmith tracing...")
    client = setup_langsmith_tracing(environment="development")
    
    if not get_tracing_enabled():
        print("⚠️  Warning: LangSmith tracing is not fully enabled.")
        print("   Tests will run but traces may not be captured.")
    
    # Run all tests
    print(f"\n🧪 Running {len(AGENT_TESTS)} agent tracing tests...")
    results = []
    
    for i, test in enumerate(AGENT_TESTS, 1):
        print(f"\n[{i}/{len(AGENT_TESTS)}] Testing {test['name']} ({test['style']})...")
        print(f"   Description: {test['description']}")
        
        success, output, exec_time = run_single_test(test["file"])
        
        result = {
            "name": test["name"],
            "file": test["file"],
            "style": test["style"],
            "success": success,
            "output": output,
            "execution_time": exec_time
        }
        results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status} in {exec_time:.1f}s")
        
        # Brief pause between tests
        time.sleep(0.5)
    
    # Print comprehensive summary
    print_summary(results)
    
    # Exit with appropriate code
    failed_count = sum(1 for r in results if not r["success"])
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 