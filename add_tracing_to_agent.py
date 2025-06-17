#!/usr/bin/env python3
"""
Helper script to add LangSmith tracing to any agent using the Warren Buffett pattern.

Usage:
    python add_tracing_to_agent.py charlie_munger
    python add_tracing_to_agent.py ben_graham
    etc.
"""

import sys
import os
from pathlib import Path

def add_tracing_to_agent(agent_name):
    """Add LangSmith tracing to an agent file."""
    
    agent_file = f"src/agents/{agent_name}.py"
    
    if not os.path.exists(agent_file):
        print(f"❌ Agent file not found: {agent_file}")
        return False
    
    print(f"🔧 Adding LangSmith tracing to {agent_name}")
    
    # Read the current file
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Check if tracing is already added
    if "from langsmith import traceable" in content:
        print(f"✅ {agent_name} already has LangSmith tracing!")
        return True
    
    # Add imports at the top
    import_additions = """from langsmith import traceable
from src.utils.tracing import create_agent_session_metadata"""
    
    # Find the existing imports section
    lines = content.split('\n')
    insert_line = 0
    
    # Find where to insert the new imports (after existing imports)
    for i, line in enumerate(lines):
        if line.startswith('from src.') or line.startswith('import '):
            insert_line = i + 1
    
    # Insert the new imports
    lines.insert(insert_line, import_additions)
    
    # Find the main agent function
    agent_function_line = None
    for i, line in enumerate(lines):
        if f"def {agent_name}_agent(state: AgentState):" in line:
            agent_function_line = i
            break
    
    if agent_function_line is None:
        print(f"❌ Could not find {agent_name}_agent function")
        return False
    
    # Add @traceable decorator before the function
    investment_style = get_investment_style(agent_name)
    decorator = f"""@traceable(
    name="{agent_name}_agent",
    tags=["hedge_fund", "{investment_style}", "{agent_name}"],
    metadata={{"agent_type": "investment_analyst", "style": "{investment_style}"}}
)"""
    
    lines.insert(agent_function_line, decorator)
    
    # Add session metadata creation after session_id creation
    session_metadata_code = f"""    
    # Create session metadata for tracing
    session_metadata = create_agent_session_metadata(
        session_id=session_id,
        agent_name="{agent_name}",
        tickers=tickers,
        model_name=model_name,
        model_provider=model_provider,
        metadata={{
            "investment_style": "{investment_style}",
            "key_metrics": {get_key_metrics(agent_name)}
        }}
    )"""
    
    # Find where to insert session metadata (after session_id creation)
    for i, line in enumerate(lines):
        if 'session_id = f"session_' in line and i > agent_function_line:
            # Find the end of the session creation block
            j = i + 1
            while j < len(lines) and (lines[j].strip() == '' or lines[j].startswith('        ')):
                j += 1
            lines.insert(j, session_metadata_code)
            break
    
    # Write the modified content back
    new_content = '\n'.join(lines)
    
    # Create backup
    backup_file = f"{agent_file}.backup"
    with open(backup_file, 'w') as f:
        f.write(content)
    
    # Write the new content
    with open(agent_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Added basic tracing structure to {agent_name}")
    print(f"📁 Backup saved as: {backup_file}")
    print(f"⚠️  Manual steps still needed:")
    print(f"   1. Add @traceable decorators to analysis functions")
    print(f"   2. Add @traceable to generate_{agent_name}_output function")
    print(f"   3. Test with: python test_{agent_name}_tracing.py")
    
    return True

def get_investment_style(agent_name):
    """Get the investment style for tagging."""
    style_map = {
        'warren_buffett': 'value_investing',
        'charlie_munger': 'value_investing', 
        'ben_graham': 'value_investing',
        'michael_burry': 'value_investing',
        'peter_lynch': 'growth_investing',
        'phil_fisher': 'growth_investing',
        'cathie_wood': 'growth_investing',
        'bill_ackman': 'activist_investing',
        'stanley_druckenmiller': 'macro_trading',
        'aswath_damodaran': 'academic_valuation',
        'fundamentals': 'fundamental_analysis',
        'sentiment': 'sentiment_analysis',
        'valuation': 'valuation_analysis',
        'technicals': 'technical_analysis',
        'portfolio_manager': 'portfolio_management',
        'risk_manager': 'risk_management'
    }
    return style_map.get(agent_name, 'investment_analysis')

def get_key_metrics(agent_name):
    """Get key metrics for the agent."""
    metrics_map = {
        'warren_buffett': '["ROE", "debt_to_equity", "operating_margin", "intrinsic_value"]',
        'charlie_munger': '["moat_strength", "management_quality", "predictability"]',
        'ben_graham': '["PE_ratio", "PB_ratio", "current_ratio", "debt_ratio"]',
        'michael_burry': '["value_metrics", "contrarian_signals", "market_inefficiencies"]',
        'peter_lynch': '["PEG_ratio", "earnings_growth", "revenue_growth"]',
        'phil_fisher': '["growth_metrics", "innovation", "management_depth"]',
        'cathie_wood': '["innovation_metrics", "disruption_potential", "growth_trajectory"]',
        'bill_ackman': '["catalyst_analysis", "shareholder_value", "operational_improvements"]',
        'stanley_druckenmiller': '["macro_trends", "momentum", "risk_reward"]',
        'aswath_damodaran': '["DCF", "multiples", "risk_premium", "growth_assumptions"]'
    }
    return metrics_map.get(agent_name, '["analysis_score", "confidence", "reasoning"]')

def create_test_script(agent_name):
    """Create a test script for the agent."""
    
    investment_style = get_investment_style(agent_name)
    
    test_content = f'''#!/usr/bin/env python3
"""
Test script for {agent_name} agent with LangSmith tracing.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.utils.tracing import setup_langsmith_tracing, get_tracing_enabled
from src.agents.{agent_name} import {agent_name}_agent
from src.graph.state import AgentState

def test_{agent_name}_with_tracing():
    """Test {agent_name} agent with tracing enabled."""
    
    print("🚀 Testing {agent_name.replace('_', ' ').title()} Agent with LangSmith Tracing")
    print("=" * 60)
    
    # Setup tracing
    print("\\n1. Setting up LangSmith tracing...")
    client = setup_langsmith_tracing(environment="development")
    
    if not get_tracing_enabled():
        print("⚠️  LangSmith tracing is not enabled.")
        print("   Continuing without tracing...")
    
    # Create test state
    print("\\n2. Creating test analysis state...")
    test_ticker = "AAPL"  # Use Apple as test case
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    state = AgentState(
        messages=[],
        data={{
            "tickers": [test_ticker],
            "end_date": end_date,
            "start_date": "2023-01-01",
            "analyst_signals": {{}}
        }},
        metadata={{
            "model_name": "gpt-4o-mini",
            "model_provider": "OpenAI", 
            "show_reasoning": True
        }},
        session_id=f"test_{agent_name}_session_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
    )
    
    print(f"   📊 Analyzing ticker: {{test_ticker}}")
    print(f"   📅 End date: {{end_date}}")
    print(f"   🤖 Model: {{state['metadata']['model_name']}} ({{state['metadata']['model_provider']}})")
    print(f"   💭 Investment Style: {investment_style}")
    
    # Run {agent_name} analysis
    print(f"\\n3. Running {agent_name.replace('_', ' ').title()} analysis for {{test_ticker}}...")
    try:
        result = {agent_name}_agent(state)
        
        print("✅ Analysis completed successfully!")
        
        # Display results
        if "analyst_signals" in result["data"] and "{agent_name}_agent" in result["data"]["analyst_signals"]:
            analysis = result["data"]["analyst_signals"]["{agent_name}_agent"][test_ticker]
            
            print(f"\\n📈 Results for {{test_ticker}}:")
            print(f"   Signal: {{analysis['signal'].upper()}}")
            print(f"   Confidence: {{analysis['confidence']:.1f}}%") 
            print(f"   Reasoning: {{analysis['reasoning'][:200]}}...")
            
            if get_tracing_enabled():
                print(f"\\n🔍 Tracing Information:")
                print(f"   Session ID: {{state['session_id']}}")
                print(f"   Project: {{os.getenv('LANGCHAIN_PROJECT', 'ai-hedge-fund-dev')}}")
                print(f"   Investment Style: {investment_style}")
                print(f"   Check your LangSmith dashboard for detailed traces!")
                print(f"   URL: https://smith.langchain.com/")
        
    except Exception as e:
        print(f"❌ Analysis failed: {{str(e)}}")
        print(f"   Make sure you have the required API keys configured")
        
        if get_tracing_enabled():
            print(f"   - Check LangSmith for error traces")
    
    print(f"\\n4. Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_{agent_name}_with_tracing()
'''
    
    test_file = f"test_{agent_name}_tracing.py"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"📝 Created test script: {test_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python add_tracing_to_agent.py <agent_name>")
        print("Example: python add_tracing_to_agent.py charlie_munger")
        print("\\nAvailable agents:")
        print("  Investment Style: charlie_munger, ben_graham, michael_burry, peter_lynch")
        print("  Investment Style: phil_fisher, cathie_wood, bill_ackman, stanley_druckenmiller")
        print("  Investment Style: aswath_damodaran")
        print("  Analysis: fundamentals, sentiment, valuation, technicals")
        print("  Management: portfolio_manager, risk_manager")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    
    print(f"🎯 Adding LangSmith tracing to {agent_name} agent...")
    
    success = add_tracing_to_agent(agent_name)
    
    if success:
        create_test_script(agent_name)
        print(f"\\n🎉 Ready to implement tracing for {agent_name}!")
        print(f"\\nNext steps:")
        print(f"1. Review the modified file: src/agents/{agent_name}.py")
        print(f"2. Add @traceable decorators to analysis functions manually")
        print(f"3. Test with: python test_{agent_name}_tracing.py")
        print(f"4. Check LangSmith dashboard for traces")

if __name__ == "__main__":
    main() 