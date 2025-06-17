#!/usr/bin/env python3
"""
Simple script to verify environment variables are loaded correctly.
"""

import os
from dotenv import load_dotenv

print("🔍 Verifying Environment Variables")
print("=" * 50)

# Load environment variables
load_dotenv()

# Check for LangSmith variables
langchain_tracing = os.getenv("LANGCHAIN_TRACING_V2")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
langchain_project = os.getenv("LANGCHAIN_PROJECT")

print(f"LANGCHAIN_TRACING_V2: {langchain_tracing}")
print(f"LANGCHAIN_API_KEY: {'✅ Set' if langchain_api_key else '❌ Not set'}")
print(f"LANGCHAIN_PROJECT: {langchain_project}")

# Check LLM provider keys
openai_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")

if langchain_tracing == "true" and langchain_api_key:
    print("\n✅ LangSmith tracing should work!")
else:
    print("\n❌ LangSmith tracing will be disabled")
    
print("\n" + "=" * 50) 